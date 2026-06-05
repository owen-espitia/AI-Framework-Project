# Item Manager — Full Stack Application

A full-stack Item Management application with an AI agent built on **FastAPI**, **MongoDB**, **Ollama (llama3.2)**, and **Nginx**, containerized with Docker Compose.

## Quick Start

```bash
docker-compose up --build
```

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| API + Swagger | http://localhost:8000/docs |
| Ollama | http://localhost:11434 |
| MongoDB | mongodb://localhost:27017 |

```bash
docker-compose down       # stop
docker-compose down -v    # stop and remove data volumes
```

---

## Architecture

### Services

| Service | Tech | Port |
|---|---|---|
| `api` | FastAPI + Uvicorn | 8000 |
| `mongodb` | MongoDB | 27017 |
| `frontend` | Nginx (static SPA) | 3000 |
| `ollama` | Ollama LLM server | 11434 |
| `model-service` | FastAPI (PyTorch) | 8001 (optional) |

All services communicate over a Docker bridge network (`app-network`). Nginx proxies all API traffic from the browser to the `api` container.

### Project Structure

```
├── api/
│   ├── main.py               # All API endpoints + agent loop
│   ├── dal.py                # MongoDB data access layer
│   ├── models.py             # Pydantic request/response models
│   ├── model_training.py     # PyTorch SimpleClassifier definition
│   ├── Dockerfile
│   └── init-mongo.js         # MongoDB seed script
├── model_service/
│   ├── serve.py              # Iris classifier inference endpoint
│   ├── model_training.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── model/
│       └── refined_simple_classifier.pth
├── front-end/
│   ├── Dockerfile
│   ├── nginx.conf
│   └── static/
│       ├── index.html
│       └── style.css
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## API Endpoints

### Items

| Method | Path | Description |
|---|---|---|
| GET | `/items` | List all items |
| GET | `/items/{id}` | Get single item |
| POST | `/items` | Create item — body: `{name, price, description}` |
| PUT | `/items/{id}` | Update item |
| DELETE | `/items/{id}` | Delete item |

### AI

| Method | Path | Description |
|---|---|---|
| POST | `/chat` | Conversational chat with llama3.2 |
| POST | `/analyze` | Structured content analysis (sentiment, categories, tags, summary) |
| POST | `/ask` | RAG query over inventory (TF-IDF retrieval + LLM answer) |
| POST | `/agent` | Agentic task execution with tool calling and reasoning trace |

### ML

| Method | Path | Description |
|---|---|---|
| POST | `/predict` | Iris flower species classification via model-service |

---

## AI Agent

### Path Chosen: A — From Scratch

The agent loop is implemented manually around the Ollama Python client's tool-calling API with no external agent framework. This was the right choice for this project for two reasons: (1) the existing codebase already uses the `ollama` library directly, so there's no new dependency to justify, and (2) Path A makes every step of the agent loop explicit — the message list, the tool dispatch, the guardrail checks — which is the most transparent approach for a learning context. LangChain or a provider SDK would have hidden the loop inside abstractions, making it harder to understand what's actually happening and harder to debug when llama3.2 misbehaves on tool formatting.

### Agent Architecture

```
POST /agent
    │
    ▼
System prompt + user task
    │
    ▼
┌─────────────────────────────┐
│  Agent loop  (max 10 steps) │
│                             │
│  ollama.chat(tools=...)     │──► no tool_calls → return final answer
│         │                   │
│  tool_calls present?        │
│         │                   │
│  destructive + unconfirmed? │──► return needs_confirmation (pause)
│         │                   │
│  execute_tool(name, args)   │──► append tool result to messages
│         │                   │
│  loop back to ollama.chat   │
└─────────────────────────────┘
    │
    ▼
{ result, steps, status }
```

The model decides which tool to call and with what arguments. The Python code executes the function and feeds the result back into the message history. The model never runs code — it only produces structured tool call requests.

### Tools

#### `search_items`
- **Description:** Search for items in the inventory by keyword. Matches against item name and description fields. Always called before `create_item` to avoid duplicates.
- **API call:** Internal — `dal.read_items()` filtered client-side by keyword match
- **Input:** `{ "query": string }`
- **Output:** JSON with `found` count and matching `items` array, or a not-found message

#### `create_item`
- **Description:** Create a new item in the inventory. The model is instructed to only call this after a search confirms the item doesn't already exist.
- **API call:** Internal — `dal.create_item(Item(...))`
- **Input:** `{ "name": string, "price": number, "description": string }`
- **Output:** JSON with `success`, `id`, and `name`, or an error message
- **Guardrail:** Requires explicit user confirmation before executing (see below)

#### `query_knowledge`
- **Description:** Natural language question answering over the inventory using RAG. Retrieves semantically relevant items via TF-IDF cosine similarity, then generates an answer with llama3.2 using those items as context.
- **API call:** Internal — calls `_rag_query()`, which is the same logic as `POST /ask`
- **Input:** `{ "query": string }`
- **Output:** AI-generated answer string grounded in the most relevant inventory items

### RAG Implementation (`POST /ask`)

The `/ask` endpoint provides lightweight retrieval-augmented generation over the item inventory:

1. Fetch all items from MongoDB
2. Build a TF-IDF matrix from item `name + description` strings using scikit-learn's `TfidfVectorizer`
3. Compute cosine similarity between the query vector and every item vector
4. Select up to 3 items with similarity > 0.01
5. Inject those items as context into a llama3.2 prompt and return the generated answer

This avoids the need for a vector database or embedding model while still giving the agent grounded, context-aware answers about the inventory.

### Guardrails

#### Max iterations
The agent loop is capped at `MAX_AGENT_STEPS = 10`. If the model hasn't produced a final answer by step 10, the endpoint returns with `status: "max_steps_reached"` and the partial trace. This prevents runaway loops where a confused model keeps calling tools indefinitely, consuming LLM compute and potentially mutating state in unexpected ways.

#### Tool confirmation for destructive actions
`create_item` is in the `DESTRUCTIVE_TOOLS` set. When the model requests this tool and `auto_confirm_create` is `False` (the default), the agent loop stops and returns `status: "needs_confirmation"` with the pending tool name and arguments. The frontend surfaces a modal showing exactly what the agent wants to create. The user must click **Approve** to re-run with `auto_confirm_create: true`, or **Deny** to cancel. This ensures the agent cannot write to the database without the user seeing and approving the specific action first.

#### Tool error handling
Every tool call is wrapped in a `try/except`. If a tool raises an exception (MongoDB down, bad input, sklearn error), the error is caught and returned as a plain-text error string back to the model rather than crashing the loop. The model can then decide to retry with different arguments or give up gracefully. Surfacing stack traces to the model doesn't help it recover; a human-readable error string does.

### Example Task and Trace

**Task:** `"Find all items related to keyboards. If there aren't any, create one."`

**Step 1 — search_items**
```json
{
  "tool": "search_items",
  "input": { "query": "keyboard" },
  "output": "{\"found\": 0, \"items\": [], \"message\": \"No items found matching 'keyboard'\"}"
}
```

**Step 2 — (needs_confirmation returned)**
The agent decides to call `create_item`. The endpoint pauses and returns:
```json
{
  "status": "needs_confirmation",
  "pending_action": {
    "tool": "create_item",
    "args": {
      "name": "Mechanical Keyboard",
      "price": 89.99,
      "description": "Full-size mechanical keyboard with Cherry MX switches and RGB backlight."
    }
  },
  "steps": [{ "tool": "search_items", ... }]
}
```
The frontend shows the confirmation modal. User clicks **Approve**.

**Step 3 — create_item (re-run with auto_confirm_create: true)**
```json
{
  "tool": "create_item",
  "input": {
    "name": "Mechanical Keyboard",
    "price": 89.99,
    "description": "Full-size mechanical keyboard with Cherry MX switches and RGB backlight."
  },
  "output": "{\"success\": true, \"id\": \"6649f3a2c1e4b900123abc01\", \"name\": \"Mechanical Keyboard\"}"
}
```

**Final response**
```json
{
  "result": "I searched the inventory for keyboards and found none. I created a new item: 'Mechanical Keyboard' at $89.99.",
  "steps": [ ... ],
  "status": "complete"
}
```

---

## Technologies

| Layer | Technology |
|---|---|
| Backend | FastAPI, Uvicorn, Pydantic |
| Database | MongoDB, PyMongo |
| LLM | Ollama, llama3.2 |
| RAG | scikit-learn (TF-IDF + cosine similarity) |
| ML inference | PyTorch (SimpleClassifier, Iris dataset) |
| Frontend | Vanilla JS, Nginx |
| Containerization | Docker, Docker Compose |

## Environment Variables

Set in `docker-compose.yml`:

| Variable | Default | Description |
|---|---|---|
| `MONGODB_URL` | `mongodb://mongodb:27017` | MongoDB connection string |
| `MONGODB_DATABASE` | `yourdb` | Database name |
| `MONGODB_COLLECTION` | `items` | Collection name |
| `OLLAMA_URL` | `http://ollama:11434` | Ollama service URL |

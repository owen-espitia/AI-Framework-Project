import os
import ollama
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import Item, PredictionRequest, ChatRequest, ChatResponse, AnalyzeRequest, AskRequest, AgentRequest
from dal import MongoDAL

import requests

dal = None
app = FastAPI()

model = None

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    global model, dal
    dal = MongoDAL()

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")

# ── Items ──────────────────────────────────────────────────────────────────────

@app.get("/items", status_code=200)
def read_items():
    return dal.read_items()

@app.get("/items/{item_id}", status_code=200)
def get_item(item_id: str):
    try:
        return dal.read_item(item_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/items", status_code=201)
def create_item(item: Item):
    try:
        item_id = dal.create_item(item)
        return {"id": item_id, "name": item.name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create item: {str(e)}")

@app.put("/items/{item_id}", status_code=200)
def update_item(item_id: str, new_item: Item):
    try:
        dal.update_item(item_id, new_item)
        return {"id": item_id, "updated_item": new_item.model_dump()}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update item: {str(e)}")

@app.delete("/items/{item_id}", status_code=200)
def delete_item(item_id: str):
    try:
        dal.delete_item(item_id)
        return {"message": f"Item with ID {item_id} deleted successfully."}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete item: {str(e)}")

# ── ML Predict ─────────────────────────────────────────────────────────────────

@app.post("/predict")
def predict(req: PredictionRequest):
    print(f"api received prediction request: {req}")
    features = [req.sepal_length, req.sepal_width, req.petal_length, req.petal_width]
    try:
        response = requests.post(
            "http://model-service:8001/predict",
            json={"features": features},
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Model service error: {str(e)}")

# ── Chat ───────────────────────────────────────────────────────────────────────

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    messages = [
        {"role": "system", "content": "You are a helpful assistant for inventory items. Talk like you are a bumble bee pretending to be a human, but be concise and helpful."}
    ]
    messages.extend(request.conversation_history)
    messages.append({"role": "user", "content": request.message})

    try:
        client = ollama.Client(host=OLLAMA_URL)
        response = client.chat(
            model="llama3.2",
            messages=messages,
            options={'temperature': 0.7, 'num_predict': 512}
        )
        reply = response['message']['content']

        updated_history = request.conversation_history + [
            {"role": "user", "content": request.message},
            {"role": "assistant", "content": reply}
        ]
        return ChatResponse(reply=reply, conversation_history=updated_history)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ── Analyze ────────────────────────────────────────────────────────────────────

@app.post("/analyze")
def analyze(request: AnalyzeRequest):
    system_prompt = """You are a data analysis assistant. Analyze the provided content
            and respond with ONLY valid JSON in this exact format:
            {
                "categories": ["category1", "category2"],
                "tags": ["tag1", "tag2", "tag3"],
                "sentiment": "positive" | "negative" | "neutral",
                "summary": "one sentence summary"
            }
            Do not include any text outside the JSON object."""

    few_shot = """Example:
Input: "The new laptop is incredibly fast and the battery lasts all day. Best purchase this year."
Output: {"categories": ["technology", "review"], "tags": ["laptop", "performance", "battery"], "sentiment": "positive", "summary": "Highly positive review praising laptop speed and battery life."}
Input: "The honey I bought off of this website is amazing!."
Output: {"categories": ["homegoods", "review"], "tags": ["food", "tastey"], "sentiment": "positive", "summary": "Highly positive review praising the high quality of honey."}"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": few_shot + "\n\nNow analyze this:\n" + request.content}
    ]

    try:
        client = ollama.Client(host=OLLAMA_URL)
        response = client.chat(
            model="llama3.2",
            messages=messages,
            options={'temperature': 0.2, 'num_predict': 512}
        )
        raw = response['message']['content']

        result = json.loads(raw)

        required = ["categories", "tags", "sentiment", "summary"]
        for field in required:
            if field not in result:
                raise ValueError(f"Missing field: {field}")
        return result

    except json.JSONDecodeError:
        raise HTTPException(status_code=422, detail="LLM returned invalid JSON. Try again.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ── RAG ────────────────────────────────────────────────────────────────────────

def _rag_query(query: str) -> dict:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    items = dal.read_items()
    if not items:
        return {"answer": "The inventory is empty.", "relevant_items": []}

    corpus = [f"{item['name']} {item['description']}" for item in items]

    try:
        vectorizer = TfidfVectorizer(stop_words='english', min_df=1)
        tfidf = vectorizer.fit_transform(corpus + [query])
        sims = cosine_similarity(tfidf[-1:], tfidf[:-1])[0]
    except ValueError:
        return {"answer": "Could not process the query.", "relevant_items": []}

    top_n = min(3, len(items))
    top_idx = sims.argsort()[-top_n:][::-1]
    relevant = [items[i] for i in top_idx if sims[i] > 0.01]

    if not relevant:
        return {"answer": "No relevant items found for your query.", "relevant_items": []}

    context = "\n".join(
        [f"- {i['name']} (${i['price']}): {i['description']}" for i in relevant]
    )

    client = ollama.Client(host=OLLAMA_URL)
    resp = client.chat(
        model="llama3.2",
        messages=[{
            "role": "user",
            "content": f"Based on these inventory items:\n{context}\n\nAnswer concisely: {query}"
        }],
        options={'temperature': 0.3, 'num_predict': 256}
    )
    return {"answer": resp['message']['content'], "relevant_items": relevant}


@app.post("/ask")
def ask(request: AskRequest):
    try:
        return _rag_query(request.query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ── Agent tools ────────────────────────────────────────────────────────────────

AGENT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_items",
            "description": (
                "Search for items in the inventory database by keyword. "
                "Returns matching items with name, price, and description. "
                "Always search before creating to avoid duplicates."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search term or keyword to find matching items"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_item",
            "description": (
                "Create a new item in the inventory. "
                "Only call this after a search confirms the item does not already exist."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name":        {"type": "string", "description": "Name of the item"},
                    "price":       {"type": "number", "description": "Price in USD"},
                    "description": {"type": "string", "description": "Detailed description of the item"}
                },
                "required": ["name", "price", "description"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "query_knowledge",
            "description": (
                "Query the inventory knowledge base with a natural language question. "
                "Uses semantic search to find relevant items and returns an AI-generated answer."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language question about the inventory"
                    }
                },
                "required": ["query"]
            }
        }
    }
]

DESTRUCTIVE_TOOLS = {"create_item"}
MAX_AGENT_STEPS = 10


def _tool_search_items(query: str) -> str:
    items = dal.read_items()
    q = query.lower()
    matches = [i for i in items if q in i['name'].lower() or q in i['description'].lower()]
    if not matches:
        return json.dumps({"found": 0, "items": [], "message": f"No items found matching '{query}'"})
    return json.dumps({"found": len(matches), "items": matches})


def _tool_create_item(name: str, price, description: str) -> str:
    try:
        item = Item(name=name, price=float(price), description=description)
        item_id = dal.create_item(item)
        return json.dumps({"success": True, "id": item_id, "name": name})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


def _tool_query_knowledge(query: str) -> str:
    try:
        result = _rag_query(query)
        return result["answer"]
    except Exception as e:
        return f"Knowledge base error: {str(e)}"


def _extract_str(tool_args: dict, key: str, default: str = "") -> str:
    val = tool_args.get(key, default)
    # llama3.2 occasionally wraps string values in a dict; coerce to str
    if isinstance(val, dict):
        val = val.get("value", val.get(key, default))
    return str(val) if val is not None else default


def _execute_tool(tool_name: str, tool_args) -> str:
    # Ollama may return arguments as a JSON string on some server versions
    if isinstance(tool_args, str):
        try:
            tool_args = json.loads(tool_args)
        except (json.JSONDecodeError, ValueError):
            tool_args = {}
    if not isinstance(tool_args, dict):
        tool_args = {}

    if tool_name == "search_items":
        return _tool_search_items(_extract_str(tool_args, "query"))
    if tool_name == "create_item":
        price_raw = tool_args.get("price", 0)
        try:
            price = float(price_raw)
        except (TypeError, ValueError):
            price = 0.0
        return _tool_create_item(
            _extract_str(tool_args, "name"),
            price,
            _extract_str(tool_args, "description")
        )
    if tool_name == "query_knowledge":
        return _tool_query_knowledge(_extract_str(tool_args, "query"))
    return f"Unknown tool: {tool_name}"

# ── Agent endpoint ─────────────────────────────────────────────────────────────

@app.post("/agent")
def agent(request: AgentRequest):
    client = ollama.Client(host=OLLAMA_URL)

    messages = [
        {
            "role": "system",
            "content": (
                "You are an inventory management agent. Use your tools to complete tasks. "
                "Use search_items to find existing items, create_item to add new ones, "
                "and query_knowledge to answer inventory questions. "
                "Always search before creating to avoid duplicates. Be concise."
            )
        },
        {"role": "user", "content": request.task}
    ]

    steps = []

    for _ in range(MAX_AGENT_STEPS):
        try:
            response = client.chat(
                model="llama3.2",
                messages=messages,
                tools=AGENT_TOOLS,
                options={'temperature': 0.1, 'num_predict': 1024}
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"LLM error: {str(e)}")

        msg = response.message
        content = msg.content or ""
        tool_calls = msg.tool_calls or []

        # No tool calls → the model has a final answer
        if not tool_calls:
            return {"result": content or "Task completed.", "steps": steps, "status": "complete"}

        # Append assistant turn (with tool_calls) as a plain dict to avoid serialization issues
        assistant_dict = {"role": "assistant", "content": content}
        if tool_calls:
            assistant_dict["tool_calls"] = [
                {"function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                for tc in tool_calls
            ]
        messages.append(assistant_dict)

        # Process each requested tool call
        for tc in tool_calls:
            tool_name = tc.function.name
            tool_args = tc.function.arguments

            # Guardrail: pause and surface destructive actions for user approval
            if tool_name in DESTRUCTIVE_TOOLS and not request.auto_confirm_create:
                return {
                    "result": "",
                    "steps": steps,
                    "status": "needs_confirmation",
                    "pending_action": {"tool": tool_name, "args": tool_args}
                }

            # Execute with error handling so a bad tool result doesn't crash the loop
            try:
                output = _execute_tool(tool_name, tool_args)
            except Exception as e:
                output = f"Tool '{tool_name}' error: {str(e)}"

            steps.append({"tool": tool_name, "input": tool_args, "output": output})
            messages.append({"role": "tool", "content": output})

    return {
        "result": "Maximum steps reached without completing the task.",
        "steps": steps,
        "status": "max_steps_reached"
    }

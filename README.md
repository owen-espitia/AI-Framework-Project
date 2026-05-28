# Item Manager - Full Stack Application

## Project Overview
A full-stack Item Management application built with **FastAPI**, **MongoDB**, and **Nginx**. The application is containerized using Docker Compose and consists of three services: an API backend, a MongoDB database, and a Nginx-based frontend.

## Architecture

### Services:
1. **API** (FastAPI) - Backend REST API running on port 8000
2. **MongoDB** - Database service running on port 27017
3. **Frontend** (Nginx) - Web UI served on port 3000
4. **Model Service** (FastAPI) - ML model inference service running on port 8001

### Network:
All services communicate via a custom Docker bridge network (`app-network`) for secure, isolated inter-service communication.

## Prerequisites
- Docker
- Docker Compose

## Quick Start

### Run the Application
```bash
docker-compose up --build
```

The application will be accessible at:
- **Frontend:** http://localhost:3000
- **API:** http://localhost:8000
- **API Docs (Swagger):** http://localhost:8000/docs
- **API Docs (ReDoc):** http://localhost:8000/redoc
- **Model Service:** http://localhost:8001
- **Model Service Health:** http://localhost:8001/health
- **MongoDB:** mongodb://localhost:27017 (local access only)

### Stopping the Application
```bash
docker-compose down
```

To also remove the MongoDB data volume:
```bash
docker-compose down -v
```

## Project Structure

```
├── api/
│   ├── main.py           # FastAPI application and PredictionRequest
│   ├── model_training.py # ML model architecture (SimpleClassifier)
│   ├── Dockerfile        # Docker build configuration for API
│   └── init-mongo.js     # MongoDB initialization script
├── model_service/
│   ├── serve.py          # FastAPI model inference service
│   ├── model_training.py # SimpleClassifier model definition
│   ├── Dockerfile        # Docker build configuration for Model Service
│   ├── requirements.txt   # Python dependencies for model service
│   └── model/
│       └── refined_simple_classifier.pth  # Trained PyTorch model
│   ├── Dockerfile        # Docker build configuration for API
│   └── init-mongo.js     # MongoDB initialization script
├── front-end/
│   ├── Dockerfile        # Docker build configuration for Frontend
│   ├── nginx.conf        # Nginx configuration with API proxy
│   └── static/
│       ├── index.html    # Frontend UI
│       └── style.css     # Styling
├── docker-compose.yml    # Docker Compose configuration
├── requirements.txt      # Python dependencies
└── README.md            # This file
```
Iris species prediction with confidence scores
- Error handling and status messages

### Backend API
- RESTful endpoints for item management
- Integration with the Model Service for ML predictions
- MongoDB integration for persistent data storage
- Proper error handling with HTTP status codes
- CORS enabled for cross-origin requests
- Automatic API documentation with Swagger UI

### Model Service
- Standalone FastAPI microservice for ML inference
- Loads a trained PyTorch SimpleClassifier model
- Performs Iris species classification
- Health check endpoint for service monitoring
- Isolated on separate port (8001) with independent scaling
- Error handling and status messages

### Backend API
- RESTful endpoints for item management
- MongoDB integration for persistent data storage
- Proper error handling with HTTP status codes
- CORS enabled for cross-origin requests
- Automatic API documentation with Swagger UI

### Database
- MongoDB with automatic initialization
- Sample data seeded on first startup
- Indexed fields for optimal query performance
- Proper schema with name, price, and description fields

## API Endpoints

### GET `/items`
- **Description:** Retrieve all items
- **Response:** Array of item objects with id, name, price, description
- **Status Code:** 200

### GET `/items/{item_id}`
- **Description:** Retrieve a specific item by ID
- **Parameters:** `item_id` (MongoDB ObjectId)
- **Response:** Single item object
- **Status Code:** 200 or 404 if not found

### POST `/items`
- **Description:** Create a new item
- **Body:** `{ "name": string, "price": number, "description": string }`
- **Response:** Created item with assigned ID
- **Status Code:** 201

### PUT `/items/{item_id}`
- **Description:** Update an existing item
- **Parameters:** `item_id` (MongoDB Objec

### POST `/predict`
- **Description:** Classify Iris flower species using ML model
- **Body:** `{ "sepal_length": float, "sepal_width": float, "petal_length": float, "petal_width": float }`
- **Response:** `{ "species": string, "confidence": float, "model": string }`
- **Status Code:** 200 or 503 if model service is unavailable
- **Example Request:**
```jPyTorch** - Machine learning framework for model inference
- **son
{
  "sepal_length": 5.1,
  "sepal_width": 3.5,
  "petal_length": 1.4,
  "petal_width": 0.2
}
```
- **Example Response:**
```json
{
  "species": "Setosa",
  "confidence": 0.98,
  "model": "simple-classifier-v1"
}
```

### POST `/chat`
- **Description:** Chat with an AI assistant about inventory items
- **Body:** `{ "message": string, "conversation_history": array }`
  - `message`: User's current message
  - `conversation_history`: Array of previous messages in format `[{"role": "user"/"assistant", "content": string}, ...]`
- **Response:** `{ "reply": string, "conversation_history": array }`
- **Status Code:** 200 or 500 if LLM service is unavailable
- **Example Request:**
```json
{
  "message": "What is our most expensive item?",
  "conversation_history": []
}
```
- **Example Response:**
```json
{
  "reply": "Bzzzz... I must check the inventory for you! *flaps wings* The most expensive item costs $1299.99. Is there anything else I can help with?",
  "conversation_history": [
    {"role": "user", "content": "What is our most expensive item?"},
    {"role": "assistant", "content": "Bzzzz... I must check the inventory for you! *flaps wings* The most expensive item costs $1299.99. Is there anything else I can help with?"}
  ]
}
```

### POST `/analyze`
- **Description:** Analyze content and extract structured insights using AI
- **Body:** `{ "content": string }`
- **Response:** `{ "categories": array, "tags": array, "sentiment": string, "summary": string }`
  - `categories`: List of applicable content categories
  - `tags`: List of relevant tags
  - `sentiment`: One of "positive", "negative", or "neutral"
  - `summary`: One sentence summary of the content
- **Status Code:** 200, 422 (invalid JSON response from LLM), or 500 (LLM service error)
- **Example Request:**
```json
{
  "content": "The new laptop is incredibly fast and the battery lasts all day. Best purchase this year."
}
```
- **Example Response:**
```json
{
  "categories": ["technology", "review"],
  "tags": ["laptop", "performance", "battery"],
  "sentiment": "positive",
  "summary": "Highly positive review praising laptop speed and battery life."
}
```

## Microservices Architecture
The application now uses a microservices architecture with:
- **API Service** - Handles CRUD operations and coordinates with other services
- **Model Service** - Isolated ML inference service that can be scaled independently
- Both services communicate via the Docker bridge network

The Model Service:
- Loads the trained PyTorch model on startup
- Performs health checks to ensure model loading succeeded
- Can be restarted independently without affecting other services
- Implements proper error handling and service monitoring

### Circular Import Fix
The `models.py` file was created to resolve circular imports between `main.py` and `dal.py`. Both modules now import the `Item` model from `models.py`.

### Nginx Proxy Configuration
The frontend Nginx server proxies `/items` API requests to the backend API service using the Docker network's internal DNS naming (`http://api:8000`).

- `MONGODB_COLLECTION` - Collection name (default: `items`)
- `MODEL_PATH` - Path to the trained model file (default: `/app/model/refined_simple_classifier.pth`)
### MongoDB Initialization
The MongoDB container automatically initializes with:
- A default database named `yourdb`
- An `items` collection
- Indexes on `name`, `price`, and compound fields
- Sample data (Laptop, Mouse, Keyboard)

### Model Service Healthcheck
The model service includes a Docker healthcheck that:
- Tests the `/health` endpoint every 10 seconds
- Waits 30 seconds before starting health checks (startup grace period)
- Requires 5 consecutive passes to mark as healthy
- Is used as a dependency condition in Docker Compose
- **Body:** `{ "name": string, "price": number, "description": string }`
- **Response:** Updated item object
- **Status Code:** 200 or 404 if not found

### DELETE `/items/{item_id}`
- **Description:** Delete an item
- **Parameters:** `item_id` (MongoDB ObjectId)
- **Response:** Success message
- **Status Code:** 200 or 404 if not found

## Technologies Used

- **FastAPI** - Modern Python web framework for building APIs
- **Pydantic** - Data validation using Python type annotations
- **MongoDB** - NoSQL document database
- **PyMongo** - MongoDB driver for Python
- **Nginx** - Reverse proxy and web server
- **Docker & Docker Compose** - Containerization and orchestration
- **Uvicorn** - ASGI server for FastAPI

## Development Notes

### Build Context
The API Dockerfile uses the repository root as build context, allowing it to access files from both the `api/` and `requirements.txt`.

### Circular Import Fix
The `models.py` file was created to resolve circular imports between `main.py` and `dal.py`. Both modules now import the `Item` model from `models.py`.

### Nginx Proxy Configuration
The frontend Nginx server proxies `/items` API requests to the backend API service using the Docker network's internal DNS naming (`http://api:8000`).

### MongoDB Initialization
The MongoDB container automatically initializes with:
- A default database named `yourdb`
- An `items` collection
- Indexes on `name`, `price`, and compound fields
- Sample data (Laptop, Mouse, Keyboard)

## Environment Variables

Set in `docker-compose.yml`:
- `MONGODB_URL` - MongoDB connection string (default: `mongodb://mongodb:27017/yourdb`)
- `MONGODB_DATABASE` - Database name (default: `yourdb`)
- `MONGODB_COLLECTION` - Collection name (default: `items`)

### DELETE `/items/{item_id}`
- Parameters:
  - `item_id`: integer
- Deletes item, returns confirmation, or 404 if missing

## Notes
- Data is stored in-memory (`items_db`) and will reset on restart.
- Add validation by replacing raw `dict` payloads with `pydantic` models for stronger typing.

# Note: This README has been generated by Microsoft Copilot based on the contents of the project.
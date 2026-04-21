# Item Manager - Full Stack Application

## Project Overview
A full-stack Item Management application built with **FastAPI**, **MongoDB**, and **Nginx**. The application is containerized using Docker Compose and consists of three services: an API backend, a MongoDB database, and a Nginx-based frontend.

## Architecture

### Services:
1. **API** (FastAPI) - Backend REST API running on port 8000
2. **MongoDB** - Database service running on port 27017
3. **Frontend** (Nginx) - Web UI served on port 3000

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
│   ├── main.py           # FastAPI application and endpoints
│   ├── dal.py            # Data Access Layer for MongoDB operations
│   ├── models.py         # Pydantic models (Item definition)
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

## Key Features

### Frontend
- Clean, responsive HTML/CSS interface
- Create, Read, Update, Delete (CRUD) operations for items
- Real-time item list display
- Forms for adding and editing items
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
- **Parameters:** `item_id` (MongoDB ObjectId)
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
import os
import ollama
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from models import Item, PredictionRequest, ChatRequest, ChatResponse, AnalyzeRequest
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

# Your endpoints here

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

#TODO: Update this function to use the ollama service outlined in the docker-compose    
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    # Build messages array with system prompt + history + new message
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

        # Return updated history so the frontend can send it back
        updated_history = request.conversation_history + [
            {"role": "user", "content": request.message},
            {"role": "assistant", "content": reply}
        ]
        return ChatResponse(reply=reply, conversation_history=updated_history)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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

    # Few-shot example in the prompt
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

        # Parse and validate JSON
        result = json.loads(raw)

        # Validate expected fields exist
        required = ["categories", "tags", "sentiment", "summary"]
        for field in required:
            if field not in result:
                raise ValueError(f"Missing field: {field}")
        print(f"Analysis result: {result}")
        return result

    except json.JSONDecodeError:
        # Retry once or return fallback
        raise HTTPException(status_code=422, detail="LLM returned invalid JSON. Try again.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
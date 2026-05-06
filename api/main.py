import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from models import Item, PredictionRequest
from model import SimpleClassifier
from dal import MongoDAL
import torch
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
    model_path = os.getenv("MODEL_PATH", "/main/simple_classifier.pth")
    
    if not os.path.exists(model_path):
        raise RuntimeError(f"Model file not found at {model_path}")
    
    model = SimpleClassifier(input_size=4, hidden_size=10, num_classes=3)
    model.load_state_dict(torch.load(model_path, weights_only=True))
    model.eval()
    print(f"Model loaded successfully from {model_path}")

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
    # 1. Convert input to tensor
    # 2. Run inference (model.eval(), torch.no_grad())
    # 3. Return prediction as JSON
    req_tensor = torch.tensor(req)
    with torch.no_grad():
        output = model(req_tensor)
        predicted_class = torch.argmax(output, dim=1).item()
    return {"predicted_class": predicted_class}
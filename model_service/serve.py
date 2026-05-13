#FastAPI app that loads and serves model.
from fastapi import FastAPI
import torch  # or tensorflow
import numpy as np
from model_training import SimpleClassifier
import os
app = FastAPI()

# Load model at startup
model = None

@app.on_event("startup")
def load_model():
    global model
    model_path = os.getenv("MODEL_PATH", "/model/refined_simple_classifier.pth")
    
    if not os.path.exists(model_path):
        raise RuntimeError(f"Model file not found at {model_path}")
    
    model = SimpleClassifier(input_size=4, hidden_size=10, num_classes=3)
    model.load_state_dict(torch.load(model_path, weights_only=True))
    model.eval()

@app.get("/health")
def health():
    return {"status": "healthy", "model_loaded": model is not None}

@app.post("/predict")
def predict(data: dict):
    print(f"model-service received prediction request: {data}")
    # Convert input to tensor, run prediction, return result
    input_data = np.array(data["features"], dtype=np.float32)
    input_tensor = torch.tensor(input_data, dtype=torch.float32)
    
    # Ensure batch dimension
    if input_tensor.dim() == 1:
        input_tensor = input_tensor.unsqueeze(0)
    
    species_names = ["Setosa", "Versicolor", "Virginica"]
    
    with torch.no_grad():
        result = model(input_tensor)
        
        # Ensure result is 2D [batch, classes]
        if result.dim() == 1:
            result = result.unsqueeze(0)
        
        probabilities = torch.softmax(result, dim=1)
        predicted_class = torch.argmax(result, dim=1).item()
        confidence = probabilities[0, predicted_class].item()
    
    return {"species": species_names[predicted_class], "confidence": float(confidence), "model": "simple-classifier-v1"}
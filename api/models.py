from pydantic import BaseModel


class Item(BaseModel):
    name: str
    price: float
    description: str

class PredictionRequest(BaseModel):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float

class ChatRequest(BaseModel):
    message: str
    conversation_history: list = []

class ChatResponse(BaseModel):
    reply: str
    conversation_history: list

class AnalyzeRequest(BaseModel):
    content: str  # e.g., item descriptions, user text, etc.

class AskRequest(BaseModel):
    query: str

class AgentRequest(BaseModel):
    task: str
    auto_confirm_create: bool = False

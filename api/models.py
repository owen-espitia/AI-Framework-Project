from pydantic import BaseModel


class Item(BaseModel):
    name: str
    price: float
    description: str

class PredictionRequest(BaseModel):
    features: list[float]
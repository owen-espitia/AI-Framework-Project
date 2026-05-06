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
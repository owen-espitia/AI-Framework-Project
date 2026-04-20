from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Your Pydantic model(s) here
class Item(BaseModel):
    name: str
    price: float
    description: str



# In-memory storage
items_db: dict[int, dict] = {}
next_id: int = 1

# Your endpoints here

@app.get("/items", status_code=200)
def read_items():
    return items_db

@app.get("/items/{item_id}", status_code=200)
def get_item(item_id: int):
    item = items_db.get(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="No items with that ID")
    return item

@app.post("/items", status_code=201)
def create_item(item: Item):
    global next_id
    item_id = next_id
    items_db[item_id] = item.model_dump()
    next_id += 1
    return {"id": item_id, "name": item.name}

@app.put("/items/{item_id}", status_code=200)
def update_item(new_item: Item, item_id: int):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="No item with specified ID")
    items_db[item_id] = new_item.model_dump()
    return {"id": item_id, "updated_item": new_item.model_dump()}

@app.delete("/items/{item_id}", status_code=200)
def delete_item(item_id: int):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="No item with specified ID")
    del items_db[item_id]
    return {"message": f"Item with ID {item_id} deleted successfully."}

app.mount("/", StaticFiles(directory="front-end/static", html=True), name="static")
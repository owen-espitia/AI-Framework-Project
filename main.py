from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# Your Pydantic model(s) here

# In-memory storage
items_db: dict[int, dict] = {}
next_id: int = 1

# Your endpoints here
@app.get("/", status_code=200)
def landing_page():
    return "Welcome to my first python API!"

@app.get("/items", status_code=200)
def read_items():
    return items_db

@app.get("/items/{item_id}", status_code=200)
def get_item(item_id: str):
    item = items_db.get(int(item_id))
    if item is None:
        raise HTTPException(status_code=404, detail="No items with that ID")
    return item

@app.post("/items", status_code=201)
def create_item(item: dict):
    global next_id
    item_id = next_id
    items_db[item_id] = {**item}
    next_id += 1
    return {"id": item_id, **item}

@app.put("/items/{item_id}", status_code=200)
def update_item(new_item: dict, item_id: str):
    try:
        items_db[int(item_id)] = new_item
        return {"id": item_id, "updated_item": new_item}
    except:
        raise HTTPException(status_code=404, detail="No item with specified ID")

@app.delete("/items/{item_id}", status_code=200)
def delete_item(item_id: str):
    try:
        del items_db[int(item_id)]
        return {"message": f"Item with ID {item_id} deleted successfully."}
    except:
        raise HTTPException(status_code=404, detail="No item with specified ID")
# Run with: uvicorn main:app --reload
#TODO: Finish documentation and testing!
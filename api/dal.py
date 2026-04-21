import os
from pymongo import MongoClient
from dotenv import load_dotenv
from models import Item
from bson import ObjectId

load_dotenv()

class MongoDAL:
    def __init__(self):
        self.client = MongoClient(os.getenv("MONGODB_URL"))
        self.db = self.client[os.getenv("MONGODB_DATABASE")]
        #Check to see if the collection exists, if not, create it.
        if os.getenv("MONGODB_COLLECTION") not in self.db.list_collection_names():
            self.coll = self.db.create_collection(os.getenv("MONGODB_COLLECTION"), capped=True, size=5242880)
        else:
            self.coll = self.db[os.getenv("MONGODB_COLLECTION")]
    def create_item(self, item: Item) -> str:
        result = self.coll.insert_one(item.model_dump())
        return str(result.inserted_id)
    def read_items(self) -> list[dict]:
        items = list(self.coll.find({}, {"_id": 1, "name": 1, "price": 1, "description": 1}))
        # Convert _id to id for cleaner API responses
        for item in items:
            item["id"] = str(item.pop("_id"))
        return items
    def read_item(self, item_id: str) -> dict:
        item = self.coll.find_one({"_id": ObjectId(item_id)}, {"_id": 1, "name": 1, "price": 1, "description": 1})
        if item is None:
            raise ValueError("No item with that ID")
        # Convert _id to id for cleaner API responses
        item["id"] = str(item.pop("_id"))
        return item
    def update_item(self, item_id: str, new_item: Item) -> None:

        result = self.coll.update_one({"_id": ObjectId(item_id)}, {"$set": new_item.model_dump()})
        if result.matched_count == 0:
            raise ValueError(f"No item with ID: {item_id}")
    def delete_item(self, item_id: str) -> None:

        result = self.coll.delete_one({"_id": ObjectId(item_id)})
        if result.deleted_count == 0:
            raise ValueError(f"No item with ID: {item_id}")

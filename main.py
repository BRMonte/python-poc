from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Model
class Item(BaseModel):
    name: str
    description: str = None
    price: float
    tax: float = None

# Database simulation
db = []

# CRUD operations
@app.post("/items/", response_model=Item)
async def create_item(item: Item):
    db.append(item)
    return item

@app.get("/items/", response_model=List[Item])
async def read_items(skip: int = 0, limit: int = 10):
    return db[skip : skip + limit]

@app.get("/items/{item_id}", response_model=Item)
async def read_item(item_id: int):
    try:
        return db[item_id]
    except IndexError:
        raise HTTPException(status_code=404, detail="Item not found")

@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: int, item: Item):
    try:
        db[item_id] = item
        return item
    except IndexError:
        raise HTTPException(status_code=404, detail="Item not found")

@app.delete("/items/{item_id}", response_model=Item)
async def delete_item(item_id: int):
    try:
        deleted_item = db.pop(item_id)
        return deleted_item
    except IndexError:
        raise HTTPException(status_code=404, detail="Item not found")

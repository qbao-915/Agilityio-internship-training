from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field
from typing import List

router = APIRouter(prefix="/items", tags=["Items"])

# Mock database to store items
items_db = []

# Pydantic Schemas
class ItemCreate(BaseModel):
    item_name: str = Field(..., min_length=1, description="Name of the item")

class ItemUpdate(BaseModel):
    item_name: str = Field(..., min_length=1, description="New name of the item")

class ItemResponse(BaseModel):
    item_id: int
    item_name: str

@router.post('', response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(payload: ItemCreate):
    # Loại bỏ khoảng trắng thừa ở hai đầu
    item_name = payload.item_name.strip()
    if not item_name:
        raise HTTPException(status_code=400, detail="Item name cannot be empty")

    if any(item["item_name"] == item_name for item in items_db):
        raise HTTPException(status_code=400, detail="Item name already exists")

    existing_ids = {item["item_id"] for item in items_db}
    next_id = 1
    while next_id in existing_ids:
        next_id += 1
    
    new_item = {"item_id": next_id, "item_name": item_name}
    items_db.append(new_item)
    items_db.sort(key=lambda x: x["item_id"])
    return new_item

@router.get('', response_model=List[ItemResponse])
def read_items(skip: int = Query(1, gt=0), limit: int = 10):
    sorted_items = sorted(items_db, key=lambda x: x["item_id"])
    return sorted_items[skip - 1 : skip - 1 + limit]

@router.get('/{item_id_or_name}', response_model=ItemResponse)
def read_item(item_id_or_name: str):
    target_id = None
    try:
        target_id = int(item_id_or_name)
    except ValueError:
        pass

    for item in items_db:
        if (target_id is not None and item["item_id"] == target_id) or (item["item_name"] == item_id_or_name):
            return item
    raise HTTPException(status_code=404, detail="Item not found")

@router.put('/{item_id_or_name}', response_model=ItemResponse)
def update_item(item_id_or_name: str, payload: ItemUpdate):
    new_name = payload.item_name.strip()
    if not new_name:
        raise HTTPException(status_code=400, detail="New item name cannot be empty")

    target_id = None
    try:
        target_id = int(item_id_or_name)
    except ValueError:
        pass

    target_item = None
    for item in items_db:
        if (target_id is not None and item["item_id"] == target_id) or (item["item_name"] == item_id_or_name):
            target_item = item
            break

    if target_item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    if target_item["item_name"] == new_name:
        raise HTTPException(status_code=400, detail="New name cannot be same as old name")

    if any(item["item_name"] == new_name and item["item_id"] != target_item["item_id"] for item in items_db):
        raise HTTPException(status_code=400, detail="Item name already exists")

    target_item["item_name"] = new_name
    return target_item

@router.delete('/{item_id_or_name}')
def delete_item(item_id_or_name: str):
    target_id = None
    try:
        target_id = int(item_id_or_name)
    except ValueError:
        pass

    for item in items_db:
        if (target_id is not None and item["item_id"] == target_id) or (item["item_name"] == item_id_or_name):
            name = item["item_name"]
            items_db.remove(item)
            return {"message": f"Item {name} deleted successfully"}
            
    raise HTTPException(status_code=404, detail="Item not found")

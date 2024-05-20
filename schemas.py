from pydantic import BaseModel
from datetime import datetime
from typing import List, Tuple

class ItemModel(BaseModel):
    id: int
    vendor: str
    address: str
    recipient: str
    phone_number: str
    note: str
    product: List[Tuple[str, int]]
    cargo_type: str
    created_at: datetime
    status: str
    username: str
    position: str
    grouped_item_id: int
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BookOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    author: str
    price: int

class OrderIn(BaseModel):
    user_id: int
    book_id: int

class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    user_id: int
    book_id: int
    status: str
    created_at: datetime
    updated_at: datetime

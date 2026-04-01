import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class OrderCreateRequest(BaseModel):
    product_id: str = Field(min_length=1, max_length=100)
    quantity: int = Field(gt=0, le=100000)
    user_id: str = Field(min_length=1, max_length=100)


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    product_id: str
    quantity: int
    user_id: str
    status: str
    created_at: datetime

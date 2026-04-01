import uuid

from pydantic import BaseModel, ConfigDict, Field


class InventoryUpdateRequest(BaseModel):
    product_id: str = Field(min_length=1, max_length=100)
    stock: int = Field(ge=0, le=1000000)


class InventoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    product_id: str
    stock: int

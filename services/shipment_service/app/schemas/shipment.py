import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

ShipmentStatus = Literal["PROCESSING", "IN_TRANSIT", "DELIVERED", "CANCELLED"]


class ShipmentStatusUpdateRequest(BaseModel):
    status: ShipmentStatus


class ShipmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    order_id: str
    product_id: str
    quantity: int
    status: ShipmentStatus
    tracking_id: str
    created_at: datetime
    updated_at: datetime

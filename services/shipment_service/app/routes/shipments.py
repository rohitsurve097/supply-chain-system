import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.schemas.shipment import ShipmentResponse, ShipmentStatusUpdateRequest
from app.services.shipment_service import ShipmentService

router = APIRouter(prefix="/shipments", tags=["shipments"])


async def get_shipment_service(
    session: AsyncSession = Depends(get_db_session),
) -> ShipmentService:
    return ShipmentService(session=session)


@router.get("/{shipment_id}", response_model=ShipmentResponse)
async def get_shipment(
    shipment_id: uuid.UUID,
    shipment_service: ShipmentService = Depends(get_shipment_service),
) -> ShipmentResponse:
    shipment = await shipment_service.get_by_id(shipment_id)
    if shipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shipment '{shipment_id}' not found",
        )

    return ShipmentResponse.model_validate(shipment)


@router.get("/order/{order_id}", response_model=ShipmentResponse)
async def get_shipment_by_order_id(
    order_id: str,
    shipment_service: ShipmentService = Depends(get_shipment_service),
) -> ShipmentResponse:
    shipment = await shipment_service.get_by_order_id(order_id)
    if shipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shipment for order '{order_id}' not found",
        )

    return ShipmentResponse.model_validate(shipment)


@router.post("/{shipment_id}/status", response_model=ShipmentResponse)
async def update_shipment_status(
    shipment_id: uuid.UUID,
    request: ShipmentStatusUpdateRequest,
    shipment_service: ShipmentService = Depends(get_shipment_service),
) -> ShipmentResponse:
    shipment = await shipment_service.update_status(shipment_id=shipment_id, status=request.status)
    if shipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shipment '{shipment_id}' not found",
        )

    return ShipmentResponse.model_validate(shipment)

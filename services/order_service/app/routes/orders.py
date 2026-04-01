import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import get_db_session
from app.events.publisher import SqsEventPublisher
from app.schemas.order import OrderCreateRequest, OrderResponse
from app.services.order_service import OrderService

router = APIRouter(prefix="/orders", tags=["orders"])


async def get_event_publisher() -> SqsEventPublisher:
    settings = get_settings()
    return SqsEventPublisher(
        queue_url=settings.order_sqs_queue_url,
        region_name=settings.aws_region,
        access_key_id=settings.aws_access_key_id,
        secret_access_key=settings.aws_secret_access_key,
        endpoint_url=settings.aws_endpoint_url,
    )


async def get_order_service(
    session: AsyncSession = Depends(get_db_session),
    event_publisher: SqsEventPublisher = Depends(get_event_publisher),
) -> OrderService:
    return OrderService(session=session, event_publisher=event_publisher)


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    request: OrderCreateRequest,
    order_service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    try:
        order = await order_service.create_order(request)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to create order due to downstream dependency error",
        ) from exc

    return OrderResponse.model_validate(order)


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: uuid.UUID,
    order_service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    order = await order_service.get_order(order_id)
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order '{order_id}' not found",
        )

    return OrderResponse.model_validate(order)

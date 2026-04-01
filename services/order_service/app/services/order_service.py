import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.events.publisher import SqsEventPublisher
from app.models.order import Order
from app.schemas.order import OrderCreateRequest

logger = logging.getLogger(__name__)


class OrderService:
    def __init__(self, session: AsyncSession, event_publisher: SqsEventPublisher) -> None:
        self.session = session
        self.event_publisher = event_publisher

    async def create_order(self, payload: OrderCreateRequest) -> Order:
        order = Order(
            product_id=payload.product_id,
            quantity=payload.quantity,
            user_id=payload.user_id,
            status="CREATED",
        )
        self.session.add(order)

        try:
            await self.session.flush()
            await self.event_publisher.publish_order_created(order)
            await self.session.commit()
            await self.session.refresh(order)
        except Exception:
            await self.session.rollback()
            logger.exception("Failed to create order")
            raise

        return order

    async def get_order(self, order_id: uuid.UUID) -> Order | None:
        return await self.session.get(Order, order_id)

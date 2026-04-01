import logging
import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.shipment import Shipment
from app.schemas.shipment import ShipmentStatus

logger = logging.getLogger(__name__)


class ShipmentService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, shipment_id: uuid.UUID) -> Shipment | None:
        return await self.session.get(Shipment, shipment_id)

    async def get_by_order_id(self, order_id: str) -> Shipment | None:
        stmt = select(Shipment).where(Shipment.order_id == order_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_from_inventory_reserved(
        self,
        order_id: str,
        product_id: str,
        quantity: int,
    ) -> Shipment:
        existing = await self.get_by_order_id(order_id)
        if existing is not None:
            return existing

        shipment = Shipment(
            order_id=order_id,
            product_id=product_id,
            quantity=quantity,
            status="PROCESSING",
            tracking_id=f"TRK-{uuid.uuid4()}",
        )
        self.session.add(shipment)

        try:
            await self.session.commit()
            await self.session.refresh(shipment)
            return shipment
        except IntegrityError:
            await self.session.rollback()
            # Idempotency fallback in case concurrent consumer inserted same order shipment.
            existing = await self.get_by_order_id(order_id)
            if existing is None:
                raise
            return existing

    async def update_status(
        self,
        shipment_id: uuid.UUID,
        status: ShipmentStatus,
    ) -> Shipment | None:
        shipment = await self.get_by_id(shipment_id)
        if shipment is None:
            return None

        shipment.status = status
        await self.session.commit()
        await self.session.refresh(shipment)
        return shipment

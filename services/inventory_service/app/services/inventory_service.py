import logging

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.inventory import Inventory
from app.schemas.inventory import InventoryUpdateRequest

logger = logging.getLogger(__name__)


class InventoryService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_product_id(self, product_id: str) -> Inventory | None:
        stmt = select(Inventory).where(Inventory.product_id == product_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def upsert_stock(self, payload: InventoryUpdateRequest) -> Inventory:
        inventory = await self.get_by_product_id(payload.product_id)
        if inventory is None:
            inventory = Inventory(product_id=payload.product_id, stock=payload.stock)
            self.session.add(inventory)
        else:
            inventory.stock = payload.stock

        await self.session.commit()
        await self.session.refresh(inventory)
        return inventory

    async def reserve_stock(self, product_id: str, quantity: int) -> Inventory | None:
        stmt = (
            update(Inventory)
            .where(Inventory.product_id == product_id, Inventory.stock >= quantity)
            .values(stock=Inventory.stock - quantity)
            .returning(Inventory)
        )
        result = await self.session.execute(stmt)
        reserved_inventory = result.scalar_one_or_none()

        if reserved_inventory is None:
            await self.session.rollback()
            logger.warning(
                "Stock reservation failed",
                extra={"product_id": product_id, "quantity": quantity},
            )
            return None

        await self.session.commit()
        return reserved_inventory

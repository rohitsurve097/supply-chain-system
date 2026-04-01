from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.schemas.inventory import InventoryResponse, InventoryUpdateRequest
from app.services.inventory_service import InventoryService

router = APIRouter(prefix="/inventory", tags=["inventory"])


async def get_inventory_service(
    session: AsyncSession = Depends(get_db_session),
) -> InventoryService:
    return InventoryService(session=session)


@router.get("/{product_id}", response_model=InventoryResponse)
async def get_inventory(
    product_id: str,
    inventory_service: InventoryService = Depends(get_inventory_service),
) -> InventoryResponse:
    inventory = await inventory_service.get_by_product_id(product_id)
    if inventory is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inventory for product '{product_id}' not found",
        )

    return InventoryResponse.model_validate(inventory)


@router.post("/update", response_model=InventoryResponse)
async def update_inventory(
    request: InventoryUpdateRequest,
    inventory_service: InventoryService = Depends(get_inventory_service),
) -> InventoryResponse:
    inventory = await inventory_service.upsert_stock(request)
    return InventoryResponse.model_validate(inventory)

import asyncio
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI

from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db.session import init_db
from app.events.consumer import ShipmentEventConsumer
from app.routes.shipments import router as shipment_router

settings = get_settings()
configure_logging(settings.log_level)


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_db()

    stop_event = asyncio.Event()
    consumer = ShipmentEventConsumer(settings)
    consumer_task = asyncio.create_task(consumer.run(stop_event))

    try:
        yield
    finally:
        stop_event.set()
        consumer_task.cancel()
        with suppress(asyncio.CancelledError):
            await consumer_task


app = FastAPI(
    title="Shipment Service",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(shipment_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}

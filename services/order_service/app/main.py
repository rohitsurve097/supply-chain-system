from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db.session import init_db
from app.routes.orders import router as order_router

settings = get_settings()
configure_logging(settings.log_level)


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Order Service",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(order_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}

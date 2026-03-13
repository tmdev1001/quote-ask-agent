from __future__ import annotations

from fastapi import FastAPI

from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.routers import admin, customers, conversations, health, quotes, extract


configure_logging()
logger = get_logger(__name__)

app = FastAPI(title="Lyra Quote Ask Agent")


@app.on_event("startup")
async def on_startup() -> None:
    """Startup hook to log basic environment information."""

    settings = get_settings()
    logger.info("startup", environment=settings.environment)


app.include_router(health.router)
app.include_router(customers.router)
app.include_router(conversations.router)
app.include_router(quotes.router)
app.include_router(admin.router)
app.include_router(extract.router)


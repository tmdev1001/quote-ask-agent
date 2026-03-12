from __future__ import annotations

from fastapi import FastAPI

from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.routers import health


configure_logging()
logger = get_logger(__name__)

app = FastAPI(title="Lyra Quote Ask Agent")


@app.on_event("startup")
async def on_startup() -> None:
    """Startup hook to log basic environment information."""

    settings = get_settings()
    logger.info("startup", environment=settings.environment)


app.include_router(health.router)


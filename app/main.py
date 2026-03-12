from __future__ import annotations

from typing import Any, Dict

from fastapi import Depends, FastAPI

from .config import get_settings
from .logging_config import configure_logging, get_logger
from .routers import admin, telegram


configure_logging()
logger = get_logger(__name__)

app = FastAPI(title="Lyra Quote Ask Agent")


@app.on_event("startup")
async def on_startup() -> None:
    settings = get_settings()
    logger.info("startup", environment=settings.environment)


@app.get("/health", tags=["meta"])
async def healthcheck() -> Dict[str, Any]:
    """Simple healthcheck endpoint."""

    settings = get_settings()
    return {
        "status": "ok",
        "environment": settings.environment,
        "app_name": settings.app_name,
    }


app.include_router(telegram.router, prefix="/telegram", tags=["telegram"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])


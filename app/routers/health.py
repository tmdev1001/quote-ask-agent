from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter

from app.core.config import get_settings
from app.core.constants import APP_VERSION


router = APIRouter()


@router.get("/health", summary="Health check")
async def health() -> Dict[str, Any]:
    """Basic health endpoint to verify the service is running."""

    settings = get_settings()
    return {
        "status": "ok",
        "app_name": settings.app_name,
        "environment": settings.environment,
        "version": APP_VERSION,
    }


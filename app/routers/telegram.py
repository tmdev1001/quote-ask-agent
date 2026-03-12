from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Depends, Header
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import get_settings
from ..db import get_db
from ..logging_config import get_logger


router = APIRouter()
logger = get_logger(__name__)


@router.post("/webhook")
async def telegram_webhook(
    update: Dict[str, Any],
    x_telegram_secret_token: str | None = Header(default=None, alias="X-Telegram-Bot-Api-Secret-Token"),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Receive Telegram updates.

    V1: minimal validation + logging.
    Later this will call Lyra's agent orchestration.
    """

    settings = get_settings()

    if settings.telegram_webhook_secret:
        if x_telegram_secret_token != settings.telegram_webhook_secret:
            logger.warning("invalid_webhook_secret")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook secret",
            )

    logger.info("telegram_update", update=update)

    # TODO: integrate with Lyra agent orchestration and return any messages to send back.

    return {"ok": True}


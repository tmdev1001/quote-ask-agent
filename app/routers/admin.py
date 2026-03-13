from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import AuditLog, Conversation, Customer, Quote


router = APIRouter()


@router.get("/admin/summary", response_model=Dict[str, Any])
async def admin_summary(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """
    Lightweight admin summary with simple counts.

    Useful for quickly checking that migrations and data writes are working.
    """

    counts: Dict[str, int] = {}

    for model, key in (
        (Customer, "customers"),
        (Conversation, "conversations"),
        (Quote, "quotes"),
        (AuditLog, "audit_logs"),
    ):
        result = await db.execute(select(func.count()).select_from(model))
        counts[key] = int(result.scalar_one())

    return counts



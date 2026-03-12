from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db
from ..models import Customer, Quote


router = APIRouter()


@router.get("/customers", response_model=List[Dict[str, Any]])
async def list_customers(db: AsyncSession = Depends(get_db)) -> List[Dict[str, Any]]:
    """Simple JSON view of customers (PoC admin)."""

    result = await db.execute(select(Customer))
    customers = result.scalars().all()
    return [
        {
            "id": c.id,
            "telegram_user_id": c.telegram_user_id,
            "cpf": c.cpf,
            "name": c.name,
        }
        for c in customers
    ]


@router.get("/quotes", response_model=List[Dict[str, Any]])
async def list_quotes(db: AsyncSession = Depends(get_db)) -> List[Dict[str, Any]]:
    """Simple JSON view of quotes (PoC admin)."""

    result = await db.execute(select(Quote))
    quotes = result.scalars().all()
    return [
        {
            "id": q.id,
            "customer_id": q.customer_id,
            "premium": q.premium,
            "currency": q.currency,
            "status": q.status,
        }
        for q in quotes
    ]


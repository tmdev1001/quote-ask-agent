from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories import QuoteRepository
from app.schemas.quote import QuoteRead
from app.services.checkout_service import CheckoutService
from app.services.quote_service import QuoteService


router = APIRouter()


class QuoteSimulateRequest(BaseModel):
    conversation_id: int
    customer_id: Optional[int] = None
    cpf: Optional[str] = None
    vehicle_plate: Optional[str] = None
    extra_payload: Optional[dict] = None


@router.post("/api/quotes/simulate", response_model=QuoteRead)
async def simulate_quote(
    payload: QuoteSimulateRequest,
    db: AsyncSession = Depends(get_db),
) -> QuoteRead:
    """Simulate a quote using simple rule-based logic."""

    service = QuoteService(db)
    quote = await service.simulate_quote(
        conversation_id=payload.conversation_id,
        customer_id=payload.customer_id,
        cpf=payload.cpf,
        vehicle_plate=payload.vehicle_plate,
        extra_payload=payload.extra_payload,
    )
    return QuoteRead.model_validate(quote)


@router.post("/api/quotes/{quote_id}/checkout", response_model=QuoteRead)
async def create_checkout_for_quote(
    quote_id: int,
    db: AsyncSession = Depends(get_db),
) -> QuoteRead:
    """
    Generate a fake checkout URL for an existing quote and persist it.
    """

    repo = QuoteRepository(db)
    quote = await repo.get(quote_id)
    if quote is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quote not found")

    checkout = CheckoutService()
    quote.checkout_url = checkout.build_checkout_url(quote)

    await db.flush()
    await db.commit()
    await db.refresh(quote)

    return QuoteRead.model_validate(quote)


@router.get("/api/quotes", response_model=List[QuoteRead])
async def list_quotes(
    db: AsyncSession = Depends(get_db),
) -> List[QuoteRead]:
    """List all quotes."""

    repo = QuoteRepository(db)
    quotes = await repo.list()
    return [QuoteRead.model_validate(q) for q in quotes]


@router.get("/api/quotes/{quote_id}", response_model=QuoteRead)
async def get_quote(
    quote_id: int,
    db: AsyncSession = Depends(get_db),
) -> QuoteRead:
    """Fetch a single quote by id."""

    repo = QuoteRepository(db)
    quote = await repo.get(quote_id)
    if quote is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quote not found")
    return QuoteRead.model_validate(quote)


from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel

from app.schemas.base import ORMBaseModel, TimestampedModel


class QuoteBase(BaseModel):
    conversation_id: int
    customer_id: Optional[int] = None
    quote_code: str
    payload_json: Optional[Dict[str, Any]] = None
    monthly_price: float
    annual_price: float
    status: str = "simulated"
    checkout_url: Optional[str] = None


class QuoteCreate(QuoteBase):
    """Payload for creating a quote (simulated or real)."""


class QuoteRead(TimestampedModel, QuoteBase, ORMBaseModel):
    """API-facing representation of a quote."""

    id: int


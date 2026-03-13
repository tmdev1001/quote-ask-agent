from __future__ import annotations

from typing import Optional

from pydantic import BaseModel

from app.schemas.base import ORMBaseModel, TimestampedModel


class CustomerBase(BaseModel):
    full_name: Optional[str] = None
    cpf: str
    phone: Optional[str] = None
    telegram_user_id: Optional[str] = None
    address: Optional[str] = None


class CustomerCreate(CustomerBase):
    """Payload for creating a new customer."""


class CustomerUpdate(BaseModel):
    """Payload for updating an existing customer."""

    full_name: Optional[str] = None
    phone: Optional[str] = None
    telegram_user_id: Optional[str] = None
    address: Optional[str] = None


class CustomerRead(TimestampedModel, CustomerBase, ORMBaseModel):
    """API-facing representation of a customer."""

    id: int


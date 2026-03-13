from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories import CustomerRepository
from app.schemas.customer import CustomerRead
from app.services.customer_service import CustomerService


router = APIRouter()


class CustomerLookupRequest(BaseModel):
    """Request body for customer lookup / upsert."""

    cpf: Optional[str] = None
    telegram_user_id: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


@router.post("/api/customers/lookup", response_model=CustomerRead)
async def lookup_customer(
    payload: CustomerLookupRequest,
    db: AsyncSession = Depends(get_db),
) -> CustomerRead:
    """
    Lookup or create/update a customer.

    - If CPF is provided, it is the primary key for ensure_customer.
    - If only telegram_user_id is provided, attempts a lookup by Telegram.
    """

    service = CustomerService(db)

    if payload.cpf:
        customer = await service.ensure_customer(
            cpf=payload.cpf,
            full_name=payload.full_name,
            telegram_user_id=payload.telegram_user_id,
            phone=payload.phone,
            address=payload.address,
        )
        return CustomerRead.model_validate(customer)

    if payload.telegram_user_id:
        existing = await service.get_by_telegram_user_id(payload.telegram_user_id)
        if existing is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found for given telegram_user_id and no CPF provided.",
            )
        return CustomerRead.model_validate(existing)

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Provide at least cpf or telegram_user_id.",
    )


@router.get("/api/customers", response_model=List[CustomerRead])
async def list_customers(db: AsyncSession = Depends(get_db)) -> List[CustomerRead]:
    """Return all customers (for local admin/testing)."""

    repo = CustomerRepository(db)
    customers = await repo.list()
    return [CustomerRead.model_validate(c) for c in customers]


@router.get("/api/customers/{customer_id}", response_model=CustomerRead)
async def get_customer(
    customer_id: int,
    db: AsyncSession = Depends(get_db),
) -> CustomerRead:
    """Fetch a single customer by id."""

    repo = CustomerRepository(db)
    customer = await repo.get(customer_id)
    if customer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return CustomerRead.model_validate(customer)


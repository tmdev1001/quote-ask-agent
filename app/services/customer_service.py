from __future__ import annotations

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Customer
from app.repositories import CustomerRepository
from app.schemas.customer import CustomerCreate, CustomerUpdate


class CustomerService:
    """High-level operations for managing customers."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = CustomerRepository(session)

    async def get_by_telegram_user_id(self, telegram_user_id: str) -> Optional[Customer]:
        """Lookup a customer by Telegram user id."""

        return await self.repo.get_by_telegram_user_id(telegram_user_id)

    async def get_by_cpf(self, cpf: str) -> Optional[Customer]:
        """Lookup a customer by CPF."""

        return await self.repo.get_by_cpf(cpf)

    async def create_customer(self, data: CustomerCreate) -> Customer:
        """Create a new customer."""

        customer = await self.repo.create_from_schema(data)
        await self.session.commit()
        return customer

    async def update_customer(self, customer: Customer, data: CustomerUpdate) -> Customer:
        """Update mutable customer fields."""

        updated = await self.repo.update_from_schema(customer, data)
        await self.session.commit()
        return updated

    async def ensure_customer(
        self,
        *,
        cpf: str,
        full_name: Optional[str] = None,
        telegram_user_id: Optional[str] = None,
        phone: Optional[str] = None,
        address: Optional[str] = None,
    ) -> Customer:
        """
        Find or create a customer by CPF, updating missing fields when provided.

        Intended for use by tools/agents when new information arrives.
        """

        existing = await self.repo.get_by_cpf(cpf)
        if existing is None:
            data = CustomerCreate(
                cpf=cpf,
                full_name=full_name,
                phone=phone,
                telegram_user_id=telegram_user_id,
                address=address,
            )
            return await self.create_customer(data)

        update_payload = CustomerUpdate(
            full_name=full_name or existing.full_name,
            phone=phone or existing.phone,
            telegram_user_id=telegram_user_id or existing.telegram_user_id,
            address=address or existing.address,
        )
        return await self.update_customer(existing, update_payload)


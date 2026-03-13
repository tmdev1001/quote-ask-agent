from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Customer
from app.repositories.base import BaseRepository
from app.schemas.customer import CustomerCreate, CustomerUpdate


class CustomerRepository(BaseRepository[Customer]):
    """Persistence operations for customers."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Customer)

    async def get_by_cpf(self, cpf: str) -> Optional[Customer]:
        stmt = select(Customer).where(Customer.cpf == cpf)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_telegram_user_id(self, telegram_user_id: str) -> Optional[Customer]:
        stmt = select(Customer).where(Customer.telegram_user_id == telegram_user_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def create_from_schema(self, data: CustomerCreate) -> Customer:
        obj = Customer(
            full_name=data.full_name,
            cpf=data.cpf,
            phone=data.phone,
            telegram_user_id=data.telegram_user_id,
            address=data.address,
        )
        return await self.add(obj)

    async def update_from_schema(self, customer: Customer, data: CustomerUpdate) -> Customer:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(customer, field, value)
        await self.session.flush()
        await self.session.refresh(customer)
        return customer


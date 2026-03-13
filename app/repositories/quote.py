from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Quote
from app.repositories.base import BaseRepository
from app.schemas.quote import QuoteCreate


class QuoteRepository(BaseRepository[Quote]):
    """Persistence operations for quotes."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Quote)

    async def create_from_schema(self, data: QuoteCreate) -> Quote:
        obj = Quote(
            conversation_id=data.conversation_id,
            customer_id=data.customer_id,
            quote_code=data.quote_code,
            payload_json=data.payload_json or {},
            monthly_price=data.monthly_price,
            annual_price=data.annual_price,
            status=data.status,
            checkout_url=data.checkout_url,
        )
        return await self.add(obj)

    async def get_by_code(self, quote_code: str) -> Optional[Quote]:
        stmt = select(Quote).where(Quote.quote_code == quote_code)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_for_conversation(self, conversation_id: int) -> List[Quote]:
        stmt = select(Quote).where(Quote.conversation_id == conversation_id)
        return await self.list(stmt)


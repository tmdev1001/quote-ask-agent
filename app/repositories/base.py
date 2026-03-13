from __future__ import annotations

from typing import Any, Generic, List, Optional, Type, TypeVar

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base


ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """Generic async repository providing common helpers."""

    def __init__(self, session: AsyncSession, model: Type[ModelT]) -> None:
        self.session = session
        self.model = model

    async def get(self, id_: int) -> Optional[ModelT]:
        return await self.session.get(self.model, id_)

    async def list(self, stmt: Optional[Select[Any]] = None) -> List[ModelT]:
        query = stmt or select(self.model)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def add(self, obj: ModelT) -> ModelT:
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj


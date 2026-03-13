from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AuditLog
from app.repositories.base import BaseRepository


class AuditLogRepository(BaseRepository[AuditLog]):
    """Persistence operations for audit logs."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, AuditLog)

    async def add_event(
        self,
        event_type: str,
        conversation_id: Optional[int],
        event_data: Optional[dict] = None,
    ) -> AuditLog:
        obj = AuditLog(
            conversation_id=conversation_id,
            event_type=event_type,
            event_data_json=event_data or {},
        )
        return await self.add(obj)

    async def list_for_conversation(self, conversation_id: int) -> List[AuditLog]:
        stmt = select(AuditLog).where(AuditLog.conversation_id == conversation_id)
        return await self.list(stmt)


from __future__ import annotations

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AuditLog
from app.repositories import AuditLogRepository


class AuditService:
    """Persist useful audit trail events."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = AuditLogRepository(session)

    async def log_event(
        self,
        *,
        event_type: str,
        conversation_id: Optional[int] = None,
        event_data: Optional[dict] = None,
    ) -> AuditLog:
        """
        Save a new audit log event.

        Intended for tools / agent orchestration to record important actions.
        """

        log = await self.repo.add_event(
            event_type=event_type,
            conversation_id=conversation_id,
            event_data=event_data,
        )
        await self.session.commit()
        return log


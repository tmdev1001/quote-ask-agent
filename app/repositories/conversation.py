from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Conversation, ConversationMessage, ConversationState
from app.repositories.base import BaseRepository
from app.schemas.conversation import (
    ConversationCreate,
    ConversationMessageCreate,
    ConversationUpdate,
)


class ConversationRepository(BaseRepository[Conversation]):
    """Persistence operations for conversations."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Conversation)

    async def create_from_schema(self, data: ConversationCreate) -> Conversation:
        now = datetime.now(timezone.utc)
        obj = Conversation(
            customer_id=data.customer_id,
            channel=data.channel,
            channel_user_id=data.channel_user_id,
            status=data.status,
            flow_name=data.flow_name,
            started_at=now,
            last_message_at=now,
        )
        return await self.add(obj)

    async def list_active_by_channel_user(
        self,
        channel: str,
        channel_user_id: str,
    ) -> List[Conversation]:
        stmt: Select[Conversation] = select(Conversation).where(
            Conversation.channel == channel,
            Conversation.channel_user_id == channel_user_id,
            Conversation.status == "active",
        )
        return await self.list(stmt)

    async def touch_last_message(self, conversation: Conversation) -> None:
        conversation.last_message_at = datetime.now(timezone.utc)
        await self.session.flush()

    async def update_from_schema(self, conversation: Conversation, data: ConversationUpdate) -> Conversation:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(conversation, field, value)
        await self.session.flush()
        await self.session.refresh(conversation)
        return conversation


class MessageRepository(BaseRepository[ConversationMessage]):
    """Persistence operations for conversation messages."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ConversationMessage)

    async def append(self, data: ConversationMessageCreate) -> ConversationMessage:
        obj = ConversationMessage(
            conversation_id=data.conversation_id,
            direction=data.direction,
            message_type=data.message_type,
            content_text=data.content_text,
            raw_payload_json=data.raw_payload_json,
        )
        return await self.add(obj)


class StateRepository(BaseRepository[ConversationState]):
    """Persistence operations for conversation state."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ConversationState)

    async def get_by_conversation_id(self, conversation_id: int) -> Optional[ConversationState]:
        stmt = select(ConversationState).where(ConversationState.conversation_id == conversation_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def upsert_state(
        self,
        conversation_id: int,
        current_step: Optional[str],
        status: str,
        collected_fields: Optional[dict] = None,
        missing_fields: Optional[dict] = None,
        last_tool_action: Optional[str] = None,
    ) -> ConversationState:
        state = await self.get_by_conversation_id(conversation_id)
        if state is None:
            state = ConversationState(
                conversation_id=conversation_id,
                current_step=current_step,
                status=status,
                collected_fields_json=collected_fields or {},
                missing_fields_json=missing_fields or {},
                last_tool_action=last_tool_action,
            )
            return await self.add(state)

        state.current_step = current_step
        state.status = status
        if collected_fields is not None:
            state.collected_fields_json = collected_fields
        if missing_fields is not None:
            state.missing_fields_json = missing_fields
        state.last_tool_action = last_tool_action
        await self.session.flush()
        await self.session.refresh(state)
        return state


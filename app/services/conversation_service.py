from __future__ import annotations

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Conversation
from app.repositories import ConversationRepository, MessageRepository
from app.schemas.conversation import (
    ConversationCreate,
    ConversationMessageCreate,
)


class ConversationService:
    """Operations for creating and managing conversations and messages."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.conv_repo = ConversationRepository(session)
        self.msg_repo = MessageRepository(session)

    async def find_or_create_conversation(
        self,
        *,
        channel: str,
        channel_user_id: str,
        customer_id: Optional[int] = None,
        flow_name: Optional[str] = None,
    ) -> Conversation:
        """
        Find an active conversation by channel and channel_user_id,
        or create a new one if none exists.
        """

        existing_list = await self.conv_repo.list_active_by_channel_user(
            channel=channel,
            channel_user_id=channel_user_id,
        )
        if existing_list:
            return existing_list[0]

        created = await self.conv_repo.create_from_schema(
            ConversationCreate(
                customer_id=customer_id,
                channel=channel,
                channel_user_id=channel_user_id,
                flow_name=flow_name,
            )
        )
        await self.session.commit()
        return created

    async def add_inbound_message(
        self,
        conversation_id: int,
        *,
        text: Optional[str],
        raw_payload: Optional[dict] = None,
    ) -> None:
        """Create an inbound (user) message record."""

        await self.msg_repo.append(
            ConversationMessageCreate(
                conversation_id=conversation_id,
                direction="in",
                message_type="text",
                content_text=text,
                raw_payload_json=raw_payload,
            )
        )
        conversation = await self.conv_repo.get(conversation_id)
        if conversation is not None:
            await self.conv_repo.touch_last_message(conversation)
        await self.session.commit()

    async def add_outbound_message(
        self,
        conversation_id: int,
        *,
        text: Optional[str],
        raw_payload: Optional[dict] = None,
    ) -> None:
        """Create an outbound (Lyra) message record."""

        await self.msg_repo.append(
            ConversationMessageCreate(
                conversation_id=conversation_id,
                direction="out",
                message_type="text",
                content_text=text,
                raw_payload_json=raw_payload,
            )
        )
        conversation = await self.conv_repo.get(conversation_id)
        if conversation is not None:
            await self.conv_repo.touch_last_message(conversation)
        await self.session.commit()

    async def get_conversation(self, conversation_id: int) -> Optional[Conversation]:
        """
        Fetch a conversation by id.

        For now this returns the ORM object; higher layers can convert
        to Pydantic schemas when needed.
        """

        return await self.conv_repo.get(conversation_id)


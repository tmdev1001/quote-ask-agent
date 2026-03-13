from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import ConversationMessage
from app.repositories import ConversationRepository, MessageRepository
from app.schemas.conversation import (
    ConversationMessageRead,
    ConversationRead,
    ConversationStateRead,
)
from app.services.state_service import StateService


router = APIRouter()


@router.get("/api/conversations", response_model=List[ConversationRead])
async def list_conversations(
    db: AsyncSession = Depends(get_db),
) -> List[ConversationRead]:
    """List all conversations (for local testing)."""

    repo = ConversationRepository(db)
    conversations = await repo.list()
    return [ConversationRead.model_validate(c) for c in conversations]


@router.get("/api/conversations/{conversation_id}", response_model=ConversationRead)
async def get_conversation(
    conversation_id: int,
    db: AsyncSession = Depends(get_db),
) -> ConversationRead:
    """Fetch a single conversation."""

    repo = ConversationRepository(db)
    conv = await repo.get(conversation_id)
    if conv is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return ConversationRead.model_validate(conv)


@router.get(
    "/api/conversations/{conversation_id}/messages",
    response_model=List[ConversationMessageRead],
)
async def list_conversation_messages(
    conversation_id: int,
    db: AsyncSession = Depends(get_db),
) -> List[ConversationMessageRead]:
    """Return all messages belonging to a conversation."""

    repo = MessageRepository(db)
    stmt = select(ConversationMessage).where(ConversationMessage.conversation_id == conversation_id)
    messages = await repo.list(stmt)
    return [ConversationMessageRead.model_validate(m) for m in messages]


@router.get(
    "/api/conversations/{conversation_id}/state",
    response_model=ConversationStateRead,
)
async def get_conversation_state(
    conversation_id: int,
    db: AsyncSession = Depends(get_db),
) -> ConversationStateRead:
    """
    Return the flow state for a conversation.

    Uses the default 'auto_insurance_quote' flow for now.
    """

    service = StateService(db)
    state = await service.get_or_create_state(conversation_id, flow_name="auto_insurance_quote")
    return ConversationStateRead.model_validate(state)


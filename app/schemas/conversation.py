from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel

from app.schemas.base import ORMBaseModel, TimestampedModel


class ConversationBase(BaseModel):
    channel: str
    channel_user_id: str
    status: str = "active"
    flow_name: Optional[str] = None


class ConversationCreate(ConversationBase):
    """Payload to create a new conversation."""

    customer_id: Optional[int] = None


class ConversationUpdate(BaseModel):
    """Partial update for a conversation."""

    customer_id: Optional[int] = None
    status: Optional[str] = None
    flow_name: Optional[str] = None
    started_at: Optional[datetime] = None
    last_message_at: Optional[datetime] = None


class ConversationRead(TimestampedModel, ConversationBase, ORMBaseModel):
    """API-facing representation of a conversation."""

    id: int
    customer_id: Optional[int] = None
    started_at: Optional[datetime] = None
    last_message_at: Optional[datetime] = None


class ConversationMessageBase(BaseModel):
    direction: Literal["in", "out"]
    message_type: str = "text"
    content_text: Optional[str] = None
    raw_payload_json: Optional[Dict[str, Any]] = None


class ConversationMessageCreate(ConversationMessageBase):
    """Payload to append a message to a conversation."""

    conversation_id: int


class ConversationMessageRead(ORMBaseModel, ConversationMessageBase):
    """Representation of a conversation message."""

    id: int
    conversation_id: int
    created_at: datetime


class ConversationStateRead(ORMBaseModel):
    """Snapshot of the current conversational state."""

    id: int
    conversation_id: int
    current_step: Optional[str] = None
    status: str
    collected_fields_json: Optional[Dict[str, Any]] = None
    missing_fields_json: Optional[Dict[str, Any]] = None
    last_tool_action: Optional[str] = None
    updated_at: datetime


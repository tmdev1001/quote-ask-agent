"""
SQLAlchemy 2 typed models for Lyra quote intake.

SQLite-compatible; portable to PostgreSQL.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Float, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import CreatedAtMixin, TimestampMixin, UpdatedAtMixin

if TYPE_CHECKING:
    pass


class Customer(Base, TimestampMixin):
    """Customer identified by CPF and optional Telegram user."""

    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    cpf: Mapped[str] = mapped_column(String(32), index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    telegram_user_id: Mapped[Optional[str]] = mapped_column(String(64), index=True, nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    conversations: Mapped[list["Conversation"]] = relationship(
        back_populates="customer",
        foreign_keys="Conversation.customer_id",
    )
    quotes: Mapped[list["Quote"]] = relationship(
        back_populates="customer",
        foreign_keys="Quote.customer_id",
    )


class Conversation(Base, TimestampMixin):
    """Conversation thread (e.g. Telegram chat) with optional customer link."""

    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    customer_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("customers.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    channel: Mapped[str] = mapped_column(String(64), index=True)
    channel_user_id: Mapped[str] = mapped_column(String(64), index=True)
    status: Mapped[str] = mapped_column(String(32), default="active")
    flow_name: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    last_message_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    customer: Mapped[Optional["Customer"]] = relationship(
        back_populates="conversations",
        foreign_keys=[customer_id],
    )
    messages: Mapped[list["ConversationMessage"]] = relationship(
        back_populates="conversation",
        cascade="all, delete-orphan",
    )
    state: Mapped[Optional["ConversationState"]] = relationship(
        back_populates="conversation",
        uselist=False,
        cascade="all, delete-orphan",
    )
    documents: Mapped[list["Document"]] = relationship(
        back_populates="conversation",
        cascade="all, delete-orphan",
    )
    quotes: Mapped[list["Quote"]] = relationship(
        back_populates="conversation",
        foreign_keys="Quote.conversation_id",
    )


class ConversationMessage(Base, CreatedAtMixin):
    """Single message in a conversation (inbound or outbound)."""

    __tablename__ = "conversation_messages"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"),
        index=True,
    )
    direction: Mapped[str] = mapped_column(String(16))  # e.g. in, out
    message_type: Mapped[str] = mapped_column(String(32), default="text")
    content_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    raw_payload_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=dict)

    conversation: Mapped["Conversation"] = relationship(back_populates="messages")


class ConversationState(Base, UpdatedAtMixin):
    """Current flow state for a conversation (one row per conversation)."""

    __tablename__ = "conversation_states"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"),
        unique=True,
        index=True,
    )
    current_step: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="collecting")
    collected_fields_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=dict)
    missing_fields_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=dict)
    last_tool_action: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)

    conversation: Mapped["Conversation"] = relationship(back_populates="state")


class Document(Base, CreatedAtMixin):
    """Uploaded document (e.g. ID photo) with optional OCR and extracted fields."""

    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"),
        index=True,
    )
    file_name: Mapped[str] = mapped_column(String(255))
    file_type: Mapped[str] = mapped_column(String(64))
    file_path: Mapped[str] = mapped_column(Text)
    ocr_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    extracted_fields_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=dict)

    conversation: Mapped["Conversation"] = relationship(back_populates="documents")


class Quote(Base, TimestampMixin):
    """Simulated or real quote tied to a conversation and optional customer."""

    __tablename__ = "quotes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"),
        index=True,
    )
    customer_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("customers.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    quote_code: Mapped[str] = mapped_column(String(64), index=True)
    payload_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=dict)
    monthly_price: Mapped[float] = mapped_column(Float)
    annual_price: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(32), default="simulated")
    checkout_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    conversation: Mapped["Conversation"] = relationship(
        back_populates="quotes",
        foreign_keys=[conversation_id],
    )
    customer: Mapped[Optional["Customer"]] = relationship(
        back_populates="quotes",
        foreign_keys=[customer_id],
    )


class AuditLog(Base, CreatedAtMixin):
    """Audit trail for events (e.g. quote requested, checkout opened)."""

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    conversation_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("conversations.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    event_type: Mapped[str] = mapped_column(String(64), index=True)
    event_data_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=dict)

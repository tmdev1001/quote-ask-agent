from __future__ import annotations

from typing import Optional

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class Customer(Base):
    """Customer identified by Telegram user and CPF."""

    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_user_id: Mapped[str] = mapped_column(String(64), index=True)
    cpf: Mapped[str] = mapped_column(String(32), index=True)
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    conversations: Mapped[list["Conversation"]] = relationship(
        back_populates="customer",
        cascade="all, delete-orphan",
    )
    quotes: Mapped[list["Quote"]] = relationship(
        back_populates="customer",
        cascade="all, delete-orphan",
    )


class Conversation(Base):
    """Conversation state for a customer and Telegram chat."""

    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), index=True)
    telegram_chat_id: Mapped[str] = mapped_column(String(64), index=True)
    state: Mapped[str] = mapped_column(String(64), default="collecting")
    known_fields_json: Mapped[str] = mapped_column(
        Text,
        default="{}",
        comment="JSON blob of collected fields for the intake flow",
    )

    customer: Mapped[Customer] = relationship(back_populates="conversations")


class Quote(Base):
    """Simulated quote associated with a customer."""

    __tablename__ = "quotes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), index=True)
    premium: Mapped[float]
    currency: Mapped[str] = mapped_column(String(8), default="BRL")
    status: Mapped[str] = mapped_column(String(32), default="simulated")
    details_json: Mapped[str] = mapped_column(Text, default="{}")

    customer: Mapped[Customer] = relationship(back_populates="quotes")


class CheckoutSession(Base):
    """Simulated checkout session for a quote."""

    __tablename__ = "checkout_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    quote_id: Mapped[int] = mapped_column(ForeignKey("quotes.id"), index=True)
    checkout_url: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), default="pending")


"""
Model exports and wiring for Alembic and application code.

Import this package so that Base.metadata includes all tables.
"""

from __future__ import annotations

from app.core.database import Base
from app.models.models import (
    AuditLog,
    Conversation,
    ConversationMessage,
    ConversationState,
    Customer,
    Document,
    Quote,
)

__all__ = [
    "Base",
    "AuditLog",
    "Conversation",
    "ConversationMessage",
    "ConversationState",
    "Customer",
    "Document",
    "Quote",
]

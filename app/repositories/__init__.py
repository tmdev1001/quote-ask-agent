"""
Repository layer for encapsulating database operations.

Each repository is async and uses SQLAlchemy AsyncSession.
"""

from __future__ import annotations

from app.repositories.customer import CustomerRepository
from app.repositories.conversation import (
    ConversationRepository,
    MessageRepository,
    StateRepository,
)
from app.repositories.document import DocumentRepository
from app.repositories.quote import QuoteRepository
from app.repositories.audit import AuditLogRepository

__all__ = [
    "CustomerRepository",
    "ConversationRepository",
    "MessageRepository",
    "StateRepository",
    "DocumentRepository",
    "QuoteRepository",
    "AuditLogRepository",
]


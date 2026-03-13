"""
Pydantic v2 schemas for the Lyra quote intake backend.

These are intentionally minimal and focused on API boundaries and tools.
"""

from __future__ import annotations

from app.schemas.customer import (
    CustomerCreate,
    CustomerRead,
    CustomerUpdate,
)
from app.schemas.conversation import (
    ConversationCreate,
    ConversationRead,
    ConversationUpdate,
    ConversationMessageCreate,
    ConversationMessageRead,
    ConversationStateRead,
)
from app.schemas.quote import (
    QuoteCreate,
    QuoteRead,
)
from app.schemas.document import (
    DocumentCreate,
    DocumentRead,
)
from app.schemas.extraction import (
    ExtractionRequest,
    ExtractionResult,
)

__all__ = [
    "CustomerCreate",
    "CustomerRead",
    "CustomerUpdate",
    "ConversationCreate",
    "ConversationRead",
    "ConversationUpdate",
    "ConversationMessageCreate",
    "ConversationMessageRead",
    "ConversationStateRead",
    "QuoteCreate",
    "QuoteRead",
    "DocumentCreate",
    "DocumentRead",
    "ExtractionRequest",
    "ExtractionResult",
]


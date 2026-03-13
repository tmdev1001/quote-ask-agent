from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class ExtractionRequest(BaseModel):
    """Schema for requesting extraction from text or OCR."""

    conversation_id: int
    raw_text: Optional[str] = None
    document_ids: Optional[List[int]] = None
    target_fields: List[str]


class ExtractionResult(BaseModel):
    """Schema for returning extracted fields and confidence scores."""

    conversation_id: int
    extracted_fields: Dict[str, Any]
    missing_fields: List[str]


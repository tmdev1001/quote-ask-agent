from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel

from app.schemas.base import ORMBaseModel


class DocumentBase(BaseModel):
    conversation_id: int
    file_name: str
    file_type: str
    file_path: str
    ocr_text: Optional[str] = None
    extracted_fields_json: Optional[Dict[str, Any]] = None


class DocumentCreate(DocumentBase):
    """Payload for storing a new document reference."""


class DocumentRead(ORMBaseModel, DocumentBase):
    """Representation of a stored document."""

    id: int
    created_at: datetime


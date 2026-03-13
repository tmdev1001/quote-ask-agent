from __future__ import annotations

from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Document
from app.repositories.base import BaseRepository
from app.schemas.document import DocumentCreate


class DocumentRepository(BaseRepository[Document]):
    """Persistence operations for documents."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Document)

    async def create_from_schema(self, data: DocumentCreate) -> Document:
        obj = Document(
            conversation_id=data.conversation_id,
            file_name=data.file_name,
            file_type=data.file_type,
            file_path=data.file_path,
            ocr_text=data.ocr_text,
            extracted_fields_json=data.extracted_fields_json or {},
        )
        return await self.add(obj)

    async def list_for_conversation(self, conversation_id: int) -> List[Document]:
        stmt = select(Document).where(Document.conversation_id == conversation_id)
        return await self.list(stmt)


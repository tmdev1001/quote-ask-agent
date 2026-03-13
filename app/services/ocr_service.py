from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Document
from app.repositories import DocumentRepository
from app.schemas.document import DocumentRead


class BaseOCRProvider(ABC):
    """Abstract OCR provider interface."""

    @abstractmethod
    async def recognize(self, document: Document) -> str:  # pragma: no cover - interface
        """Return recognized text for the given document."""


class MockOCRProvider(BaseOCRProvider):
    """Simple mock OCR provider that returns deterministic placeholder text."""

    async def recognize(self, document: Document) -> str:
        return f"Mock OCR text for {document.file_name}"


class OCRService:
    """
    Service for running OCR on stored documents.

    Uses a swappable provider so real OCR can be plugged in later.
    """

    def __init__(
        self,
        session: AsyncSession,
        provider: BaseOCRProvider | None = None,
    ) -> None:
        self.session = session
        self.repo = DocumentRepository(session)
        self.provider = provider or MockOCRProvider()

    async def run_ocr_for_document(self, document_id: int) -> Document:
        """
        Run OCR for a single document and persist the recognized text.

        Returns the updated Document ORM instance.
        """

        document = await self.repo.get(document_id)
        if document is None:
            raise ValueError(f"Document {document_id} not found")

        ocr_text = await self.provider.recognize(document)
        document.ocr_text = ocr_text
        await self.session.flush()
        await self.session.refresh(document)
        await self.session.commit()
        return document


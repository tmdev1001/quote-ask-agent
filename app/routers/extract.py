from __future__ import annotations

from fastapi import APIRouter

from app.schemas.extraction import ExtractionRequest, ExtractionResult
from app.services.extraction_service import ExtractionService


router = APIRouter()


@router.post("/api/extract/text", response_model=ExtractionResult)
async def extract_from_text(payload: ExtractionRequest) -> ExtractionResult:
    """
    Run deterministic extraction against raw text for testing.

    Note: document_ids are ignored in this PoC endpoint; only raw_text
    is used.
    """

    if not payload.raw_text:
        return ExtractionResult(
            conversation_id=payload.conversation_id,
            extracted_fields={},
            missing_fields=payload.target_fields,
        )

    service = ExtractionService()
    return service.extract(payload, payload.raw_text)


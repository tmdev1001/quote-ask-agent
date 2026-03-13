"""
Lyra agent tools.

These are thin adapters around existing services and repositories so that
the OpenAI Agents SDK can call into the domain logic without duplicating it.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import ConversationRepository, DocumentRepository, QuoteRepository
from app.schemas.document import DocumentCreate
from app.schemas.extraction import ExtractionRequest, ExtractionResult
from app.schemas.quote import QuoteRead
from app.services import (
    AuditService,
    CheckoutService,
    ConversationService,
    CustomerService,
    ExtractionService,
    OCRService,
    QuoteService,
    StateService,
)


class LyraToolContext:
    """
    Simple context object that groups the async DB session and services.

    This is what the agent layer passes into tools so they can call the
    appropriate services without global state.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.customer_service = CustomerService(session)
        self.conversation_service = ConversationService(session)
        self.state_service = StateService(session)
        self.ocr_service = OCRService(session)
        self.quote_service = QuoteService(session)
        self.audit_service = AuditService(session)
        self.checkout_service = CheckoutService()
        self.extraction_service = ExtractionService()
        self.conversation_repo = ConversationRepository(session)
        self.document_repo = DocumentRepository(session)
        self.quote_repo = QuoteRepository(session)


# --- Customer and state tools -------------------------------------------------


async def lookup_customer(
    ctx: LyraToolContext,
    *,
    cpf: Optional[str] = None,
    telegram_user_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Lookup customer by CPF or Telegram id.

    Does not create new records; creation is handled explicitly elsewhere.
    """

    customer = None
    if cpf:
        customer = await ctx.customer_service.get_by_cpf(cpf)
    if customer is None and telegram_user_id:
        customer = await ctx.customer_service.get_by_telegram_user_id(telegram_user_id)

    if customer is None:
        return {"found": False}

    return {
        "found": True,
        "id": customer.id,
        "cpf": customer.cpf,
        "full_name": customer.full_name,
        "phone": customer.phone,
        "telegram_user_id": customer.telegram_user_id,
        "address": customer.address,
    }


async def get_conversation_state(
    ctx: LyraToolContext,
    *,
    conversation_id: int,
    flow_name: str = "auto_insurance_quote",
) -> Dict[str, Any]:
    """Return the current state record for a conversation."""

    state = await ctx.state_service.get_or_create_state(conversation_id, flow_name)
    return {
        "conversation_id": state.conversation_id,
        "current_step": state.current_step,
        "status": state.status,
        "collected_fields": state.collected_fields_json or {},
        "missing_fields": state.missing_fields_json or {},
        "last_tool_action": state.last_tool_action,
    }


async def update_collected_fields(
    ctx: LyraToolContext,
    *,
    conversation_id: int,
    new_fields: Dict[str, Any],
    flow_name: str = "auto_insurance_quote",
    current_step: Optional[str] = None,
    status: Optional[str] = None,
    last_tool_action: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Merge new collected fields into state and recompute missing fields.
    """

    state, collected, missing = await ctx.state_service.update_state_for_fields(
        conversation_id=conversation_id,
        flow_name=flow_name,
        new_fields=new_fields,
        current_step=current_step,
        status=status,
        last_tool_action=last_tool_action or "update_fields",
    )
    return {
        "conversation_id": state.conversation_id,
        "collected_fields": collected,
        "missing_fields": missing,
        "status": state.status,
        "current_step": state.current_step,
    }


async def get_missing_fields(
    ctx: LyraToolContext,
    *,
    conversation_id: int,
    flow_name: str = "auto_insurance_quote",
) -> List[str]:
    """
    Return the list of currently missing required fields.
    """

    state_info = await get_conversation_state(ctx, conversation_id=conversation_id, flow_name=flow_name)
    missing_flags: Dict[str, bool] = state_info.get("missing_fields", {})
    return [name for name, is_missing in missing_flags.items() if is_missing]


# --- Document and OCR tools ---------------------------------------------------


async def save_document_metadata(
    ctx: LyraToolContext,
    *,
    conversation_id: int,
    file_name: str,
    file_type: str,
    file_path: str,
) -> Dict[str, Any]:
    """
    Persist metadata for an uploaded document belonging to a conversation.
    """

    doc = await ctx.document_repo.create_from_schema(
        DocumentCreate(
            conversation_id=conversation_id,
            file_name=file_name,
            file_type=file_type,
            file_path=file_path,
        )
    )
    await ctx.session.commit()
    return {
        "id": doc.id,
        "conversation_id": doc.conversation_id,
        "file_name": doc.file_name,
        "file_type": doc.file_type,
        "file_path": doc.file_path,
    }


async def run_ocr_on_document(
    ctx: LyraToolContext,
    *,
    document_id: int,
) -> Dict[str, Any]:
    """
    Run OCR against a previously saved document.
    """

    updated = await ctx.ocr_service.run_ocr_for_document(document_id)
    return {
        "id": updated.id,
        "ocr_text": updated.ocr_text,
    }


# --- Extraction tools ---------------------------------------------------------


async def extract_fields_from_text(
    ctx: LyraToolContext,
    *,
    conversation_id: int,
    text: str,
    target_fields: List[str],
) -> ExtractionResult:
    """
    Use deterministic extraction to get structured fields from text.

    Returns an ExtractionResult with both values and confidence metadata.
    """

    request = ExtractionRequest(
        conversation_id=conversation_id,
        raw_text=text,
        document_ids=None,
        target_fields=target_fields,
    )
    return ctx.extraction_service.extract(request, text)


# --- Quote and checkout tools -------------------------------------------------


async def simulate_quote(
    ctx: LyraToolContext,
    *,
    conversation_id: int,
    customer_id: Optional[int],
    cpf: Optional[str],
    vehicle_plate: Optional[str],
    extra_payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Simulate a quote using the quote service.
    """

    quote = await ctx.quote_service.simulate_quote(
        conversation_id=conversation_id,
        customer_id=customer_id,
        cpf=cpf,
        vehicle_plate=vehicle_plate,
        extra_payload=extra_payload,
    )
    return {
        "id": quote.id,
        "quote_code": quote.quote_code,
        "monthly_price": quote.monthly_price,
        "annual_price": quote.annual_price,
        "status": quote.status,
        "checkout_url": quote.checkout_url,
    }


async def generate_checkout_link(
    ctx: LyraToolContext,
    *,
    quote_id: int,
) -> Dict[str, Any]:
    """
    Generate and persist a checkout URL for a quote.
    """

    quote = await ctx.quote_repo.get(quote_id)
    if quote is None:
        raise ValueError(f"Quote {quote_id} not found")

    checkout_url = ctx.checkout_service.build_checkout_url(quote)
    quote.checkout_url = checkout_url
    await ctx.session.flush()
    await ctx.session.commit()
    await ctx.session.refresh(quote)

    return {
        "id": quote.id,
        "quote_code": quote.quote_code,
        "checkout_url": quote.checkout_url,
    }


async def finalize_quote_flow(
    ctx: LyraToolContext,
    *,
    conversation_id: int,
    quote_id: int,
    flow_name: str = "auto_insurance_quote",
) -> Dict[str, Any]:
    """
    Mark the quote flow as complete for a conversation and log an audit event.
    """

    state, collected, missing = await ctx.state_service.update_state_for_fields(
        conversation_id=conversation_id,
        flow_name=flow_name,
        new_fields={},
        current_step="completed",
        status="completed",
        last_tool_action="finalize_quote_flow",
    )

    await ctx.audit_service.log_event(
        event_type="quote_flow_completed",
        conversation_id=conversation_id,
        event_data={
            "quote_id": quote_id,
            "missing_fields_at_completion": missing,
        },
    )

    return {
        "conversation_id": conversation_id,
        "quote_id": quote_id,
        "status": state.status,
        "current_step": state.current_step,
    }


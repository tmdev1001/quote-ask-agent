from __future__ import annotations

import hashlib
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Quote
from app.repositories import QuoteRepository
from app.schemas.quote import QuoteCreate, QuoteRead


class QuoteService:
    """
    Simulate quotes using simple rule-based logic.

    This is intentionally deterministic / lightly randomized and suitable
    for a PoC without real rating integration.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = QuoteRepository(session)

    def _base_premium(self, key: str) -> tuple[float, float]:
        """
        Compute a deterministic base premium from an identifier (e.g. CPF or plate).

        Uses a hash mod to jitter the price within a narrow range.
        """

        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
        jitter = int(digest[:4], 16) % 50  # 0-49
        monthly = 120.0 + float(jitter)
        annual = monthly * 10.0
        return monthly, annual

    def _generate_quote_code(self, conversation_id: int) -> str:
        return f"Q-{conversation_id:06d}"

    async def simulate_quote(
        self,
        *,
        conversation_id: int,
        customer_id: Optional[int],
        cpf: Optional[str],
        vehicle_plate: Optional[str],
        extra_payload: Optional[dict] = None,
    ) -> Quote:
        """
        Generate a simulated quote for a conversation.

        Uses CPF or vehicle plate as a stable key for deterministic pricing.
        """

        key = cpf or vehicle_plate or f"conv-{conversation_id}"
        monthly, annual = self._base_premium(key)
        quote_code = self._generate_quote_code(conversation_id)

        data = QuoteCreate(
            conversation_id=conversation_id,
            customer_id=customer_id,
            quote_code=quote_code,
            payload_json=extra_payload or {
                "pricing_key": key,
                "strategy": "simple_rule",
            },
            monthly_price=monthly,
            annual_price=annual,
            status="simulated",
            checkout_url=None,
        )

        quote = await self.repo.create_from_schema(data)
        await self.session.commit()
        return quote


from __future__ import annotations

from app.core.config import get_settings
from app.models import Quote


class CheckoutService:
    """
    Generate fake checkout URLs for quotes.

    For the PoC this simply points to a predictable path under the base URL.
    """

    def __init__(self) -> None:
        self.settings = get_settings()

    def build_checkout_url(self, quote: Quote) -> str:
        """Return a fake checkout URL for the given quote."""

        base = self.settings.base_url.rstrip("/")
        return f"{base}/checkout/{quote.quote_code}"


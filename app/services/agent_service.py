from __future__ import annotations

"""
AgentService: adapter between FastAPI/services and the OpenAI Agents SDK.

This layer is responsible for:
- creating the Lyra Agent
- wiring in the LyraToolContext so tools can talk to the database/services
- running the agent for a single user turn

The concrete runner API (e.g. Runner.run, Runner.run_streamed) is encapsulated
here so it can be swapped later without touching routers or business logic.
"""

from typing import Any, Dict

from agents import Runner  # type: ignore[import-not-found]
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.lyra_agent import build_lyra_agent
from app.agents.tools import LyraToolContext


class AgentService:
    """High-level entrypoint for running the Lyra agent."""

    def __init__(self) -> None:
        # The Agent is stateless across calls; sessions/memory are handled
        # by the Agents SDK and our own database-backed services.
        self._agent = build_lyra_agent()

    async def run_lyra_turn(
        self,
        *,
        session: AsyncSession,
        user_message: str,
        conversation_id: int,
        telegram_user_id: str | None = None,
    ) -> Dict[str, Any]:
        """
        Run a single Lyra turn for a user message.

        Returns a dict containing:
        - reply_text: what Lyra should say back to the user
        - tool_calls: any tool call summaries (if exposed by the SDK)

        Routers / Telegram handlers can use this to drive the conversation.
        """

        ctx = LyraToolContext(session)

        # The Agents SDK Runner will call our tools. We rely on the SDK to
        # handle tool-calling and agent loop orchestration.
        #
        # We pass conversation-related context through the initial message
        # metadata so Lyra (and tools) can resolve the right rows in the DB.
        #
        # NOTE: If the exact Runner API changes, adapt this call site only.
        result = await Runner.run(
            self._agent,
            user_message,
            extra_context={
                "conversation_id": conversation_id,
                "telegram_user_id": telegram_user_id,
                "tool_context": ctx,
            },
        )

        # The exact result shape depends on the Agents SDK. We expect a
        # 'final_output' text field and optionally structured tool summaries.
        reply_text = getattr(result, "final_output", None) or str(result)
        tool_calls = getattr(result, "tool_calls", None) or []

        return {
            "reply_text": reply_text,
            "tool_calls": tool_calls,
        }


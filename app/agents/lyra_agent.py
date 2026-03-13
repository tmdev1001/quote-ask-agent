"""
Lyra agent definition using the OpenAI Agents SDK.

This module defines the Agent object and how it is configured with
instructions and tools. The actual running of the agent loop is handled
by app.services.agent_service.AgentService so that the SDK can be swapped
or upgraded without touching business logic.
"""

from __future__ import annotations

from typing import Any, Dict, List

from agents import Agent  # type: ignore[import-not-found]

from app.agents.instructions import build_lyra_system_prompt, build_lyra_tool_instructions
from app.agents import tools as lyra_tools


def build_lyra_agent() -> Agent:
    """
    Construct the Lyra Agent instance.

    Notes:
    - We bind Python function tools from app.agents.tools.
    - The OpenAI model and API configuration are handled by the Agents SDK
      and environment variables, not here.
    """

    instructions = "\n\n".join(
        [
            build_lyra_system_prompt(),
            build_lyra_tool_instructions(),
        ]
    )

    # The Agents SDK supports registering callables as tools. We expose a
    # focused set that correspond to the domain services.
    function_tools: Dict[str, Any] = {
        "lookup_customer": lyra_tools.lookup_customer,
        "get_conversation_state": lyra_tools.get_conversation_state,
        "update_collected_fields": lyra_tools.update_collected_fields,
        "get_missing_fields": lyra_tools.get_missing_fields,
        "save_document_metadata": lyra_tools.save_document_metadata,
        "run_ocr_on_document": lyra_tools.run_ocr_on_document,
        "extract_fields_from_text": lyra_tools.extract_fields_from_text,
        "simulate_quote": lyra_tools.simulate_quote,
        "generate_checkout_link": lyra_tools.generate_checkout_link,
        "finalize_quote_flow": lyra_tools.finalize_quote_flow,
    }

    agent = Agent(
        name="Lyra",
        instructions=instructions,
        tools=list(function_tools.values()),
    )

    # Attach a mapping from tool name to function so the AgentService can
    # construct the LyraToolContext and pass it as the first argument.
    agent._lyra_tool_map = function_tools  # type: ignore[attr-defined]

    return agent


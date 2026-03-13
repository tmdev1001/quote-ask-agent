from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ConversationState
from app.repositories import StateRepository
from app.services.flow_config_service import FlowConfigService


class StateService:
    """
    Manage conversational state, collected fields, and missing fields.

    This service is intentionally generic so that a single flow config
    drives which fields are required and how progression works.
    """

    def __init__(
        self,
        session: AsyncSession,
        flow_service: Optional[FlowConfigService] = None,
    ) -> None:
        self.session = session
        self.repo = StateRepository(session)
        self.flow_service = flow_service or FlowConfigService()

    async def get_or_create_state(
        self,
        conversation_id: int,
        flow_name: str,
    ) -> ConversationState:
        """Find or create state row for a conversation."""

        state = await self.repo.get_by_conversation_id(conversation_id)
        if state is not None:
            return state

        required_fields = self.flow_service.get_required_fields(flow_name)
        state = await self.repo.upsert_state(
            conversation_id=conversation_id,
            current_step="greet",
            status="collecting",
            collected_fields={},
            missing_fields={field: True for field in required_fields},
            last_tool_action="init_state",
        )
        await self.session.commit()
        return state

    def _merge_collected_fields(
        self,
        existing: Dict[str, object],
        new_data: Dict[str, object],
    ) -> Dict[str, object]:
        """
        Merge new collected fields into existing ones.

        New non-null values overwrite previous ones, but we keep everything
        in a single flat dictionary for simplicity.
        """

        merged = dict(existing or {})
        for key, value in new_data.items():
            if value is not None:
                merged[key] = value
        return merged

    def _compute_missing_flags(
        self,
        required_fields: List[str],
        collected: Dict[str, object],
    ) -> Dict[str, bool]:
        """
        Compute which required fields are still missing.

        Avoid duplicate asks by marking only fields that are truly unknown.
        """

        flags: Dict[str, bool] = {}
        for field in required_fields:
            flags[field] = field not in collected or collected.get(field) in (None, "")
        return flags

    async def update_state_for_fields(
        self,
        *,
        conversation_id: int,
        flow_name: str,
        new_fields: Dict[str, object],
        current_step: Optional[str] = None,
        status: Optional[str] = None,
        last_tool_action: Optional[str] = None,
    ) -> Tuple[ConversationState, Dict[str, object], List[str]]:
        """
        Merge new collected fields, recompute missing fields, and update state.

        Returns:
        - updated state
        - merged collected_fields
        - list of missing field names
        """

        state = await self.get_or_create_state(conversation_id, flow_name)
        required = self.flow_service.get_required_fields(flow_name)

        collected_merged = self._merge_collected_fields(
            state.collected_fields_json or {},
            new_fields,
        )
        missing_flags = self._compute_missing_flags(required, collected_merged)
        missing_fields = [name for name, is_missing in missing_flags.items() if is_missing]

        updated_state = await self.repo.upsert_state(
            conversation_id=conversation_id,
            current_step=current_step or state.current_step,
            status=status or state.status,
            collected_fields=collected_merged,
            missing_fields=missing_flags,
            last_tool_action=last_tool_action,
        )
        await self.session.commit()
        return updated_state, collected_merged, missing_fields


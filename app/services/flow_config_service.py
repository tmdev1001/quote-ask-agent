from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List


class FlowConfigService:
    """Utility for loading and exposing flow configuration files."""

    def __init__(self, base_path: Path | None = None) -> None:
        self.base_path = base_path or Path(__file__).resolve().parent.parent / "flows"

    def _flow_path(self, flow_name: str) -> Path:
        return self.base_path / f"{flow_name}.json"

    @lru_cache(maxsize=8)
    def load_flow(self, flow_name: str) -> Dict[str, Any]:
        """Load a flow config JSON from disk (cached)."""

        path = self._flow_path(flow_name)
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def get_required_fields(self, flow_name: str) -> List[str]:
        """Return the list of required fields for a flow."""

        config = self.load_flow(flow_name)
        return list(config.get("required_fields", []))

    def get_field_prompts(self, flow_name: str) -> Dict[str, str]:
        """Return per-field prompts for a flow."""

        config = self.load_flow(flow_name)
        return dict(config.get("field_prompts", {}))


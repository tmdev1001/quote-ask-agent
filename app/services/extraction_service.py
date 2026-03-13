from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List, Tuple

from app.schemas.extraction import ExtractionRequest, ExtractionResult


class ExtractionService:
    """
    Deterministic extraction of structured fields from free text.

    Supports:
    - cpf
    - full_name
    - address
    - vehicle_plate

    Designed so that an LLM-assisted extractor can be plugged in later.
    """

    CPF_RE = re.compile(r"\b(\d{11})\b")
    VEHICLE_PLATE_RE = re.compile(r"\b([A-Z]{3}\d{4})\b", re.IGNORECASE)

    def extract(self, request: ExtractionRequest, text: str) -> ExtractionResult:
        """
        Extract fields from plain text.

        For now this uses simple regex/heuristics and returns dummy
        confidence values (e.g. 0.9 when matched).
        """

        target_fields: Iterable[str] = request.target_fields
        extracted: Dict[str, Any] = {}
        missing: List[str] = []

        # Normalise text once
        normalized = text.strip()

        for field in target_fields:
            if field == "cpf":
                match = self.CPF_RE.search(normalized)
                if match:
                    extracted["cpf"] = {
                        "value": match.group(1),
                        "confidence": 0.9,
                        "source": "regex",
                    }
                else:
                    missing.append("cpf")
            elif field == "vehicle_plate":
                match = self.VEHICLE_PLATE_RE.search(normalized)
                if match:
                    extracted["vehicle_plate"] = {
                        "value": match.group(1).upper(),
                        "confidence": 0.85,
                        "source": "regex",
                    }
                else:
                    missing.append("vehicle_plate")
            elif field == "full_name":
                # Heuristic: look for a line starting with "nome" or "nome completo"
                value, present = self._extract_line_by_prefix(
                    normalized,
                    prefixes=("nome completo", "nome"),
                )
                if present:
                    extracted["full_name"] = {
                        "value": value,
                        "confidence": 0.7,
                        "source": "heuristic",
                    }
                else:
                    missing.append("full_name")
            elif field == "address":
                value, present = self._extract_line_by_prefix(
                    normalized,
                    prefixes=("endereço", "endereco", "address"),
                )
                if present:
                    extracted["address"] = {
                        "value": value,
                        "confidence": 0.7,
                        "source": "heuristic",
                    }
                else:
                    missing.append("address")

        # Flatten to value-only structure for downstream state service,
        # but keep confidence metadata nested by field.
        flat_values: Dict[str, Any] = {
            key: meta["value"] for key, meta in extracted.items()
        }

        return ExtractionResult(
            conversation_id=request.conversation_id,
            extracted_fields={
                "values": flat_values,
                "meta": extracted,
            },
            missing_fields=missing,
        )

    def _extract_line_by_prefix(
        self,
        text: str,
        *,
        prefixes: Tuple[str, ...],
    ) -> Tuple[str, bool]:
        """
        Try to extract a value appearing after a prefix in a text line.

        Example:
            'Nome completo: Maria Silva' -> 'Maria Silva'
        """

        lowered = text.lower()
        lines = lowered.splitlines()
        original_lines = text.splitlines()

        for idx, line in enumerate(lines):
            for prefix in prefixes:
                if line.startswith(prefix.lower()):
                    # try to split on ':' or '-'
                    raw_original = original_lines[idx]
                    for sep in (":", "-", "–"):
                        if sep in raw_original:
                            value = raw_original.split(sep, 1)[1].strip()
                            if value:
                                return value, True
        return "", False


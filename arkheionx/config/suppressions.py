"""Suppression helpers for future scanner extraction."""
from __future__ import annotations

from typing import Any


def suppression_entries(config: dict[str, Any]) -> list[dict[str, Any]]:
    entries = config.get("suppressions", config.get("suppress_findings", []))
    if not isinstance(entries, list):
        return []
    return [item for item in entries if isinstance(item, dict)]


def suppressed_ids(config: dict[str, Any]) -> set[str]:
    ids: set[str] = set()
    for item in suppression_entries(config):
        finding_id = str(item.get("id", "")).strip()
        if finding_id:
            ids.add(finding_id)
    return ids

"""Demo fixture model for the Arkheionx guided demo workflow."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Demo:
    """A safe, local-only demo fixture and its recommended workflow."""

    id: str
    name: str
    description: str
    path: str  # repository-relative source path of the fixture
    recommended_target: str
    requires_foundry: bool
    expected_mode: str
    docs: str
    notes: str
    category: str
    risk_theme: str
    safety_label: str = "local-only toy demo"
    safe: bool = True
    local_only: bool = True

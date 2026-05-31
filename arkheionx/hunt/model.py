"""Hunt data model: value hotspots, hunter targets, suggested tests."""
from __future__ import annotations

from dataclasses import dataclass, field

from arkheionx.protocol.model import HEURISTIC


@dataclass
class SuggestedTest:
    target_id: str
    title: str
    test_type: str = "scenario"  # scenario | invariant | edge-case
    description: str = ""
    foundry_pattern: str = ""
    expected_property: str = ""
    evidence_level: str = HEURISTIC


@dataclass
class ValueHotspot:
    target_id: str
    target_type: str = "function"  # function | contract
    score: int = 0
    priority: str = "low"
    reasons: list[str] = field(default_factory=list)
    evidence_level: str = HEURISTIC
    suggested_next_command: str = ""


@dataclass
class HunterTarget:
    rank: int
    target_id: str
    score: int
    priority: str
    bug_classes: list[str] = field(default_factory=list)
    why_it_matters: list[str] = field(default_factory=list)
    suggested_tests: list[str] = field(default_factory=list)
    suggested_invariants: list[str] = field(default_factory=list)
    evidence_level: str = HEURISTIC
    next_command: str = ""

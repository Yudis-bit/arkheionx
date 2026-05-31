"""Proof artifact data model."""
from __future__ import annotations

from dataclasses import dataclass, field

from arkheionx.protocol.model import HEURISTIC


@dataclass
class ProofArtifact:
    target_id: str
    status: str = "scaffold_generated"
    foundry_available: bool = False
    build_status: str = "not_attempted"
    tests_generated: int = 0
    tests_run: int = 0
    tests_passed: int = 0
    tests_failed: int = 0
    trace_summary: str = ""
    evidence_level: str = HEURISTIC
    files: list[str] = field(default_factory=list)
    remaining_manual: list[str] = field(default_factory=list)

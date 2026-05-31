"""Evidence package data model."""
from __future__ import annotations

from dataclasses import dataclass, field

# Evidence-package level on top of the proof evidence levels.
EVIDENCE_READY = "EVIDENCE_READY"

# Evidence package statuses.
NO_PROOF = "no_proof"
SCAFFOLD_ONLY = "scaffold_only"
COMPILER_CONFIRMED_ONLY = "compiler_confirmed_only"
EXECUTION_CONFIRMED = "execution_confirmed"
EVIDENCE_READY_STATUS = "evidence_ready"


@dataclass
class EvidencePackage:
    target: str
    target_id: str
    evidence_level: str
    status: str
    json_path: str = ""
    text_path: str = ""
    proof_found: bool = False
    trace_found: bool = False
    tests_run: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    next_command: str = ""
    payload: dict = field(default_factory=dict)

"""Report draft data model."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ReportDraft:
    target: str
    title: str
    evidence_level: str
    status: str = "draft-created"
    md_path: str = ""
    json_path: str = ""
    proof_path: str = ""
    trace_path: str = ""
    next_command: str = ""
    payload: dict = field(default_factory=dict)

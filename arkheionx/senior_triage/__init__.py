"""Private Senior Researcher Triage mode for Arkheionx (`arkheionx triage`).

Experimental, local-only. Senior triage runs *before* `arkheionx review` and decides
what is worth reviewing and what should be killed early, so a human does not spend
time proving what should never be pursued.

It does not confirm vulnerabilities, does not assign severity, does not submit
reports, and makes no RPC or live-chain calls by default. Every output is a
local/static planning artifact and human review is required.
"""
from __future__ import annotations

from .command import triage_command
from .models import (
    ARTIFACT_TYPE,
    SCHEMA_VERSION,
    TOP_LEAD_LIMIT,
    LeadCandidate,
    SeniorTriagePack,
    TargetDecision,
)
from .pack import build_senior_triage_pack, default_triage_dir

__all__ = [
    "triage_command",
    "build_senior_triage_pack",
    "default_triage_dir",
    "SeniorTriagePack",
    "LeadCandidate",
    "TargetDecision",
    "SCHEMA_VERSION",
    "ARTIFACT_TYPE",
    "TOP_LEAD_LIMIT",
]

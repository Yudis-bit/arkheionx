"""Shared, vendor-agnostic safety wording for the v7 scope-orchestration layer.

Every generated v7 artifact restates these boundaries. The wording is checked by
``scripts/check_safety_wording.py``: it must never claim a vulnerability, assign
severity, or describe itself as a replacement for an audit.
"""
from __future__ import annotations

from arkheionx.core.safety import LOCAL_ONLY_DISCLAIMER, READINESS_DISCLAIMER

# One-line boundary embedded as ``safety_boundary`` in every v7 JSON artifact.
SAFETY_BOUNDARY = (
    "Local/static heuristic scope-planning artifact. Not a finding, not severity, "
    "not a confirmed vulnerability. Human review required."
)

BOUNDARY_LINES = [
    "These are local/static research and planning artifacts.",
    "Scope maps, review lanes, and scope tasks are planning artifacts, not findings and not exploit instructions.",
    "Evidence quality is not vulnerability validity.",
    "Candidate-with-evidence is not a confirmed vulnerability; it only means a human should review the candidate.",
    "A report candidate is not final triage.",
    "Task priority is not severity.",
    "No RPC, no live-chain calls, no transaction execution, no private keys, no exploit automation, no external AI API calls.",
    "Human review is required for every conclusion.",
]

DO_NOT_CLAIM = [
    "Do not claim a vulnerability without an independent local proof-of-concept.",
    "Do not treat task priority as severity.",
    "Do not submit a scope task or judge result directly as a finding.",
    "Do not treat a candidate-with-evidence result as a confirmed vulnerability.",
    "Do not treat known or accepted issues as new findings.",
    "Do not rely on trusted-role misbehaviour unless the scope says it is valid.",
    "Do not submit a low-only issue when the scope requires Medium/High impact.",
    "Arkheionx does not find bugs, assign severity, confirm vulnerabilities, or replace an audit.",
]

# Generic, vendor-agnostic actor terms used across generated artifacts.
ACTOR_TERMS = ("AI agent", "review agent", "human reviewer", "local test runner")


def safety_block() -> dict:
    """The ``safety`` object embedded in every v7 JSON artifact."""
    return {
        "disclaimer": LOCAL_ONLY_DISCLAIMER,
        "readiness": READINESS_DISCLAIMER,
        "boundary": list(BOUNDARY_LINES),
        "do_not_claim": list(DO_NOT_CLAIM),
        "human_review_required": True,
    }


def safety_flags() -> dict:
    """Boolean safety flags embedded in pack manifests."""
    return {
        "local_static_only": True,
        "no_rpc": True,
        "no_live_chain": True,
        "no_exploit_automation": True,
        "no_private_keys": True,
        "no_ai_api_calls": True,
        "no_vulnerability_claims": True,
        "no_severity_claims": True,
        "human_review_required": True,
    }

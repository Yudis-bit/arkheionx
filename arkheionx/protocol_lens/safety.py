"""Shared, vendor-agnostic safety wording for the v7.5 Protocol Lens layer.

Every generated lens artifact restates these boundaries. The wording is checked by
``scripts/check_safety_wording.py`` and by the layer's safety-wording tests: it must
never claim a vulnerability, assign severity, or describe itself as a replacement
for an audit, and it must never name an AI vendor.
"""
from __future__ import annotations

from arkheionx.core.safety import LOCAL_ONLY_DISCLAIMER, READINESS_DISCLAIMER

# One-line boundary embedded as ``safety_boundary`` in every lens JSON artifact.
SAFETY_BOUNDARY = (
    "Local/static heuristic protocol-lens planning artifact. Not a finding, not "
    "severity, not a confirmed vulnerability. Human review required."
)

# The four-line boundary block the spec requires on every artifact.
PLANNING_NOTICE = [
    "Planning artifact, not a finding.",
    "Evidence quality is not vulnerability validity.",
    "Human review required.",
    "No RPC, no live-chain action, no exploit automation.",
]

BOUNDARY_LINES = [
    "These are local/static protocol-aware research and planning artifacts.",
    "A protocol lens models a protocol; it does not confirm vulnerabilities.",
    "A review lane is not a vulnerability and lane priority is not severity.",
    "An evidence score is not vulnerability validity.",
    "A candidate with evidence is not confirmed; only a human can confirm it.",
    "Blind-spot ranking is a place to look, not a bug.",
    "No RPC, no live-chain calls, no transaction execution, no private keys, no exploit automation, no external AI API calls.",
    "Human review is required for every conclusion.",
]

DO_NOT_CLAIM = [
    "Do not claim a vulnerability without an independent local proof-of-concept.",
    "Do not treat a review lane or a scope task as a finding.",
    "Do not treat lane or task priority as severity.",
    "Do not treat a VALIDATED_CANDIDATE result as a confirmed vulnerability.",
    "Do not treat known or accepted issues as new findings.",
    "Do not rely on trusted-role behaviour unless the scope marks it valid.",
    "Do not modify protocol source to make a test pass.",
    "Arkheionx does not find bugs, assign severity, confirm vulnerabilities, or replace an audit.",
]

# Generic, vendor-agnostic actor terms used across generated artifacts.
ACTOR_TERMS = ("AI agent", "review agent", "human reviewer", "local test runner")


def safety_block() -> dict:
    """The ``safety`` object embedded in every lens JSON artifact."""
    return {
        "disclaimer": LOCAL_ONLY_DISCLAIMER,
        "readiness": READINESS_DISCLAIMER,
        "planning_notice": list(PLANNING_NOTICE),
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
        "no_protocol_source_modification": True,
        "no_vulnerability_claims": True,
        "no_severity_claims": True,
        "human_review_required": True,
    }


def planning_notice_block() -> str:
    """The four-line planning notice as a Markdown block."""
    return "\n".join(PLANNING_NOTICE)

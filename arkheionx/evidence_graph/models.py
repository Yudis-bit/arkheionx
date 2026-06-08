"""Data model for the v6 Evidence Graph + Interaction Matrix layer.

Defines the evidence-state and evidence-strength vocabularies, the interaction
classes and priority labels, the shared safety wording, and the lightweight
``EvidenceNode`` and ``Interaction`` dataclasses the engine builds.

Everything here is heuristic and local/static. An evidence state is not a
vulnerability claim. ``confirmed-candidate`` is not a confirmed vulnerability.
``unresolved`` does not mean vulnerable. Interaction priority is not severity.
Human review is required for every conclusion.
"""
from __future__ import annotations

from dataclasses import dataclass, field

# Reuse the v5 criticality / review-density vocabularies so v6 stays consistent
# with the blind-spot layer it builds on.
from arkheionx.blind_spots.models import (  # noqa: F401
    CRIT_HIGH,
    CRIT_LOW,
    CRIT_MEDIUM,
    CRIT_UNKNOWN,
    CRIT_VERY_HIGH,
    CRITICALITY_LABELS,
    DENSITY_MEDIUM,
    DENSITY_NONE,
    DENSITY_STRONG,
    DENSITY_UNKNOWN,
    DENSITY_WEAK,
    DENSITY_LABELS,
    criticality_rank,
)

SCHEMA_VERSION = "1.0.0"

KIND_EVIDENCE_GRAPH = "evidence-graph"
KIND_INTERACTION_MATRIX = "interaction-matrix"
KIND_UNRESOLVED_MAP = "unresolved-map"
KIND_COMPLETE_REVIEW_MANIFEST = "complete-review-manifest"

# --- Evidence state -------------------------------------------------------
# Every important surface is classified into exactly one of these states.
# None of them is a vulnerability claim.
STATE_UNCLASSIFIED = "unclassified"
STATE_UNRESOLVED = "unresolved"
STATE_TESTED = "tested"
STATE_REJECTED_WITH_EVIDENCE = "rejected-with-evidence"
STATE_CONFIRMED_CANDIDATE = "confirmed-candidate"
STATE_NEEDS_HUMAN_REVIEW = "needs-human-review"
STATE_OUT_OF_SCOPE = "out-of-scope"
STATE_INSUFFICIENT_EVIDENCE = "insufficient-evidence"

EVIDENCE_STATES = (
    STATE_UNCLASSIFIED,
    STATE_UNRESOLVED,
    STATE_TESTED,
    STATE_REJECTED_WITH_EVIDENCE,
    STATE_CONFIRMED_CANDIDATE,
    STATE_NEEDS_HUMAN_REVIEW,
    STATE_OUT_OF_SCOPE,
    STATE_INSUFFICIENT_EVIDENCE,
)

# Stable display/summary order for the state summary block.
EVIDENCE_STATE_ORDER = (
    STATE_TESTED,
    STATE_REJECTED_WITH_EVIDENCE,
    STATE_CONFIRMED_CANDIDATE,
    STATE_UNRESOLVED,
    STATE_INSUFFICIENT_EVIDENCE,
    STATE_NEEDS_HUMAN_REVIEW,
    STATE_UNCLASSIFIED,
    STATE_OUT_OF_SCOPE,
)

# States that mean "this question is not closed by local evidence".
OPEN_STATES = (
    STATE_UNRESOLVED,
    STATE_INSUFFICIENT_EVIDENCE,
    STATE_UNCLASSIFIED,
    STATE_NEEDS_HUMAN_REVIEW,
)

# --- Evidence strength ----------------------------------------------------
STRENGTH_STRONG = "strong"
STRENGTH_MEDIUM = "medium"
STRENGTH_WEAK = "weak"
STRENGTH_NONE = "none"
STRENGTH_UNKNOWN = "unknown"
EVIDENCE_STRENGTHS = (
    STRENGTH_STRONG,
    STRENGTH_MEDIUM,
    STRENGTH_WEAK,
    STRENGTH_NONE,
    STRENGTH_UNKNOWN,
)
_STRENGTH_ORDER = {
    STRENGTH_STRONG: 0,
    STRENGTH_MEDIUM: 1,
    STRENGTH_WEAK: 2,
    STRENGTH_NONE: 3,
    STRENGTH_UNKNOWN: 4,
}

# --- Confidence (heuristic, never a probability) --------------------------
CONFIDENCE_HIGH = "high"
CONFIDENCE_MEDIUM = "medium"
CONFIDENCE_LOW = "low"
CONFIDENCE_LABELS = (CONFIDENCE_HIGH, CONFIDENCE_MEDIUM, CONFIDENCE_LOW)

# --- Interaction priority (heuristic review order, never severity) --------
IP_VERY_HIGH = "very-high"
IP_HIGH = "high"
IP_MEDIUM = "medium"
IP_MONITOR = "monitor"
INTERACTION_PRIORITIES = (IP_VERY_HIGH, IP_HIGH, IP_MEDIUM, IP_MONITOR)
_IP_ORDER = {IP_VERY_HIGH: 0, IP_HIGH: 1, IP_MEDIUM: 2, IP_MONITOR: 3}

# --- Surface types --------------------------------------------------------
SURFACE_TYPES = (
    "value-entry",
    "value-exit",
    "accounting",
    "authorization",
    "oracle",
    "liquidation",
    "periphery",
    "callback-external",
    "admin-emergency",
    "lifecycle",
    "share-math",
    "blocklist",
    "fee",
    "connector",
    "review-surface",
)

# --- Evidence gap types ---------------------------------------------------
GAP_TYPES = (
    "no-direct-test",
    "no-invariant",
    "no-fuzz",
    "no-boundary-test",
    "no-negative-path-test",
    "no-interaction-test",
    "no-lifecycle-test",
    "no-pre-post-balance-check",
    "no-pre-post-state-check",
    "no-attacker-victim-separation",
    "no-cross-contract-test",
    "no-oracle-edge-test",
    "no-rounding-edge-test",
    "no-callback-order-test",
    "no-admin-path-test",
    "no-pause/blocklist-test",
    "no-preview-vs-actual-test",
    "no-fee-edge-test",
    "no-connector-accounting-test",
    "no-merkle-shape-test",
    "no-signature-replay-test",
)

# --- Shared safety boundary -----------------------------------------------
BOUNDARY_LINES = [
    "This is a local/static review artifact.",
    "Evidence state is not a vulnerability claim.",
    "Confirmed-candidate is not a confirmed vulnerability.",
    "Interaction priority is not severity.",
    "Unresolved does not mean vulnerable.",
    "No RPC, no live-chain calls, no private keys, no exploit automation.",
    "Human review is required for every conclusion.",
]

DO_NOT_CLAIM = [
    "Do not submit an evidence state as a finding.",
    "Do not treat confirmed-candidate as a confirmed vulnerability.",
    "Do not treat interaction priority as severity.",
    "Do not treat unresolved as vulnerable.",
    "Do not claim protocol safety from a tested or rejected-with-evidence state.",
    "Human review is required before any conclusion.",
]


def evidence_strength_rank(label: str) -> int:
    return _STRENGTH_ORDER.get(label, 5)


def weaker_strength(a: str, b: str) -> str:
    """Return the weaker (less complete) of two evidence-strength labels."""
    return a if evidence_strength_rank(a) >= evidence_strength_rank(b) else b


def interaction_priority_rank(label: str) -> int:
    return _IP_ORDER.get(label, 4)


@dataclass
class EvidenceNode:
    """One classified review surface in the evidence graph (JSON-ready)."""

    node_id: str
    surface_id: str
    surface_name: str
    contract: str
    function: str
    source_file: str = ""
    source_line: int = 0
    surface_type: str = "review-surface"
    criticality_potential: str = CRIT_UNKNOWN
    review_density: str = DENSITY_UNKNOWN
    blind_spot_priority: str = "monitor"
    assumptions: list[str] = field(default_factory=list)
    counterfactuals: list[str] = field(default_factory=list)
    tests_detected: int = 0
    invariants_detected: bool = False
    fuzz_detected: bool = False
    proof_plan_links: list[str] = field(default_factory=list)
    hypothesis_links: list[str] = field(default_factory=list)
    evidence_state: str = STATE_UNCLASSIFIED
    evidence_strength: str = STRENGTH_UNKNOWN
    confidence: str = CONFIDENCE_LOW
    why_state: str = ""
    unresolved_reason: str = ""
    missing_evidence: list[str] = field(default_factory=list)
    next_test_direction: str = ""
    human_review_required: bool = True

    def to_dict(self) -> dict:
        from dataclasses import asdict

        return asdict(self)


@dataclass
class Interaction:
    """One meaningful combination of surfaces that may hide bugs (JSON-ready).

    An interaction is a review candidate, never a vulnerability. Interaction
    priority is a heuristic review order, never a severity.
    """

    interaction_id: str
    interaction_class: str
    surfaces: list[str] = field(default_factory=list)
    contracts: list[str] = field(default_factory=list)
    functions: list[str] = field(default_factory=list)
    source_refs: list[str] = field(default_factory=list)
    why_combination_matters: str = ""
    criticality_potential: str = CRIT_UNKNOWN
    review_density: str = DENSITY_UNKNOWN
    evidence_state: str = STATE_UNCLASSIFIED
    evidence_strength: str = STRENGTH_UNKNOWN
    tests_detected: int = 0
    impact_score: int = 0
    review_gap_score: int = 0
    interaction_complexity_score: int = 0
    interaction_priority: str = IP_MONITOR
    score_reasons: list[str] = field(default_factory=list)
    missing_test_direction: str = ""
    suggested_invariant: str = ""
    suggested_counterfactual: str = ""
    stop_condition: str = ""
    human_review_required: bool = True

    def to_dict(self) -> dict:
        from dataclasses import asdict

        return asdict(self)

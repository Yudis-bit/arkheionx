"""Data model for the v5 Blind Spot Intelligence layer.

Defines the label vocabularies, the shared safety wording, and the lightweight
``SurfaceRecord`` dataclass that the engine builds for every reviewable surface.

Everything here is heuristic and local/static. A blind spot candidate is a place
to look, not a vulnerability. Criticality potential is a blast-radius estimate,
not a severity. Human review is required for every conclusion.
"""
from __future__ import annotations

from dataclasses import dataclass, field

SCHEMA_VERSION = "1.0.0"
KIND_BLIND_SPOTS = "blind-spots"
KIND_CRITICALITY_MAP = "criticality-map"
KIND_COUNTERFACTUALS = "counterfactuals"
KIND_RESEARCH_PACK_MANIFEST = "research-pack-manifest"

# Criticality potential — heuristic blast radius if a bug existed. NOT severity.
CRIT_VERY_HIGH = "very-high"
CRIT_HIGH = "high"
CRIT_MEDIUM = "medium"
CRIT_LOW = "low"
CRIT_UNKNOWN = "unknown"
CRITICALITY_LABELS = (CRIT_VERY_HIGH, CRIT_HIGH, CRIT_MEDIUM, CRIT_LOW, CRIT_UNKNOWN)
_CRIT_ORDER = {CRIT_VERY_HIGH: 0, CRIT_HIGH: 1, CRIT_MEDIUM: 2, CRIT_LOW: 3, CRIT_UNKNOWN: 4}

# Review density — heuristic estimate of local review evidence on a surface.
DENSITY_STRONG = "strong"
DENSITY_MEDIUM = "medium"
DENSITY_WEAK = "weak"
DENSITY_NONE = "none"
DENSITY_UNKNOWN = "unknown"
DENSITY_LABELS = (DENSITY_STRONG, DENSITY_MEDIUM, DENSITY_WEAK, DENSITY_NONE, DENSITY_UNKNOWN)
_WEAK_DENSITY = {DENSITY_WEAK, DENSITY_NONE, DENSITY_UNKNOWN}

# Blind spot priority — heuristic review order, never severity/probability.
BSP_VERY_HIGH = "very-high"
BSP_HIGH = "high"
BSP_MEDIUM = "medium"
BSP_MONITOR = "monitor"
BLIND_SPOT_PRIORITIES = (BSP_VERY_HIGH, BSP_HIGH, BSP_MEDIUM, BSP_MONITOR)
_BSP_ORDER = {BSP_VERY_HIGH: 0, BSP_HIGH: 1, BSP_MEDIUM: 2, BSP_MONITOR: 3}

# Hypothesis/finding status vocabulary (shared with the research-memory layer).
STATUS_OPEN = "open"
STATUSES = ("open", "testing", "rejected", "confirmed", "needs-human-review")

# Shared safety boundary, restated on every artifact.
BOUNDARY_LINES = [
    "Local/static heuristic review map.",
    "Blind spot candidates are not vulnerabilities.",
    "Criticality potential is not severity.",
    "Counterfactuals are research prompts, not findings.",
    "No RPC, no live-chain calls, no private keys, no exploit automation.",
    "Human review is required for every conclusion.",
]

DO_NOT_CLAIM = [
    "Do not submit blind spot output as a finding.",
    "Do not submit criticality potential as severity.",
    "Do not submit counterfactuals without a local proof.",
    "Do not claim protocol safety from rejected hypotheses.",
    "Do not run live attacks; ArkheionX is local/static only.",
    "Human review is required before any conclusion.",
]


def criticality_rank(label: str) -> int:
    return _CRIT_ORDER.get(label, 5)


def blind_spot_rank(label: str) -> int:
    return _BSP_ORDER.get(label, 4)


def is_weak_density(label: str) -> bool:
    return label in _WEAK_DENSITY


@dataclass
class SurfaceRecord:
    """One reviewable surface, enriched with heuristic signals and scores.

    Built from the review map and research surfaces. JSON-ready via
    :meth:`to_dict`. All fields are heuristic; ``manual_review_required`` is
    always true.
    """

    target: str
    contract: str
    function: str
    source: str = ""
    review_priority: str = "low"  # review-map order (high|medium|low)
    coverage_signal: str = "unknown"
    review_density: str = DENSITY_UNKNOWN
    risk_signals: list[str] = field(default_factory=list)  # human-readable labels
    auth_kinds: list[str] = field(default_factory=list)
    periphery_interactions: list[str] = field(default_factory=list)
    behavior_signals: list[str] = field(default_factory=list)
    cross_contract_targets: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)  # related assumption ids
    test_reference_count: int = 0

    # Scores (transparent, additive).
    impact_score: int = 0
    impact_dimensions: list[dict] = field(default_factory=list)  # {dimension, points}
    review_gap_score: int = 0
    complexity_score: int = 0
    assumption_score: int = 0
    blind_spot_score: int = 0

    # Labels.
    criticality_potential: str = CRIT_UNKNOWN
    blind_spot_priority: str = BSP_MONITOR

    # Reasoning + guidance.
    primary_dimension: str = ""
    secondary_dimensions: list[str] = field(default_factory=list)
    score_reasons: list[str] = field(default_factory=list)
    why_it_may_be_skipped: str = ""
    why_it_may_matter: str = ""
    suggested_counterfactual: str = ""
    suggested_local_test: str = ""
    evidence_needed: str = ""
    manual_review_required: bool = True

    def to_dict(self) -> dict:
        from dataclasses import asdict

        return asdict(self)

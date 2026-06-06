"""Data model for the Protocol Review Map (v3.1.0).

These dataclasses describe a local, static review surface for a DeFi repo:
contracts, functions, value paths, assumptions, test gaps, proof suggestions,
and evidence links. They are review guidance, not confirmed findings. Every
structure serializes deterministically via :func:`to_dict` for stable JSON.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field

SCHEMA_VERSION = "1.0.0"

# Evidence ladder. Review-map signals start at HEURISTIC and only rise when
# connected to compiler/execution/evidence artifacts and, finally, human review.
HEURISTIC = "HEURISTIC"
COMPILER_CONFIRMED = "COMPILER_CONFIRMED"
EXECUTION_CONFIRMED = "EXECUTION_CONFIRMED"
EVIDENCE_READY = "EVIDENCE_READY"
HUMAN_REVIEWED = "HUMAN_REVIEWED"
EVIDENCE_LEVELS = (HEURISTIC, COMPILER_CONFIRMED, EXECUTION_CONFIRMED, EVIDENCE_READY, HUMAN_REVIEWED)

# Review priority (never a severity; it only ranks what to look at first).
HIGH = "high"
MEDIUM = "medium"
LOW = "low"
PRIORITIES = (HIGH, MEDIUM, LOW)
_PRIORITY_ORDER = {HIGH: 0, MEDIUM: 1, LOW: 2}


def priority_rank(priority: str) -> int:
    return _PRIORITY_ORDER.get(priority, 3)


def to_dict(obj: object) -> object:
    """Deterministically serialize a review-map dataclass or container."""

    if hasattr(obj, "__dataclass_fields__"):
        return asdict(obj)
    if isinstance(obj, (list, tuple)):
        return [to_dict(item) for item in obj]
    return obj


@dataclass
class ContractSurface:
    name: str
    path: str
    kind: str = "contract"
    functions: list[str] = field(default_factory=list)
    roles: list[str] = field(default_factory=list)
    assets: list[str] = field(default_factory=list)
    external_calls: list[str] = field(default_factory=list)
    oracle_signals: list[str] = field(default_factory=list)
    value_sensitive: bool = False
    review_priority: str = LOW
    # v3.5 additive: stable protocol intelligence ID (optional, backward-compatible).
    contract_id: str = ""


@dataclass
class FunctionSurface:
    contract: str
    name: str
    signature: str = ""
    visibility: str = "unspecified"
    mutability: str = "unknown"
    path: str = ""
    line: int = 0
    value_direction: str = "none"  # in | out | both | none
    value_keywords: list[str] = field(default_factory=list)
    risk_signals: list[str] = field(default_factory=list)
    test_references: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    suggested_tests: list[str] = field(default_factory=list)
    review_priority: str = LOW
    # v3.5 additive: stable protocol intelligence ID (optional, backward-compatible).
    function_id: str = ""

    @property
    def display_id(self) -> str:
        return f"{self.contract}.{self.name}"


@dataclass
class ValuePath:
    id: str
    label: str
    entry_function: str = ""
    movement: list[str] = field(default_factory=list)
    exit_function: str = ""
    assets: list[str] = field(default_factory=list)
    conditions: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    test_coverage_hint: str = "none"  # none | partial | referenced
    evidence_level: str = HEURISTIC
    review_priority: str = LOW
    # v3.5 additive: stable protocol intelligence IDs (optional, backward-compatible).
    entry_function_id: str = ""
    exit_function_id: str = ""


@dataclass
class Assumption:
    id: str
    title: str
    description: str = ""
    category: str = "general"
    used_by: list[str] = field(default_factory=list)
    signals: list[str] = field(default_factory=list)
    missing_tests: list[str] = field(default_factory=list)
    evidence_level: str = HEURISTIC
    status: str = "unverified"


@dataclass
class TestGap:
    id: str
    title: str
    description: str = ""
    related_function: str = ""
    related_value_path: str = ""
    suggested_test: str = ""
    rationale: str = ""
    confidence: str = LOW
    evidence_level: str = HEURISTIC
    status: str = "open"
    # v3.5 additive: stable protocol intelligence ID for related_function (optional).
    function_id: str = ""


@dataclass
class ProofSuggestion:
    id: str
    target: str
    title: str = ""
    objective: str = ""
    setup: list[str] = field(default_factory=list)
    action: str = ""
    assertions: list[str] = field(default_factory=list)
    related_assumption: str = ""
    related_test_gap: str = ""
    foundry_hint: str = ""
    # v3.5 additive: stable protocol intelligence ID for target (optional).
    target_function_id: str = ""


@dataclass
class EvidenceLink:
    id: str
    source: str  # proof | trace | evidence | report | none
    artifact_path: str = ""
    related_target: str = ""
    evidence_level: str = HEURISTIC
    status: str = "linked"
    target: str = ""
    target_id: str = ""
    readiness: str = ""
    evidence_package_id: str = ""
    proof_receipt_id: str = ""
    trace_receipt_id: str = ""
    artifacts: dict[str, str] = field(default_factory=dict)
    artifact_kind: str = ""
    review_status: str = "NEEDS_HUMAN_REVIEW"
    manual_review_required: bool = True
    report_status: str = ""
    report_readiness: dict = field(default_factory=dict)
    limitations: list[str] = field(default_factory=list)


@dataclass
class ReviewerNote:
    id: str
    title: str
    body: str = ""
    next_step: str = ""
    priority: str = MEDIUM


@dataclass
class ReviewMapSummary:
    protocol_types: list[str] = field(default_factory=list)
    contracts_analyzed: int = 0
    functions_mapped: int = 0
    value_paths: int = 0
    assumptions: int = 0
    test_gaps: int = 0
    proof_suggestions: int = 0
    evidence_links: int = 0
    text: str = ""


@dataclass
class SafetyInfo:
    disclaimer: str
    boundaries: list[str] = field(default_factory=list)


@dataclass
class ReviewMap:
    schema_version: str
    generated_at: str
    repo_path: str
    mode: str
    summary: ReviewMapSummary
    contracts: list[ContractSurface] = field(default_factory=list)
    functions: list[FunctionSurface] = field(default_factory=list)
    value_paths: list[ValuePath] = field(default_factory=list)
    assumptions: list[Assumption] = field(default_factory=list)
    test_gaps: list[TestGap] = field(default_factory=list)
    proof_suggestions: list[ProofSuggestion] = field(default_factory=list)
    evidence_links: list[EvidenceLink] = field(default_factory=list)
    reviewer_notes: list[ReviewerNote] = field(default_factory=list)
    safety: SafetyInfo = field(default_factory=lambda: SafetyInfo(disclaimer=""))

    def to_payload(self) -> dict:
        """Return a JSON-ready dict with summary fields first."""

        return asdict(self)

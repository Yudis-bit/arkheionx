"""Data model for the v7.5 Protocol Lens Pack layer.

A *protocol lens* models a specific protocol family (its value flows, behavior
promises, economic invariants, temporal windows, and periphery composition) so
Arkheionx can turn a generic local review into a protocol-aware research workflow.

This layer ships in the v8.0.1 package: v4 maps value flow, v5 prioritizes blind
spots, v6 classifies evidence, v7 turns scope into lanes/tasks, v7.5 added
protocol-aware lenses, and v8 makes them generic protocol-family models behind the
primary `arkheionx review` command. The package version is ``8.0.1``; the lens layer
carries its own :data:`SCHEMA_VERSION` for its JSON artifacts.

Everything here is heuristic and local/static. A lens is not a finding. A review
lane is not a vulnerability. An evidence score is not vulnerability validity. A
candidate with evidence is not confirmed. Task priority is not severity. Human
review is required for every conclusion. No RPC, no live-chain calls, no
transaction execution, no private keys, and no exploit automation.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field

# The lens layer's own schema version (distinct from the package version, 8.0.1).
SCHEMA_VERSION = "1.0.0"
LENS_LAYER = "v8.0"

# --- Artifact kinds -------------------------------------------------------
KIND_LENS_LIST = "lens-list"
KIND_LENS_MODEL = "lens-protocol-model"
KIND_LENS_MAP = "lens-map"
KIND_LENS_LANES = "lens-lanes"
KIND_LENS_TASKS = "lens-tasks"
KIND_LENS_EVIDENCE = "lens-evidence"
KIND_LENS_REPORT_FILTER = "lens-report-filter"
KIND_LENS_PACK_MANIFEST = "lens-pack-manifest"

# --- Marker emitted when scope information is missing ----------------------
SCOPE_INCOMPLETE_LOCAL_ONLY = "SCOPE_INCOMPLETE_LOCAL_ONLY"

# --- Marker for a symbol the lens looked for but did not find locally ------
UNKNOWN_IN_LOCAL_REPO = "UNKNOWN_IN_LOCAL_REPO"

# --- Priority (heuristic review order, never severity) --------------------
PRIORITY_VERY_HIGH = "very-high"
PRIORITY_HIGH = "high"
PRIORITY_MEDIUM = "medium"
PRIORITY_MONITOR = "monitor"
PRIORITIES = (PRIORITY_VERY_HIGH, PRIORITY_HIGH, PRIORITY_MEDIUM, PRIORITY_MONITOR)
_PRIORITY_ORDER = {PRIORITY_VERY_HIGH: 0, PRIORITY_HIGH: 1, PRIORITY_MEDIUM: 2, PRIORITY_MONITOR: 3}


def priority_rank(label: str) -> int:
    return _PRIORITY_ORDER.get(label, 4)


# --- Evidence status labels (exactly nine; section 12 of the spec) --------
EV_DIRECTLY_TESTED_STRONG = "DIRECTLY_TESTED_STRONG"
EV_DIRECTLY_TESTED_WEAK = "DIRECTLY_TESTED_WEAK"
EV_INDIRECTLY_TESTED = "INDIRECTLY_TESTED"
EV_HAPPY_PATH_ONLY = "HAPPY_PATH_ONLY"
EV_FUZZED_BUT_NOT_TARGETED = "FUZZED_BUT_NOT_TARGETED"
EV_FORMALLY_PROVEN = "FORMALLY_PROVEN"
EV_COMMENT_ONLY = "COMMENT_ONLY"
EV_UNTESTED = "UNTESTED"
EV_UNKNOWN = "UNKNOWN"
EVIDENCE_STATUSES = (
    EV_DIRECTLY_TESTED_STRONG, EV_DIRECTLY_TESTED_WEAK, EV_INDIRECTLY_TESTED,
    EV_HAPPY_PATH_ONLY, EV_FUZZED_BUT_NOT_TARGETED, EV_FORMALLY_PROVEN,
    EV_COMMENT_ONLY, EV_UNTESTED, EV_UNKNOWN,
)
# Statuses that count as strong safety evidence for an invariant.
EVIDENCE_STRONG_STATUSES = (EV_DIRECTLY_TESTED_STRONG, EV_FORMALLY_PROVEN)

# --- Evidence grades (exactly five; section 4 of the spec) ----------------
GRADE_A = "A"  # strong local proof of material economic violation
GRADE_B = "B"  # likely issue, needs one more test or line confirmation
GRADE_C = "C"  # interesting but impact unclear
GRADE_D = "D"  # rejected by local test
GRADE_F = "F"  # invalid setup or out of scope
GRADES = (GRADE_A, GRADE_B, GRADE_C, GRADE_D, GRADE_F)

# --- Evidence-judge decisions (exactly six; section 14 of the spec) -------
JUDGE_VALIDATED_CANDIDATE = "VALIDATED_CANDIDATE"
JUDGE_NEEDS_HUMAN_REVIEW = "NEEDS_HUMAN_REVIEW"
JUDGE_REJECTED_WITH_TEST = "REJECTED_WITH_TEST"
JUDGE_INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
JUDGE_OUT_OF_SCOPE = "OUT_OF_SCOPE"
JUDGE_DUPLICATE_RISK_HIGH = "DUPLICATE_RISK_HIGH"
JUDGE_DECISIONS = (
    JUDGE_VALIDATED_CANDIDATE, JUDGE_NEEDS_HUMAN_REVIEW, JUDGE_REJECTED_WITH_TEST,
    JUDGE_INSUFFICIENT_EVIDENCE, JUDGE_OUT_OF_SCOPE, JUDGE_DUPLICATE_RISK_HIGH,
)

# --- Report-filter outcomes (exactly six; section 15 of the spec) ---------
REPORT_READY_FOR_HUMAN_REVIEW = "READY_FOR_HUMAN_REVIEW"
REPORT_NEEDS_MORE_EVIDENCE = "NEEDS_MORE_EVIDENCE"
REPORT_DO_NOT_SUBMIT_DUPLICATE_RISK = "DO_NOT_SUBMIT_DUPLICATE_RISK"
REPORT_DO_NOT_SUBMIT_OUT_OF_SCOPE = "DO_NOT_SUBMIT_OUT_OF_SCOPE"
REPORT_DO_NOT_SUBMIT_WEAK_IMPACT = "DO_NOT_SUBMIT_WEAK_IMPACT"
REPORT_DO_NOT_SUBMIT_INVALID_SETUP = "DO_NOT_SUBMIT_INVALID_SETUP"
REPORT_OUTCOMES = (
    REPORT_READY_FOR_HUMAN_REVIEW, REPORT_NEEDS_MORE_EVIDENCE,
    REPORT_DO_NOT_SUBMIT_DUPLICATE_RISK, REPORT_DO_NOT_SUBMIT_OUT_OF_SCOPE,
    REPORT_DO_NOT_SUBMIT_WEAK_IMPACT, REPORT_DO_NOT_SUBMIT_INVALID_SETUP,
)


def _dc(obj) -> dict:
    return asdict(obj)


# --------------------------------------------------------------------------
# Lens metadata
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class ProtocolLensMeta:
    """Static identity and capability metadata for a protocol lens."""

    lens_id: str
    display_name: str
    protocol_family: str
    families: tuple[str, ...] = ()          # the economic-system facets the lens models
    supported_languages: tuple[str, ...] = ("solidity",)
    supported_frameworks: tuple[str, ...] = ("foundry",)
    known_surfaces: tuple[str, ...] = ()    # generic surface classes the lens expects
    boundary_notice: str = ""

    def to_dict(self) -> dict:
        return {
            "lens_id": self.lens_id,
            "display_name": self.display_name,
            "protocol_family": self.protocol_family,
            "families": list(self.families),
            "supported_languages": list(self.supported_languages),
            "supported_frameworks": list(self.supported_frameworks),
            "known_surfaces": list(self.known_surfaces),
            "boundary_notice": self.boundary_notice,
        }


# --------------------------------------------------------------------------
# Extraction hints (how a lens finds itself in a local repo)
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class ExtractionGroup:
    """A named group of protocol terms/symbols the extractor searches for."""

    group_id: str
    title: str
    terms: tuple[str, ...]

    def to_dict(self) -> dict:
        return {"group_id": self.group_id, "title": self.title, "terms": list(self.terms)}


# --------------------------------------------------------------------------
# Behavior promises (section 8)
# --------------------------------------------------------------------------
@dataclass
class BehaviorPromise:
    id: str
    text: str
    source_basis: str = ""
    relevant_files: list[str] = field(default_factory=list)
    relevant_functions: list[str] = field(default_factory=list)
    state_variables: list[str] = field(default_factory=list)
    violation_condition: str = ""
    possible_impact: str = ""
    existing_evidence: list[str] = field(default_factory=list)
    missing_evidence: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return _dc(self)


# --------------------------------------------------------------------------
# Economic invariants (section 9)
# --------------------------------------------------------------------------
@dataclass
class EconomicInvariant:
    id: str
    statement: str
    relevant_files: list[str] = field(default_factory=list)
    relevant_functions: list[str] = field(default_factory=list)
    state_variables: list[str] = field(default_factory=list)
    mathematical_form: str = ""
    existing_direct_tests: list[str] = field(default_factory=list)
    existing_indirect_tests: list[str] = field(default_factory=list)
    missing_tests: list[str] = field(default_factory=list)
    impact_if_broken: str = ""

    def to_dict(self) -> dict:
        return _dc(self)


# --------------------------------------------------------------------------
# Temporal windows
# --------------------------------------------------------------------------
@dataclass
class TemporalWindow:
    id: str
    name: str
    window_description: str
    observable_state: str = ""
    risk: str = ""
    relevant_functions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return _dc(self)


# --------------------------------------------------------------------------
# Periphery function model (section 4)
# --------------------------------------------------------------------------
@dataclass
class PeripheryFunctionModel:
    name: str
    target_kind: str = UNKNOWN_IN_LOCAL_REPO     # "assets" | "units" | unknown
    side: str = UNKNOWN_IN_LOCAL_REPO            # "buy" | "sell" | "repay" | ...
    gross_net: str = UNKNOWN_IN_LOCAL_REPO       # "gross" | "net" | unknown
    caps: list[str] = field(default_factory=list)
    source: str = ""
    notes: str = ""

    def to_dict(self) -> dict:
        return _dc(self)


# --------------------------------------------------------------------------
# Value-flow path
# --------------------------------------------------------------------------
@dataclass
class ValueFlowPath:
    id: str
    name: str
    entry: str = ""
    movement: str = ""
    exit: str = ""
    signals: list[str] = field(default_factory=list)
    source_targets: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return _dc(self)


# --------------------------------------------------------------------------
# Protocol model (the structured extraction result)
# --------------------------------------------------------------------------
@dataclass
class ProtocolModel:
    lens_id: str
    families: list[str] = field(default_factory=list)
    groups: list[dict] = field(default_factory=list)        # per ExtractionGroup: matches + unknowns
    discovered_terms: list[str] = field(default_factory=list)
    unknown_terms: list[str] = field(default_factory=list)
    periphery_functions: list[dict] = field(default_factory=list)
    value_flow_paths: list[dict] = field(default_factory=list)
    source_files: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return _dc(self)


# --------------------------------------------------------------------------
# Review lane definition (declarative; section 10)
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class LensLaneDef:
    lane_id: str
    title: str
    slug: str
    default_priority: str
    focus_keywords: tuple[str, ...]
    why_this_lane_matters: str
    invariants_at_risk: tuple[str, ...]        # INV-MM-* ids
    promises_at_risk: tuple[str, ...]          # PROMISE-MM-* ids
    first_hypotheses: tuple[str, ...]
    required_evidence: tuple[str, ...]
    stop_condition: str

    def to_dict(self) -> dict:
        return {
            "lane_id": self.lane_id,
            "title": self.title,
            "slug": self.slug,
            "default_priority": self.default_priority,
            "focus_keywords": list(self.focus_keywords),
            "why_this_lane_matters": self.why_this_lane_matters,
            "invariants_at_risk": list(self.invariants_at_risk),
            "promises_at_risk": list(self.promises_at_risk),
            "first_hypotheses": list(self.first_hypotheses),
            "required_evidence": list(self.required_evidence),
            "stop_condition": self.stop_condition,
        }


# --------------------------------------------------------------------------
# Concrete review lane (built; section 4 ReviewLane fields)
# --------------------------------------------------------------------------
@dataclass
class ReviewLane:
    id: str
    title: str
    priority: str
    scope_basis: str = ""
    source_files: list[str] = field(default_factory=list)
    functions: list[str] = field(default_factory=list)
    state_variables: list[str] = field(default_factory=list)
    invariants_at_risk: list[str] = field(default_factory=list)
    promises_at_risk: list[str] = field(default_factory=list)
    why_this_lane_matters: str = ""
    first_hypotheses: list[str] = field(default_factory=list)
    required_evidence: list[str] = field(default_factory=list)
    stop_condition: str = ""
    not_severity: str = "Lane priority is review order, not severity."
    human_review_required: bool = True

    def to_dict(self) -> dict:
        return _dc(self)


# --------------------------------------------------------------------------
# Scope task (section 4 + section 11)
# --------------------------------------------------------------------------
@dataclass
class ScopeTask:
    id: str
    lane_id: str
    hypothesis: str
    invariant_at_risk: str = ""
    files: list[str] = field(default_factory=list)
    functions: list[str] = field(default_factory=list)
    setup_needed: str = ""
    exploit_attempt_description: str = ""
    expected_safe_behavior: str = ""
    failure_condition: str = ""
    suggested_test_file: str = ""
    suggested_test_name: str = ""
    duplicate_risk: str = ""
    decision_rule: str = ""
    kill_condition: str = ""
    human_review_required: bool = True

    def to_dict(self) -> dict:
        return _dc(self)


# --------------------------------------------------------------------------
# Evidence item (section 12)
# --------------------------------------------------------------------------
@dataclass
class EvidenceItem:
    invariant_id: str
    status: str = EV_UNKNOWN
    test_name: str = ""
    source: str = ""
    rationale: str = ""

    def to_dict(self) -> dict:
        return _dc(self)


# --------------------------------------------------------------------------
# Blind-spot candidate (section 13)
# --------------------------------------------------------------------------
@dataclass
class BlindSpotCandidate:
    title: str
    why_blind_spot: str = ""
    source_files: list[str] = field(default_factory=list)
    functions: list[str] = field(default_factory=list)
    state_variables: list[str] = field(default_factory=list)
    invariant_at_risk: str = ""
    existing_evidence: str = ""
    why_evidence_insufficient: str = ""
    impact_if_broken: str = ""
    duplicate_risk: str = ""
    poc_objective: str = ""
    suggested_test_file: str = ""
    suggested_test_name: str = ""
    expected_failure_condition: str = ""
    scores: dict = field(default_factory=dict)
    blind_spot_score: int = 0

    def to_dict(self) -> dict:
        return _dc(self)


# --------------------------------------------------------------------------
# Evidence grade (section 4)
# --------------------------------------------------------------------------
@dataclass
class EvidenceGrade:
    test_name: str
    invariant_tested: str = ""
    does_compile: str = EV_UNKNOWN
    does_run: str = EV_UNKNOWN
    realistic_actors: str = EV_UNKNOWN
    scoped_contracts: str = EV_UNKNOWN
    no_trusted_role_assumption: str = EV_UNKNOWN
    no_weird_token_assumption: str = EV_UNKNOWN
    proves_value_movement: str = EV_UNKNOWN
    quantifies_impact: str = EV_UNKNOWN
    addresses_duplicate_risk: str = EV_UNKNOWN
    grade: str = GRADE_F
    decision: str = JUDGE_INSUFFICIENT_EVIDENCE
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return _dc(self)


# --------------------------------------------------------------------------
# Report-filter decision (section 15)
# --------------------------------------------------------------------------
@dataclass
class ReportFilterDecision:
    candidate_id: str
    title: str = ""
    checklist: dict = field(default_factory=dict)
    outcome: str = REPORT_NEEDS_MORE_EVIDENCE
    reasons: list[str] = field(default_factory=list)
    human_review_required: bool = True

    def to_dict(self) -> dict:
        return _dc(self)

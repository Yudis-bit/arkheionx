"""Data models for the private Senior Researcher Triage mode (`arkheionx triage`).

Senior triage runs *before* `arkheionx review`. It does not confirm
vulnerabilities, it does not assign severity, it does not submit reports, and it
does not make RPC or live-chain calls by default. It only decides what is worth
reviewing and what should be killed early, so a human does not burn time proving
what should never be pursued.

Everything here is a local/static planning model. A lead is a research direction,
not a finding. A score is a research-priority ordering, not a severity. Human
review is always required.
"""
from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field

SCHEMA_VERSION = "senior-triage-v1"
ARTIFACT_TYPE = "senior_triage"
COMMAND = "triage"

# --- Target-level decision vocabulary ------------------------------------------------
TARGET_TOUCH = "TOUCH"
TARGET_SKIP = "SKIP"
TARGET_NEEDS_CONTEXT = "NEEDS_MORE_CONTEXT"
TARGET_DECISIONS = (TARGET_TOUCH, TARGET_SKIP, TARGET_NEEDS_CONTEXT)

# --- Lead-level decision vocabulary --------------------------------------------------
LEAD_PURSUE = "PURSUE"
LEAD_PARK = "PARK"
LEAD_KILL = "KILL"
LEAD_DECISIONS = (LEAD_PURSUE, LEAD_PARK, LEAD_KILL)

# --- Known-issue / dedup status vocabulary -------------------------------------------
KNOWN_UNKNOWN = "UNKNOWN"
KNOWN_NO_MATCH = "NO_MATCH_FOUND"
KNOWN_SIMILAR = "SIMILAR_KNOWN"
KNOWN_LIKELY_DUP = "LIKELY_DUPLICATE"
KNOWN_DOCUMENTED = "DOCUMENTED_BEHAVIOR"
KNOWN_ACK_RISK = "ACKNOWLEDGED_RISK"
KNOWN_OUT_OF_SCOPE = "OUT_OF_SCOPE"
KNOWN_TRUSTED_ROLE = "TRUSTED_ROLE_ONLY"
KNOWN_PUBLIC_TEST = "PUBLIC_TEST_COVERED"
KNOWN_STATUSES = (
    KNOWN_UNKNOWN, KNOWN_NO_MATCH, KNOWN_SIMILAR, KNOWN_LIKELY_DUP, KNOWN_DOCUMENTED,
    KNOWN_ACK_RISK, KNOWN_OUT_OF_SCOPE, KNOWN_TRUSTED_ROLE, KNOWN_PUBLIC_TEST,
)
# Dedup statuses that block a PURSUE decision outright.
KNOWN_BLOCKING = (
    KNOWN_LIKELY_DUP, KNOWN_DOCUMENTED, KNOWN_ACK_RISK, KNOWN_OUT_OF_SCOPE,
    KNOWN_TRUSTED_ROLE, KNOWN_PUBLIC_TEST,
)

# --- Freshness status vocabulary -----------------------------------------------------
FRESH = "FRESH"
STALE = "STALE"
UNKNOWN_FRESHNESS = "UNKNOWN_FRESHNESS"
POST_AUDIT_CHANGE = "POST_AUDIT_CHANGE"
LIVE_MISMATCH = "LIVE_MISMATCH"
NEW_ADAPTER = "NEW_ADAPTER"
NEW_REGISTRY_ENTRY = "NEW_REGISTRY_ENTRY"
NEW_IMPLEMENTATION = "NEW_IMPLEMENTATION"
NEW_MIGRATION_PATH = "NEW_MIGRATION_PATH"
FRESHNESS_STATUSES = (
    FRESH, STALE, UNKNOWN_FRESHNESS, POST_AUDIT_CHANGE, LIVE_MISMATCH,
    NEW_ADAPTER, NEW_REGISTRY_ENTRY, NEW_IMPLEMENTATION, NEW_MIGRATION_PATH,
)
# Freshness statuses that meaningfully lift research priority.
FRESHNESS_PRIORITY = (
    POST_AUDIT_CHANGE, NEW_ADAPTER, NEW_IMPLEMENTATION, LIVE_MISMATCH,
    NEW_REGISTRY_ENTRY, NEW_MIGRATION_PATH,
)

# --- Deployment-reality status vocabulary --------------------------------------------
DEPLOY_NOT_RUN = "NOT_RUN"
DEPLOY_LOCAL_ONLY = "LOCAL_ONLY"
DEPLOY_ADDRESSES_PROVIDED = "ADDRESSES_PROVIDED"
DEPLOY_RPC_READ_ONLY_CHECKED = "RPC_READ_ONLY_CHECKED"
DEPLOY_NOT_IMPLEMENTED = "DEPLOYMENT_REALITY_NOT_IMPLEMENTED"
DEPLOY_LIVE_SOURCE_MATCH = "LIVE_SOURCE_MATCH"
DEPLOY_LIVE_SOURCE_MISMATCH = "LIVE_SOURCE_MISMATCH"
DEPLOY_IMPLEMENTATION_CHANGED = "IMPLEMENTATION_CHANGED"
DEPLOY_REGISTRY_CHANGED = "REGISTRY_CHANGED"
DEPLOY_ORACLE_CHANGED = "ORACLE_CHANGED"
DEPLOY_ROLE_CHANGED = "ROLE_CHANGED"
DEPLOY_PAUSED_OR_DISABLED = "PAUSED_OR_DISABLED"

# --- Submit-readiness vocabulary -----------------------------------------------------
NOT_READY = "NOT_READY"
NEEDS_LOCAL_PROOF = "NEEDS_LOCAL_PROOF"
NEEDS_DEDUP = "NEEDS_DEDUP"
NEEDS_SCOPE_CONFIRMATION = "NEEDS_SCOPE_CONFIRMATION"
READY_FOR_REVIEW = "READY_FOR_REVIEW"
DO_NOT_SUBMIT = "DO_NOT_SUBMIT"

# Scope-confidence buckets.
CONF_LOW = "LOW"
CONF_MEDIUM = "MEDIUM"
CONF_HIGH = "HIGH"

# Severity ceiling buckets (a planning ceiling, never a severity claim).
SEV_UNKNOWN = "UNKNOWN"
SEV_LOW = "LOW"
SEV_MEDIUM = "MEDIUM"
SEV_HIGH = "HIGH"
SEV_CRITICAL = "CRITICAL"

# Outcome wording that senior triage must never emit into an artifact. These are
# checked by the artifact guard in pack.py and by tests/test_senior_triage_safety.py.
# They are listed here only so the guard can reject them; they are never rendered.
FORBIDDEN_OUTCOME_TERMS = (
    "VALID_BUG",
    "CONFIRMED_VULNERABILITY",
    "SUBMIT_NOW",
    "GUARANTEED_HIGH",
    "GUARANTEED_CRITICAL",
    "EXPLOIT_READY",
)

# Status markers used when an input is absent (never fail just because a folder is
# missing — mark the section instead).
INSUFFICIENT_CONTEXT = "INSUFFICIENT_CONTEXT"
NOT_PROVIDED = "NOT_PROVIDED"
NOT_RUN = "NOT_RUN"

# Cap: senior output shows at most this many top leads.
TOP_LEAD_LIMIT = 3
# Cap: never generate a giant graveyard of raw leads.
RAW_LEAD_LIMIT = 12


def _to_dict(obj) -> dict:
    """dataclass -> plain JSON-ready dict."""
    return dataclasses.asdict(obj)


@dataclass
class TriageContext:
    """Resolved run inputs for a single triage invocation."""

    repo_path: str
    command: str = ""
    scope_file: str = ""
    known_path: str = ""
    audits_path: str = ""
    addresses_file: str = ""
    baseline_ref: str = ""
    since_date: str = ""
    # rpc_mode is "not_provided" by default; never "enabled" — senior triage makes
    # no live-chain calls in this pass.
    rpc_mode: str = "not_provided"
    rpc_endpoint_masked: str = ""
    out_dir: str = ""

    def to_dict(self) -> dict:
        return _to_dict(self)


@dataclass
class EligibilitySignal:
    """Bounty/scope eligibility read from local scope + program rules only."""

    scope_provided: bool = False
    scope_confidence: str = CONF_LOW
    target_decision: str = TARGET_NEEDS_CONTEXT
    severity_ceiling: str = SEV_UNKNOWN
    initial_duplicate_risk: str = CONF_LOW
    requires_poc: bool = False
    kyc_noted: bool = False
    reward_notes: list[str] = field(default_factory=list)
    oos_traps: list[str] = field(default_factory=list)
    trusted_role_traps: list[str] = field(default_factory=list)
    excluded_impacts: list[str] = field(default_factory=list)
    missing_context: list[str] = field(default_factory=list)
    recommended_action: str = ""
    reason: str = ""

    def to_dict(self) -> dict:
        return _to_dict(self)


@dataclass
class KnownIssueSignal:
    """Dedup verdict for a single lead against known issues / audits / tests."""

    lead_id: str = ""
    status: str = KNOWN_UNKNOWN
    duplicate_risk_score: int = 0  # 0-100 (higher = more likely already known)
    public_test_covered: bool = False
    matched_terms: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)
    note: str = ""

    def to_dict(self) -> dict:
        return _to_dict(self)


@dataclass
class FreshnessSignal:
    """Freshness verdict for a single lead (what changed since the last review point)."""

    lead_id: str = ""
    status: str = UNKNOWN_FRESHNESS
    score: int = 40  # 0-100
    baseline: str = "none"
    signals: list[str] = field(default_factory=list)
    changed_paths: list[str] = field(default_factory=list)
    note: str = ""

    def to_dict(self) -> dict:
        return _to_dict(self)


@dataclass
class DeploymentRealitySignal:
    """Optional deployment-reality plan. Local-first; never makes live-chain calls here."""

    status: str = DEPLOY_NOT_RUN
    rpc_mode: str = "not_provided"
    addresses_provided: bool = False
    addresses: list[dict] = field(default_factory=list)
    recommended_checks: list[str] = field(default_factory=list)
    safe_commands: list[str] = field(default_factory=list)
    rpc_endpoint_masked: str = ""
    reason: str = ""
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return _to_dict(self)


@dataclass
class LeadScore:
    """Explainable research-priority score breakdown for a lead (0-100)."""

    total: int = 0
    components: dict = field(default_factory=dict)
    caps_applied: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return _to_dict(self)


@dataclass
class LeadCandidate:
    """A single research lead. Every lead must carry a kill condition."""

    id: str
    title: str
    surface: str = ""
    reason: str = ""
    linked_files: list[str] = field(default_factory=list)
    linked_functions: list[str] = field(default_factory=list)
    # Component sub-scores (0-100 each) used by scoring.
    scope_confidence: int = 0
    freshness_score: int = 40
    attacker_reachability_score: int = 0
    materiality_score: int = 0
    duplicate_risk_score: int = 0
    trusted_role_risk_score: int = 0
    proof_difficulty_score: int = 50
    time_cost_score: int = 50
    # Verdicts.
    research_priority_score: int = 0
    decision: str = LEAD_PARK
    dedup_status: str = KNOWN_UNKNOWN
    freshness_status: str = UNKNOWN_FRESHNESS
    submit_readiness: str = NOT_READY
    expected_severity_ceiling: str = SEV_UNKNOWN
    kill_condition: str = ""
    next_command: str = ""
    score_reasons: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return _to_dict(self)


@dataclass
class TargetDecision:
    """Top-level verdict: should this target be touched at all?"""

    decision: str = TARGET_NEEDS_CONTEXT
    confidence: str = CONF_LOW
    reason: str = ""

    def to_dict(self) -> dict:
        return _to_dict(self)


@dataclass
class SeniorTriagePack:
    """Aggregate result of one triage run."""

    context: TriageContext
    generated_at: str
    arkheionx_version: str
    target_decision: TargetDecision
    eligibility: EligibilitySignal
    deployment_reality: DeploymentRealitySignal
    leads: list[LeadCandidate] = field(default_factory=list)
    known_issue_map: list[KnownIssueSignal] = field(default_factory=list)
    freshness_diff: list[FreshnessSignal] = field(default_factory=list)
    do_not_touch: list[dict] = field(default_factory=list)
    missing_context: list[str] = field(default_factory=list)
    counts: dict = field(default_factory=dict)

    def top_leads(self) -> list[LeadCandidate]:
        pursue = [lead for lead in self.leads if lead.decision == LEAD_PURSUE]
        park = [lead for lead in self.leads if lead.decision == LEAD_PARK]
        ordered = pursue + park
        return ordered[:TOP_LEAD_LIMIT]

    def to_dict(self) -> dict:
        return _to_dict(self)

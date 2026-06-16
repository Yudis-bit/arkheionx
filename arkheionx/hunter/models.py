"""Data models and vocabulary for Arkheionx V9 Universal Senior Exploit Hunter Mode.

Hunter mode (`arkheionx hunter`) is a local-first senior research *decision* engine.
It helps a human researcher answer one question before manual review:

    Where should I spend the next 30-90 minutes to maximize the chance of a fresh,
    in-scope, payable, non-duplicate, attacker-reachable bug?

Everything here is a planning model. A lead is a research direction, not a finding.
A score is a research-priority ordering, not a severity. A decision is a
time-allocation call, not a vulnerability claim. Hunter mode never confirms a bug,
never assigns a final severity, never submits a report, and makes no live-chain
mutation. Read-only RPC is opt-in only and the endpoint is always masked. Human
review is always required.

This module is generic on purpose: no company, protocol, chain, repo, or bounty
name is hardcoded. Targets are inferred from input files.
"""
from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field

SCHEMA_VERSION = "v9-universal-hunter"
ARTIFACT_TYPE = "hunter_triage"
MANIFEST_TYPE = "hunter_manifest"
COMMAND = "hunter"

# ---------------------------------------------------------------------------
# Generic input/context status markers (never fail just because input is absent).
# ---------------------------------------------------------------------------
NOT_PROVIDED = "NOT_PROVIDED"
NOT_RUN = "NOT_RUN"
INSUFFICIENT_CONTEXT = "INSUFFICIENT_CONTEXT"

# ---------------------------------------------------------------------------
# Address parser v2 statuses.
# ---------------------------------------------------------------------------
ADDRESS_OK = "ADDRESS_OK"
ADDRESS_PARSE_ERROR = "ADDRESS_PARSE_ERROR"
ADDRESS_FILE_EMPTY = "ADDRESS_FILE_EMPTY"
ADDRESS_FILE_MISSING = "ADDRESS_FILE_MISSING"
ADDRESS_NONE_PROVIDED = "ADDRESS_NONE_PROVIDED"
ADDRESS_EMPTY_CONTRACTS = "ADDRESS_EMPTY_CONTRACTS"  # explicit empty contracts array (valid)

# ---------------------------------------------------------------------------
# Scope collision warnings.
# ---------------------------------------------------------------------------
SCOPE_COLLISION_WARNING = "SCOPE_COLLISION_WARNING"
VERSION_COLLISION_WARNING = "VERSION_COLLISION_WARNING"
PRODUCT_COLLISION_WARNING = "PRODUCT_COLLISION_WARNING"
ADDRESS_SCOPE_MISMATCH = "ADDRESS_SCOPE_MISMATCH"
REPO_SCOPE_MISMATCH = "REPO_SCOPE_MISMATCH"
KNOWN_CORPUS_SCOPE_MISMATCH = "KNOWN_CORPUS_SCOPE_MISMATCH"
CHAIN_SCOPE_MISMATCH = "CHAIN_SCOPE_MISMATCH"
SCOPE_COLLISIONS = (
    SCOPE_COLLISION_WARNING, VERSION_COLLISION_WARNING, PRODUCT_COLLISION_WARNING,
    ADDRESS_SCOPE_MISMATCH, REPO_SCOPE_MISMATCH, KNOWN_CORPUS_SCOPE_MISMATCH,
    CHAIN_SCOPE_MISMATCH,
)

# Overall scope status.
SCOPE_OK = "SCOPE_OK"
SCOPE_PARTIAL = "SCOPE_PARTIAL"
SCOPE_MISSING = "SCOPE_MISSING"
SCOPE_COLLISION = "SCOPE_COLLISION"

# ---------------------------------------------------------------------------
# Source recovery statuses.
# ---------------------------------------------------------------------------
SOURCE_LOCAL = "SOURCE_LOCAL"
SOURCE_ARTIFACT = "SOURCE_ARTIFACT"
SOURCE_PROVIDED = "SOURCE_PROVIDED"
SOURCE_SOURCIFY_EXACT = "SOURCE_SOURCIFY_EXACT"
SOURCE_SOURCIFY_PARTIAL = "SOURCE_SOURCIFY_PARTIAL"
SOURCE_ETHERSCAN_VERIFIED = "SOURCE_ETHERSCAN_VERIFIED"
SOURCE_ABI_ONLY = "SOURCE_ABI_ONLY"
SOURCE_MISSING = "SOURCE_MISSING"
SOURCE_RECOVERY_FAILED = "SOURCE_RECOVERY_FAILED"
SOURCE_STATUSES = (
    SOURCE_LOCAL, SOURCE_ARTIFACT, SOURCE_PROVIDED, SOURCE_SOURCIFY_EXACT,
    SOURCE_SOURCIFY_PARTIAL, SOURCE_ETHERSCAN_VERIFIED, SOURCE_ABI_ONLY,
    SOURCE_MISSING, SOURCE_RECOVERY_FAILED,
)
# Source statuses that authoritatively back source-level analysis.
SOURCE_AUTHORITATIVE = (
    SOURCE_LOCAL, SOURCE_ARTIFACT, SOURCE_PROVIDED, SOURCE_SOURCIFY_EXACT,
    SOURCE_ETHERSCAN_VERIFIED,
)
# Source statuses that mean source-level leads must be capped.
SOURCE_INADEQUATE = (SOURCE_ABI_ONLY, SOURCE_MISSING, SOURCE_RECOVERY_FAILED)

# ---------------------------------------------------------------------------
# Dedup corpus-quality statuses.
# ---------------------------------------------------------------------------
DEDUP_BLIND = "DEDUP_BLIND"
DEDUP_PARTIAL = "DEDUP_PARTIAL"
DEDUP_USABLE = "DEDUP_USABLE"
DEDUP_STRONG = "DEDUP_STRONG"
DEDUP_QUALITY = (DEDUP_BLIND, DEDUP_PARTIAL, DEDUP_USABLE, DEDUP_STRONG)

# Known-match statuses (per lead).
NO_MATCH_FOUND = "NO_MATCH_FOUND"
SIMILAR_KNOWN = "SIMILAR_KNOWN"
LIKELY_DUPLICATE = "LIKELY_DUPLICATE"
DOCUMENTED_BEHAVIOR = "DOCUMENTED_BEHAVIOR"
ACKNOWLEDGED_RISK = "ACKNOWLEDGED_RISK"
OUT_OF_SCOPE = "OUT_OF_SCOPE"
TRUSTED_ROLE_ONLY = "TRUSTED_ROLE_ONLY"
PUBLIC_TEST_COVERED = "PUBLIC_TEST_COVERED"
KNOWN_UNKNOWN = "UNKNOWN"
KNOWN_MATCH_STATUSES = (
    NO_MATCH_FOUND, SIMILAR_KNOWN, LIKELY_DUPLICATE, DOCUMENTED_BEHAVIOR,
    ACKNOWLEDGED_RISK, OUT_OF_SCOPE, TRUSTED_ROLE_ONLY, PUBLIC_TEST_COVERED,
    KNOWN_UNKNOWN,
)
UNPARSED_PDF = "UNPARSED_PDF_TEXT_EXTRACTION_UNAVAILABLE"

# ---------------------------------------------------------------------------
# Freshness statuses (V9). A positive freshness status requires evidence.
# ---------------------------------------------------------------------------
FRESHNESS_UNKNOWN = "FRESHNESS_UNKNOWN"
BASELINE_UNKNOWN = "BASELINE_UNKNOWN"
AUDIT_COVERED = "AUDIT_COVERED"
POST_AUDIT_CHANGE = "POST_AUDIT_CHANGE"
NEW_DEPLOYED_IMPLEMENTATION = "NEW_DEPLOYED_IMPLEMENTATION"
IMPLEMENTATION_CHANGED = "IMPLEMENTATION_CHANGED"
NEW_LIVE_REGISTRY_ENTRY = "NEW_LIVE_REGISTRY_ENTRY"
NEW_VALUE_OUT_SURFACE = "NEW_VALUE_OUT_SURFACE"
NEW_STATE_MACHINE_VALUE_FLOW = "NEW_STATE_MACHINE_VALUE_FLOW"
SOURCE_RECOVERED_NO_BASELINE = "SOURCE_RECOVERED_NO_BASELINE"
FRESHNESS_STATUSES = (
    FRESHNESS_UNKNOWN, BASELINE_UNKNOWN, AUDIT_COVERED, POST_AUDIT_CHANGE,
    NEW_DEPLOYED_IMPLEMENTATION, IMPLEMENTATION_CHANGED, NEW_LIVE_REGISTRY_ENTRY,
    NEW_VALUE_OUT_SURFACE, NEW_STATE_MACHINE_VALUE_FLOW, SOURCE_RECOVERED_NO_BASELINE,
)
# Statuses that genuinely lift research priority (evidence-backed only).
FRESHNESS_POSITIVE = (
    POST_AUDIT_CHANGE, NEW_DEPLOYED_IMPLEMENTATION, IMPLEMENTATION_CHANGED,
    NEW_LIVE_REGISTRY_ENTRY, NEW_VALUE_OUT_SURFACE, NEW_STATE_MACHINE_VALUE_FLOW,
)
# Statuses that mean "no baseline" and force a PARK_BASELINE cap by themselves.
FRESHNESS_NO_BASELINE = (FRESHNESS_UNKNOWN, BASELINE_UNKNOWN)

# ---------------------------------------------------------------------------
# Deployment reality statuses.
# ---------------------------------------------------------------------------
RPC_NOT_PROVIDED = "RPC_NOT_PROVIDED"
READ_ONLY_RPC_ENABLED = "READ_ONLY_RPC_ENABLED"
ADDRESS_NO_CODE = "ADDRESS_NO_CODE"
DIRECT_CONTRACT = "DIRECT_CONTRACT"
EIP1967_PROXY = "EIP1967_PROXY"
BEACON_PROXY = "BEACON_PROXY"
UNKNOWN_PROXY_PATTERN = "UNKNOWN_PROXY_PATTERN"
IMPLEMENTATION_MATCH = "IMPLEMENTATION_MATCH"
DEPLOY_IMPLEMENTATION_CHANGED = "IMPLEMENTATION_CHANGED"
ADMIN_MATCH = "ADMIN_MATCH"
ADMIN_CHANGED = "ADMIN_CHANGED"
BEACON_MATCH = "BEACON_MATCH"
BEACON_CHANGED = "BEACON_CHANGED"
LIVE_SOURCE_MATCH = "LIVE_SOURCE_MATCH"
LIVE_SOURCE_MISMATCH = "LIVE_SOURCE_MISMATCH"
LIVE_SOURCE_UNKNOWN = "LIVE_SOURCE_UNKNOWN"
ROLE_WIRING_MATCH = "ROLE_WIRING_MATCH"
ROLE_WIRING_MISMATCH = "ROLE_WIRING_MISMATCH"
DEPLOYMENT_CONTEXT_INCOMPLETE = "DEPLOYMENT_CONTEXT_INCOMPLETE"
RPC_CHECK_FAILED = "RPC_CHECK_FAILED"
# Deployment statuses that are a hard priority boost (live differs from expected).
DEPLOYMENT_MISMATCH_STATUSES = (
    DEPLOY_IMPLEMENTATION_CHANGED, LIVE_SOURCE_MISMATCH, ADMIN_CHANGED, BEACON_CHANGED,
)

# ---------------------------------------------------------------------------
# Live registry / live-set diff statuses.
# ---------------------------------------------------------------------------
LIVE_AND_LISTED = "LIVE_AND_LISTED"
LIVE_NOT_LISTED = "LIVE_NOT_LISTED"
LISTED_NOT_LIVE = "LISTED_NOT_LIVE"
REGISTRY_DIFF_UNKNOWN = "REGISTRY_DIFF_UNKNOWN"
REGISTRY_CALL_FAILED = "REGISTRY_CALL_FAILED"
REGISTRY_NOT_RUN = "REGISTRY_NOT_RUN"

# ---------------------------------------------------------------------------
# Call-graph edge statuses (only real edges become graph edges).
# ---------------------------------------------------------------------------
DIRECT_CALL = "DIRECT_CALL"
INTERFACE_CALL = "INTERFACE_CALL"
LOW_LEVEL_CALL = "LOW_LEVEL_CALL"
DELEGATECALL = "DELEGATECALL"
STATICCALL = "STATICCALL"
POSSIBLE_REFERENCE = "POSSIBLE_REFERENCE"
NO_CALL_EDGE = "NO_CALL_EDGE"
REAL_CALL_EDGES = (DIRECT_CALL, INTERFACE_CALL, LOW_LEVEL_CALL, DELEGATECALL, STATICCALL)

# ---------------------------------------------------------------------------
# Universal lead types.
# ---------------------------------------------------------------------------
VALUE_OUT_PATH = "VALUE_OUT_PATH"
STATE_MACHINE_VALUE_FLOW = "STATE_MACHINE_VALUE_FLOW"
DEPLOYMENT_MISMATCH = "DEPLOYMENT_MISMATCH"
LIVE_REGISTRY_DIFF = "LIVE_REGISTRY_DIFF"
SOURCE_RECOVERY_GAP = "SOURCE_RECOVERY_GAP"
SHARE_ACCOUNTING = "SHARE_ACCOUNTING"
ORACLE_RATE_ACCOUNTING = "ORACLE_RATE_ACCOUNTING"
FEE_DISPATCH = "FEE_DISPATCH"
REWARD_ACCOUNTING = "REWARD_ACCOUNTING"
WITHDRAWAL_QUEUE = "WITHDRAWAL_QUEUE"
CLAIM_QUEUE = "CLAIM_QUEUE"
VALIDATOR_KEY_ACCOUNTING = "VALIDATOR_KEY_ACCOUNTING"
BRIDGE_MESSAGE_ACCOUNTING = "BRIDGE_MESSAGE_ACCOUNTING"
CROSS_POOL_ISOLATION = "CROSS_POOL_ISOLATION"
CROSS_CHAIN_DOMAIN_SEPARATION = "CROSS_CHAIN_DOMAIN_SEPARATION"
INITIALIZATION_WIRING = "INITIALIZATION_WIRING"
REENTRANCY_ORDERING = "REENTRANCY_ORDERING"
MIGRATION_ACCOUNTING = "MIGRATION_ACCOUNTING"
LOCK_UNLOCK_ACCOUNTING = "LOCK_UNLOCK_ACCOUNTING"
ADAPTER_WITHDRAWABILITY = "ADAPTER_WITHDRAWABILITY"
EMERGENCY_EXIT_ACCOUNTING = "EMERGENCY_EXIT_ACCOUNTING"
GENERIC_VALUE_SURFACE = "GENERIC_VALUE_SURFACE"
LEAD_TYPES = (
    VALUE_OUT_PATH, STATE_MACHINE_VALUE_FLOW, DEPLOYMENT_MISMATCH, LIVE_REGISTRY_DIFF,
    SOURCE_RECOVERY_GAP, SHARE_ACCOUNTING, ORACLE_RATE_ACCOUNTING, FEE_DISPATCH,
    REWARD_ACCOUNTING, WITHDRAWAL_QUEUE, CLAIM_QUEUE, VALIDATOR_KEY_ACCOUNTING,
    BRIDGE_MESSAGE_ACCOUNTING, CROSS_POOL_ISOLATION, CROSS_CHAIN_DOMAIN_SEPARATION,
    INITIALIZATION_WIRING, REENTRANCY_ORDERING, MIGRATION_ACCOUNTING,
    LOCK_UNLOCK_ACCOUNTING, ADAPTER_WITHDRAWABILITY, EMERGENCY_EXIT_ACCOUNTING,
    GENERIC_VALUE_SURFACE,
)

# State-machine value-flow subtypes.
WITHDRAWAL_STATE = "WITHDRAWAL_STATE"
CLAIM_STATE = "CLAIM_STATE"
REWARD_STATE = "REWARD_STATE"
FEE_STATE = "FEE_STATE"
QUEUE_STATE = "QUEUE_STATE"
MIGRATION_STATE = "MIGRATION_STATE"
ORACLE_ROUND_STATE = "ORACLE_ROUND_STATE"
COVERAGE_STATE = "COVERAGE_STATE"
MATURITY_STATE = "MATURITY_STATE"
BRIDGE_MESSAGE_STATE = "BRIDGE_MESSAGE_STATE"
VALIDATOR_KEY_STATE = "VALIDATOR_KEY_STATE"
LOCK_UNLOCK_STATE = "LOCK_UNLOCK_STATE"
STATE_MACHINE_SUBTYPES = (
    WITHDRAWAL_STATE, CLAIM_STATE, REWARD_STATE, FEE_STATE, QUEUE_STATE,
    MIGRATION_STATE, ORACLE_ROUND_STATE, COVERAGE_STATE, MATURITY_STATE,
    BRIDGE_MESSAGE_STATE, VALIDATOR_KEY_STATE, LOCK_UNLOCK_STATE,
)

# ---------------------------------------------------------------------------
# Decision policy.
# ---------------------------------------------------------------------------
PURSUE_NOW = "PURSUE_NOW"
NEEDS_POC = "NEEDS_POC"
PARK_SCOPE = "PARK_SCOPE"
PARK_DEDUP = "PARK_DEDUP"
PARK_DEPLOYMENT = "PARK_DEPLOYMENT"
PARK_SOURCE = "PARK_SOURCE"
PARK_BASELINE = "PARK_BASELINE"
# V9.1: who-can-call is unresolved (custom modifier / auth helper). Conservative cap:
# never assume unprivileged; park until reachability is proven.
PARK_REACHABILITY = "PARK_REACHABILITY"
KILL_DUPLICATE = "KILL_DUPLICATE"
KILL_OOS = "KILL_OOS"
KILL_TRUSTED_ROLE = "KILL_TRUSTED_ROLE"
KILL_PUBLIC_TEST_COVERED = "KILL_PUBLIC_TEST_COVERED"
KILL_DOCUMENTED_BEHAVIOR = "KILL_DOCUMENTED_BEHAVIOR"
KILL_LOW_ONLY = "KILL_LOW_ONLY"
KILL_NO_MATERIAL_IMPACT = "KILL_NO_MATERIAL_IMPACT"
KILL_NOT_ATTACKER_REACHABLE = "KILL_NOT_ATTACKER_REACHABLE"
DECISIONS = (
    PURSUE_NOW, NEEDS_POC, PARK_SCOPE, PARK_DEDUP, PARK_DEPLOYMENT, PARK_SOURCE,
    PARK_BASELINE, PARK_REACHABILITY, KILL_DUPLICATE, KILL_OOS, KILL_TRUSTED_ROLE,
    KILL_PUBLIC_TEST_COVERED, KILL_DOCUMENTED_BEHAVIOR, KILL_LOW_ONLY,
    KILL_NO_MATERIAL_IMPACT, KILL_NOT_ATTACKER_REACHABLE,
)
PARK_DECISIONS = (PARK_SCOPE, PARK_DEDUP, PARK_DEPLOYMENT, PARK_SOURCE, PARK_BASELINE,
                  PARK_REACHABILITY)
KILL_DECISIONS = (
    KILL_DUPLICATE, KILL_OOS, KILL_TRUSTED_ROLE, KILL_PUBLIC_TEST_COVERED,
    KILL_DOCUMENTED_BEHAVIOR, KILL_LOW_ONLY, KILL_NO_MATERIAL_IMPACT,
    KILL_NOT_ATTACKER_REACHABLE,
)
PURSUEABLE = (PURSUE_NOW, NEEDS_POC)

# ---------------------------------------------------------------------------
# PoC planner statuses.
# ---------------------------------------------------------------------------
POC_READY = "POC_READY"
POC_NEEDS_SOURCE = "POC_NEEDS_SOURCE"
POC_NEEDS_DEPLOYMENT_STATE = "POC_NEEDS_DEPLOYMENT_STATE"
POC_NEEDS_BASELINE = "POC_NEEDS_BASELINE"
# V9.1: a pursued lead whose reachability is unresolved needs an explicit
# modifier-bypass / auth-helper-bug / role-gate-ineffective hypothesis first.
POC_NEEDS_REACHABILITY = "POC_NEEDS_REACHABILITY"
POC_BLOCKED_OOS = "POC_BLOCKED_OOS"
POC_BLOCKED_DUPLICATE = "POC_BLOCKED_DUPLICATE"
POC_BLOCKED_TRUSTED_ROLE = "POC_BLOCKED_TRUSTED_ROLE"
POC_BLOCKED_NO_MATERIAL_IMPACT = "POC_BLOCKED_NO_MATERIAL_IMPACT"
POC_STATUSES = (
    POC_READY, POC_NEEDS_SOURCE, POC_NEEDS_DEPLOYMENT_STATE, POC_NEEDS_BASELINE,
    POC_NEEDS_REACHABILITY, POC_BLOCKED_OOS, POC_BLOCKED_DUPLICATE,
    POC_BLOCKED_TRUSTED_ROLE, POC_BLOCKED_NO_MATERIAL_IMPACT,
)

# ---------------------------------------------------------------------------
# Submission risk statuses + severity ceiling.
# ---------------------------------------------------------------------------
PAYABLE_CANDIDATE = "PAYABLE_CANDIDATE"
RISK_NEEDS_POC = "NEEDS_POC"
RISK_PARK_SCOPE = "PARK_SCOPE"
RISK_PARK_DEDUP = "PARK_DEDUP"
RISK_PARK_DEPLOYMENT = "PARK_DEPLOYMENT"
RISK_PARK_SOURCE = "PARK_SOURCE"
RISK_PARK_REACHABILITY = "PARK_REACHABILITY"
RISK_KILL_DUPLICATE = "KILL_DUPLICATE"
RISK_KILL_OOS = "KILL_OOS"
RISK_KILL_TRUSTED_ROLE = "KILL_TRUSTED_ROLE"
RISK_KILL_LOW_ONLY = "KILL_LOW_ONLY"
RISK_KILL_NO_MATERIAL_IMPACT = "KILL_NO_MATERIAL_IMPACT"

CRITICAL_POSSIBLE = "CRITICAL_POSSIBLE"
HIGH_POSSIBLE = "HIGH_POSSIBLE"
MEDIUM_POSSIBLE = "MEDIUM_POSSIBLE"
LOW_ONLY = "LOW_ONLY"
INFO_ONLY = "INFO_ONLY"
NOT_ELIGIBLE = "NOT_ELIGIBLE"
SEVERITY_CEILINGS = (
    CRITICAL_POSSIBLE, HIGH_POSSIBLE, MEDIUM_POSSIBLE, LOW_ONLY, INFO_ONLY, NOT_ELIGIBLE,
)

# Confidence / risk ladder.
LOW = "LOW"
MEDIUM = "MEDIUM"
HIGH = "HIGH"

# Risk magnitude ladder (used by submission-risk fields).
RISK_LOW = "LOW"
RISK_MEDIUM = "MEDIUM"
RISK_HIGH = "HIGH"

# ---------------------------------------------------------------------------
# Forbidden outcome terms (the artifact guard rejects these; never rendered).
# ---------------------------------------------------------------------------
FORBIDDEN_OUTCOME_TERMS = (
    "VALID_BUG",
    "CONFIRMED_VULNERABILITY",
    "SUBMIT_NOW",
    "GUARANTEED_HIGH",
    "GUARANTEED_CRITICAL",
    "EXPLOIT_READY",
    "AUTO_SUBMITTED",
)

# Caps: hunter output stays focused.
TOP_LEAD_LIMIT = 5
RAW_LEAD_LIMIT = 25


def _to_dict(obj) -> dict:
    return dataclasses.asdict(obj)


# ===========================================================================
# Dataclasses
# ===========================================================================
@dataclass
class HunterContext:
    """Resolved run inputs for a single hunter invocation."""

    repo_path: str
    command: str = "hunter"
    scope_file: str = ""
    known_path: str = ""
    audits_path: str = ""
    addresses_file: str = ""
    source_dir: str = ""
    baseline_ref: str = ""
    since_date: str = ""
    audit_date: str = ""
    fresh_allowlist: list = field(default_factory=list)
    source_recovery_mode: str = "auto"  # sourcify | etherscan | none | auto
    rpc_mode: str = RPC_NOT_PROVIDED
    rpc_endpoint_masked: str = ""
    strict_context: bool = False
    out_dir: str = ""

    def to_dict(self) -> dict:
        return _to_dict(self)


@dataclass
class ContractAddress:
    """One normalized address entry (address parser v2 output)."""

    name: str = ""
    address: str = ""
    chain_id: str = ""
    network: str = ""
    category: str = ""
    proxy_expected: object = None  # bool | None
    expected_implementation: object = None  # str | None
    source_reference: str = ""
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return _to_dict(self)


@dataclass
class AddressParseResult:
    """Result of parsing the addresses file (parser v2)."""

    status: str = ADDRESS_NONE_PROVIDED
    path: str = ""
    detected_format: str = ""
    addresses: list = field(default_factory=list)  # ContractAddress dicts
    chain_ids: list = field(default_factory=list)
    networks: list = field(default_factory=list)
    errors: list = field(default_factory=list)
    notes: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return _to_dict(self)


@dataclass
class ProgramIdentity:
    """Inferred program identity / scope map. Generic; nothing hardcoded."""

    program_name: str = ""
    company: str = ""
    platform: str = ""
    bounty_url: str = ""
    repo_urls: list = field(default_factory=list)
    contract_families: list = field(default_factory=list)
    addresses: list = field(default_factory=list)
    chain_ids: list = field(default_factory=list)
    in_scope_keywords: list = field(default_factory=list)
    out_of_scope_keywords: list = field(default_factory=list)
    trusted_roles: list = field(default_factory=list)
    known_issue_links: list = field(default_factory=list)
    reward_severities: list = field(default_factory=list)
    poc_required: bool = False
    scope_status: str = SCOPE_MISSING
    scope_confidence: str = LOW
    scope_warnings: list = field(default_factory=list)
    notes: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return _to_dict(self)


@dataclass
class SourceRecord:
    """Source-provenance record for a single deployed contract / family."""

    address: str = ""
    chain_id: str = ""
    contract_name: str = ""
    source_origin: str = SOURCE_MISSING
    match_type: str = ""
    compiler_version: str = ""
    file_count: int = 0
    source_path: str = ""
    metadata_hash: str = ""
    deduped_source_set_id: str = ""
    limitations: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return _to_dict(self)


@dataclass
class SourceProvenance:
    """Aggregate source-recovery result."""

    overall_status: str = SOURCE_MISSING
    records: list = field(default_factory=list)  # SourceRecord dicts
    recovery_mode: str = "auto"
    network_recovery_attempted: bool = False
    notes: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return _to_dict(self)


@dataclass
class DedupQuality:
    """Corpus-quality verdict for the whole run (BLIND/PARTIAL/USABLE/STRONG)."""

    status: str = DEDUP_BLIND
    parsed_docs: int = 0
    known_docs: int = 0
    audit_docs: int = 0
    test_docs: int = 0
    unparsed: list = field(default_factory=list)
    reasons: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return _to_dict(self)


@dataclass
class KnownMatch:
    """Per-lead dedup verdict."""

    lead_id: str = ""
    dedup_status: str = DEDUP_BLIND
    known_match_status: str = KNOWN_UNKNOWN
    known_issue_confidence: str = LOW
    dedup_similarity_score: float = 0.0
    dedup_evidence: list = field(default_factory=list)
    dedup_reasoning: list = field(default_factory=list)
    dedup_confidence_cap: str = LOW
    public_test_covered: bool = False

    def to_dict(self) -> dict:
        return _to_dict(self)


@dataclass
class FreshnessVerdict:
    """Per-lead freshness verdict (evidence-based only)."""

    lead_id: str = ""
    freshness_status: str = FRESHNESS_UNKNOWN
    freshness_confidence: str = LOW
    freshness_evidence: list = field(default_factory=list)
    freshness_caps: list = field(default_factory=list)
    score: int = 40

    def to_dict(self) -> dict:
        return _to_dict(self)


@dataclass
class DeploymentResult:
    """Per-address read-only deployment result."""

    name: str = ""
    address: str = ""
    chain_id: int = 0
    status: str = ""
    has_code: bool = False
    code_size: int = 0
    code_hash: str = ""
    proxy_pattern: str = ""
    implementation: str = ""
    expected_implementation: str = ""
    admin: str = ""
    beacon: str = ""
    calls: list = field(default_factory=list)
    notes: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return _to_dict(self)


@dataclass
class DeploymentReality:
    """Aggregate deployment-reality signal."""

    status: str = RPC_NOT_PROVIDED
    rpc_mode: str = RPC_NOT_PROVIDED
    chain_id: int = 0
    addresses_provided: bool = False
    results: list = field(default_factory=list)
    mismatches: list = field(default_factory=list)
    recommended_checks: list = field(default_factory=list)
    safe_commands: list = field(default_factory=list)
    rpc_endpoint_masked: str = ""
    reason: str = ""
    notes: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return _to_dict(self)


@dataclass
class RegistryDiff:
    """Live registry / live-set diff result."""

    status: str = REGISTRY_NOT_RUN
    live_entries: list = field(default_factory=list)
    listed_entries: list = field(default_factory=list)
    missing_entries: list = field(default_factory=list)   # listed but not live
    extra_entries: list = field(default_factory=list)      # live but not listed
    scope_confidence: str = LOW
    notes: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return _to_dict(self)


@dataclass
class ValuePath:
    """A single value-flow path through the protocol."""

    path_id: str = ""
    entry_function: str = ""
    entry_asset: str = ""
    accounting_variables: list = field(default_factory=list)
    state_machine_variables: list = field(default_factory=list)
    external_calls: list = field(default_factory=list)
    state_update_ordering: str = ""
    exit_function: str = ""
    recipient: str = ""
    attacker_reachability: str = ""
    trusted_role_required: bool = False
    reachability_confidence: str = ""
    reachability_decision_class: str = ""
    reachability_evidence: list = field(default_factory=list)
    reachability_warnings: list = field(default_factory=list)
    impact_if_broken: str = ""
    source_lines: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return _to_dict(self)


@dataclass
class StateMachine:
    """A detected state machine that gates value flow."""

    state_machine_id: str = ""
    contract: str = ""
    subtype: str = ""
    state_variables: list = field(default_factory=list)
    transitions: list = field(default_factory=list)
    touches_value: bool = False
    value_surfaces: list = field(default_factory=list)
    source_lines: list = field(default_factory=list)
    notes: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return _to_dict(self)


@dataclass
class CallEdge:
    """A precise call-graph edge (only real edges are emitted)."""

    caller: str = ""
    callee: str = ""
    status: str = NO_CALL_EDGE
    evidence_line: int = 0

    def to_dict(self) -> dict:
        return _to_dict(self)


@dataclass
class PocPlan:
    """A minimal PoC plan for a single pursueable lead."""

    poc_plan_id: str = ""
    lead_id: str = ""
    status: str = POC_NEEDS_SOURCE
    hypothesis: str = ""
    why_eligible: str = ""
    why_not_duplicate: str = ""
    why_not_oos: str = ""
    why_not_trusted_role_only: str = ""
    baseline: str = ""
    attack: str = ""
    expected_assertion: str = ""
    measured_impact: str = ""
    required_actors: list = field(default_factory=list)
    required_balances: list = field(default_factory=list)
    required_contract_state: list = field(default_factory=list)
    required_mocks: list = field(default_factory=list)
    existing_harness: str = ""
    target_files: list = field(default_factory=list)
    target_functions: list = field(default_factory=list)
    suggested_test_filename: str = ""
    minimal_skeleton: str = ""
    kill_condition: str = ""
    stop_condition: str = ""
    report_condition: str = ""

    def to_dict(self) -> dict:
        return _to_dict(self)


@dataclass
class SubmissionRisk:
    """Submission rejection-risk model for a single lead."""

    lead_id: str = ""
    status: str = RISK_NEEDS_POC
    expected_severity_ceiling: str = INFO_ONLY
    expected_payout_eligibility: str = LOW
    duplicate_rejection_risk: str = RISK_MEDIUM
    oos_rejection_risk: str = RISK_LOW
    trusted_role_rejection_risk: str = RISK_LOW
    known_corpus_gap_risk: str = RISK_MEDIUM
    deployment_context_gap_risk: str = RISK_LOW
    materiality_risk: str = RISK_MEDIUM
    proof_difficulty_risk: str = RISK_MEDIUM
    reviewer_pushback: list = field(default_factory=list)
    evidence_needed: list = field(default_factory=list)
    submit_ready_threshold: str = ""

    def to_dict(self) -> dict:
        return _to_dict(self)


@dataclass
class ReportFilterRow:
    """Report-filter row (defaults to Submit: NO)."""

    lead_id: str = ""
    title: str = ""
    contract: str = ""
    address: str = ""
    function: str = ""
    lead_type: str = ""
    severity_candidate: str = INFO_ONLY
    eligibility: str = ""
    scope: str = ""
    freshness: str = ""
    dedup: str = ""
    deployment: str = ""
    attacker: str = ""
    trusted_role_required: bool = False
    principal_loss: bool = False
    yield_theft: bool = False
    fee_theft: bool = False
    permanent_freeze: bool = False
    temporary_freeze: bool = False
    materiality: str = ""
    oos_flags: list = field(default_factory=list)
    known_issue_flags: list = field(default_factory=list)
    public_test_flags: list = field(default_factory=list)
    poc_status: str = ""
    expected_assertion: str = ""
    submit: str = "NO"
    human_rewrite_required: bool = True
    reason: str = ""

    def to_dict(self) -> dict:
        return _to_dict(self)


@dataclass
class HunterLead:
    """A single research lead with the full V9 decision envelope."""

    lead_id: str = ""
    title: str = ""
    lead_type: str = GENERIC_VALUE_SURFACE
    contract: str = ""
    function: str = ""
    surface: str = ""
    source_lines: list = field(default_factory=list)
    linked_files: list = field(default_factory=list)
    value_path_ids: list = field(default_factory=list)
    state_machine_ids: list = field(default_factory=list)
    scope_confidence: str = LOW
    freshness_status: str = FRESHNESS_UNKNOWN
    dedup_status: str = DEDUP_BLIND
    known_match_status: str = KNOWN_UNKNOWN
    deployment_status: str = ""
    attacker_reachability: str = ""
    reachability_confidence: str = ""
    reachability_decision_class: str = ""
    reachability_evidence: list = field(default_factory=list)
    reachability_warnings: list = field(default_factory=list)
    trusted_role_risk: str = RISK_LOW
    materiality: str = MEDIUM
    proof_difficulty: str = MEDIUM
    submission_risk: str = RISK_NEEDS_POC
    expected_severity_ceiling: str = INFO_ONLY
    expected_payout_ev: int = 0
    decision: str = PARK_BASELINE
    decision_reasons: list = field(default_factory=list)
    kill_conditions: list = field(default_factory=list)
    poc_plan_id: str = ""
    # internal sub-scores (0-100) used by scoring, not part of the public contract.
    score: int = 0
    score_breakdown: dict = field(default_factory=dict)
    decision_caps: list = field(default_factory=list)
    priority_boosts: list = field(default_factory=list)
    # raw sub-signals (0-100) carried from the lead builder.
    scope_confidence_score: int = 0
    freshness_score: int = 40
    attacker_reachability_score: int = 0
    materiality_score: int = 0
    duplicate_risk_score: int = 0
    trusted_role_risk_score: int = 0
    proof_difficulty_score: int = 50
    source_status: str = SOURCE_MISSING
    notes: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return _to_dict(self)


@dataclass
class EngineEvaluation:
    """Honest self-evaluation of the run (no marketing)."""

    scope_parsing_quality: str = ""
    source_recovery_quality: str = ""
    known_corpus_quality: str = ""
    dedup_quality: str = ""
    freshness_quality: str = ""
    deployment_reality_quality: str = ""
    value_flow_quality: str = ""
    state_machine_quality: str = ""
    top_lead_quality: str = ""
    poc_planner_usefulness: str = ""
    submission_risk_usefulness: str = ""
    false_positive_risk: str = ""
    false_negative_risk: str = ""
    missed_surface_risk: str = ""
    manual_review_dependency: str = ""
    biggest_uncertainty: str = ""
    what_arkheionx_got_wrong: list = field(default_factory=list)
    what_to_fix_next: list = field(default_factory=list)
    scores: dict = field(default_factory=dict)  # named 0-10 scores

    def to_dict(self) -> dict:
        return _to_dict(self)


@dataclass
class HunterPack:
    """Aggregate result of one hunter run."""

    context: HunterContext
    generated_at: str
    arkheionx_version: str
    program_identity: ProgramIdentity
    address_parse: AddressParseResult
    source_provenance: SourceProvenance
    dedup_quality: DedupQuality
    deployment_reality: DeploymentReality
    registry_diff: RegistryDiff
    engine_evaluation: EngineEvaluation
    leads: list = field(default_factory=list)               # HunterLead
    known_matches: list = field(default_factory=list)        # KnownMatch
    freshness_verdicts: list = field(default_factory=list)   # FreshnessVerdict
    value_paths: list = field(default_factory=list)          # ValuePath
    state_machines: list = field(default_factory=list)       # StateMachine
    call_edges: list = field(default_factory=list)           # CallEdge
    function_reachability: list = field(default_factory=list)  # FunctionReachability dicts
    reachability_summary: dict = field(default_factory=dict)
    poc_plans: list = field(default_factory=list)            # PocPlan
    submission_risks: list = field(default_factory=list)     # SubmissionRisk
    report_filter: list = field(default_factory=list)        # ReportFilterRow
    hard_kills: list = field(default_factory=list)
    decision_caps: list = field(default_factory=list)
    engine_warnings: list = field(default_factory=list)
    missing_context: list = field(default_factory=list)
    counts: dict = field(default_factory=dict)

    def ranked_leads(self) -> list:
        order = {d: i for i, d in enumerate(
            (PURSUE_NOW, NEEDS_POC) + PARK_DECISIONS + KILL_DECISIONS)}
        return sorted(self.leads, key=lambda x: (-x.score, order.get(x.decision, 99), x.lead_id))

    def top_leads(self, limit: int = TOP_LEAD_LIMIT) -> list:
        pursueable = [x for x in self.ranked_leads() if x.decision in PURSUEABLE]
        parked = [x for x in self.ranked_leads() if x.decision in PARK_DECISIONS]
        return (pursueable + parked)[: max(0, limit)]

    def to_dict(self) -> dict:
        return _to_dict(self)

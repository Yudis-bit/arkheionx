"""Internal protocol intelligence dataclasses (v3.5, additive, internal-only).

These dataclasses describe one normalized, local/static review model that links
contracts, functions, value paths, assumptions, test gaps, proof suggestions,
proof/trace receipts, evidence packages, report drafts, and evidence links
through stable IDs. Every node carries an ``aliases`` map (legacy display names,
slugs, and old IDs) and a ``metadata`` map (uncertain/heuristic extras), so old
identity is preserved rather than replaced.

The model is review guidance only. It never asserts confirmed vulnerabilities,
final severity, or submission readiness, and it performs no RPC, live-chain, or
exploit behavior. ``confidence`` reflects heuristic model certainty and
``evidence_level`` reflects proof strength; the two are never merged.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field

SCHEMA_VERSION = "0.1.0"

# Evidence ladder, kept identical to the review-map vocabulary for compatibility.
HEURISTIC = "HEURISTIC"
COMPILER_CONFIRMED = "COMPILER_CONFIRMED"
EXECUTION_CONFIRMED = "EXECUTION_CONFIRMED"
EVIDENCE_READY = "EVIDENCE_READY"
HUMAN_REVIEWED = "HUMAN_REVIEWED"


def to_dict(obj: object) -> object:
    """Deterministically serialize an intelligence dataclass or container."""

    if hasattr(obj, "__dataclass_fields__"):
        return asdict(obj)
    if isinstance(obj, (list, tuple)):
        return [to_dict(item) for item in obj]
    return obj


@dataclass
class ContractNode:
    contract_id: str
    name: str = ""
    path: str = ""
    kind: str = "contract"
    roles: list[str] = field(default_factory=list)
    value_holding: bool = False
    confidence: str = "medium"
    aliases: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)


@dataclass
class FunctionNode:
    function_id: str
    contract_id: str = ""
    signature: str = ""
    display_name: str = ""
    source_location: str = ""
    mutability: str = "unknown"
    value_sensitivity: str = "none"
    role_surface: list[str] = field(default_factory=list)
    confidence: str = "medium"
    aliases: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)


@dataclass
class ValuePathNode:
    value_path_id: str
    entry_function_id: str = ""
    exit_function_id: str = ""
    label: str = ""
    assets: list[str] = field(default_factory=list)
    conditions: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    priority: str = "low"
    confidence: str = "medium"
    aliases: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)


@dataclass
class AssumptionNode:
    assumption_id: str
    assumption_type: str = "general"
    description: str = ""
    linked_function_ids: list[str] = field(default_factory=list)
    linked_value_path_ids: list[str] = field(default_factory=list)
    evidence_level: str = HEURISTIC
    confidence: str = "medium"
    aliases: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)


@dataclass
class TestGapNode:
    test_gap_id: str
    linked_function_id: str = ""
    linked_assumption_id: str = ""
    scenario: str = ""
    priority: str = "low"
    confidence: str = "low"
    proof_suggestion_id: str = ""
    aliases: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)


@dataclass
class ProofSuggestionNode:
    proof_suggestion_id: str
    linked_test_gap_id: str = ""
    target_function_id: str = ""
    objective: str = ""
    setup: list[str] = field(default_factory=list)
    action: str = ""
    assertions: list[str] = field(default_factory=list)
    aliases: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)


@dataclass
class ProofReceiptNode:
    proof_receipt_id: str
    linked_proof_suggestion_id: str = ""
    target_function_id: str = ""
    status: str = ""
    evidence_level: str = HEURISTIC
    source_artifacts: dict = field(default_factory=dict)
    aliases: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)


@dataclass
class TraceReceiptNode:
    trace_receipt_id: str
    linked_proof_receipt_id: str = ""
    target_function_id: str = ""
    status: str = ""
    evidence_level: str = HEURISTIC
    source_artifacts: dict = field(default_factory=dict)
    aliases: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)


@dataclass
class EvidencePackageNode:
    evidence_package_id: str
    linked_proof_receipt_id: str = ""
    linked_trace_receipt_id: str = ""
    target_function_id: str = ""
    evidence_level: str = HEURISTIC
    manifest: dict = field(default_factory=dict)
    readiness: str = ""
    aliases: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)


@dataclass
class ReportDraftNode:
    report_id: str
    linked_evidence_package_id: str = ""
    linked_target_function_id: str = ""
    review_status: str = "NEEDS_HUMAN_REVIEW"
    report_readiness: dict = field(default_factory=dict)
    safety_boundary: list[str] = field(default_factory=list)
    aliases: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)


@dataclass
class EvidenceLinkNode:
    evidence_link_id: str
    linked_target_function_id: str = ""
    linked_artifact_kind: str = ""
    linked_artifact_path: str = ""
    evidence_package_id: str = ""
    proof_receipt_id: str = ""
    trace_receipt_id: str = ""
    report_id: str = ""
    evidence_level: str = HEURISTIC
    aliases: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)


@dataclass
class ProtocolModel:
    protocol_id: str
    repo_path: str = ""
    generated_at: str = ""
    schema_version: str = SCHEMA_VERSION
    contracts: list[ContractNode] = field(default_factory=list)
    functions: list[FunctionNode] = field(default_factory=list)
    value_paths: list[ValuePathNode] = field(default_factory=list)
    assumptions: list[AssumptionNode] = field(default_factory=list)
    test_gaps: list[TestGapNode] = field(default_factory=list)
    proof_suggestions: list[ProofSuggestionNode] = field(default_factory=list)
    proof_receipts: list[ProofReceiptNode] = field(default_factory=list)
    trace_receipts: list[TraceReceiptNode] = field(default_factory=list)
    evidence_packages: list[EvidencePackageNode] = field(default_factory=list)
    report_drafts: list[ReportDraftNode] = field(default_factory=list)
    evidence_links: list[EvidenceLinkNode] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Return a plain, JSON-ready dict (deterministic for stable inputs)."""

        return asdict(self)

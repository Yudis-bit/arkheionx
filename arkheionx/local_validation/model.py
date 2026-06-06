"""Internal local validation dataclasses and constants (v3.7, additive, internal-only).

These dataclasses describe a local, static record of a Foundry / local validation
run: the run itself, per-test results, optional trace receipts, written artifacts,
and a repo-level summary. They are pure containers: they read nothing, write
nothing, run no subprocess, call no Foundry tool, and perform no RPC, live-chain,
key-handling, or exploit behavior. They never assert a confirmed vulnerability, a
final severity, an audit outcome, or submission readiness, and they never emit a
human-reviewed status automatically.

This module defines shapes, status vocabulary, a safety boundary, and a
deterministic serializer only. Parser, builder, writer, CLI, and review-package
integration are later v3.7 work. Timestamps are never auto-stamped and IDs are
never auto-generated here; callers mint IDs via ``arkheionx.local_validation.ids``.
"""
from __future__ import annotations

from dataclasses import dataclass, field, fields, is_dataclass
from pathlib import PurePath

SCHEMA_VERSION = "0.1.0"

# Run statuses (the furthest honest state of a local validation run).
LOCAL_VALIDATION_NOT_RUN = "LOCAL_VALIDATION_NOT_RUN"
LOCAL_VALIDATION_RUNNING = "LOCAL_VALIDATION_RUNNING"
LOCAL_VALIDATION_PASSED = "LOCAL_VALIDATION_PASSED"
LOCAL_VALIDATION_FAILED = "LOCAL_VALIDATION_FAILED"
LOCAL_VALIDATION_PARTIAL = "LOCAL_VALIDATION_PARTIAL"
LOCAL_VALIDATION_ERROR = "LOCAL_VALIDATION_ERROR"
LOCAL_VALIDATION_SKIPPED = "LOCAL_VALIDATION_SKIPPED"

# Per-test statuses.
TEST_PASSED = "TEST_PASSED"
TEST_FAILED = "TEST_FAILED"
TEST_SKIPPED = "TEST_SKIPPED"
TEST_ERROR = "TEST_ERROR"
TEST_UNKNOWN = "TEST_UNKNOWN"

# Trace statuses.
TRACE_NOT_AVAILABLE = "TRACE_NOT_AVAILABLE"
TRACE_AVAILABLE = "TRACE_AVAILABLE"
TRACE_PARTIAL = "TRACE_PARTIAL"
TRACE_PARSE_ERROR = "TRACE_PARSE_ERROR"

# Evidence-support signal vocabulary. Separate from the existing evidence ladder;
# local validation never promotes HEURISTIC/COMPILER/EXECUTION/EVIDENCE levels.
SUPPORT_NONE = "SUPPORT_NONE"
SUPPORT_TESTED = "SUPPORT_TESTED"
SUPPORT_TRACE_BOUND = "SUPPORT_TRACE_BOUND"
SUPPORT_MANUAL_REVIEW_REQUIRED = "SUPPORT_MANUAL_REVIEW_REQUIRED"

# Artifact kinds (used by later writer / review-package integration).
ARTIFACT_KIND_RUN = "local_validation_run"
ARTIFACT_KIND_TEST_RESULT = "local_test_result"
ARTIFACT_KIND_TRACE_RECEIPT = "local_trace_receipt"
ARTIFACT_KIND_SUMMARY = "local_validation_summary"
ARTIFACT_KIND_STDOUT = "local_validation_stdout"
ARTIFACT_KIND_STDERR = "local_validation_stderr"
ARTIFACT_KIND_RAW_JSON = "local_validation_raw_json"
ARTIFACT_KIND_RAW_TEXT = "local_validation_raw_text"
ARTIFACT_KIND_TRACE = "local_validation_trace"

LOCAL_VALIDATION_ARTIFACT_KINDS = (
    ARTIFACT_KIND_RUN, ARTIFACT_KIND_TEST_RESULT, ARTIFACT_KIND_TRACE_RECEIPT,
    ARTIFACT_KIND_SUMMARY, ARTIFACT_KIND_STDOUT, ARTIFACT_KIND_STDERR,
    ARTIFACT_KIND_RAW_JSON, ARTIFACT_KIND_RAW_TEXT, ARTIFACT_KIND_TRACE,
)

# Local validation is local/static review context only. This boundary records
# what it must never do: it performs no RPC, no fork-url behavior, and no
# live-chain calls; it holds no private keys and reads no seed phrases; it
# broadcasts no transactions, runs no exploit automation, and never auto-submits.
# It never emits a human-reviewed status and never claims a confirmed
# vulnerability, a final severity, an audit-passed outcome, or bounty
# eligibility. Manual review is required and a result is not ready for submission.
DEFAULT_LOCAL_VALIDATION_SAFETY_BOUNDARY: dict[str, object] = {
    "local_static_only": True,
    "no_rpc": True,
    "no_fork_url": True,
    "no_live_chain_calls": True,
    "no_private_keys": True,
    "no_seed_phrases": True,
    "no_transaction_broadcasting": True,
    "no_exploit_automation": True,
    "no_auto_submit": True,
    "no_automatic_human_reviewed": True,
    "no_confirmed_vulnerabilities": True,
    "no_final_severity": True,
    "no_audit_passed_claim": True,
    "no_bounty_eligibility": True,
    "manual_review_required": True,
    "ready_for_submission": False,
}

DEFAULT_LOCAL_VALIDATION_LIMITATIONS: list[str] = [
    "Local/static local validation record only; not an audit.",
    "A passing local test does not prove absence of bugs.",
    "A failing local test does not by itself prove a vulnerability.",
    "No final severity and no bounty eligibility; manual review is required.",
]


@dataclass
class LocalValidationRun:
    run_id: str = ""
    tool: str = "foundry"
    repo_fingerprint: str = ""
    command: list[str] = field(default_factory=list)
    status: str = LOCAL_VALIDATION_NOT_RUN
    exit_code: int | None = None
    stdout_path: str = ""
    stderr_path: str = ""
    result_path: str = ""
    trace_path: str = ""
    artifact_ids: list[str] = field(default_factory=list)
    test_result_ids: list[str] = field(default_factory=list)
    trace_receipt_ids: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    safety_boundary: dict[str, object] = field(default_factory=lambda: dict(DEFAULT_LOCAL_VALIDATION_SAFETY_BOUNDARY))
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass
class LocalTestResult:
    test_result_id: str = ""
    run_id: str = ""
    tool: str = "foundry"
    test_name: str = ""
    contract_name: str = ""
    function_name: str = ""
    selector: str = ""
    status: str = TEST_UNKNOWN
    duration_ms: int | None = None
    gas_used: int | None = None
    file_path: str = ""
    line: int | None = None
    linked_function_ids: list[str] = field(default_factory=list)
    linked_value_path_ids: list[str] = field(default_factory=list)
    linked_assumption_ids: list[str] = field(default_factory=list)
    linked_test_gap_ids: list[str] = field(default_factory=list)
    evidence_support: str = SUPPORT_NONE
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass
class LocalTraceReceipt:
    trace_receipt_id: str = ""
    run_id: str = ""
    test_result_id: str = ""
    tool: str = "foundry"
    trace_kind: str = ""
    trace_status: str = TRACE_NOT_AVAILABLE
    trace_path: str = ""
    linked_function_ids: list[str] = field(default_factory=list)
    call_count: int = 0
    external_call_count: int = 0
    value_transfer_count: int = 0
    delegatecall_count: int = 0
    staticcall_count: int = 0
    events_count: int = 0
    evidence_support: str = SUPPORT_NONE
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass
class LocalValidationArtifact:
    artifact_id: str = ""
    run_id: str = ""
    tool: str = "foundry"
    kind: str = ""
    path: str = ""
    relative_path: str = ""
    checksum_sha256: str = ""
    exists: bool = False
    size_bytes: int = 0
    status: str = ""
    linked_ids: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass
class LocalValidationSummary:
    summary_id: str = ""
    repo_fingerprint: str = ""
    tool: str = "foundry"
    run_ids: list[str] = field(default_factory=list)
    artifact_ids: list[str] = field(default_factory=list)
    test_result_ids: list[str] = field(default_factory=list)
    trace_receipt_ids: list[str] = field(default_factory=list)
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    skipped_tests: int = 0
    errored_tests: int = 0
    unknown_tests: int = 0
    trace_receipts: int = 0
    linked_function_count: int = 0
    linked_value_path_count: int = 0
    linked_assumption_count: int = 0
    linked_test_gap_count: int = 0
    status: str = LOCAL_VALIDATION_NOT_RUN
    coverage_notes: list[str] = field(default_factory=list)
    limitations: list[str] = field(default_factory=lambda: list(DEFAULT_LOCAL_VALIDATION_LIMITATIONS))
    warnings: list[str] = field(default_factory=list)
    safety_boundary: dict[str, object] = field(default_factory=lambda: dict(DEFAULT_LOCAL_VALIDATION_SAFETY_BOUNDARY))
    manual_review_required: bool = True
    ready_for_submission: bool = False
    metadata: dict[str, object] = field(default_factory=dict)


def to_dict(value: object) -> object:
    """Recursively convert a local-validation dataclass/container to JSON-safe data.

    Converts dataclasses, lists/tuples, and dicts recursively; converts Path-like
    values to POSIX strings; preserves booleans, ``None``, and empty containers;
    does not mutate the source; and raises ``TypeError`` for unsupported objects.
    """

    if isinstance(value, bool) or value is None or isinstance(value, (str, int, float)):
        return value
    if isinstance(value, PurePath):
        return value.as_posix()
    if is_dataclass(value) and not isinstance(value, type):
        return {f.name: to_dict(getattr(value, f.name)) for f in fields(value)}
    if isinstance(value, dict):
        return {str(key): to_dict(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_dict(item) for item in value]
    raise TypeError(f"to_dict cannot serialize object of type {type(value).__name__}")


def local_validation_status_from_counts(
    passed: int, failed: int, skipped: int, errored: int, unknown: int = 0
) -> str:
    """Derive a conservative run status from test counts.

    Rules: zero total -> NOT_RUN; any errored -> ERROR; any failed with any
    passed/skipped -> PARTIAL; failed-only -> FAILED; all passed -> PASSED; all
    skipped -> SKIPPED. A run mixing passed with skipped/unknown (and no
    failed/errored), or unknown-only, is PARTIAL, because skipped and unknown
    tests are not proof. This never claims an audit passed or a confirmed
    vulnerability.
    """

    total = passed + failed + skipped + errored + unknown
    if total <= 0:
        return LOCAL_VALIDATION_NOT_RUN
    if errored > 0:
        return LOCAL_VALIDATION_ERROR
    if failed > 0:
        return LOCAL_VALIDATION_PARTIAL if (passed > 0 or skipped > 0) else LOCAL_VALIDATION_FAILED
    if passed == 0 and skipped == 0:
        return LOCAL_VALIDATION_PARTIAL  # unknown-only is not proof
    if passed == 0:
        return LOCAL_VALIDATION_SKIPPED
    if skipped == 0 and unknown == 0:
        return LOCAL_VALIDATION_PASSED
    return LOCAL_VALIDATION_PARTIAL

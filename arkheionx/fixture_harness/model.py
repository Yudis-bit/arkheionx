"""Internal fixture harness dataclasses and constants (v3.9, additive, internal-only).

These pure dataclasses describe a local, static fixture harness: a protocol
fixture (metadata), fixture artifact references, fixture runs, fixture results,
fixture snapshot references, and a fixture suite rollup. They are review-surface
scaffolding for benchmarking and regression only. They never assert a confirmed
vulnerability, a final severity, an audit outcome, or submission readiness; a
fixture passing never proves safety and a fixture failing never proves a
vulnerability.

This module defines shapes, a controlled vocabulary, deterministic builder
helpers, and a JSON-safe serializer only. It reads nothing, writes nothing, runs
no subprocess, performs no RPC, fork-url, live-chain, key-handling, or exploit
behavior, and adds no CLI command. Timestamps are never auto-stamped; IDs are
minted deterministically via ``arkheionx.fixture_harness.ids``. Importing this
module has no side effects.
"""
from __future__ import annotations

from dataclasses import dataclass, field, fields, is_dataclass
from pathlib import PurePath

from .ids import (
    fixture_id as _mint_fixture_id,
    short_fixture_hash,
    slugify_fixture_token,
)

SCHEMA_VERSION = "0.1.0"

# --- Controlled fixture categories ------------------------------------------

FIXTURE_CATEGORY_ERC20 = "FIXTURE_CATEGORY_ERC20"
FIXTURE_CATEGORY_LENDING_VAULT = "FIXTURE_CATEGORY_LENDING_VAULT"
FIXTURE_CATEGORY_STAKING_REWARD = "FIXTURE_CATEGORY_STAKING_REWARD"
FIXTURE_CATEGORY_AMM_SWAP = "FIXTURE_CATEGORY_AMM_SWAP"
FIXTURE_CATEGORY_ORACLE_DEPENDENT = "FIXTURE_CATEGORY_ORACLE_DEPENDENT"
FIXTURE_CATEGORY_UPGRADEABLE_PROXY = "FIXTURE_CATEGORY_UPGRADEABLE_PROXY"
FIXTURE_CATEGORY_BRIDGE_MESSAGE = "FIXTURE_CATEGORY_BRIDGE_MESSAGE"
FIXTURE_CATEGORY_LIQUIDATION_BORROW_REPAY = "FIXTURE_CATEGORY_LIQUIDATION_BORROW_REPAY"
FIXTURE_CATEGORY_MISC = "FIXTURE_CATEGORY_MISC"

FIXTURE_CATEGORY_VALUES: tuple[str, ...] = (
    FIXTURE_CATEGORY_ERC20,
    FIXTURE_CATEGORY_LENDING_VAULT,
    FIXTURE_CATEGORY_STAKING_REWARD,
    FIXTURE_CATEGORY_AMM_SWAP,
    FIXTURE_CATEGORY_ORACLE_DEPENDENT,
    FIXTURE_CATEGORY_UPGRADEABLE_PROXY,
    FIXTURE_CATEGORY_BRIDGE_MESSAGE,
    FIXTURE_CATEGORY_LIQUIDATION_BORROW_REPAY,
    FIXTURE_CATEGORY_MISC,
)

FIXTURE_CATEGORY_DESCRIPTIONS: dict[str, str] = {
    FIXTURE_CATEGORY_ERC20: "Simple ERC20-like token (mint/burn/transfer; inflow/outflow/accounting).",
    FIXTURE_CATEGORY_LENDING_VAULT: "Lending vault (collateral/borrow-repay; oracle dependency).",
    FIXTURE_CATEGORY_STAKING_REWARD: "Staking / reward protocol (stake/claim-reward/accounting).",
    FIXTURE_CATEGORY_AMM_SWAP: "AMM / swap protocol (swap/reserves/liquidity).",
    FIXTURE_CATEGORY_ORACLE_DEPENDENT: "Oracle-dependent protocol (oracle consumer/setter paths).",
    FIXTURE_CATEGORY_UPGRADEABLE_PROXY: "Upgradeable proxy pattern (upgrade/delegatecall/authority paths).",
    FIXTURE_CATEGORY_BRIDGE_MESSAGE: "Bridge / message protocol (bridge/external-call paths).",
    FIXTURE_CATEGORY_LIQUIDATION_BORROW_REPAY: "Liquidation / borrow-repay protocol.",
    FIXTURE_CATEGORY_MISC: "Miscellaneous local/static fixture not matching another category.",
}

# --- Controlled fixture artifact kinds --------------------------------------

FIXTURE_ARTIFACT_SOURCE = "FIXTURE_ARTIFACT_SOURCE"
FIXTURE_ARTIFACT_REVIEW_MAP = "FIXTURE_ARTIFACT_REVIEW_MAP"
FIXTURE_ARTIFACT_PROTOCOL_MODEL = "FIXTURE_ARTIFACT_PROTOCOL_MODEL"
FIXTURE_ARTIFACT_LOCAL_VALIDATION = "FIXTURE_ARTIFACT_LOCAL_VALIDATION"
FIXTURE_ARTIFACT_PROTOCOL_GRAPH = "FIXTURE_ARTIFACT_PROTOCOL_GRAPH"
FIXTURE_ARTIFACT_EVIDENCE = "FIXTURE_ARTIFACT_EVIDENCE"
FIXTURE_ARTIFACT_REPORT = "FIXTURE_ARTIFACT_REPORT"
FIXTURE_ARTIFACT_REVIEW_PACKAGE = "FIXTURE_ARTIFACT_REVIEW_PACKAGE"
FIXTURE_ARTIFACT_SNAPSHOT = "FIXTURE_ARTIFACT_SNAPSHOT"
FIXTURE_ARTIFACT_UNKNOWN = "FIXTURE_ARTIFACT_UNKNOWN"

FIXTURE_ARTIFACT_KIND_VALUES: tuple[str, ...] = (
    FIXTURE_ARTIFACT_SOURCE,
    FIXTURE_ARTIFACT_REVIEW_MAP,
    FIXTURE_ARTIFACT_PROTOCOL_MODEL,
    FIXTURE_ARTIFACT_LOCAL_VALIDATION,
    FIXTURE_ARTIFACT_PROTOCOL_GRAPH,
    FIXTURE_ARTIFACT_EVIDENCE,
    FIXTURE_ARTIFACT_REPORT,
    FIXTURE_ARTIFACT_REVIEW_PACKAGE,
    FIXTURE_ARTIFACT_SNAPSHOT,
    FIXTURE_ARTIFACT_UNKNOWN,
)

# --- Controlled fixture run statuses (furthest honest state of a run) --------

FIXTURE_RUN_PLANNED = "FIXTURE_RUN_PLANNED"
FIXTURE_RUN_READY = "FIXTURE_RUN_READY"
FIXTURE_RUN_EXECUTED = "FIXTURE_RUN_EXECUTED"
FIXTURE_RUN_PARTIAL = "FIXTURE_RUN_PARTIAL"
FIXTURE_RUN_FAILED = "FIXTURE_RUN_FAILED"
FIXTURE_RUN_SKIPPED = "FIXTURE_RUN_SKIPPED"

FIXTURE_RUN_STATUS_VALUES: tuple[str, ...] = (
    FIXTURE_RUN_PLANNED,
    FIXTURE_RUN_READY,
    FIXTURE_RUN_EXECUTED,
    FIXTURE_RUN_PARTIAL,
    FIXTURE_RUN_FAILED,
    FIXTURE_RUN_SKIPPED,
)

# --- Controlled fixture result statuses -------------------------------------

FIXTURE_RESULT_OBSERVED = "FIXTURE_RESULT_OBSERVED"
FIXTURE_RESULT_MATCHED_SNAPSHOT = "FIXTURE_RESULT_MATCHED_SNAPSHOT"
FIXTURE_RESULT_DRIFT_DETECTED = "FIXTURE_RESULT_DRIFT_DETECTED"
FIXTURE_RESULT_NEEDS_REVIEW = "FIXTURE_RESULT_NEEDS_REVIEW"
FIXTURE_RESULT_FAILED = "FIXTURE_RESULT_FAILED"
FIXTURE_RESULT_SKIPPED = "FIXTURE_RESULT_SKIPPED"

FIXTURE_RESULT_STATUS_VALUES: tuple[str, ...] = (
    FIXTURE_RESULT_OBSERVED,
    FIXTURE_RESULT_MATCHED_SNAPSHOT,
    FIXTURE_RESULT_DRIFT_DETECTED,
    FIXTURE_RESULT_NEEDS_REVIEW,
    FIXTURE_RESULT_FAILED,
    FIXTURE_RESULT_SKIPPED,
)

# --- Controlled benchmark dimensions ----------------------------------------

BENCHMARK_DIMENSION_ID_STABILITY = "BENCHMARK_DIMENSION_ID_STABILITY"
BENCHMARK_DIMENSION_JSON_STABILITY = "BENCHMARK_DIMENSION_JSON_STABILITY"
BENCHMARK_DIMENSION_GRAPH_COUNTS = "BENCHMARK_DIMENSION_GRAPH_COUNTS"
BENCHMARK_DIMENSION_CROSSREF_OUTCOMES = "BENCHMARK_DIMENSION_CROSSREF_OUTCOMES"
BENCHMARK_DIMENSION_EXPORT_CHECKSUM = "BENCHMARK_DIMENSION_EXPORT_CHECKSUM"
BENCHMARK_DIMENSION_JSON_PURITY = "BENCHMARK_DIMENSION_JSON_PURITY"
BENCHMARK_DIMENSION_NO_OVERCLAIM = "BENCHMARK_DIMENSION_NO_OVERCLAIM"
BENCHMARK_DIMENSION_REVIEW_CONTEXT = "BENCHMARK_DIMENSION_REVIEW_CONTEXT"

BENCHMARK_DIMENSION_VALUES: tuple[str, ...] = (
    BENCHMARK_DIMENSION_ID_STABILITY,
    BENCHMARK_DIMENSION_JSON_STABILITY,
    BENCHMARK_DIMENSION_GRAPH_COUNTS,
    BENCHMARK_DIMENSION_CROSSREF_OUTCOMES,
    BENCHMARK_DIMENSION_EXPORT_CHECKSUM,
    BENCHMARK_DIMENSION_JSON_PURITY,
    BENCHMARK_DIMENSION_NO_OVERCLAIM,
    BENCHMARK_DIMENSION_REVIEW_CONTEXT,
)


# --- Dataclasses ------------------------------------------------------------

@dataclass
class FixtureSafetyBoundary:
    """Local/static-only boundary for fixture harness records (review context).

    Every flag records what the harness must never do. A fixture is review-surface
    input only: it never proves safety and never proves a vulnerability.
    """

    local_static_only: bool = True
    no_rpc: bool = True
    no_fork_url: bool = True
    no_live_chain_calls: bool = True
    no_private_keys: bool = True
    no_seed_phrases: bool = True
    no_transaction_broadcasting: bool = True
    no_exploit_automation: bool = True
    no_auto_submit: bool = True
    no_automatic_human_reviewed: bool = True
    no_confirmed_vulnerabilities: bool = True
    no_final_severity: bool = True
    no_audit_passed_claim: bool = True
    no_bounty_eligibility: bool = True
    manual_review_required: bool = True
    ready_for_submission: bool = False


@dataclass
class ProtocolFixture:
    fixture_id: str = ""
    name: str = ""
    category: str = FIXTURE_CATEGORY_MISC
    description: str = ""
    relative_path: str = ""
    source_files: list[str] = field(default_factory=list)
    expected_artifact_kinds: list[str] = field(default_factory=list)
    benchmark_dimensions: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    safety_boundary: FixtureSafetyBoundary = field(default_factory=FixtureSafetyBoundary)
    warnings: list[str] = field(default_factory=list)
    manual_review_required: bool = True
    ready_for_submission: bool = False
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass
class FixtureArtifactRef:
    artifact_id: str = ""
    fixture_id: str = ""
    artifact_kind: str = FIXTURE_ARTIFACT_UNKNOWN
    relative_path: str = ""
    checksum_sha256: str = ""
    size_bytes: int = 0
    linked_ids: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    manual_review_required: bool = True
    ready_for_submission: bool = False
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass
class FixtureRun:
    run_id: str = ""
    fixture_id: str = ""
    runner: str = ""
    command_label: str = ""
    input_artifact_ids: list[str] = field(default_factory=list)
    output_artifact_ids: list[str] = field(default_factory=list)
    run_status: str = FIXTURE_RUN_PLANNED
    benchmark_dimensions: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    manual_review_required: bool = True
    ready_for_submission: bool = False
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass
class FixtureResult:
    result_id: str = ""
    fixture_id: str = ""
    run_id: str = ""
    result_kind: str = ""
    result_status: str = FIXTURE_RESULT_OBSERVED
    subject_id: str = ""
    observed_value: object = None
    expected_value: object = None
    drift_detected: bool = False
    warnings: list[str] = field(default_factory=list)
    manual_review_required: bool = True
    ready_for_submission: bool = False
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass
class FixtureSnapshotRef:
    snapshot_id: str = ""
    fixture_id: str = ""
    snapshot_kind: str = ""
    subject_ids: list[str] = field(default_factory=list)
    relative_path: str = ""
    checksum_sha256: str = ""
    warnings: list[str] = field(default_factory=list)
    manual_review_required: bool = True
    ready_for_submission: bool = False
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass
class FixtureSuite:
    suite_id: str = ""
    name: str = ""
    fixtures: list[ProtocolFixture] = field(default_factory=list)
    artifact_refs: list[FixtureArtifactRef] = field(default_factory=list)
    runs: list[FixtureRun] = field(default_factory=list)
    results: list[FixtureResult] = field(default_factory=list)
    snapshots: list[FixtureSnapshotRef] = field(default_factory=list)
    fixture_count: int = 0
    run_count: int = 0
    result_count: int = 0
    drift_count: int = 0
    warnings: list[str] = field(default_factory=list)
    manual_review_required: bool = True
    ready_for_submission: bool = False
    metadata: dict[str, object] = field(default_factory=dict)


# --- Serialization ----------------------------------------------------------

def fixture_harness_to_dict(value: object) -> object:
    """Recursively convert a fixture-harness dataclass/container to JSON-safe data.

    Converts dataclasses, lists/tuples, and dicts recursively; converts Path-like
    values to POSIX strings; preserves booleans, ``None``, and numbers/strings;
    does not mutate the source; and raises ``TypeError`` for unsupported objects.
    """

    if isinstance(value, bool) or value is None or isinstance(value, (str, int, float)):
        return value
    if isinstance(value, PurePath):
        return value.as_posix()
    if is_dataclass(value) and not isinstance(value, type):
        return {f.name: fixture_harness_to_dict(getattr(value, f.name)) for f in fields(value)}
    if isinstance(value, dict):
        return {str(key): fixture_harness_to_dict(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [fixture_harness_to_dict(item) for item in value]
    raise TypeError(f"fixture_harness_to_dict cannot serialize object of type {type(value).__name__}")


# --- Builder helpers --------------------------------------------------------

def build_protocol_fixture(name: str, category: str, relative_path: str = "", **kwargs: object) -> ProtocolFixture:
    """Build a ``ProtocolFixture``, minting a deterministic ID when absent.

    A supplied non-empty ``fixture_id`` is preserved; otherwise it is minted from
    the name, category, and relative path. An unknown (non-controlled) category is
    kept (non-inventive) but records a warning. Reads no file and runs nothing.
    """

    warnings = list(kwargs.get("warnings", []) or [])  # type: ignore[arg-type]
    if category not in FIXTURE_CATEGORY_VALUES:
        note = f"unknown fixture category: {category}"
        if note not in warnings:
            warnings.append(note)
    supplied_id = str(kwargs.get("fixture_id", "") or "").strip()
    fid = supplied_id or _mint_fixture_id(name, category, relative_path)
    return ProtocolFixture(
        fixture_id=fid,
        name=str(name or ""),
        category=str(category or FIXTURE_CATEGORY_MISC),
        description=str(kwargs.get("description", "") or ""),
        relative_path=str(relative_path or ""),
        source_files=list(kwargs.get("source_files", []) or []),  # type: ignore[arg-type]
        expected_artifact_kinds=list(kwargs.get("expected_artifact_kinds", []) or []),  # type: ignore[arg-type]
        benchmark_dimensions=list(kwargs.get("benchmark_dimensions", []) or []),  # type: ignore[arg-type]
        tags=list(kwargs.get("tags", []) or []),  # type: ignore[arg-type]
        safety_boundary=kwargs.get("safety_boundary") or FixtureSafetyBoundary(),  # type: ignore[arg-type]
        warnings=warnings,
        manual_review_required=True,
        ready_for_submission=False,
        metadata=dict(kwargs.get("metadata", {}) or {}),  # type: ignore[arg-type]
    )


def fixture_suite_id(name: str, fixture_ids: list[str]) -> str:
    """Deterministic suite ID: ``fixture-suite:<name>:<12hex>``.

    Requires a non-empty ``name``. ``fixture_ids`` are sorted before hashing, so
    the suite ID does not depend on fixture order.
    """

    name_text = str(name or "").strip()
    if not name_text:
        raise ValueError("name is required for fixture_suite_id")
    sorted_ids = sorted(str(f) for f in (fixture_ids or []))
    seed = {"name": name_text, "fixture_ids": sorted_ids}
    return f"fixture-suite:{slugify_fixture_token(name_text)}:{short_fixture_hash(seed)}"


def _merge_warnings(*groups: list[str]) -> list[str]:
    """Merge component warnings into a deterministic, de-duplicated sorted list."""

    merged: set[str] = set()
    for group in groups:
        for warning in group or []:
            if warning:
                merged.add(str(warning))
    return sorted(merged)


def build_fixture_suite(
    name: str,
    fixtures: list[ProtocolFixture] | None = None,
    artifact_refs: list[FixtureArtifactRef] | None = None,
    runs: list[FixtureRun] | None = None,
    results: list[FixtureResult] | None = None,
    snapshots: list[FixtureSnapshotRef] | None = None,
) -> FixtureSuite:
    """Build a ``FixtureSuite`` with a deterministic suite ID and rollups.

    The suite ID is order-independent (derived from sorted fixture IDs). Counts
    and the drift count are deterministic; component warnings are merged into a
    deterministic, de-duplicated, sorted suite warning list. Reads no file, runs
    no fixture, generates no artifact, and executes no benchmark.
    """

    fixtures = list(fixtures or [])
    artifact_refs = list(artifact_refs or [])
    runs = list(runs or [])
    results = list(results or [])
    snapshots = list(snapshots or [])

    suite_id = fixture_suite_id(name, [f.fixture_id for f in fixtures])
    warnings = _merge_warnings(
        [w for f in fixtures for w in f.warnings],
        [w for a in artifact_refs for w in a.warnings],
        [w for r in runs for w in r.warnings],
        [w for r in results for w in r.warnings],
        [w for s in snapshots for w in s.warnings],
    )
    return FixtureSuite(
        suite_id=suite_id,
        name=str(name or ""),
        fixtures=fixtures,
        artifact_refs=artifact_refs,
        runs=runs,
        results=results,
        snapshots=snapshots,
        fixture_count=len(fixtures),
        run_count=len(runs),
        result_count=len(results),
        drift_count=sum(1 for r in results if r.drift_detected),
        warnings=warnings,
        manual_review_required=True,
        ready_for_submission=False,
    )

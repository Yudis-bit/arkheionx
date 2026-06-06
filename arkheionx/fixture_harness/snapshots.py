"""Deterministic local benchmark snapshot baselines (v3.9, additive, internal).

A benchmark snapshot is a small, plain, deterministic summary of a benchmarked
fixture suite: schema version, suite name and ID, counts, sorted fixture /
artifact / result IDs, the union of benchmark dimensions and expected artifact
kinds, the aggregated safety flags, the review-state booleans, and a neutral
notice. It is regression and review context only -- it lets a later change be
diffed against a committed baseline.

A snapshot never contains an absolute path, a username, a hostname, a temporary
path, a dynamic timestamp, a private value, an RPC or fork URL, an automatic
reviewed-status token, or any confirmed-vulnerability, final-severity,
audit-outcome, safety, or bounty claim. Building a snapshot runs no subprocess and
performs no network, RPC, fork-url, or live-chain access; loading reads only the
committed baseline JSON under the local fixtures tree. A matching snapshot never
proves the source is safe and a drifting snapshot never proves a vulnerability;
``manual_review_required`` stays true and ``ready_for_submission`` stays false.
Importing this module has no side effects.
"""
from __future__ import annotations

import json
from dataclasses import fields
from pathlib import Path

from .model import FixtureSafetyBoundary, FixtureSuite, fixture_harness_to_dict
from .runner import benchmark_set1_fixture_suite, benchmark_all_fixture_suite

SNAPSHOT_SCHEMA_VERSION = "0.1.0"

# Committed baseline locations (relative to the repository root). Read-only.
SET1_SNAPSHOT_RELPATH = "tests/fixtures/fixture_harness/snapshots/set1/benchmark_snapshot.json"
ALL_SNAPSHOT_RELPATH = "tests/fixtures/fixture_harness/snapshots/all/benchmark_snapshot.json"

_NEUTRAL_NOTICE = "Snapshot is deterministic benchmark context only. Manual review remains required."
_COMPARE_NOTICE = (
    "Snapshot comparison is deterministic benchmark context only. "
    "Manual review remains required."
)

# Field names of the safety boundary, taken from the dataclass itself so no flag
# name is hardcoded as a literal in this module. The two review-state booleans are
# surfaced at the top level of the snapshot, so they are not duplicated here.
_REVIEW_STATE_FIELDS = ("manual_review_required", "ready_for_submission")
_SAFETY_FLAG_FIELDS = tuple(
    f.name for f in fields(FixtureSafetyBoundary) if f.name not in _REVIEW_STATE_FIELDS
)


def _repo_root() -> Path:
    """Return the repository root (two parents above this package directory)."""

    return Path(__file__).resolve().parents[2]


def _sorted_unique(values: object) -> list[str]:
    """Return a sorted, de-duplicated list of string values."""

    return sorted({str(v) for v in values})


def _aggregate_safety_flags(suite: FixtureSuite) -> dict[str, bool]:
    """Aggregate each safety-boundary flag as true only if true for every fixture.

    With no fixtures the aggregate is empty (nothing to assert). Flag names are
    read from the dataclass, so this module hardcodes no flag literal.
    """

    flags: dict[str, bool] = {}
    for name in _SAFETY_FLAG_FIELDS:
        if suite.fixtures:
            flags[name] = all(
                bool(getattr(f.safety_boundary, name, False)) for f in suite.fixtures
            )
        else:
            flags[name] = False
    return flags


def _snapshot_from_suite(suite: FixtureSuite) -> dict[str, object]:
    """Build a deterministic snapshot dictionary from a benchmarked suite."""

    benchmark_dimensions = _sorted_unique(
        d for f in suite.fixtures for d in (f.benchmark_dimensions or [])
    )
    expected_artifact_kinds = _sorted_unique(
        k for f in suite.fixtures for k in (f.expected_artifact_kinds or [])
    )
    snapshot = {
        "snapshot_schema_version": SNAPSHOT_SCHEMA_VERSION,
        "fixture_suite_name": str(suite.name),
        "fixture_suite_id": str(suite.suite_id),
        "fixture_count": int(suite.fixture_count),
        "artifact_count": int(len(suite.artifact_refs)),
        "result_count": int(suite.result_count),
        "drift_count": int(suite.drift_count),
        "fixture_ids": _sorted_unique(f.fixture_id for f in suite.fixtures),
        "artifact_ids": _sorted_unique(a.artifact_id for a in suite.artifact_refs),
        "result_ids": _sorted_unique(r.result_id for r in suite.results),
        "benchmark_dimensions": benchmark_dimensions,
        "expected_artifact_kinds": expected_artifact_kinds,
        "safety_flags": _aggregate_safety_flags(suite),
        "manual_review_required": True,
        "ready_for_submission": False,
        "neutral_notice": _NEUTRAL_NOTICE,
    }
    return snapshot_to_jsonable(snapshot)


def snapshot_to_jsonable(snapshot: object) -> dict[str, object]:
    """Return a JSON-safe plain-dict form of a snapshot (no dataclasses/paths).

    Round-trips through the fixture-harness serializer and a JSON dump/load so the
    result contains only plain JSON types and is safe to write or compare. Raises
    ``TypeError`` if the snapshot is not a mapping.
    """

    data = fixture_harness_to_dict(snapshot)
    if not isinstance(data, dict):
        raise TypeError("snapshot must be a mapping")
    return json.loads(json.dumps(data, sort_keys=True))


def build_set1_benchmark_snapshot() -> dict[str, object]:
    """Build the deterministic Set 1 benchmark snapshot (pure, local/static)."""

    return _snapshot_from_suite(benchmark_set1_fixture_suite())


def build_all_benchmark_snapshot() -> dict[str, object]:
    """Build the deterministic combined all-fixtures benchmark snapshot.

    Summarizes all nine benchmarked fixtures (Set 1 + Set 2 + Set 3). The
    ``result_count`` is strictly greater than the Set 1-only snapshot's.
    """

    return _snapshot_from_suite(benchmark_all_fixture_suite())


def _load_snapshot(relpath: str) -> dict[str, object]:
    """Load a committed snapshot baseline JSON from a repository-relative path."""

    path = _repo_root() / relpath
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def load_set1_benchmark_snapshot() -> dict[str, object]:
    """Load the committed Set 1 benchmark snapshot baseline from the fixtures tree.

    Reads the committed JSON only; runs nothing and touches no network. Raises
    ``FileNotFoundError`` if the baseline is absent.
    """

    return _load_snapshot(SET1_SNAPSHOT_RELPATH)


def load_all_benchmark_snapshot() -> dict[str, object]:
    """Load the committed combined all-fixtures benchmark snapshot baseline.

    Reads the committed JSON only; runs nothing and touches no network. Raises
    ``FileNotFoundError`` if the baseline is absent.
    """

    return _load_snapshot(ALL_SNAPSHOT_RELPATH)


def _diff_snapshots(observed: dict[str, object], baseline: dict[str, object]) -> list[dict[str, object]]:
    """Return a sorted list of field-level differences between two snapshots."""

    differences: list[dict[str, object]] = []
    for key in sorted(set(observed) | set(baseline)):
        want = baseline.get(key)
        have = observed.get(key)
        if want != have:
            differences.append({"field": key, "expected": want, "observed": have})
    return differences


def compare_set1_benchmark_snapshot(
    observed: dict[str, object] | None = None,
    baseline: dict[str, object] | None = None,
) -> dict[str, object]:
    """Compare an observed snapshot against a baseline and report drift.

    Defaults: ``observed`` is a freshly built snapshot and ``baseline`` is the
    committed baseline. Returns a deterministic result with ``matches``, a
    ``drift_count`` (number of differing fields), a sorted ``differences`` list, the
    review-state booleans, and a neutral notice. Reports drift only; it never
    asserts a vulnerability or a safety outcome.
    """

    observed = snapshot_to_jsonable(observed) if observed is not None else build_set1_benchmark_snapshot()
    baseline = snapshot_to_jsonable(baseline) if baseline is not None else load_set1_benchmark_snapshot()
    differences = _diff_snapshots(observed, baseline)
    return {
        "matches": not differences,
        "drift_count": len(differences),
        "differences": differences,
        "manual_review_required": True,
        "ready_for_submission": False,
        "neutral_notice": _COMPARE_NOTICE,
    }


def compare_all_benchmark_snapshot(
    observed: dict[str, object] | None = None,
    baseline: dict[str, object] | None = None,
) -> dict[str, object]:
    """Compare an observed all-fixtures snapshot against a baseline and report drift.

    Defaults: ``observed`` is a freshly built combined snapshot and ``baseline`` is
    the committed combined baseline. Returns the same deterministic, neutral result
    shape as :func:`compare_set1_benchmark_snapshot`. Reports drift only; it never
    asserts a vulnerability or a safety outcome.
    """

    observed = snapshot_to_jsonable(observed) if observed is not None else build_all_benchmark_snapshot()
    baseline = snapshot_to_jsonable(baseline) if baseline is not None else load_all_benchmark_snapshot()
    differences = _diff_snapshots(observed, baseline)
    return {
        "matches": not differences,
        "drift_count": len(differences),
        "differences": differences,
        "manual_review_required": True,
        "ready_for_submission": False,
        "neutral_notice": _COMPARE_NOTICE,
    }

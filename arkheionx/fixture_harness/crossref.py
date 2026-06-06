"""Standalone fixture benchmark cross-reference context (v3.9, additive, internal).

A crossref is a small, plain, deterministic summary that links a benchmarked
fixture suite to the wider Arkheionx evidence graph by ID only: the suite ID,
counts, sorted fixture / artifact / benchmark-result IDs, the review-state
booleans, three context-availability flags (review package, local validation,
evidence), and an explicit no-overclaim context block. It is review context only.

This module is standalone: it imports no review-package, local-validation, or
evidence code and edits none of those subsystems. The context-availability flags
are computed with ``importlib.util.find_spec``, which detects whether a context
module is importable without importing or executing it, so building a crossref has
no side effects. Building runs no subprocess and performs no network, RPC,
fork-url, or live-chain access.

A crossref never asserts a confirmed vulnerability, a final severity, an audit
outcome, or submission readiness; the no-overclaim block states this explicitly. A
benchmark is not an audit and not a submission, and it does not confirm
vulnerabilities. ``manual_review_required`` stays true and ``ready_for_submission``
stays false. Importing this module has no side effects.
"""
from __future__ import annotations

import importlib.util
import json

from .model import FixtureSuite, fixture_harness_to_dict
from .runner import benchmark_set1_fixture_suite, benchmark_all_fixture_suite

_NEUTRAL_NOTICE = (
    "Fixture benchmark crossref is deterministic review context only. "
    "Manual review remains required."
)


def _context_available(module_name: str) -> bool:
    """Return whether a context module is importable, without importing it.

    Uses ``find_spec`` (no execution of the target module). Any lookup error is
    treated as "not available".
    """

    try:
        return importlib.util.find_spec(module_name) is not None
    except (ImportError, ValueError, ModuleNotFoundError):
        return False


def _sorted_ids(values: object) -> list[str]:
    """Return a sorted, de-duplicated list of string IDs."""

    return sorted({str(v) for v in values})


def build_fixture_benchmark_crossref(suite: FixtureSuite) -> dict[str, object]:
    """Build a deterministic, JSON-safe crossref for a (benchmarked) fixture suite.

    Reads the suite's IDs and counts only; does not mutate the suite. The
    ``benchmark_result_ids`` are taken from the suite's results (empty if the suite
    has not been benchmarked). Output is plain JSON types only.
    """

    crossref = {
        "fixture_suite_id": str(suite.suite_id),
        "fixture_count": int(suite.fixture_count),
        "artifact_count": int(len(suite.artifact_refs)),
        "result_count": int(suite.result_count),
        "fixture_ids": _sorted_ids(f.fixture_id for f in suite.fixtures),
        "artifact_ids": _sorted_ids(a.artifact_id for a in suite.artifact_refs),
        "benchmark_result_ids": _sorted_ids(r.result_id for r in suite.results),
        "manual_review_required": True,
        "ready_for_submission": False,
        "review_context_available": _context_available("arkheionx.review_package"),
        "local_validation_context_available": _context_available("arkheionx.local_validation"),
        "evidence_context_available": _context_available("arkheionx.evidence"),
        "no_overclaim_context": {
            "benchmark_is_not_audit": True,
            "benchmark_is_not_submission": True,
            "benchmark_does_not_confirm_vulnerabilities": True,
            "manual_review_required": True,
        },
        "neutral_notice": _NEUTRAL_NOTICE,
    }
    # Guarantee plain JSON types (and a stable, mutation-free copy).
    return json.loads(json.dumps(fixture_harness_to_dict(crossref), sort_keys=True))


def build_set1_fixture_crossref() -> dict[str, object]:
    """Build the crossref for the benchmarked Set 1 fixture suite."""

    return build_fixture_benchmark_crossref(benchmark_set1_fixture_suite())


def build_all_fixture_crossref() -> dict[str, object]:
    """Build the crossref for the benchmarked combined all-fixtures suite."""

    return build_fixture_benchmark_crossref(benchmark_all_fixture_suite())

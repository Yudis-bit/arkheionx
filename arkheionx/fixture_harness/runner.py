"""Deterministic local/static fixture benchmark runner (v3.9, additive, internal).

This module benchmarks registered protocol fixtures by recording deterministic,
review-surface observations about each fixture and its artifact references: ID
stability, JSON-serialization stability, path safety, safety-boundary flags, a
no-overclaim scan, and a confined read of the local fixture source text. It
produces ``FixtureRun`` and ``FixtureResult`` records and rolls them into a
``FixtureSuite`` using the existing fixture harness model only.

Safety boundary (what this runner must never do): it runs no subprocess, makes
no network call, performs no RPC or fork-url or live-chain access, never compiles
or executes any fixture source, never broadcasts a transaction, never reads a
private key or seed phrase, and never automates an exploit. The only filesystem
access is an optional read-only text read of small fixture source files confined
to the local fixture-harness fixtures tree; a missing, oversized, non-UTF-8, or
unsafe path is handled neutrally and never raises. Importing this module has no
side effects.

These benchmarks are deterministic regression and review context only. A fixture
passing a benchmark never proves the source is safe, and a fixture failing a
benchmark never proves a vulnerability; no record asserts a confirmed
vulnerability, a final severity, an audit outcome, or bounty eligibility. Every
record keeps ``manual_review_required`` true and ``ready_for_submission`` false.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .fixtures import build_set1_fixture_suite, build_all_fixture_suite
from .ids import (
    fixture_artifact_id,
    fixture_id as _mint_fixture_id,
    fixture_result_id,
    fixture_run_id,
    normalize_fixture_path,
)
from .model import (
    FIXTURE_ARTIFACT_SOURCE,
    FIXTURE_RESULT_NEEDS_REVIEW,
    FIXTURE_RESULT_OBSERVED,
    FIXTURE_RUN_EXECUTED,
    FIXTURE_RUN_PARTIAL,
    FixtureArtifactRef,
    FixtureResult,
    FixtureRun,
    FixtureSuite,
    ProtocolFixture,
    build_fixture_suite,
    fixture_harness_to_dict,
)

# --- Runner constants -------------------------------------------------------

# Stable runner identity and benchmark seed version (no timestamp, no randomness).
_RUNNER_NAME = "fixture-harness-benchmark"
_BENCHMARK_VERSION = "v1"

# The runner only ever reads text confined to this local fixtures subtree, anchored
# at the repository root (two parents above this package). A path outside this
# subtree, or any unsafe path, is never read.
_SOURCE_READ_ROOT = "tests/fixtures/fixture_harness"

# A fixture source larger than this byte budget is treated as "not small" and is
# not read into memory (the benchmark stays neutral rather than loading big files).
_MAX_SOURCE_BYTES = 65536

# Required local/static disclaimer marker every fixture source is expected to carry.
_LOCAL_STATIC_MARKER = "local/static"

# Dangerous machine patterns a local/static fixture source must never contain.
# These are tokenized forms that only appear in genuinely unsafe content (real
# endpoints, secrets, broadcast cheatcodes) -- the runner must reject them. The
# required negated disclaimer words a fixture keeps on purpose ("no RPC", "no fork
# url", "no private keys", "no seed phrases", "no live chain") are deliberately
# NOT in this list and must never be flagged. Comparison is lowercase substring.
_DANGEROUS_PATTERNS: tuple[str, ...] = (
    "http://",
    "https://",
    "--rpc-url",
    "rpc-url",
    "rpc_url",
    "--fork-url",
    "fork-url",
    "fork_url",
    "privatekey",
    "private_key",
    "mnemonic",
    "seedphrase",
    "seed_phrase",
    "vm.broadcast",
    "vm.startbroadcast",
    "startbroadcast",
)

# Overclaim phrases that must never appear in serialized benchmark output. The
# token "HUMAN_REVIEWED" is checked case-sensitively (it is an uppercase status
# name); the rest are checked as lowercase substrings. None of these are emitted
# by the runner -- the scan asserts their absence as a review-context guarantee.
_OVERCLAIM_PHRASES: tuple[str, ...] = (
    "confirmed vulnerability",
    "final severity",
    "audit passed",
    "bounty eligible",
    "bounty eligibility",
    "proves safety",
    "proves a vulnerability",
    "proves vulnerability",
    "benchmark pass proves",
    "benchmark failure proves",
    "fixture pass proves",
    "fixture failure proves",
)
_HUMAN_REVIEWED_TOKEN = "HUMAN_REVIEWED"


# --- Pure helpers (no I/O) --------------------------------------------------

def _repo_root() -> Path:
    """Return the repository root (two parents above this package directory)."""

    return Path(__file__).resolve().parents[2]


def _safe_relative(path: str) -> str | None:
    """Return the normalized relative POSIX path, or ``None`` if it is unsafe.

    Never raises: a backslash, absolute, or ``..``-traversal path returns ``None``.
    An empty path also returns ``None`` (nothing to resolve).
    """

    try:
        normalized = normalize_fixture_path(path)
    except ValueError:
        return None
    return normalized or None


def _stable_json(value: object) -> str:
    """Return canonical JSON for a fixture-harness object (sorted keys, compact)."""

    return json.dumps(fixture_harness_to_dict(value), sort_keys=True, separators=(",", ":"))


def _scan_overclaim(blob: str) -> list[str]:
    """Return the sorted list of overclaim tokens found in a serialized blob."""

    found: set[str] = set()
    if _HUMAN_REVIEWED_TOKEN in blob:
        found.add(_HUMAN_REVIEWED_TOKEN)
    low = blob.lower()
    for phrase in _OVERCLAIM_PHRASES:
        if phrase in low:
            found.add(phrase)
    return sorted(found)


def _scan_dangerous(text: str) -> list[str]:
    """Return the sorted list of dangerous machine patterns found in source text."""

    low = text.lower()
    return sorted({pattern for pattern in _DANGEROUS_PATTERNS if pattern in low})


# --- Confined, read-only fixture source reader ------------------------------

def _resolve_source_path(relative_path: str) -> tuple[Path | None, str]:
    """Resolve a registered fixture source path under the local fixtures tree."""

    normalized = _safe_relative(relative_path)
    if normalized is None:
        return None, "unsafe_path"
    if not (normalized == _SOURCE_READ_ROOT or normalized.startswith(_SOURCE_READ_ROOT + "/")):
        return None, "outside_root"

    candidate = (_repo_root() / normalized).resolve()
    # Defense in depth: confirm the resolved path stays under the allowed root.
    allowed_root = (_repo_root() / _SOURCE_READ_ROOT).resolve()
    try:
        candidate.relative_to(allowed_root)
    except ValueError:
        return None, "outside_root"
    return candidate, "ok"


def _read_source_bytes(relative_path: str) -> tuple[bytes | None, str]:
    """Read a small registered fixture source as bytes, confined and read-only."""

    candidate, status = _resolve_source_path(relative_path)
    if candidate is None:
        return None, status

    try:
        if not candidate.is_file():
            return None, "missing"
        raw = candidate.read_bytes()
    except OSError:
        return None, "unreadable"
    if len(raw) > _MAX_SOURCE_BYTES:
        return None, "too_large"
    return raw, "ok"


def _read_source_text(relative_path: str) -> tuple[str | None, str]:
    """Read a small local fixture source, confined and read-only.

    Returns ``(text, status)``. ``status`` is ``"ok"`` on a successful read, or a
    neutral reason (``"unsafe_path"``, ``"outside_root"``, ``"missing"``,
    ``"too_large"``, ``"not_utf8"``, ``"unreadable"``) otherwise. Never raises,
    never executes, never runs a subprocess, and never touches the network. Only
    text under the local fixture-harness fixtures subtree can be read.
    """

    raw, status = _read_source_bytes(relative_path)
    if raw is None:
        return None, status
    try:
        return raw.decode("utf-8"), "ok"
    except UnicodeDecodeError:
        return None, "not_utf8"


# --- Result construction ----------------------------------------------------

def _result(
    run_id: str,
    fixture_id: str,
    result_kind: str,
    *,
    observed: object,
    subject_id: str = "",
    needs_review: bool = False,
    warnings: list[str] | None = None,
) -> FixtureResult:
    """Build a deterministic ``FixtureResult``.

    ``drift_detected`` is always false here: this runner records baseline
    observations only and performs no snapshot comparison (snapshot drift is a
    later agent's concern). A check that could not be evaluated is marked
    ``FIXTURE_RESULT_NEEDS_REVIEW`` rather than failed, keeping the output neutral.
    """

    subject = subject_id or fixture_id
    return FixtureResult(
        result_id=fixture_result_id(run_id, result_kind, subject),
        fixture_id=fixture_id,
        run_id=run_id,
        result_kind=result_kind,
        result_status=FIXTURE_RESULT_NEEDS_REVIEW if needs_review else FIXTURE_RESULT_OBSERVED,
        subject_id=subject,
        observed_value=observed,
        expected_value=None,
        drift_detected=False,
        warnings=sorted(set(warnings or [])),
        manual_review_required=True,
        ready_for_submission=False,
    )


def _benchmark_one(
    fixture: ProtocolFixture,
    artifact_refs: list[FixtureArtifactRef],
) -> tuple[FixtureRun, list[FixtureResult]]:
    """Benchmark a single fixture, returning its run and its result records.

    Reads the fixture's local source text (confined, read-only) at most once. Does
    not mutate ``fixture`` or any artifact reference. Deterministic across calls.
    """

    arts = [a for a in artifact_refs if a.fixture_id == fixture.fixture_id]
    input_artifact_ids = sorted(a.artifact_id for a in arts)
    run_id = fixture_run_id(
        fixture.fixture_id,
        _RUNNER_NAME,
        inputs={"benchmark_version": _BENCHMARK_VERSION, "artifact_ids": input_artifact_ids},
    )

    results: list[FixtureResult] = []

    # 1. Fixture ID deterministic (re-mint from name/category/relative_path).
    try:
        reminted = _mint_fixture_id(fixture.name, fixture.category, fixture.relative_path)
        id_stable = reminted == fixture.fixture_id
        id_warn: list[str] = [] if id_stable else ["fixture id is not re-mintable from its fields"]
        results.append(_result(run_id, fixture.fixture_id, "fixture_id_stable",
                               observed=id_stable, needs_review=not id_stable, warnings=id_warn))
    except ValueError:
        results.append(_result(run_id, fixture.fixture_id, "fixture_id_stable",
                               observed=False, needs_review=True,
                               warnings=["fixture id not recomputable: unsafe relative path"]))

    # 2. Fixture JSON serialization deterministic.
    json_stable = _stable_json(fixture) == _stable_json(fixture)
    results.append(_result(run_id, fixture.fixture_id, "fixture_json_stable",
                           observed=json_stable, needs_review=not json_stable))

    # 3. Fixture relative path safe and relative.
    path_ok = _safe_relative(fixture.relative_path) is not None
    results.append(_result(run_id, fixture.fixture_id, "fixture_relative_path_safe",
                           observed=path_ok, needs_review=not path_ok,
                           warnings=[] if path_ok else ["fixture relative path is unsafe or empty"]))

    # 4. Source files safe and relative.
    source_files = list(fixture.source_files or [])
    files_ok = bool(source_files) and all(_safe_relative(s) is not None for s in source_files)
    results.append(_result(run_id, fixture.fixture_id, "fixture_source_files_safe",
                           observed=files_ok, needs_review=not files_ok,
                           warnings=[] if files_ok else ["one or more source files are unsafe or absent"]))

    # 9-13. Safety-boundary flags (must all be true for a local/static fixture).
    boundary = fixture.safety_boundary
    for kind, flag in (
        ("safety_local_static_only", "local_static_only"),
        ("safety_no_rpc", "no_rpc"),
        ("safety_no_fork_url", "no_fork_url"),
        ("safety_no_private_keys", "no_private_keys"),
        ("safety_no_seed_phrases", "no_seed_phrases"),
    ):
        value = bool(getattr(boundary, flag, False))
        results.append(_result(run_id, fixture.fixture_id, kind,
                               observed=value, needs_review=not value,
                               warnings=[] if value else [f"safety flag {flag} is not true"]))

    # 14. manual_review_required true.
    mrr = fixture.manual_review_required is True
    results.append(_result(run_id, fixture.fixture_id, "manual_review_required",
                           observed=mrr, needs_review=not mrr,
                           warnings=[] if mrr else ["manual_review_required is not true"]))

    # 15. ready_for_submission false.
    rfs_ok = fixture.ready_for_submission is False
    results.append(_result(run_id, fixture.fixture_id, "ready_for_submission_false",
                           observed=rfs_ok, needs_review=not rfs_ok,
                           warnings=[] if rfs_ok else ["ready_for_submission is not false"]))

    # 16-24. Serialized fixture output carries no overclaim wording.
    fixture_overclaim = _scan_overclaim(_stable_json(fixture))
    results.append(_result(run_id, fixture.fixture_id, "fixture_serialized_no_overclaim",
                           observed=(not fixture_overclaim),
                           needs_review=bool(fixture_overclaim),
                           warnings=[f"overclaim token in serialized fixture: {t}" for t in fixture_overclaim]))

    # 5-7. Per-artifact: ref resolves, ID deterministic, JSON deterministic, no overclaim.
    for art in arts:
        results.append(_result(run_id, fixture.fixture_id, "artifact_ref_resolves",
                               subject_id=art.artifact_id,
                               observed=(art.fixture_id == fixture.fixture_id)))
        try:
            reminted_art = fixture_artifact_id(art.fixture_id, art.artifact_kind, art.relative_path)
            art_id_stable = reminted_art == art.artifact_id
            results.append(_result(run_id, fixture.fixture_id, "artifact_id_stable",
                                   subject_id=art.artifact_id, observed=art_id_stable,
                                   needs_review=not art_id_stable))
        except ValueError:
            results.append(_result(run_id, fixture.fixture_id, "artifact_id_stable",
                                   subject_id=art.artifact_id, observed=False, needs_review=True,
                                   warnings=["artifact id not recomputable: unsafe relative path"]))
        art_json_stable = _stable_json(art) == _stable_json(art)
        results.append(_result(run_id, fixture.fixture_id, "artifact_json_stable",
                               subject_id=art.artifact_id, observed=art_json_stable,
                               needs_review=not art_json_stable))
        art_overclaim = _scan_overclaim(_stable_json(art))
        results.append(_result(run_id, fixture.fixture_id, "artifact_serialized_no_overclaim",
                               subject_id=art.artifact_id, observed=(not art_overclaim),
                               needs_review=bool(art_overclaim),
                               warnings=[f"overclaim token in serialized artifact: {t}" for t in art_overclaim]))

    # 8 + source-text checks. Read the local source once, confined and read-only.
    text, status = _read_source_text(fixture.relative_path)
    source_present = status == "ok"
    results.append(_result(run_id, fixture.fixture_id, "artifact_source_present",
                           observed=source_present, needs_review=not source_present,
                           warnings=[] if source_present else [f"source not readable: {status}"]))
    if text is not None:
        results.append(_result(run_id, fixture.fixture_id, "source_text_utf8", observed=True))
        results.append(_result(run_id, fixture.fixture_id, "source_text_small", observed=True))
        has_marker = _LOCAL_STATIC_MARKER in text.lower()
        results.append(_result(run_id, fixture.fixture_id, "source_text_local_static_wording",
                               observed=has_marker, needs_review=not has_marker,
                               warnings=[] if has_marker else ["source is missing the local/static disclaimer"]))
        dangerous = _scan_dangerous(text)
        results.append(_result(run_id, fixture.fixture_id, "source_text_no_dangerous_patterns",
                               observed=(not dangerous), needs_review=bool(dangerous),
                               warnings=[f"dangerous pattern in source: {p}" for p in dangerous]))
    else:
        for kind in ("source_text_utf8", "source_text_small",
                     "source_text_local_static_wording", "source_text_no_dangerous_patterns"):
            results.append(_result(run_id, fixture.fixture_id, kind, observed=None,
                                   needs_review=True, warnings=[f"source not evaluated: {status}"]))

    needs_review_count = sum(1 for r in results if r.result_status == FIXTURE_RESULT_NEEDS_REVIEW)
    run_warnings = sorted({w for r in results for w in r.warnings})
    run = FixtureRun(
        run_id=run_id,
        fixture_id=fixture.fixture_id,
        runner=_RUNNER_NAME,
        command_label="local/static deterministic fixture benchmark (no Foundry, no RPC, no network, no subprocess)",
        input_artifact_ids=input_artifact_ids,
        output_artifact_ids=[],
        run_status=FIXTURE_RUN_PARTIAL if needs_review_count else FIXTURE_RUN_EXECUTED,
        benchmark_dimensions=list(fixture.benchmark_dimensions or []),
        warnings=run_warnings,
        manual_review_required=True,
        ready_for_submission=False,
        metadata={
            "benchmark_version": _BENCHMARK_VERSION,
            "result_count": len(results),
            "needs_review_count": needs_review_count,
            "artifact_count": len(arts),
        },
    )
    return run, results


# --- Public helpers ---------------------------------------------------------

def build_fixture_source_fingerprints(suite: FixtureSuite) -> list[FixtureArtifactRef]:
    """Return fingerprinted source artifact refs for registered fixture sources.

    This is an opt-in hardening helper: it reads only source paths already
    registered on fixtures in ``suite`` and only when those paths are safe,
    relative paths under ``tests/fixtures/fixture_harness/``. It computes
    deterministic SHA-256 checksums and byte sizes from local fixture source
    files. It does not mutate the input suite, reads no path outside the fixture
    tree, runs no subprocess, touches no network, performs no RPC or live-chain
    access, and serializes no absolute host paths.
    """

    existing: dict[tuple[str, str], FixtureArtifactRef] = {}
    for art in suite.artifact_refs:
        normalized = _safe_relative(art.relative_path)
        if normalized:
            existing[(art.fixture_id, normalized)] = art

    planned: list[tuple[str, str]] = []
    fixture_by_id = {fixture.fixture_id: fixture for fixture in suite.fixtures}
    for fixture in suite.fixtures:
        source_paths = list(fixture.source_files or [])
        if not source_paths and fixture.relative_path:
            source_paths = [fixture.relative_path]
        for source_path in source_paths:
            normalized = _safe_relative(source_path)
            if not normalized:
                continue
            if not normalized.startswith(_SOURCE_READ_ROOT + "/"):
                continue
            planned.append((fixture.fixture_id, normalized))

    artifacts: list[FixtureArtifactRef] = []
    for fixture_id_value, relative_path in sorted(set(planned)):
        if fixture_id_value not in fixture_by_id:
            continue
        base = existing.get((fixture_id_value, relative_path))
        artifact_id = (
            base.artifact_id
            if base is not None
            else fixture_artifact_id(fixture_id_value, FIXTURE_ARTIFACT_SOURCE, relative_path)
        )
        raw, status = _read_source_bytes(relative_path)
        warnings = list(base.warnings if base is not None else [])
        checksum = ""
        size = 0
        if raw is None:
            warnings.append(f"source fingerprint unavailable: {status}")
        else:
            checksum = hashlib.sha256(raw).hexdigest()
            size = len(raw)
        artifacts.append(FixtureArtifactRef(
            artifact_id=artifact_id,
            fixture_id=fixture_id_value,
            artifact_kind=FIXTURE_ARTIFACT_SOURCE,
            relative_path=relative_path,
            checksum_sha256=checksum,
            size_bytes=size,
            linked_ids=list(base.linked_ids if base is not None else []),
            warnings=sorted(set(warnings)),
            manual_review_required=True,
            ready_for_submission=False,
            metadata=dict(base.metadata if base is not None else {}),
        ))
    return artifacts


def run_fixture_benchmark(
    fixture: ProtocolFixture,
    artifact_refs: list[FixtureArtifactRef] | None = None,
) -> FixtureRun:
    """Benchmark one fixture and return its deterministic ``FixtureRun``.

    ``artifact_refs`` is the optional list of artifact references for the fixture
    (only those whose ``fixture_id`` matches are used). The input fixture and its
    artifacts are never mutated. Returns the run record only; use
    :func:`run_fixture_benchmark_suite` to also collect per-check results.
    """

    run, _results = _benchmark_one(fixture, list(artifact_refs or []))
    return run


def run_fixture_benchmark_suite(suite: FixtureSuite) -> FixtureSuite:
    """Benchmark every fixture in ``suite`` and return a new rolled-up suite.

    The returned suite preserves the input suite's name, fixtures, and artifact
    references, attaches the benchmark runs and results, and carries no snapshots.
    The suite ID is unchanged (it derives from the name and fixture IDs). The input
    suite is not mutated. Deterministic across calls.
    """

    runs: list[FixtureRun] = []
    results: list[FixtureResult] = []
    for fixture in suite.fixtures:
        run, fixture_results = _benchmark_one(fixture, list(suite.artifact_refs))
        runs.append(run)
        results.extend(fixture_results)
    return build_fixture_suite(
        suite.name,
        fixtures=list(suite.fixtures),
        artifact_refs=list(suite.artifact_refs),
        runs=runs,
        results=results,
        snapshots=[],
    )


def benchmark_set1_fixture_suite() -> FixtureSuite:
    """Build and benchmark the Set 1 fixture suite (deterministic, local/static)."""

    return run_fixture_benchmark_suite(build_set1_fixture_suite())


def benchmark_all_fixture_suite() -> FixtureSuite:
    """Build and benchmark the combined all-fixtures suite (Set 1 + 2 + 3).

    Deterministic and local/static: it benchmarks all nine registered fixtures and
    rolls the runs and results into one suite with no snapshots. The combined
    result count is strictly greater than the Set 1-only result count.
    """

    return run_fixture_benchmark_suite(build_all_fixture_suite())

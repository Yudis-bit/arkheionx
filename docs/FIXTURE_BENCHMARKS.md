# Fixture Benchmarks (v3.9)

The fixture benchmark runner (`arkheionx/fixture_harness/runner.py`) records
deterministic, review-surface observations about each registered fixture and its
artifact references. It is local/static regression and review context only.

See `docs/FIXTURE_HARNESS.md` for the harness model and
`docs/FIXTURE_SNAPSHOT_WORKFLOW.md` for snapshot baselines.

## Helpers

- `run_fixture_benchmark(fixture, artifact_refs=None)` — benchmarks one fixture and
  returns its run record.
- `run_fixture_benchmark_suite(suite)` — benchmarks every fixture in a suite and
  returns a new suite carrying the runs and results (no snapshots).
- `benchmark_set1_fixture_suite()` — benchmarks the Set 1 suite.
- `benchmark_all_fixture_suite()` — benchmarks the combined all-fixtures suite.
- `build_fixture_source_fingerprints(suite)` — returns fingerprinted source
  artifact refs for registered fixture source files only.

```python
import arkheionx.fixture_harness as fh

suite = fh.benchmark_all_fixture_suite()
suite.fixture_count   # 9
suite.run_count       # 9
suite.result_count    # 189
suite.drift_count     # 0

fingerprints = fh.build_fixture_source_fingerprints(fh.build_all_fixture_suite())
fingerprints[0].checksum_sha256  # deterministic SHA-256 of a local fixture source
fingerprints[0].size_bytes       # source size in bytes
```

## Per-fixture benchmark checks

For each fixture the runner records deterministic observations as fixture results:

- Fixture ID re-mint stability and JSON-serialization stability.
- Fixture relative-path safety and source-file path safety.
- Per artifact: reference resolution, ID re-mint stability, JSON stability, and a
  no-overclaim scan of the serialized artifact.
- The safety-boundary flags (local/static-only, no RPC, no fork-url, no private
  keys, no seed phrases).
- `manual_review_required` true and `ready_for_submission` false.
- A no-overclaim scan of the serialized fixture.
- Confined source-text checks: the source is present, UTF-8, small, carries the
  local/static disclaimer, and contains none of the dangerous machine patterns
  (real endpoints, secret forms, or broadcast cheatcodes).

A check that evaluates cleanly is recorded as an observed result; a check that
cannot be evaluated (for example an unreadable source) is recorded as
needs-review, never as drift. A run whose checks all evaluate cleanly is reported
as executed; otherwise it is reported as partial. For the bundled fixtures every
run is executed and every result is observed.

## Source reading is confined and read-only

The runner's only filesystem access is an optional read-only text read of small
fixture sources under the local fixtures tree. A path that is unsafe (a backslash,
an absolute path, or a parent-traversal segment), that resolves outside the
fixtures tree, that is missing, that is oversized, or that is not UTF-8 is handled
neutrally and never raises and never reads outside the tree. The runner runs no
subprocess, makes no network call, performs no RPC, fork-url, or live-chain access,
invokes no Foundry tool, and never compiles or executes a source.

The fingerprint helper uses the same confinement boundary. It reads only source
paths registered on fixtures in the provided suite, only when those paths are
relative paths under `tests/fixtures/fixture_harness/`, and emits repo-relative
paths only. It does not alter the suite or committed snapshot baselines.

## All-fixtures suite

`benchmark_all_fixture_suite()` benchmarks all nine fixtures (Set 1, Set 2, Set 3)
in a fixed order. The combined result count is strictly greater than the Set 1-only
result count. The combined suite ID is deterministic and order-independent, and it
is distinct from each per-set suite ID.

## Crossrefs

`crossref.py` links a benchmarked suite to the wider Arkheionx evidence graph by ID
only:

```python
import arkheionx.fixture_harness as fh

fh.build_set1_fixture_crossref()
fh.build_all_fixture_crossref()
```

A crossref records the suite ID, the counts, the sorted fixture / artifact /
benchmark-result IDs, the review-state booleans, three context-availability flags
(review package, local validation, evidence — detected without importing those
modules), and an explicit no-overclaim context block. It is standalone and edits
none of those subsystems.

## Determinism

Run IDs derive from the fixture ID, the fixed runner name, and a canonical inputs
seed; result IDs derive from the run ID, the check kind, and the subject ID. No ID,
run, result, or crossref uses a timestamp, randomness, or process `hash()`.
Repeated benchmarks produce byte-identical canonical JSON.

## What a benchmark does not mean

A benchmark is not an audit and not a submission, and it does not confirm
vulnerabilities. A benchmark passing never proves the source is safe, and a
benchmark failing never proves a vulnerability. Manual review remains required, and
`ready_for_submission` stays false on every run, result, suite, and crossref.

# Fixture Snapshot Workflow (v3.9)

A benchmark snapshot (`arkheionx/fixture_harness/snapshots.py`) is a small, plain,
deterministic summary of a benchmarked fixture suite. Committed baselines let a
later change be diffed against a known-good summary so unintended drift is caught
in review. Snapshots are regression and review context only.

See `docs/FIXTURE_HARNESS.md` and `docs/FIXTURE_BENCHMARKS.md` for the harness and
the runner.

## What a snapshot contains

- `snapshot_schema_version`, `fixture_suite_name`, and `fixture_suite_id`.
- `fixture_count`, `artifact_count`, `result_count`, and `drift_count`.
- Sorted `fixture_ids`, `artifact_ids`, and `result_ids`.
- The union of `benchmark_dimensions` and `expected_artifact_kinds`.
- The aggregated `safety_flags`.
- `manual_review_required` true and `ready_for_submission` false.
- A neutral notice.

A snapshot never contains an absolute path, a username, a hostname, a temporary
path, a dynamic timestamp, a private value, an RPC or fork URL, an automatic
reviewed-status token, or any confirmed-vulnerability, final-severity, audit,
safety, or bounty claim.

## Helpers

- `build_set1_benchmark_snapshot()` / `build_all_benchmark_snapshot()` — build a
  snapshot from the benchmarked Set 1 or combined suite.
- `load_set1_benchmark_snapshot()` / `load_all_benchmark_snapshot()` — read the
  committed baseline JSON (read-only).
- `compare_set1_benchmark_snapshot(observed=None, baseline=None)` /
  `compare_all_benchmark_snapshot(...)` — diff an observed snapshot against a
  baseline and report drift.
- `snapshot_to_jsonable(snapshot)` — return a plain JSON-safe form.

## Committed baselines

- Set 1: `tests/fixtures/fixture_harness/snapshots/set1/benchmark_snapshot.json`.
- All fixtures: `tests/fixtures/fixture_harness/snapshots/all/benchmark_snapshot.json`.

Both are checked by tests: the generated snapshot must equal the committed
baseline.

## Comparing and reading drift

```python
import arkheionx.fixture_harness as fh

result = fh.compare_all_benchmark_snapshot()
result["matches"]       # True when the build matches the committed baseline
result["drift_count"]   # number of differing top-level fields
result["differences"]   # sorted list of {field, expected, observed}
```

Drift is reported field by field; it is review context only. Drift never asserts a
vulnerability and a match never asserts safety.

## Snapshot update workflow

When a change to the harness, the registries, or the runner intentionally changes a
benchmarked summary, the comparison will report drift and the
generated-equals-committed tests will fail until the committed baseline is
regenerated. To update a baseline after an intentional, reviewed change:

1. Confirm the change is intended and review the reported `differences`.
2. Regenerate the committed baseline from the build output, for example:

   ```sh
   python3 - <<'PY'
   import json, pathlib
   from arkheionx.fixture_harness import snapshots as s
   for build, relpath in (
       (s.build_set1_benchmark_snapshot, s.SET1_SNAPSHOT_RELPATH),
       (s.build_all_benchmark_snapshot, s.ALL_SNAPSHOT_RELPATH),
   ):
       pathlib.Path(relpath).write_text(
           json.dumps(build(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
   PY
   ```

3. Re-run the fixture-harness tests and review the committed baseline diff before
   committing it.

Regenerating a baseline is a deliberate, human-reviewed step; the baseline is never
regenerated automatically as part of a normal run.

## Deferred to v4.0

Snapshot governance beyond exact-match baselines — for example tolerances,
per-dimension snapshots, or a snapshot-update helper command — is out of scope for
v3.9 and tracked as v4.0 planning, not current runtime capability.

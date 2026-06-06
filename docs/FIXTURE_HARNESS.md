# Fixture Harness (v3.9)

The fixture harness is an internal, local/static layer
(`arkheionx/fixture_harness/`) that gives Arkheionx a small set of realistic,
deterministic protocol "shapes" to run its review and benchmark machinery over. It
exists so the Protocol Intelligence Core's IDs, counts, and outputs stay stable and
reviewable across releases.

It is internal infrastructure: it adds no public CLI command, changes no public
artifact schema, and is not a public API. It is additive and import side-effect
free.

## What the harness is

- A controlled vocabulary and a set of pure dataclasses (`model.py`): a protocol
  fixture, a fixture artifact reference, a fixture run, a fixture result, a fixture
  snapshot reference, and a fixture suite.
- Deterministic ID and path utilities (`ids.py`).
- Three registries of small local/static illustrative source fixtures
  (`fixtures.py`): Set 1, Set 2, and Set 3.
- A benchmark runner (`runner.py`) — see `docs/FIXTURE_BENCHMARKS.md`.
- Snapshot baselines (`snapshots.py`) — see `docs/FIXTURE_SNAPSHOT_WORKFLOW.md`.
- A standalone crossref module (`crossref.py`).

## Fixture IDs

Every fixture, artifact, run, result, snapshot, and suite carries a deterministic,
prefix-tagged ID minted from a canonical JSON seed (sorted keys, compact
separators) hashed with SHA-256, plus a human-readable prefix:

- `fixture:<category>:<name>:<12hex>`
- `fixture-artifact:<kind>:<12hex>`
- `fixture-run:<runner>:<12hex>`
- `fixture-result:<kind>:<12hex>`
- `fixture-suite:<name>:<12hex>`

IDs never use a timestamp, randomness, or process `hash()`; identical inputs always
produce the same ID across runs, and suite IDs are order-independent (they hash the
sorted fixture IDs).

## Artifacts, runs, and results

- A fixture artifact reference records a source file by relative path and kind
  (for example a source artifact). Registry helpers stay pure and leave checksums
  and sizes empty at registration; `build_fixture_source_fingerprints(suite)` can
  opt in to read only registered local fixture sources and return fingerprinted
  source artifact refs with SHA-256 checksums and byte sizes.
- A fixture run records that the benchmark machinery ran over a fixture: the runner
  name, a neutral command label, the input artifact IDs, the run status, and merged
  warnings.
- A fixture result records one deterministic observation per benchmark check (ID
  stability, JSON stability, path safety, the safety-boundary flags, a no-overclaim
  scan, and the confined source-text checks).

## The three fixture sets

Each set has three tiny local/static illustrative Solidity-like source files under
`tests/fixtures/fixture_harness/`:

- Set 1 (`set1/`): an ERC20-like token, a lending vault, and a staking/reward
  shape.
- Set 2 (`set2/`): an AMM/swap shape, an oracle-dependent vault shape, and an
  upgradeable proxy shape.
- Set 3 (`set3/`): a bridge/message shape, a liquidation/borrow-repay shape, and a
  governance/timelock shape.

Nine fixtures in total. Their IDs are disjoint across sets, and a combined
all-fixtures suite composes them in the fixed order Set 1, Set 2, Set 3.

## What the harness does not do

- It does not perform any RPC, fork-url, live-chain, or network access.
- It uses no private keys and no seed phrases.
- It does not broadcast transactions and automates no exploit.
- It does not compile or execute the fixture sources; they are read as static
  text only, and only from within the local fixtures tree.
- It asserts no confirmed vulnerability, no final severity, no audit outcome, and
  no bounty eligibility.

A fixture passing the harness never proves the source is safe, and a fixture
failing the harness never proves the source has a vulnerability. Manual review
remains required, and `ready_for_submission` stays false on every record.

## Developer commands

The harness is exercised from Python (there is no CLI surface):

```python
import arkheionx.fixture_harness as fh

# Registries (no I/O):
fh.set1_fixture_definitions()      # 3 fixtures
fh.set2_fixture_definitions()      # 3 fixtures
fh.set3_fixture_definitions()      # 3 fixtures
fh.all_fixture_definitions()       # 9 fixtures, set order set1, set2, set3

# Suites:
fh.build_set1_fixture_suite()
fh.build_all_fixture_suite()

# Opt-in source fingerprints (confined read-only source reads):
fh.build_fixture_source_fingerprints(fh.build_all_fixture_suite())

# JSON-safe serialization of any harness object:
import json
json.dumps(fh.fixture_harness_to_dict(fh.build_all_fixture_suite()))
```

The test suites `tests/test_fixture_harness_*.py` cover the model, IDs, registries,
runner, snapshots, all-fixtures integration, and crossrefs. Run them with
`python3 -m unittest discover -s tests -p "test_fixture_harness_*.py"`.

## Deferred to v4.0

Additional fixture categories and any public surface for the harness are out of
scope for v3.9 and tracked as v4.0 planning, not current runtime capability.

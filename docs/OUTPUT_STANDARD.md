# Arkheionx Output Standard

The workbench commands share one output contract so results stay clean,
consistent, and easy to read. Arkheionx draws the protocol for you; it does not
dump raw Foundry noise.

## Terminal

Every command prints a stable header:

```text
ARKHEIONX <COMMAND>
Target: <path>
Mode: <heuristic | compiler | execution | report-ready>
Status: <ok | warning | error>
```

`map` then prints the full section set:

1. Protocol Snapshot
2. User Journey
3. Money Flow
4. Contract Roles (table)
5. Function Risk Map (table)
6. Top Hunter Targets
7. Suggested Tests
8. Artifacts
9. Limitations
10. Recommended Next Command

`flow`, `hunt`, and `prove` print focused views of the same data with the same
header, an Artifacts block, a Limitations block, and a Recommended Next Command.

Default terminal output is concise. Detailed output is written to artifact
files and shown on stdout only with `--json`, `--markdown`, `--mermaid`, or
`--verbose`.

## Evidence Levels

Every major result carries one label:

- `HEURISTIC` — static scan, names, modifiers, external-call terms.
- `COMPILER_CONFIRMED` — confirmed by `forge build` / compiled artifacts.
- `EXECUTION_CONFIRMED` — confirmed by running Foundry tests or traces.
- `REPORT_READY` — enough structured evidence for a researcher to write a report.

Heuristic guesses are never presented as proof.

## JSON

Stable top-level keys:

```text
meta, protocol_snapshot, user_journeys, money_flow, contracts, functions,
value_hotspots, hunter_targets, suggested_tests, invariants, foundry,
artifacts, limitations, next_commands
```

Schemas live under [`../schemas`](../schemas):

- [`protocol-map.schema.json`](../schemas/protocol-map.schema.json)
- [`value-flow.schema.json`](../schemas/value-flow.schema.json)
- [`hunt-report.schema.json`](../schemas/hunt-report.schema.json)
- [`proof-artifact.schema.json`](../schemas/proof-artifact.schema.json)

## Mermaid

`flow` emits a simple `flowchart LR` with sanitized node ids and escaped
labels, so generated graphs never break Mermaid parsing.

## Artifacts

Artifacts are developer-tool style (JSON + Mermaid + proof text), not
report-first Markdown. They are written under `.arkheionx/out/` (relative to
the chosen base directory, default: current working directory):

```text
.arkheionx/out/
  map.json
  flow.json
  hunt.json
  money-flow.mmd
  proof/<target>/
    proof.json
    generated-test.sol
    foundry-build.txt
  evidence/<target>/
    evidence.json
    evidence.txt
  reports/<target>/
    report.json
    report.md
```

Overwrites are allowed only inside `.arkheionx/out/` and are deterministic.
This directory is gitignored. Pass `--no-artifacts` to skip writing entirely.

## Flags

- `--full` — detailed terminal output (tables, all edges).
- `--show-all` — include interfaces/tests/invariants/mocks/fixtures hidden by default.
- `--json` — print machine-readable JSON to stdout.
- `--mermaid` — (flow) print the Mermaid graph to stdout.
- `--build` — run `forge build` for compiler-confirmed evidence.
- `--no-artifacts` — do not write artifact files.
- `--top N` — number of top targets.

## Exit codes

- `0` — ok (compiler-confirmed or execution-confirmed).
- `1` — heuristic-only / usable warning (e.g. Foundry not used; a scaffold was
  generated but not proven).
- `2` — failure (bad path, missing/ambiguous target, cannot complete).
- `doctor` returns `0` whenever the tool is usable; `2` only if the package
  itself is broken.

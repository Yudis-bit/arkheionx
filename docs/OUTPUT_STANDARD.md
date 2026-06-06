# Arkheionx Output Standard

The workbench commands share one output contract so results stay clean,
consistent, and easy to read. Arkheionx draws the protocol for you; it does not
dump raw Foundry noise.

## Terminal

Every command prints a stable header:

```text
ARKHEIONX <COMMAND>
Target: <path>
Mode: <heuristic | compiler | execution | evidence-ready>
Status: <ok | warning | error>
```

Human-facing terminal output uses restrained color (bold headings; green/yellow/
red statuses; evidence levels colored by level) when stdout is a TTY. Color is
disabled automatically for pipes, captured output, and CI, and is never applied
to JSON output or to artifact files written under `.arkheionx/out/`. Control it
with `ARKHEIONX_COLOR=always|never|auto` or `NO_COLOR`.

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
- `EVIDENCE_READY` — proof and trace artifacts are packaged for review.
- `HUMAN_REVIEWED` — explicit human reviewer attestation only; local tooling does
  not emit this automatically.

`REPORT_READY` is legacy protocol-era terminology for the same support level as
`EVIDENCE_READY`. It may still appear in older schema contracts or compatibility
contexts, but `EVIDENCE_READY` is the current canonical evidence package term.
No schema or validator migration is introduced in v3.2.0.

Heuristic guesses are never presented as proof. Review priority is review order,
not severity. Confidence, evidence level, validation status, and release
readiness are separate concepts and should not be collapsed into a vulnerability
confirmation.

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
- [`review-map.schema.json`](../schemas/review-map.schema.json)

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
  review-map/
    review-map.json
    review-map.md
    value-paths.json
    test-gaps.json
    assumptions.json
    proof-plan.json
    evidence-links.json
    review-summary.md
    review-map.mmd
    test-gap-map.json
    test-gap-map.md
  artifacts-index.json
```

Overwrites are allowed only inside `.arkheionx/out/` and are deterministic.
This directory is generated local state, gitignored by default, and not intended
to be committed in v3.2.0. Pass `--no-artifacts` to skip writing entirely.

## Flags

- `--full` — detailed terminal output (tables, all edges).
- `--show-all` — include interfaces/tests/invariants/mocks/fixtures hidden by default.
- `--json` — print machine-readable JSON to stdout.
- `--mermaid` — (flow) print the Mermaid graph to stdout.
- `--build` — run `forge build` for compiler-confirmed evidence.
- `--no-artifacts` — do not write artifact files.
- `--top N` — number of top targets.

## Exit codes

- `0` — ok / clean validation.
- `1` — attention needed: heuristic-only review guidance, incomplete evidence,
  or `validate-artifacts` validation issues. This is not a crash.
- `2` — command/input failure (bad path, missing/ambiguous target, cannot
  complete).
- `3` — safety rejection for config validation.
- `doctor` returns `0` whenever the tool is usable; `2` only if the package
  itself is broken.

`validate-artifacts` does not get a dedicated artifact-validation failure code
in v3.2.0. Strict CI should use `validate-artifacts --json` and fail on
`status != "ok"` until a future strict mode or dedicated code is introduced.

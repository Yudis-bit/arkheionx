# V7.5 — Protocol Lens Packs

Protocol Lens Packs turn a general Solidity repository review into a
**protocol-aware** research workflow. Where v4 maps value flow, v5 prioritizes
blind spots, v6 classifies evidence, and v7 turns a scope note into review lanes
and tasks, **v7.5 adds a protocol lens**: a model of a specific protocol family —
its value flows, behavior promises, economic invariants, temporal windows, and
periphery composition — that the existing engines bind to your local repository.

> Arkheionx protocol lenses help structure research.
> They do not confirm vulnerabilities.
> They do not replace audits.
> They do not run on live chains.
> They do not auto-submit reports.

V7.5 ships in the **v7.5.0** package. The package version is `7.5.0`; the protocol
lens layer additionally carries its own lens schema version for its JSON artifacts. Nothing in
the v4 review-map workflow or the v5/v6/v7 commands changes.

## What a protocol lens is

A protocol lens is declarative, local/static protocol knowledge:

- **Extraction groups** — the terms, function names, and state variables that
  locate the protocol in a repository.
- **Behavior promises** — the properties the protocol is expected to keep.
- **Economic invariants** — the value-conservation properties to preserve.
- **Temporal windows** — the moments where intermediate state can be observed.
- **Review lanes** — the canonical research tracks for the protocol family.

A lens encodes no line numbers and no specific known bug. It is a model, not a
finding. The first implemented lens is
[Fixed Credit Market](FIXED_CREDIT_MARKET_LENS.md) (`fixed-credit-market`). The architecture
supports future lenses (kiln-omnivault, silo-v2, veda, generic-erc4626,
generic-lending); none of those are implemented yet.

## Commands

All commands are local/static. They never call RPC, never run a live chain, and
never run `forge`.

```bash
# List implemented (and planned) lenses
arkheionx lens-list

# Protocol-aware map: protocol model + scope + behavior promises + invariants
arkheionx lens-map . --lens fixed-credit-market --scope-file scope.md

# Review lanes (review order, never severity)
arkheionx lens-lanes . --lens fixed-credit-market --scope-file scope.md

# Precise, bounded, evidence-oriented scope tasks
arkheionx lens-tasks . --lens fixed-credit-market --scope-file scope.md

# A complete local lens pack (writes by default)
arkheionx lens-pack . --lens fixed-credit-market --scope-file scope.md --out .arkheionx/lens-pack

# Classify local-test evidence per economic invariant
arkheionx lens-evidence . --lens fixed-credit-market --scope-file scope.md

# Classify report candidates before submission (not final triage)
arkheionx lens-report-filter . --lens fixed-credit-market --scope-file scope.md
```

Every command accepts `--lens` (default `fixed-credit-market`), `--scope-file`,
`--out`, `--top`, `--json`, and `--no-write`.

## What `lens-pack` generates

`lens-pack` writes a per-lens directory (e.g. `.arkheionx/lens-pack/fixed-credit-market/`)
containing human-readable Markdown and one machine-readable JSON:

```text
00-run-context.md         Lens, repo, families, scope status
01-scope-map.md           Scope turned into structured rules
02-protocol-model.md      Discovered terms/functions; UNKNOWN_IN_LOCAL_REPO markers
03-value-flow-map.md      Lend / borrow / settle / bundle / liquidate paths
04-behavior-promises.md   The behavior promises with evidence placeholders
05-economic-invariants.md The economic invariants with math forms
06-temporal-windows.md    Where intermediate state can be observed
07-periphery-bundle-map.md Periphery functions and cap/target dimensions
08-evidence-map.md        Evidence status per invariant
09-review-lanes.md        Review lanes (review order, not severity)
10-scope-tasks.md         Precise, bounded, testable tasks per lane
11-blindspot-ranking.md   Top blind spots (places to look, not bugs)
12-evidence-rubric.md     How evidence is graded (A-F) and decided
13-report-filter.md       Candidate classification before submission
agent-input.md            Model-agnostic instructions for an AI agent
lens-pack.json            All structured data for an AI agent
```

## What the outputs mean — and do not mean

- A **lens** is a model of a protocol, not a finding.
- A **review lane** is a research track, not a vulnerability; lane priority is
  review order, not severity.
- An **evidence status** describes local test coverage, not vulnerability
  validity.
- A **blind spot** is a place to look, not a confirmed bug.
- A **VALIDATED_CANDIDATE** is a human judgment requiring a local proof-of-concept;
  the static judge never auto-confirms a vulnerability.
- A **report-filter outcome** is not final triage. The filter never says "submit
  now"; the most positive outcome is `READY_FOR_HUMAN_REVIEW`, and a human still
  decides.

## Exit codes and CI

Arkheionx analysis commands may return exit code 1 when the result is heuristic and
requires human review. This is a warning-style exit code, not necessarily a runtime
failure. `lens-list` returns `0`; the analysis commands (`lens-map`, `lens-lanes`,
`lens-tasks`, `lens-pack`, `lens-evidence`, `lens-report-filter`) return `1` whenever
they emit a heuristic, human-review-required result — which is the normal case — and
`2` only on invalid usage or a genuine runtime error. In CI, drive the commands with
`--json` and inspect the decision fields (for example the `report_filter` outcomes,
the `evidence_judge` grades, or `human_review_required`) instead of treating every
non-zero analysis exit as a crash. A robust pattern is to capture stdout, parse the
JSON, and gate on the fields you care about while tolerating exit code `1`. The CLI
intentionally does not ship an `--exit-zero-on-warning` flag in this release, so that
the heuristic-warning signal stays stable; parse the JSON instead.

## Using it with Foundry

1. Run `lens-pack` and read `01-scope-map.md` and `09-review-lanes.md` first.
2. Give `agent-input.md` plus `10-scope-tasks.md` to a reviewer or AI agent.
3. For each task, write a **local** Foundry test that reproduces the failure
   condition. Arkheionx does not run `forge`; you run it locally.
4. Run `arkheionx lens-evidence` to classify what your tests cover.
5. Run `arkheionx lens-report-filter` to classify candidates before any human
   review. A human makes the final call.

## Keeping private scope local

Keep a private contest scope under `.arkheionx/private/` (gitignored). Generated
output belongs under `.arkheionx/` (also gitignored). If you point `--out` at a
public path, `lens-pack` prints a warning; if the scope note itself is private,
the warning is stronger. Never commit private scope or scope-derived artifacts.
See [SCOPE_ORCHESTRATION.md](SCOPE_ORCHESTRATION.md) for the shared scope and
leak-guard model.

## Related

- [Fixed Credit Market lens](FIXED_CREDIT_MARKET_LENS.md)
- [Scope-aware orchestration (v7)](SCOPE_ORCHESTRATION.md)
- [Evidence judge](EVIDENCE_JUDGE.md)
- [Report filter](REPORT_FILTER.md)
- [V7 workflow](V7_WORKFLOW.md)

Local/static only. Not a finding, not severity, not a confirmed vulnerability.
Human review is required.

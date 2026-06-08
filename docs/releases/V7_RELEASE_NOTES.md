# Arkheionx v7.0.0 — Scope-Aware Orchestration

**Release title:** Arkheionx v7.0.0 — Scope-Aware Orchestration

**Summary:** V7 adds scope-aware orchestration: scope map, review lanes, scope
tasks, evidence judging, report filtering, and complete scope packs for
local/static, human-reviewed smart-contract security research.

Release metadata is finalized locally and is pending the founder's push, tag,
GitHub release, and site deploy. The package version is `7.0.0`; the last published
tag remains `v4.0.0`.

## New commands

| Command | Purpose |
| --- | --- |
| `arkheionx scope-map` | Parse a scope note into structured review rules |
| `arkheionx scope-lanes` | Generate scope-aware review lanes |
| `arkheionx scope-tasks` | Turn lanes into precise, testable tasks |
| `arkheionx scope-pack` | Bundle a complete local scope-aware research pack |
| `arkheionx evidence-judge` | Grade whether local tests prove the intended task |
| `arkheionx report-filter` | Classify candidates against scope before submission |

## Positioning

V7 turns audit scope into review lanes, task packs, evidence requirements, and
report filters so AI-assisted security review starts from rules and evidence
instead of vague prompts.

## Known limitations

Local/static and heuristic. No bug prediction. No severity. No exploit automation.
No live-chain or RPC. No auto-submission. Human review is required. Private scope
files are local only and must not be committed.

## Docs

- [`SCOPE_ORCHESTRATION.md`](../SCOPE_ORCHESTRATION.md)
- [`V7_WORKFLOW.md`](../V7_WORKFLOW.md)
- [`SCOPE_MAP.md`](../SCOPE_MAP.md)
- [`SCOPE_TASKS.md`](../SCOPE_TASKS.md)
- [`EVIDENCE_JUDGE.md`](../EVIDENCE_JUDGE.md)
- [`REPORT_FILTER.md`](../REPORT_FILTER.md)

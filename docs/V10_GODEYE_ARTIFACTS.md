# V10 GodEye War Engine — Artifacts (private, internal)

`arkheionx war-run <target> --scope scope.yaml --out <dir>` writes the following
under the output directory (default `<target>/.arkheionx/war-run/`). All artifacts
are local; nothing is pushed or submitted; no report is generated.

| Artifact | Format | Produced by | Contents |
| --- | --- | --- | --- |
| `01-scope-map.md` | Markdown | warrun | Program, chain, in/out-of-scope, rules, indexed contracts |
| `02-semantic-map.json` | JSON | semantic | Full semantic map (contracts, functions, calls, storage, data flow) |
| `02-semantic-map.md` | Markdown | semantic | Human summary + notable data-flow hints |
| `03-call-graph.json` | JSON | semantic | Typed call edges (internal/interface/external/low-level) |
| `04-storage-access-map.json` | JSON | semantic | Per-function storage reads/writes/deletes with lines |
| `15-dataflow-taint.json` / `.md` | JSON+MD | semantic | Named taint findings (calldata/oracle/credit/message-id -> value sinks) |
| `05-defi-entities.json` / `.md` | JSON+MD | defi | Detected economic entities with direction, confidence, evidence |
| `06-state-transitions.json` / `.md` | JSON+MD | state | Before/action/after transitions, flags, invariant hints |
| `16-state-contradictions.json` / `.md` | JSON+MD | state | Broken-lifecycle contradictions (transition, likely invariant, PoC family) |
| `07-invariants.md` | Markdown | invariants | Candidate invariants; suspicious-here ones first, with reasons |
| `08-invariants.json` | JSON | invariants | Machine-readable invariant set + classification |
| `09-attack-graph.json` / `.md` | JSON+MD | attack | Attack candidates and their capability->impact chains |
| `10-candidate-ranking.md` | Markdown | attack | Ranked candidates in the fixed decision format |
| `11-poc-skeletons/` | dir | pocgen | One Foundry `.t.sol` skeleton per top candidate + README |
| `12-fork-plan.md` | Markdown | forklab | When/why fork proof is needed (redacted; env var names only) |
| `fork-requirements.json` | JSON | forklab | Machine-readable fork requirements |
| `13-economic-severity.md` | Markdown | severity | Per-candidate severity verdict and reasoning |
| `economic-severity.json` | JSON | severity | Machine-readable severity verdicts |
| `14-dedup-scope-risk.md` | Markdown | memory | Root-cause hash, duplicate risk, scope risk per candidate |
| `quality-gates.json` / `.md` | JSON+MD | warrun | Pre-output verification gates (pass/warn/fail + affected) |
| `triage.json` | JSON | warrun | Full machine-readable run (artifact_type `godeye_war_run`) |
| `manifest.json` | JSON | warrun | Per-artifact list (type/path/generated/warnings), version/safety metadata |

## Standard artifact header

Every JSON artifact carries a standard machine-readable header so the set is stable
and tool-ingestible: `schema_version`, `engine_version` (the V10 milestone),
`generated_at` (UTC), `target_label` (basename only — never an absolute path),
`target_hash` (a short sha256 of the target path), `semantic_mode`, `confidence`,
`warnings` (always a list), and `artifact_type`. The manifest's `artifacts` list
enumerates every artifact with its `path`, `artifact_type`, `generated` flag, and
`warnings` count.

## Most important outputs

`07-invariants.md`, `08-invariants.json`, `09-attack-graph.json`,
`10-candidate-ranking.md`, `11-poc-skeletons/`, and `13-economic-severity.md`.

## triage.json shape (summary)

- `artifact_type`: `godeye_war_run`; `milestone`: `v10.0.0-dev`; `report_generated`: `false`.
- `semantic`: mode/confidence/counts.
- `entities`, `transitions`, `invariants`, `attack_candidates`, `economic_severity`,
  `fork_requirements`, `dataflow_taint`, `state_contradictions`, `quality_gates`,
  `counts` (incl. `taint_findings`, `contradictions`, `quality_gate_status`).
- `safety_flags`: local_only, no_rpc_by_default, no_broadcast, no_signing_keys,
  no_auto_submit, no_report_generated, fork_is_plan_only, human_review_required.

## Candidate ranking format (`10-candidate-ranking.md`)

Each candidate is rendered as: Decision, Root cause, Broken invariant, Attacker,
Victim, Asset at risk, Entry point, Attack sequence, Evidence, PoC strategy +
skeleton path, Economic gate (impact / likelihood / cap / repeatability / gas /
realism / final recommendation), Dedup/scope, and Next action.

## Safety

A fork plan references RPC endpoints by env var name only and never writes a URL or
a key. A redaction pass scrubs any URL/key-like text from rendered artifacts, and
the orchestrator scans all output for secret-like strings before writing.

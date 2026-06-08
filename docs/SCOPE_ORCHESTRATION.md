# Scope-Aware Orchestration (V7)

V4 maps value flow. V5 prioritizes likely blind spots. V6 classifies evidence and
unresolved interactions. **V7 turns audit scope into review lanes, task packs,
evidence requirements, and report filters so AI-assisted security review starts
from rules and evidence instead of vague prompts.**

Instead of "find bugs in this repo," V7 lets a researcher start from:

> here are the high-impact scoped surfaces, here are the assumptions, here are the
> known / invalid paths, here are the exact counterfactuals, here is the local
> evidence required, and here is how to judge whether a test actually proves
> anything.

Everything is local and static. There is no RPC, no live-chain call, no
transaction execution, no private key handling, no exploit automation, and no
external AI API call. A scope task is a research instruction, not an exploit
instruction. Evidence quality is not vulnerability validity. Candidate-with-evidence
is not a confirmed vulnerability. Task priority is not severity. A human always
makes the security call.

## The five capabilities

1. **Scope Map** — parse a contest/audit/program scope note into structured review
   rules. See [`SCOPE_MAP.md`](SCOPE_MAP.md).
2. **Scope-Aware Review Lanes** — generate generic review lanes from repository
   surfaces plus scope rules.
3. **Scope-Aware Tasks** — turn lanes into precise, testable tasks. See
   [`SCOPE_TASKS.md`](SCOPE_TASKS.md).
4. **Evidence Judge** — judge whether local tests actually prove the intended
   task. See [`EVIDENCE_JUDGE.md`](EVIDENCE_JUDGE.md).
5. **Report Filter / Scope Pack** — classify report candidates against the scope
   before submission, and bundle everything into a local pack. See
   [`REPORT_FILTER.md`](REPORT_FILTER.md).

## Commands

```bash
arkheionx scope-map     <repo> --scope-file <scope.md>
arkheionx scope-lanes   <repo> --scope-file <scope.md>
arkheionx scope-tasks   <repo> --scope-file <scope.md>
arkheionx scope-pack    <repo> --scope-file <scope.md> --out .arkheionx/scope-pack
arkheionx evidence-judge <repo> --scope-file <scope.md>
arkheionx report-filter  <repo> --scope-file <scope.md>
```

All commands accept `--scope-file` (optional), `--json`, and `--out`. If no scope
file is provided, a generic map is inferred from repository structure and clearly
labelled as such.

Try it on the bundled synthetic fixture:

```bash
arkheionx scope-pack examples/scope-fixture --scope-file examples/scope-fixture/scope-note.md --out .arkheionx/scope-pack
```

## Why audit contests need this

Audit contests differ from normal repo review: they have scope boundaries,
severity rules, trusted roles, accepted risks, known issues, prior audits, sponsor
and off-chain assumptions, external-protocol trust assumptions, intended design
choices, recommended focus areas, issues that are valid only at Medium/High
impact, issues that are invalid because they rely on trusted-admin mistakes,
duplicate-prone classes, and low-only issues that are not worth the time. V7
ingests this context and uses it to prioritize contest-valid, high-impact,
evidence-backed research tasks. The goal is not to find bugs automatically; it is
to spend review time where it counts and to avoid wasted or invalid submissions.

## Private scope stays local

A private scope note belongs only in local, gitignored files under
`.arkheionx/private/` (for example `.arkheionx/private/scope.md` and
`.arkheionx/private/private-terms.txt`). Nothing under `.arkheionx/` is committed.
A built-in leak guard scans the public, committed surface for any private term you
list, so target names never leak into source, tests, fixtures, docs, or output.
See [`V7_WORKFLOW.md`](V7_WORKFLOW.md) for the end-to-end private workflow.

## What V7 is not

- It does not confirm vulnerabilities or assign severity.
- It does not replace an audit or a human reviewer.
- It does not prove a protocol is safe.
- It does not submit reports or run live-chain operations.

Human review is required for every conclusion.

# Evidence Judge (V7)

`arkheionx evidence-judge <repo>` judges whether local tests and evidence actually
prove the intended task. It is local/static and heuristic. **It does not confirm
vulnerabilities.** Evidence quality is not vulnerability validity.
Candidate-with-evidence is not a confirmed vulnerability; it only means a human
should review the candidate. Human review required.

## Inputs

- `<repo>` path
- `--scope-file <scope.md>` (optional) — applies scope-aware filters
- `--tasks-file <scope-tasks.json>` (optional) — aligns evidence to tasks
- `--evidence-dir <dir>` (optional) — defaults to scanning `.arkheionx/scope-pack`,
  `.arkheionx/evidence`, `.arkheionx/private`, `test`, and `tests`

## Rubric

For each test or evidence file it checks: does it call the target; exercise the
right lane; reproduce the counterfactual; include setup, action, and an assertion
(not just "did not revert"); check pre/post state or accounting deltas where value
moves; separate attacker/victim/role; test the negative path for
authorization/compliance; test a boundary; avoid mocking away the risk; avoid
relying on a trusted-role mistake the scope marks invalid; avoid duplicating a
known/accepted issue; avoid low-only impact when Medium/High is required; record
the command result; and explain the impact path.

## Labels

Evidence quality: `strong`, `medium`, `weak`, `invalid`, `insufficient`,
`unknown`.

Judgment: `rejected-with-strong-evidence`, `rejected-with-medium-evidence`,
`candidate-with-evidence`, `insufficient-evidence`, `invalid-test`,
`likely-known-issue`, `likely-accepted-risk`, `likely-trusted-role-assumption`,
`likely-out-of-scope`, `likely-low-only`, `needs-human-review`.

A `rejected-with-evidence` result is not proof the protocol has no bugs. A
`candidate-with-evidence` result still requires human review.

## Output

`evidence-judge.md` (Boundary, Summary, Judged Evidence, Weak / Invalid Tests,
Candidate With Evidence, Likely Invalid / Known / Accepted / Out-of-Scope, Next
Actions) and `evidence-judge.json` (validated by
`schemas/evidence-judge.schema.json`).

```bash
arkheionx evidence-judge examples/scope-fixture --scope-file examples/scope-fixture/scope-note.md
```

The bundled fixture ships a deliberately strong, weak, and invalid test so the
grades are visible. See [`SCOPE_ORCHESTRATION.md`](SCOPE_ORCHESTRATION.md) and
[`V7_WORKFLOW.md`](archive/versions/V7_WORKFLOW.md).

## V7.5: protocol-lens evidence

The [V7.5 protocol lens](archive/versions/V7_5_PROTOCOL_LENS.md) layer adds two protocol-aware
evidence surfaces: `arkheionx lens-evidence` classifies each economic invariant's
local-test coverage into one of nine statuses
(`DIRECTLY_TESTED_STRONG`, `DIRECTLY_TESTED_WEAK`, `INDIRECTLY_TESTED`,
`HAPPY_PATH_ONLY`, `FUZZED_BUT_NOT_TARGETED`, `FORMALLY_PROVEN`, `COMMENT_ONLY`,
`UNTESTED`, `UNKNOWN`), and the lens evidence rubric grades discovered tests A-F
with decisions `VALIDATED_CANDIDATE`, `NEEDS_HUMAN_REVIEW`, `REJECTED_WITH_TEST`,
`INSUFFICIENT_EVIDENCE`, `OUT_OF_SCOPE`, `DUPLICATE_RISK_HIGH`. Only grade A may
become `VALIDATED_CANDIDATE`, and the static judge never auto-assigns it. See
[`FIXED_CREDIT_MARKET_LENS.md`](FIXED_CREDIT_MARKET_LENS.md).

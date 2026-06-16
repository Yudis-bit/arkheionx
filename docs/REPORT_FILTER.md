# Report Filter (V7)

`arkheionx report-filter <repo> --scope-file <scope.md>` classifies report
candidates against the scope rules before submission. **The report filter is not
final triage.** Human review required.

This is critical for real contests: it stops a researcher from wasting a
submission on an invalid, known, accepted, out-of-scope, low-only, or duplicate
candidate.

## Inputs

It composes scope tasks, the scope map, the evidence judge, and (when present) a
hypothesis log, then applies the scope's known issues, accepted risks, trusted
assumptions, out-of-scope areas, low-only patterns, and severity rules.

## Classifications

- `potentially-reportable` — a local test gives candidate-with-evidence support
  (still requires human review; still not final triage)
- `needs-more-evidence`
- `likely-known-issue`
- `likely-accepted-risk`
- `likely-trusted-role-assumption`
- `likely-out-of-scope`
- `likely-low-only`
- `duplicate-prone`
- `not-a-finding`
- `needs-human-review`

## Human pre-submission checklist

Is it in scope? Is it not a known/accepted issue? Does it avoid relying only on
trusted-role mistakes? Is the impact Medium/High under the scope rules? Is there a
local proof-of-concept? Is there a clear loss / lock / incorrect-accounting /
unauthorized-action / invariant-break path? Is it not merely a UX or spec
deviation unless impact qualifies? Is it not centralization-only? Is it not an
external-dependency failure unless stated valid? Is the report minimal and
evidence-backed?

## Output

`report-filter.md` (Boundary, Candidate Summary, Potentially Reportable Candidates,
Needs More Evidence, Likely Invalid, Known / Accepted / Trusted / Low-only Filters,
Human Pre-Submission Checklist) and `report-filter.json` (validated by
`schemas/report-filter.schema.json`).

```bash
arkheionx report-filter examples/scope-fixture --scope-file examples/scope-fixture/scope-note.md
```

See [`SCOPE_ORCHESTRATION.md`](SCOPE_ORCHESTRATION.md) and
[`V7_WORKFLOW.md`](archive/versions/V7_WORKFLOW.md).

## V7.5: protocol-lens report filter

The [V7.5 protocol lens](archive/versions/V7_5_PROTOCOL_LENS.md) layer adds
`arkheionx lens-report-filter`, which runs a 15-point pre-submission checklist over
lens evidence candidates and assigns one of six outcomes: `READY_FOR_HUMAN_REVIEW`,
`NEEDS_MORE_EVIDENCE`, `DO_NOT_SUBMIT_DUPLICATE_RISK`, `DO_NOT_SUBMIT_OUT_OF_SCOPE`,
`DO_NOT_SUBMIT_WEAK_IMPACT`, `DO_NOT_SUBMIT_INVALID_SETUP`. It never says "submit
now"; the most positive outcome is `READY_FOR_HUMAN_REVIEW`, and a human still
decides. See [`FIXED_CREDIT_MARKET_LENS.md`](FIXED_CREDIT_MARKET_LENS.md).

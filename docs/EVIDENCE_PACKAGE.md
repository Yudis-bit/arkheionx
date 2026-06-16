# Evidence Package

An evidence package organizes local proof and trace artifacts around a review question.

It can support or reject a hypothesis. It does not confirm severity or final vulnerability validity.

## Command

```bash
arkheionx evidence . --target Vault.withdraw
arkheionx evidence . --from-proof .arkheionx/out/proof/Vault_withdraw/proof.json
```

## What it records

- target identity;
- linked proof artifact;
- linked trace artifact when available;
- evidence level;
- manifest/source records;
- local context from review artifacts;
- human-review-required markers.

## Evidence levels

| level | meaning |
|---|---|
| `HEURISTIC` | Static or planning context only. |
| `COMPILER_CONFIRMED` | A relevant local build or scaffold reached compiler-confirmed state. |
| `EXECUTION_CONFIRMED` | A relevant local test executed. |
| `EVIDENCE_READY` | Execution-confirmed proof and trace evidence exist and are linked. |

Evidence readiness is not vulnerability validity.

## What evidence can do

- Show that a local proof direction was attempted.
- Link a claim to specific local artifacts.
- Help reviewers decide whether a hypothesis is weak, rejected, or worth continuing.
- Make reproduction steps easier to review.

## What evidence cannot do

- Replace PoC review.
- Confirm final severity.
- Decide scope eligibility.
- Prove the absence of bugs.
- Guarantee report acceptance.
- Replace a human security reviewer.

## Human validation

Before a case study or report candidate uses an evidence package, a human should check:

- Does the test exercise the relevant value path?
- Are actors, balances, shares, oracle values, and timing realistic enough?
- Is the assertion tied to impact?
- Does the trace support the claim?
- Are trusted-role, known-issue, and out-of-scope filters handled?
- Is the outcome recorded honestly?

See [`INTERPRET_RESULTS.md`](INTERPRET_RESULTS.md), [`OUTPUT_ARTIFACTS.md`](OUTPUT_ARTIFACTS.md), and [`CASE_STUDIES.md`](CASE_STUDIES.md).

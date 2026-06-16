# Case Studies

Case studies are the credibility layer for ArkheionX.

They should show how ArkheionX helped during actual review work without claiming acceptance, severity, endorsement, or automatic vulnerability discovery.

## Standard

A case study must answer:

- What target was reviewed?
- What review question was asked?
- What value path or trust assumption mattered?
- What weak or missing test area was identified?
- What evidence was generated?
- What did a human validate?
- What is the PoC status?
- What was the outcome?
- What did ArkheionX not decide?

## Current case-study types

| type | meaning |
|---|---|
| Fixture case study | Demonstrates the workflow on toy or synthetic code. Useful for docs and regression tests. |
| Review workflow case study | Records a real review workflow and the evidence path. Does not imply acceptance. |
| Accepted external finding | Only used when there is proof that an external program, audit, contest, or protocol accepted the issue. |

## Current review workflow case studies

- [`dreusd-reward-stream-zero-share.md`](case-studies/dreusd-reward-stream-zero-share.md)
- [`dreusd-distributor-migration.md`](case-studies/dreusd-distributor-migration.md)

These are framed as review workflow case studies. They do not claim accepted findings.

## Existing fixture case studies

- [`ORACLE_STAKING_FIXTURE_CASE_STUDY.md`](case-studies/ORACLE_STAKING_FIXTURE_CASE_STUDY.md)
- [`ORACLE_STAKING_BEFORE_AFTER.md`](case-studies/ORACLE_STAKING_BEFORE_AFTER.md)

## Template

Use [`case-studies/TEMPLATE.md`](case-studies/TEMPLATE.md).

## Rules

- Do not claim a finding is accepted unless there is proof.
- Do not claim ArkheionX found the issue automatically.
- Do not claim final severity automatically.
- Do not publish private target details without permission.
- Do not include live exploit steps for unresolved targets.
- Keep PoC status separate from report outcome.
- Keep ArkheionX output separate from human validation.

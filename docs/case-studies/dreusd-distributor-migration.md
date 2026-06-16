# Case Study: dreUSD Distributor Migration Accounting

## Target

`dreUSDs.setRewardsDistributor`.

## Context

This is a case study from a review workflow, not an accepted-finding claim.

It is separate from the reward-stream zero-share issue. The focus here is stale accounting during active rewards distributor migration.

## Review question

Can changing the rewards distributor while accounting is active leave stale reward state, mismatched accrual, or value distribution assumptions that require explicit validation?

## ArkheionX role

ArkheionX was used to organize value-flow and trust-assumption review around distributor authority, migration timing, accounting freshness, and the evidence needed to reason about a live distributor change.

ArkheionX did not decide that the issue was valid. It helped make the review question explicit.

## Value path

The review path involved:

- rewards accruing or being tracked under an active distributor;
- privileged or configured distributor migration through `setRewardsDistributor`;
- downstream accounting after distributor replacement;
- users whose reward state may depend on pre-migration accounting.

## Trust assumptions

- Distributor migration preserves or settles accounting state.
- The old and new distributor states cannot create stale accounting.
- Users do not lose or gain reward value due only to migration timing.
- Privileged distributor changes are scoped, intentional, and test-covered.

## Missing or weak test area

The weak area was distributor migration during active accounting, especially tests that compare pre-migration and post-migration reward state under realistic conditions.

## Evidence generated

Review workflow evidence was generated around the migration/accounting path. Exact public artifact paths and reproduction commands should be added only when shareable and verified.

## Human validation

Human validation was required and remains the source of the security judgment.

## PoC status

Submitted review workflow evidence. Public PoC reproduction details are not recorded in this repository yet.

## Outcome

Submitted as a Sherlock issue.

Do not claim accepted, paid, confirmed, or high severity unless there is later proof.

## What ArkheionX helped clarify

- The difference between distributor migration and zero-share reward-stream behavior.
- The trusted role and migration authority involved.
- The accounting freshness assumptions that needed testing.
- Why active migration should be reviewed separately from deposit/share math.

## What ArkheionX did not decide

- Whether the issue is accepted.
- Final severity.
- Scope eligibility.
- Economic impact.
- Whether distributor authority is an accepted trust assumption.

## Limitations

This case study records the review workflow without claiming external acceptance.

It should be updated if public, reproducible evidence or an external decision becomes available.

## Reproduction

To be completed with safe, shareable commands and artifact paths when available.

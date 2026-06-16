# Case Study: dreUSD Reward Stream Zero-Share Deposit

## Target

dreUSD / dreUSDs / rewards distributor.

## Context

This is a case study from a review workflow, not an accepted-finding claim.

The review focused on ERC4626-style reward-stream accounting where deposits, shares, and distributor-funded rewards interact.

## Review question

Can reward-stream accounting create a share-inflation or zero-share deposit edge where value can move without proportional share accounting?

## ArkheionX role

ArkheionX was used as value-flow and accounting-path review support.

The useful role was not "finding a bug automatically." The useful role was organizing the reviewer’s attention around value movement, share accounting, reward distribution, weak evidence areas, and the questions a PoC needed to answer.

## Value path

The review path involved:

- deposits into dreUSD/dreUSDs-style accounting;
- reward distributor funding or accrual;
- share minting or share accounting around small deposits;
- withdrawal or redemption paths affected by the accounting state.

## Trust assumptions

- Share issuance remains proportional to deposited value.
- Reward-stream accounting does not let an actor shift value without corresponding shares.
- Zero-share or dust-share deposits are either impossible or harmless.
- Distributor-funded rewards are accounted for consistently across users.

## Missing or weak test area

The weak area was adversarial accounting around a zero-share or near-zero-share deposit during a reward-stream state where shares and claimable value may diverge.

Useful tests need to cover realistic balances, reward state, share conversion, and the before/after value distribution.

## Evidence generated

Human review produced a mock-free Base fork PoC according to the review workflow notes available to this session.

The public case-study record should add exact artifact paths, block numbers, transactions, and reproduction commands only when they can be shared safely and accurately.

## Human validation

Human validation was required and remains the source of the security judgment.

ArkheionX helped structure the path and evidence question; it did not validate the finding by itself.

## PoC status

Mock-free Base fork PoC reported by the reviewer.

## Outcome

Submitted as a Sherlock issue.

Do not claim accepted, paid, confirmed, or high severity unless there is later proof.

## What ArkheionX helped clarify

- Which accounting path needed review.
- Which share/reward assumptions mattered.
- Why zero-share or near-zero-share behavior needed explicit local evidence.
- What kind of PoC would be relevant.

## What ArkheionX did not decide

- Whether the issue is accepted.
- Final severity.
- Scope eligibility.
- Economic impact.
- Whether the protocol team or contest judges agree.

## Limitations

This case study intentionally avoids acceptance language and exact exploit details not present in this repository.

The case study should be updated only when reproducible public evidence is available.

## Reproduction

To be completed with safe, shareable commands and artifact paths when available.


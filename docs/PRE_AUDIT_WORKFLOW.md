# Pre-audit workflow

ArkheionX helps builders and reviewers prepare a DeFi repository **before** a
formal audit. It does not replace the audit, prove safety, or confirm
vulnerabilities — it makes the review surface explicit so the audit time is
spent where value moves.

This workflow is for protocol engineers getting ready for review, and for
reviewers onboarding to an unfamiliar codebase.

## Goal

Hand a reviewer a clearer surface: a map of value paths, the assumptions that
guard them, the value-sensitive functions that lack tests, and notes on what to
inspect first.

## Steps

Run from a local checkout of the repository you own or are authorized to review:

```sh
arkheionx doctor
arkheionx review-map .
arkheionx value-paths .
arkheionx assumptions .
arkheionx test-gap-map .
arkheionx proof-plan .
```

Then work the output by hand:

1. **Read the "Inspect first" list.** It is review order, not severity. Start
   with the money-moving and privileged functions.
2. **Walk each value path.** Confirm that value entering, moving, and exiting is
   accounted for, and that each path's assumptions are actually enforced in code.
3. **Close the test gaps.** For each gap, open its `Source: <file>:<line>` and
   write a targeted Foundry test that exercises the path under adversarial
   inputs. Re-run `review-map` and watch the gap’s coverage change.
4. **Document assumptions.** Capture the trust conditions (oracle freshness,
   access control, share proportionality, no-reentrancy, standard ERC20) as
   explicit notes for the reviewer.
5. **Prepare the handoff.** Share the review map, the new tests, and your notes
   so the reviewer starts from context instead of rebuilding it.

## What this gives the reviewer

- A consistent map of contracts, roles, value paths, and assumptions.
- A list of previously untested value-sensitive functions, now covered.
- A shared vocabulary for the review.

## Limits (kept honest)

- A clean review map does not mean the protocol is safe.
- Passing the tests you added does not prove the absence of bugs.
- ArkheionX assigns no severity and confirms no vulnerability.
- Cross-contract value flow is surfaced as per-contract paths; connecting them
  end to end is roadmap work.
- A formal audit and human review are still required.

## Related

- [`TRY_IN_5_MINUTES.md`](TRY_IN_5_MINUTES.md) — first run.
- [`INTERPRET_RESULTS.md`](INTERPRET_RESULTS.md) — what the output means.
- [`BUG_BOUNTY_WORKFLOW.md`](BUG_BOUNTY_WORKFLOW.md) — the triage variant.
- [`V4_STABLE_SCOPE.md`](V4_STABLE_SCOPE.md) — what is stable in V4.
- [`WHAT_ARKHEIONX_IS_NOT.md`](WHAT_ARKHEIONX_IS_NOT.md) — the boundaries.

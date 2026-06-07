# Real-protocol proof plan

## Goal

Show that ArkheionX is useful on **one authorized, real, open-source DeFi
repository** — not just on bundled fixtures — without claiming any
vulnerability.

This is honest about the current state: ArkheionX's depth is demonstrated on
local fixtures only. A fixture run is **not** a real-protocol proof, and this
document deliberately does not present one. It defines the exact steps to earn
that proof.

## Candidate target requirements

Pick a target that is:

- open-source with a clear license that permits local review;
- legally reviewable by you (public code; no NDA-only material);
- Solidity / Foundry (the review-map engine is tuned for this);
- self-contained and small enough for a first pass (a few core contracts);
- already shipping a test suite (so test-gap signal is meaningful);
- not a live target — analysis is local and static, with no on-chain action.

Do **not** clone or analyze code you are not authorized to review, and do not
point any workflow at deployed contracts, RPC endpoints, or production systems.

## Method

Run the standard local workflow against a local checkout of the target:

```sh
git clone <authorized-open-source-repo> target && cd target
arkheionx doctor
arkheionx review-map .
arkheionx value-paths .
arkheionx assumptions .
arkheionx test-gap-map .
arkheionx proof-plan .
```

Then evaluate by hand:

1. Record the **top 5 review hypotheses** ArkheionX surfaces (highest-priority
   value exits, admin setters, and untested paths, with their `Source:` refs).
2. Open each referenced `file:line` and judge whether the prompt is **useful**
   (points at something a reviewer would genuinely want to check) or **noisy**
   (obvious, already covered, or irrelevant).
3. Note what ArkheionX **missed** that a human reviewer cares about.
4. Note what humans still had to do that the tool did not help with.

## Output: a case study

Write the result to `docs/case-studies/<target>-review-map.md` using
[`../templates/case_study_template.md`](../templates/case_study_template.md) as
the structure, and [`CASE_STUDY_SAMPLE.md`](CASE_STUDY_SAMPLE.md) as a reference
for tone. The case study must record:

- what ArkheionX surfaced (the map, value paths, assumptions, test gaps);
- what was genuinely useful;
- what was wrong, noisy, or low-value;
- what the human still had to do independently;
- an honest usefulness verdict.

Hard rules for the case study:

- No vulnerability claims unless independently confirmed **and** responsibly
  disclosed to the project first.
- No severity, exploitability, or impact claims.
- No bounty claims.
- No adoption, endorsement, or partnership claims about the target project.
- Attribute the target accurately and respect its license and disclosure policy.

## Definition of done

The real-protocol proof is achieved when at least one case study under
`docs/case-studies/` documents a run on an authorized real repository with an
honest usefulness assessment (useful vs. noisy), and contains no vulnerability,
severity, or bounty claims. Until then, broad-readiness messaging must continue
to say depth is shown on fixtures, with real-protocol validation **planned**.

## Related

- [`PUBLIC_ALPHA_READINESS.md`](PUBLIC_ALPHA_READINESS.md) — fixtures-only depth
  is listed there as a deferred item.
- [`BUG_BOUNTY_WORKFLOW.md`](BUG_BOUNTY_WORKFLOW.md) — the same triage workflow,
  applied by a human on an authorized target.
- [`INTERPRET_RESULTS.md`](INTERPRET_RESULTS.md) — how to read the output you
  will be judging.

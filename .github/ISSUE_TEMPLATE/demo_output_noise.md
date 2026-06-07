---
name: Review-map output noise / quality
about: A review-map result was noisy, wrong, or low-value (e.g. a flagged gap that is actually covered, or a missed value path).
title: "[review-map] "
labels: ["feedback", "review-map"]
---

## What looked wrong?

- [ ] A test gap was flagged for a function that **is** tested
- [ ] A value-sensitive path was **missed**
- [ ] An assumption was irrelevant or misleading
- [ ] A `Source: <file>:<line>` reference was wrong
- [ ] Ranking / "Inspect first" order felt unhelpful
- [ ] Other (describe below)

## Command

```
arkheionx review-map <repo-or-fixture>
```

## What ArkheionX reported

```
<paste the relevant lines of output>
```

## What you expected instead

<!-- Why is the result noisy/wrong? Point at the function or file if you can. -->

## Repository context

<!-- Public repo/fixture name if shareable, or a minimal shape: how many
contracts, what the function does, whether a test exercises it. -->

## Environment

- ArkheionX version (`arkheionx version`):

---

ArkheionX output is heuristic review guidance, not a confirmed finding. Noise
reports are expected and welcome in the public alpha — they help calibrate the
heuristics. Local/static only: please do not include secrets or point the tool
at systems you are not authorized to review.

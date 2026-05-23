# Backlog Rejection Criteria

A candidate is rejected when admitting it to the registry would weaken
the corpus's standard. Rejection is not a moral judgment on the
incident — it is a decision about what this archive is for.

The rejection happens at intake. A candidate is closed with one of the
reasons below recorded in its issue or candidate file. The slot is
freed for a different incident.

## Hard rejections

A candidate is rejected outright if any of the following is true.

### R1 — Live-target only

The incident corresponds to a system that is currently exposed in
production. Reproducing it would aid an active attack. Such candidates
are routed through the embargoed-disclosure path described in
`docs/SECURITY.md`, not the public backlog.

### R2 — No defensive value

The PoC, even when asserted, does not teach a primitive, invariant, or
assumption that the corpus or any reasonable reader would not already
know. Repetition of a category that is already well-represented at L2+
falls here unless the candidate adds a meaningfully different
sub-mechanism.

### R3 — Insufficient public sources

There is no independent post-mortem, advisory, or contest report. A
single tweet, an anonymous claim, or an internal memo is not enough.
The corpus does not invent root causes from circumstantial evidence.

### R4 — Duplicate

The incident is already represented in the registry. Variants of the
same exploit on the same protocol on the same date are bundled into
the existing entry's `notes`, not added as new entries.

### R5 — Embargoed and unlikely to clear

The incident is under disclosure embargo and there is no reasonable
expectation that it clears within the next milestone window. The
candidate is held in private notes, not in the public backlog.

### R6 — Live-system attack-tooling repackaging

The candidate, as proposed, would import attack tooling that is still
weaponizable against contemporary versions of the affected protocol or
its forks. Asserted PoCs against historical pinned blocks are fine;
generalized attack scripts are not.

### R7 — Out of VM scope

The incident is on a VM the archive does not yet support
(`SVM`, `MoveVM`, etc. while those scaffolds remain template-only).
The candidate is held under the relevant VM's backlog folder for
future milestones, not added to the EVM registry.

## Soft rejections

A candidate is deferred (not rejected) for any of the following.

### S1 — Archival RPC unavailable

No archival RPC exists, or is reasonably accessible to the maintainer,
for the chain at the candidate's fork block. The candidate is held in
the backlog with `blocked_on: archival-rpc` until that changes.

### S2 — Taxonomy ambiguity

The category is unclear or sits between two existing categories. The
candidate is held with `blocked_on: taxonomy-review` until the
taxonomy is updated, or until a precedent is set by a similar entry.

### S3 — Source quality marginal

Public sources exist but are thin, contradictory, or behind
disappearing links. The candidate is held with
`blocked_on: source-quality` until at least one durable independent
source is found and archived.

### S4 — Maintainer bandwidth

The candidate would land but the maintainer cannot do justice to the
review within the current milestone. Held with
`blocked_on: maintainer-bandwidth` and reconsidered next milestone.

## Things that do NOT justify rejection

- The exploit is "old." Old exploits teach foundational primitives.
  The 2017 Parity incidents are still the right reference for
  unprotected initialization.
- The exploit is "small." Below-$1M incidents often have the cleanest
  root causes, and asserted PoCs teach the primitive without the
  noise.
- The exploit is "weird." Weird primitives have a reserved lane.
- The exploit happened on a chain other than mainnet. L2 / sidechain /
  alt-L1 incidents are accepted when an archival RPC is available;
  see S1 otherwise.

## Recording a rejection

Use the candidate's `rejection_reason` field. Format:

```
Rxx — short reason — link to source (if any)
```

Example:

```
R3 — only one tweet thread, no independent post-mortem — https://twitter.com/...
```

Rejected candidates remain in the backlog as a record. They are not
deleted. A future contributor can re-open one if circumstances change
(post-mortem published, embargo cleared).

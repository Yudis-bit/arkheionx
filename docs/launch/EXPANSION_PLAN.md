# Expansion Plan

This document describes how Arkheionx Vault grows from its current size to
hundreds of verified PoCs without losing the standard defined in
[POC_STANDARD.md](POC_STANDARD.md).

It does not promise timelines and does not claim milestones already
achieved. The current state is recorded honestly in `metadata/registry.json`
and the README registry table.

---

## Guiding principles

1. **Quality bar over count.** A smaller archive of verified, well-asserted
   PoCs is more valuable than a larger archive of compile-only stubs.
2. **No fake achievements.** Counts in the README must match reality. A PoC
   is not "verified" until a verification report exists for it.
3. **Mass-import is the last step, not the first.** Schema, taxonomy,
   templates, scoring, and verification reporting are built before scale.
4. **Defensive framing only.** Expansion does not include adding live
   tooling, scanners, or unauthorized exploitation paths.

## Milestones

Each milestone has a quality bar, infrastructure requirement, and review
process. A milestone is reached when **every** entry below it satisfies the
bar; partial completion does not count.

### M1 — 25 verified PoCs

- **Quality bar.** Every M1 entry is `historical` or `patched`, has a
  passing verification report, and has all assertion families required by
  its category in [ASSERTION_STANDARD.md](ASSERTION_STANDARD.md).
- **Infrastructure.** Mainnet archival RPC available. `forge fmt --check`
  and `forge build` clean. `score_pocs.py` and
  `generate_verification_report.py` integrated.
- **Bottleneck.** Archival RPC quota for replay. Some incidents may need
  multiple chains.
- **Verification workload.** Per-PoC: rerun fork, capture logs, write
  report, update metadata. Estimate one focused engineering day per PoC for
  unfamiliar incidents, less for the simpler ones already in the archive.
- **Metadata completeness.** All required fields populated. No `unknown`
  values for `block_number`, `attack_tx`, or `references` on `historical`
  entries unless explicitly justified in `notes`.
- **Review process.** PR per PoC, with verification report attached and
  passing CI.

### M2 — 50 verified PoCs

- **Quality bar.** M1 bar plus: each entry classified under a single
  primary [taxonomy](EXPLOIT_TAXONOMY.md) category, with secondary
  categories listed under `tags`.
- **Infrastructure.** At least one secondary chain alias verified end-to-end
  (Base, Arbitrum, Polygon, BNB, etc.) with a working archival RPC.
  Cross-chain helpers added to `EVM/src/` only if reused by ≥3 PoCs.
- **Bottleneck.** Cross-chain RPC sourcing; archival pruning for older
  L2 blocks.
- **Verification workload.** ~25 net new verifications + drift checks on
  M1 entries when shared infrastructure changes.
- **Metadata completeness.** Audit lesson and patch reference populated for
  ≥80% of entries.
- **Review process.** Same as M1, plus per-quarter score sweep using
  `score_pocs.py`. Any entry that drops below grade B is reopened.

### M3 — 100 verified PoCs

- **Quality bar.** M2 bar plus: every category in
  [EXPLOIT_TAXONOMY.md](EXPLOIT_TAXONOMY.md) has at least one verified
  representative entry; per-category auditor checklist exercised against
  that entry.
- **Infrastructure.** Verification report generation runs in CI for any
  metadata change. Quality matrix regenerated on each merge to main.
- **Bottleneck.** Maintainer review bandwidth, not RPC. Backlog grooming
  becomes the gating step.
- **Verification workload.** ~50 net new + maintenance churn. At this size,
  expect ~5–10% of older entries to need re-verification per quarter due
  to RPC changes, fork-state drift, or upstream library updates.
- **Metadata completeness.** Every `historical` entry has `attacker_path`,
  `invariant_broken`, `protocol_assumption_failure`, `attacker_profit_check`,
  and `victim_loss_check` populated.
- **Review process.** Two-eye review for any new entry; one-eye for
  metadata-only fixes; quarterly score sweep is mandatory.

### M4 — 300+ verified PoCs

- **Quality bar.** M3 bar plus: cross-VM coverage (SVM and MoveVM) is no
  longer template-only — at least one verified entry per non-EVM VM.
- **Infrastructure.** Backlog tooling generates draft metadata stubs from
  `metadata/backlog/candidates/*.json`. CI rejects any `historical` entry
  whose `score_pocs.py` grade is below C.
- **Bottleneck.** Source quality. At this scale, public post-mortems get
  thinner per incident; researchers must triangulate across writeups.
- **Verification workload.** Constant: one verified PoC per maintainer
  week, sustained, plus rolling re-verification of older entries.
- **Metadata completeness.** ≥95% of entries reach grade B+. No
  `historical` entry below grade C.
- **Review process.** Triage rotation. Backlog is groomed monthly,
  candidates that fail triage are closed with a recorded reason.

### M5 — 700+ verified PoCs

- **Quality bar.** M4 bar plus: full taxonomy coverage at depth (≥3
  representative entries per category), and a published methodology paper /
  long-form writeup describing the archive's process.
- **Infrastructure.** Replay sharded across multiple archival providers;
  cached fork snapshots; verification reports published as artifacts.
- **Bottleneck.** Long-tail incident attribution. Many smaller incidents
  lack public post-mortems; expect to drop a non-trivial fraction.
- **Verification workload.** Sustainable only with ≥2 active maintainers or
  paid verification time. The cost of staying at M5 is non-trivial.
- **Metadata completeness.** ≥99% of entries grade B+; no orphaned
  references; every external link archived.
- **Review process.** Maintained as a research process, not a hobby.
  Public methodology, published quality matrix, public verification logs.

## Anti-goals

These are not part of the expansion plan, regardless of milestone:

- Importing PoCs from other repositories without preserving original
  attribution and original commit SHAs.
- Counting `template` or `educational` entries toward verified totals.
- Marking `verified` without a verification report.
- Creating exploit packages that work against current production state.
- Comparing the archive to specific named firms in marketing material.

## Honest current state

See `metadata/registry.json` and the README registry table for the
authoritative count. As of writing, all entries are `historical` or
`incomplete` with `reproducibility` of `unverified` or
`requires-archival-rpc`. M1 work begins by configuring archival RPC,
running existing PoCs, and producing the first verification reports — see
the recommended next phase in the Phase 3 report.

## Intake rubric

Triage rules and rejection rubric live alongside the backlog so they
are reviewable independently of this plan:

- [`metadata/backlog/priority-lanes.md`](../metadata/backlog/priority-lanes.md)
  — the ten research lanes, lane balancing rules per milestone, and
  per-lane intake checklist.
- [`metadata/backlog/rejection-criteria.md`](../metadata/backlog/rejection-criteria.md)
  — hard and soft rejection categories, banned framings, appeal path.
- [`docs/INCIDENT_INTAKE.md`](INCIDENT_INTAKE.md) — the candidate-to-
  registry pipeline.

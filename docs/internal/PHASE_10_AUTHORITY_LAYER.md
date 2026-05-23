# Phase 10 — Authority Layer Report

## Summary

Phase 10 builds the public-facing authority layer of Arkheionx Vault.
The repository already had honest content, sober tone, and a complete
metadata pipeline after Phase 8 / 9. What was missing was the
front-of-house structure that lets a first-time visitor — a protocol
security engineer, audit-contest judge, or recruiter — read the page
and understand: what this archive is, how mature each PoC is, how
maturity is defined, how the corpus will grow, how to contribute, and
how releases get cut.

This phase adds:

- A formal **PoC maturity ladder** (L0–L5) with promotion / demotion
  rules.
- A generated **per-PoC maturity index** at
  `reports/poc_maturity_index.md`.
- A **release process** doc covering corpus, hardening, verification,
  case-study, and taxonomy releases.
- Two new **issue templates** for the public intake path: research
  candidate, and assertion hardening.
- A **priority-lane** document for backlog triage.
- README upgrades: maturity ladder section, M0–M5 roadmap, contribute
  section, doc-cluster cross-links, status snapshot referencing the
  maturity index.
- A tightened `github_surface_setup.sh` description.

No PoC source, test, metadata entry, or verification report was
modified. No verification claim was upgraded. No platform / firm
affiliation was added. Counts in the README and the maturity index
match what the registry actually contains.

---

## Public authority audit (pre-edit)

### What looked strong

- README sober tone, named maintainer, defensive-use framing, honest
  status table after Phase 8.
- Comprehensive `docs/` cluster: POC_STANDARD, ASSERTION_STANDARD,
  REPRODUCIBILITY_STANDARD, EXPLOIT_TAXONOMY, FORK_VERIFICATION,
  ROOT_CAUSE_PLAYBOOK, EXPANSION_PLAN, INCIDENT_INTAKE, AUDITOR_CHECKLIST.
- Per-PoC quality matrix (`reports/poc_quality_matrix.md`) with grade
  distribution and per-PoC weakness notes.
- Per-PoC verification report skeletons under
  `reports/verification/`, generated and idempotent.
- Scoped CI workflows (`docs.yml`, `evm.yml`, `metadata.yml`).
- Safe-by-default `scripts/github_surface_setup.sh` (dry-run unless
  `--apply`, no visibility / delete operations).
- Dark technical social-preview SVG with no firm logos or fake
  badges.
- `.gitignore` covers `.reference_data/`, secrets, lockfiles.
- `web/` already removed in Phase 9 — no off-brand frontend lingers.

### What still looked unfinished

- No formal PoC maturity model — the registry encoded `assertion_quality`
  and `reproducibility` separately, but there was no single ladder a
  visitor could read to understand "where does this PoC sit?".
- No maturity index generator — the README claimed 0
  deterministic-confirmed entries but did not show the per-PoC level
  breakdown.
- Backlog README mentioned priority lanes informally; no
  `priority-lanes.md` existed.
- No release process doc — release types, checklist, tag scheme were
  implicit.
- Issue templates covered breakage and reproducibility but not
  intake (new candidate) or assertion hardening (improvement of an
  existing entry).
- README roadmap was a flat bullet list with no milestone gates and no
  reference to maturity counts.

### What looked AI-generated

Nothing material on the public surface after Phase 9. Internal
phase-log files use a recognisable structure but they are research
provenance, not marketing copy, and live under `docs/internal/` which
is not over-linked from the README.

### What looked amateur

- Roadmap section did not gate milestones by quality.
- No documented tagging / release scheme.
- PR template did not require maturity-index regeneration.

### What should be hidden from the front page

- `docs/internal/` phase logs — they are evidence, not marketing.
  README does not link them, and Phase 10 keeps it that way.
- `.reference_data/` — already ignored, nothing surfaces it.

### What should be elevated

- Maturity ladder (added).
- M0–M5 roadmap with quality gates (added).
- Contribute / intake path (added).
- Doc cross-links to the new artifacts (added).

### What should be automated

- Maturity index regeneration: now `python3 scripts/poc_maturity_index.py`
  with a `--check` mode for CI.

---

## What changed

### Files added

- `docs/POC_MATURITY_MODEL.md` — L0–L5 ladder, requirements per level,
  what counts as evidence, demotion rules.
- `docs/RELEASE_PROCESS.md` — release types, checklist, release-notes
  rules, tag scheme.
- `metadata/backlog/priority-lanes.md` — 8 lanes, why each exists,
  triage signal, cross-lane rules.
- `scripts/poc_maturity_index.py` — generator with `--check` and
  `--stdout` modes.
- `reports/poc_maturity_index.md` — generated per-PoC index.
- `.github/ISSUE_TEMPLATE/research_candidate.md` — new-incident intake.
- `.github/ISSUE_TEMPLATE/assertion_hardening.md` — improve an existing
  PoC's assertions.

### Files modified

- `README.md` — added "PoC maturity ladder" section, expanded
  "Roadmap" to M0–M5 with explicit quality gates, added "How to
  contribute" section, added cross-links to
  `POC_MATURITY_MODEL.md`, `RELEASE_PROCESS.md`, and
  `metadata/backlog/priority-lanes.md`. Status snapshot now
  references the maturity index.
- `.github/pull_request_template.md` — requires
  `score_pocs.py --check`, `poc_maturity_index.py --check`, an
  honest-level statement, and an explicit no-overclaiming check.
- `scripts/github_surface_setup.sh` — description string aligned with
  the spec ("focused on assertions, root-cause analysis, and fork
  verification readiness").

### Files unchanged (intentional)

- `EVM/src/**`, `EVM/test/**/*.t.sol` — exploit code is out of scope
  for this phase.
- `metadata/registry.json` — no entry was upgraded; counts in the
  README track real state.
- `reports/verification/*.md` — no verification was upgraded.
- All non-EVM scaffolds (`SVM/`, `MoveVM/`).

---

## README authority upgrades

Concrete additions:

1. **PoC maturity ladder** — six-row table covering L0 through L5 with
   one-sentence meaning each. Honest counter: "0 entries at L4, 0 at
   L5". This is the single biggest authority signal added in this
   phase: any visitor can now read the front page and immediately
   place each PoC on the ladder.
2. **Roadmap** — replaced the flat bullet list with M0–M5 milestones,
   each gated by quality. M0 is marked "done" because the
   infrastructure (registry, schema, taxonomy, scoring, verification
   skeletons, maturity index) is in place. M1+ are open and not
   timeline-promised.
3. **How to contribute** — explicit two-path intake (new incident vs
   hardening existing) referencing the new issue templates and the
   priority-lanes doc. Closes the "how do I help?" loop without
   inviting unsafe submissions.
4. **Doc cross-links** — added `POC_MATURITY_MODEL.md`,
   `RELEASE_PROCESS.md`, and `metadata/backlog/priority-lanes.md` to
   the related-documents list in the Research-standard section.
5. **Status snapshot** — now references the maturity index file so
   the front-page numbers and the per-PoC view share the same source
   of truth.

What was NOT changed in the README (intentionally):

- Hero / overview / why-this-exists sections — already strong.
- "What this repository is / is not" — already explicit and honest.
- Severity table, assertion-quality table, verification-model
  section — already accurate.
- Vulnerability-registry block — generated from
  `metadata/registry.json`; markers are preserved.

---

## Maturity model

`docs/POC_MATURITY_MODEL.md` defines six levels:

- **L0 — Raw Replay**: compiles, no proof.
- **L1 — Structured Metadata**: complete registry entry, no `unknown`
  placeholders, ≥1 reference.
- **L2 — Assertion-Hardened**: `assertion_quality` is `medium` or
  `strong`; required family per category.
- **L3 — Public RPC Smoke-Tested**: `latest_public_rpc_status`
  recorded honestly (`pass`, `fail`, or `not-archival`).
- **L4 — Archival Verified**: `reproducibility = deterministic-confirmed`
  AND `verification_status = verified` AND a verification report with
  filled-in verifier handle, date, commit. Skeleton reports do not
  count.
- **L5 — Research-Grade Case Study**: L4 plus a long-form write-up,
  patch lesson, and auditor checklist walkthrough.

Demotion rules are defined: an L4 → L3 demotion is allowed when
archival RPC drifts; an L3 → L2 demotion is allowed when the
`block_number` changes without re-running the smoke test; an L2 → L1
demotion is allowed when assertions weaken. Hidden demotions are not
allowed.

---

## Maturity index results

Generated by `scripts/poc_maturity_index.py`. Honest current
distribution across the 18-entry corpus:

| Level | Count |
|---|---|
| L5 | 0 |
| L4 | 0 |
| L3 | 1 |
| L2 | 10 |
| L1 | 7 |
| L0 | 0 |

The single L3 entry is `2025-11-moonwell` (medium assertion quality
plus `public-rpc-pass`). The 7 L1 entries are the `weak`-assertion PoCs
that have not been hardened yet — promotion path is documented in
`POC_MATURITY_MODEL.md` and in the new
`assertion_hardening.md` issue template.

The script enforces honesty:

- A `weak` PoC cannot exceed L1 even with a public-RPC smoke pass —
  without hard assertions there is nothing for an archival run to
  prove.
- L4 requires a real run transcript in the verification report. The
  script searches for `Test result: ok` / `tests passed` / `passing
  tests` markers AND rejects reports containing `_to be filled by
  verifier_` placeholders. Skeleton reports cannot promote.
- L5 additionally requires a co-located `WRITEUP.md` or a
  `docs/case-studies/<id>.md` with non-zero size.

`--check` mode is wired and clean.

---

## Expansion engine

`metadata/backlog/priority-lanes.md` defines 8 lanes:

1. Historical high-impact DeFi incidents
2. Oracle manipulation
3. Reentrancy and callback failures
4. Accounting / share-price manipulation
5. Governance and access-control failures
6. Bridge and cross-chain failures
7. Vault and lending protocol failures
8. Weird edge-case primitives

Each lane has: why it exists, triage signal, and (where applicable)
examples already in the registry. The lanes set triage order; the
existing `docs/EXPANSION_PLAN.md` continues to set the milestone
quality gates. The two are explicitly cross-linked.

No fake candidates were added. The backlog `candidates/` directory
remains empty — the engine exists, the scale doesn't.

---

## Release process

`docs/RELEASE_PROCESS.md` defines:

- Five release types: corpus, assertion-hardening, verification,
  case-study, taxonomy.
- A pre-tag checklist that runs all `--check` validators including
  the new `poc_maturity_index.py --check`.
- Release-notes rules: what changed, maturity-index delta, honest
  gaps, next milestone target. No "largest" / "best" / affiliation
  claims.
- A tag scheme: `v0.<milestone>.<patch>` while the corpus is below
  100 verified PoCs; `vMAJOR.MINOR.PATCH` after M3.

The README references `RELEASE_PROCESS.md` from the doc cluster.

---

## GitHub surface setup

`scripts/github_surface_setup.sh` is unchanged in shape — still
dry-run by default, still `--apply`-gated, still rejects when `gh` is
missing or unauthenticated, still never modifies visibility or deletes
anything. Phase 10 only tightens the description string to the
spec-recommended phrasing:

> Arkheionx Vault — independent DeFi exploit PoC archive focused on
> assertions, root-cause analysis, and fork verification readiness.

Topic list is unchanged from Phase 9 (already aligned with the spec
list).

The social-preview SVG and `.github/assets/README.md` (with manual
upload steps) were already in place from Phase 9; Phase 10 did not
touch them.

---

## Root cleanup

No removals were needed in Phase 10:

- `web/` — already removed in Phase 9.
- `.reference_data/` — already in `.gitignore`.
- `docs/internal/` — kept as research provenance, not over-linked
  from the README.

No `archive/` directory was created. Nothing was moved.

---

## Files changed

```
A  .github/ISSUE_TEMPLATE/assertion_hardening.md
A  .github/ISSUE_TEMPLATE/research_candidate.md
M  .github/pull_request_template.md
A  docs/POC_MATURITY_MODEL.md
A  docs/RELEASE_PROCESS.md
A  docs/internal/PHASE_10_AUTHORITY_LAYER.md
M  README.md
A  metadata/backlog/priority-lanes.md
A  reports/poc_maturity_index.md
A  scripts/poc_maturity_index.py
M  scripts/github_surface_setup.sh
```

A separate, parallel piece of work present on the working tree —
`scripts/research_dashboard.py`, `reports/research_dashboard.md`,
`docs/internal/FINAL_RELEASE_ORCHESTRATION_LOG.md` — was not modified
by this phase. The README references the dashboard generator in the
status section.

---

## Commands run

```
python3 scripts/validate_metadata.py
python3 scripts/generate_registry.py --check
python3 scripts/score_pocs.py --check
python3 scripts/generate_verification_report.py --check
python3 scripts/poc_maturity_index.py
python3 scripts/poc_maturity_index.py --check
bash   scripts/github_surface_setup.sh --dry-run
forge  fmt --check    (from EVM/)
forge  build          (from EVM/)
git    status --short
```

## Validation results

| Command | Result |
|---|---|
| `validate_metadata.py` | ok: 18 entries valid |
| `generate_registry.py --check` | ok: 18 entries |
| `score_pocs.py --check` | ok: matrix unchanged (18 entries) |
| `generate_verification_report.py --check` | ok: 18 entries processed, 0 changed |
| `poc_maturity_index.py` | wrote `reports/poc_maturity_index.md` |
| `poc_maturity_index.py --check` | OK |
| `github_surface_setup.sh --dry-run` | clean dry-run, no apply |
| `forge fmt --check` (EVM/) | clean |
| `forge build` (EVM/) | builds; pre-existing `erc20-unchecked-transfer` lint warnings only |

No errors. No verification claim was upgraded. No registry entry was
modified.

---

## Remaining risks

- **Archival RPC still required** to promote any entry to L4. Until an
  archival endpoint is configured and a real run transcript is
  committed, the maturity index will show 0 entries at L4 / L5. This
  is honest but limits the public authority signal at the top of the
  ladder.
- **Backlog is engine-only.** Priority lanes are defined and the
  intake template is open, but `metadata/backlog/candidates/` is
  empty. This is intentional (no fake scale) and will fill over
  time.
- **L1 entries with `weak` assertions** (`spankchain`, `uniswap-imbtc`,
  `harvest`, `cheese-bank`, `saddle`, `indexed-finance`, `yeth`) are
  the most common path to mid-corpus authority. Each has a clear
  promotion target documented in the maturity index.
- **GitHub surface settings** (description, topics) are still
  dry-run-only on this branch. Applying them is a Phase 11A action.

No red flags. No overclaiming surfaces in the index, README, or new
docs.

---

## Manual GitHub steps

These are not script-applicable from this branch:

1. Apply the description and topics:
   `bash scripts/github_surface_setup.sh --apply`
   (requires `gh auth login` first; safe Phase 11A action).
2. Upload `social-preview.png` (converted from
   `.github/assets/social-preview.svg`) via Settings → Social preview.
   Conversion command is documented in `.github/assets/README.md`.
3. Optional: pin the repository on the maintainer's GitHub profile.
4. Optional: open the first `Research candidate` issue from the
   priority-lanes list to seed the backlog publicly.

---

## Recommended commit message

```
feat(repo): add Arkheionx Vault authority layer

Adds the public-facing authority layer:

- docs/POC_MATURITY_MODEL.md — L0–L5 ladder with promotion rules.
- scripts/poc_maturity_index.py — generator with --check mode.
- reports/poc_maturity_index.md — honest per-PoC index.
- docs/RELEASE_PROCESS.md — release types, checklist, tag scheme.
- metadata/backlog/priority-lanes.md — 8-lane triage order.
- .github/ISSUE_TEMPLATE/research_candidate.md — new-incident intake.
- .github/ISSUE_TEMPLATE/assertion_hardening.md — improve existing PoC.

README upgrades: maturity-ladder section, M0–M5 roadmap with quality
gates, contribute section, doc cross-links. PR template now requires
score and maturity-index --check pre-merge. github_surface_setup.sh
description tightened to spec wording.

No PoC source, test, registry entry, or verification report was
modified. No verification claim was upgraded. No firm / platform
affiliation was added. Counts in the README and the maturity index
match metadata/registry.json.
```

---

## Recommended next phases

- **Phase 11A** — apply GitHub repo settings via
  `scripts/github_surface_setup.sh --apply` (description + topics);
  upload converted social preview.
- **Phase 11B** — normalise retained legacy slugs noted in
  `metadata/registry.json` `notes` fields, without churning file
  paths.
- **Phase 11C** — continue assertion hardening for the seven L1
  `weak`-assertion PoCs, lifting them to L2 per the
  assertion-hardening template.
- **Phase 11D** — archival RPC verification plan: scope the RPC
  providers, draft per-PoC verification batches, define what evidence
  must land in `reports/verification/` for L4 promotion.

Phase 11 is not started in this commit.

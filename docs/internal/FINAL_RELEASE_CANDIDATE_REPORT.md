# Arkheionx Vault — Final Release Candidate Report

Final orchestration phase summary. This document is the bridge between
the research-grade-rebuild branch and a tagged public release. It
records what changed, what was verified, what was deliberately skipped,
and what the maintainer needs to do manually before the release goes
out.

This is a working document. It is not a marketing artifact.

## 1. Summary

This phase did **not** add PoCs, did **not** modify exploit logic, and
did **not** run archival fork verification. It assembled the authority
layer around the existing 18-entry corpus: maturity model + index,
research dashboard, contributor and intake system, expansion-engine
docs, release process, hardened CI gates, launch material, and a
release-candidate report.

The corpus truth is unchanged. Every numeric in this phase comes from
`metadata/registry.json` and the generated reports. No claim is made
about verification beyond what the artifacts back.

## 2. Current Repository Truth

| Metric | Value |
|---|---|
| Total PoCs | 18 |
| Deterministic-confirmed (L4+) | 0 |
| Assertion-hardened (medium / strong) | 11 |
| Strong static assertions | 7 |
| Medium static assertions | 4 |
| Weak static assertions | 7 |
| Public-RPC smoke attempted | 2 |
| Needs verification | 18 |
| Legacy slug retained (Phase 6A) | 7 |
| L3 PoCs | 1 |
| L2 PoCs | 10 |
| L1 PoCs | 7 |
| L0 PoCs | 0 |
| L4 PoCs | 0 |
| L5 PoCs | 0 |

**Public RPC limitation.** Most historical mainnet PoCs return
`historical state ... is not available` against public endpoints;
those entries record `latest_public_rpc_status: public-rpc-not-archival`
and stay at L1/L2 until archival RPC is configured.

**Archival RPC requirement.** L4 promotion requires
`reproducibility: deterministic-confirmed`,
`verification_status: verified`, `assertion_quality >= medium`, and a
verification report whose verifier handle, date, and commit are filled
in (not the skeleton placeholder values).

## 3. What Changed in This Final Phase

### Added

- `scripts/research_dashboard.py` and `reports/research_dashboard.md`.
- `.github/ISSUE_TEMPLATE/unsafe_content_report.md`.
- `metadata/backlog/rejection-criteria.md`.
- `docs/RELEASE_PROCESS.md`,
  `docs/RELEASE_CHECKLIST.md`,
  `docs/LAUNCH_PLAN.md`.
- `docs/launch/GITHUB_RELEASE_NOTES.md`,
  `docs/launch/LINKEDIN_LAUNCH_POST.md`,
  `docs/launch/X_THREAD.md`.
- `docs/internal/FINAL_RELEASE_ORCHESTRATION_LOG.md`.
- `docs/internal/FINAL_RELEASE_CANDIDATE_REPORT.md` (this file).

### Already in tree from Phase 10 (audited; kept)

- `docs/POC_MATURITY_MODEL.md`.
- `scripts/poc_maturity_index.py`.
- `reports/poc_maturity_index.md`.
- `.github/ISSUE_TEMPLATE/research_candidate.md`.
- `.github/ISSUE_TEMPLATE/assertion_hardening.md`.
- `metadata/backlog/priority-lanes.md`.
- `.github/assets/social-preview.svg` and asset README.
- `scripts/github_surface_setup.sh` (description text polished).

### Edited

- `README.md` — current-status table refreshed, dashboard links added.
- `.github/workflows/metadata.yml` — added `score_pocs.py`,
  `generate_verification_report.py`, `poc_maturity_index.py`, and
  `research_dashboard.py` `--check` jobs; broadened path triggers.
- `.github/workflows/docs.yml` — added required-doc list (model,
  release docs, intake docs); added banned-phrase scan over the public
  surface.
- `.github/workflows/evm.yml` — clarified the skip-notice text.
- `.github/pull_request_template.md` — extended checklist with the new
  generated artifacts and the no-fake-verification gate.
- `docs/EXPANSION_PLAN.md` — references the lane and rejection rubric.
- `scripts/github_surface_setup.sh` — already had the polished
  description string in the working tree.

### Not changed

- `EVM/src/**` and `EVM/test/**/*.t.sol` — out of scope for this phase.
- `metadata/registry.json` — no new PoCs, no flips of verification or
  reproducibility.
- `reports/verification/*.md` — skeletons untouched; archival
  verification is a separate phase.

## 4. README / Public Surface

- Hero, thesis, maintainer attribution intact.
- Status table now shows dashboard-derived metrics and links to all
  three generated reports.
- Maturity ladder, severity table, assertion-quality table all match
  the model in `docs/POC_MATURITY_MODEL.md`.
- "Not the largest archive" disclaimer kept; banned-phrase scan
  excludes this line as it is the disclaimer itself.
- No stale `web/` references on the public surface (historical phase
  logs under `docs/internal/` retain provenance and are excluded from
  CI scans).

## 5. Maturity Model and Index

- Model: L0 → L5 with promotion gates, demotion rules, and "what does
  not count" sections per level.
- Index generator (`scripts/poc_maturity_index.py`): supports
  `--check` and `--stdout`; refuses to mark L4 unless metadata claims
  deterministic-confirmed AND verified AND a real (non-skeleton)
  verification report exists; refuses to mark L5 without a case-study
  artifact.
- Current index distribution: L0=0, L1=7, L2=10, L3=1, L4=0, L5=0.

## 6. Research Dashboard

- Single-page snapshot of the registry under
  `reports/research_dashboard.md`.
- Aggregates: total, assertion-hardened, archival-verified,
  needs-verification, legacy-slug-retained, archival-RPC-blocked,
  maturity distribution, milestone progress (M0/M1a/M1b/M2/M3),
  distributions for assertion quality, reproducibility, verification
  status, public-RPC status, category, severity, top next actions, and
  per-bucket working sets.
- Generator (`scripts/research_dashboard.py`) supports `--check` and
  `--stdout`. No invented metrics — every value is derived from the
  registry or from `poc_maturity_index.maturity_level`.

## 7. Contributor System

Issue templates now cover the full intake surface:

| Template | Purpose |
|---|---|
| `bug_report.md` | A previously listed PoC no longer reproduces. |
| `poc_verification_issue.md` | A PoC builds but assertions don't match documented post-state. |
| `documentation_issue.md` | Doc correction, metadata mismatch, or unsafe-content concern. |
| `research_candidate.md` | Propose a new historical incident as a candidate PoC. |
| `assertion_hardening.md` | Propose lifting a PoC from L1 to L2 or weakening to strong. |
| `unsafe_content_report.md` | Flag content that may aid attack against an unpatched live system. |

PR template hardened with explicit `--check` gates for every
generated artifact, a one-PoC-per-PR rule for hardening and
verification, and an explicit "no fake verification, no fake claims"
gate.

## 8. Expansion Engine

- `metadata/backlog/priority-lanes.md` — 8 lanes (lane 8 is
  "weird/edge-case primitives"), per-lane triage signals, examples,
  and cross-lane rules.
- `metadata/backlog/rejection-criteria.md` — hard and soft rejections,
  banned framings, appeal path. Records that rejected candidate files
  are kept (not deleted) to preserve the public record.
- `docs/EXPANSION_PLAN.md` — milestones M1–M5, intake rubric section
  pointing at the lane and rejection docs.

## 9. Release System

- `docs/RELEASE_PROCESS.md` — release types, versioning,
  pre-release validation gate, no-fixed-cadence rule.
- `docs/RELEASE_CHECKLIST.md` — printable per-release checklist
  covering tree state, metadata, build, reports, README,
  documentation, GitHub surface, safety scan, release notes, CI, tag
  and publish, announcement decision, and post-release follow-up.
- `docs/LAUNCH_PLAN.md` — channels (GitHub, LinkedIn, X), banned
  framings, follow-up cadence, recovery rules, single-author rule.

## 10. GitHub Surface Setup

- `scripts/github_surface_setup.sh` — `--dry-run` default, `--apply`
  required, `gh` presence + auth check, never changes visibility,
  never deletes, never force-pushes. Description and topic list match
  the spec in this phase.
- Manual upload still required for the social preview PNG. The SVG
  and an asset README live under `.github/assets/`.

## 11. CI / Validation Gates

- `metadata` workflow now runs the full set: validate, registry
  --check, score --check, verification report --check, maturity
  --check, dashboard --check.
- `docs` workflow now requires the new docs (maturity model, release
  process / checklist, launch plan, lane / rejection docs) and runs a
  banned-phrase scan over README + public docs (with documented
  exclusions).
- `evm` workflow unchanged structurally; skip-notice text clarified so
  the green check on a no-RPC run cannot be mistaken for verification.
- Fork tests remain RPC-gated and never run automatically without
  configured secrets.

## 12. Safety and Secret Scan

Public-surface scans (excluding `docs/internal/` historical phase
logs) all clean:

- Hype framings (`world-class`, `industry-leading`, `military-grade`,
  `trusted by <Capital>`): zero hits on README and public `docs/`.
- Stale `web/` references: only inside `RELEASE_CHECKLIST.md` itself,
  where the checklist instructs the next release to scan for them.
- Live-target framings (`live exploit`, `drain helper`, `target scan`,
  `attacker automation`): only inside the prohibition lists themselves
  (rejection criteria, unsafe-content template, release checklist,
  intake doc, metadata schema). No instances in PoC source or PoC
  metadata.
- Secrets: only env-var **names** appear (`ETH_RPC_URL`, `BASE_RPC_URL`,
  etc.) in workflow files, README, and reproducibility docs. No
  values, no `.env`, no API keys, no private keys. `.reference_data/`
  is `.gitignore`-d and remains untracked.

## 13. Files Changed

Modified (tracked):

- `README.md`
- `.github/pull_request_template.md`
- `.github/workflows/docs.yml`
- `.github/workflows/evm.yml`
- `.github/workflows/metadata.yml`
- `docs/EXPANSION_PLAN.md`
- `scripts/github_surface_setup.sh`

New (untracked, ready to commit):

- `.github/ISSUE_TEMPLATE/research_candidate.md`
- `.github/ISSUE_TEMPLATE/assertion_hardening.md`
- `.github/ISSUE_TEMPLATE/unsafe_content_report.md`
- `docs/POC_MATURITY_MODEL.md`
- `docs/RELEASE_PROCESS.md`
- `docs/RELEASE_CHECKLIST.md`
- `docs/LAUNCH_PLAN.md`
- `docs/launch/GITHUB_RELEASE_NOTES.md`
- `docs/launch/LINKEDIN_LAUNCH_POST.md`
- `docs/launch/X_THREAD.md`
- `docs/internal/FINAL_RELEASE_ORCHESTRATION_LOG.md`
- `docs/internal/FINAL_RELEASE_CANDIDATE_REPORT.md`
- `docs/internal/PHASE_10_AUTHORITY_LAYER.md` (Phase 10 working log
  already present from prior session)
- `metadata/backlog/priority-lanes.md`
- `metadata/backlog/rejection-criteria.md`
- `reports/poc_maturity_index.md`
- `reports/research_dashboard.md`
- `scripts/poc_maturity_index.py`
- `scripts/research_dashboard.py`

Not modified (out of scope):

- `EVM/src/**`
- `EVM/test/**/*.t.sol`
- `metadata/registry.json`
- `reports/verification/*.md`

## 14. Commands Run

Read-only inspection:

```sh
git status --short
git diff --stat
git log --oneline -25
git branch --show-current
find . -maxdepth 2 -type d
find . -maxdepth 2 -type f
ls -la docs/internal docs/templates metadata/backlog reports reports/verification
ls -la .github .github/workflows .github/ISSUE_TEMPLATE .github/assets
```

Validation:

```sh
python3 scripts/validate_metadata.py
python3 scripts/generate_registry.py --check
python3 scripts/score_pocs.py --check
python3 scripts/generate_verification_report.py --check
python3 scripts/poc_maturity_index.py
python3 scripts/poc_maturity_index.py --check
python3 scripts/research_dashboard.py
python3 scripts/research_dashboard.py --check
bash scripts/github_surface_setup.sh --dry-run
forge fmt --check     # in EVM/
forge build           # in EVM/
```

Safety scans:

```sh
grep -RInE '\b(world-class|industry-leading|military-grade|trusted by [A-Z])' \
  README.md docs/ --include='*.md' \
  ':!docs/internal/**' ':!docs/BRAND.md'
grep -RIn 'web/|next build|npm run build|web/public' \
  --include='*.md' --include='*.yml' --include='*.json' \
  --include='*.py' --include='*.sh' \
  ':!docs/internal/**'
git grep -nE 'PRIVATE_KEY|api_key|apikey|RPC_URL|ETH_RPC_URL|BASE_RPC_URL' \
  -- '*.md' '*.json' '*.py' '*.sh' '*.yml' ':!docs/internal/**'
```

## 15. Passing Checks

| Check | Result |
|---|---|
| `validate_metadata.py` | ok: 18 entries valid |
| `generate_registry.py --check` | ok: 18 entries |
| `score_pocs.py --check` | ok: matrix unchanged (18 entries) |
| `generate_verification_report.py --check` | ok: 18 entries processed, 0 changed |
| `poc_maturity_index.py --check` | ok |
| `research_dashboard.py --check` | ok |
| `forge fmt --check` (EVM) | ok |
| `forge build` (EVM) | ok (lint warnings only on existing PoC code; not regressions) |
| `github_surface_setup.sh --dry-run` | renders intended description + 12 topics; no apply |
| Hype-phrase scan | zero hits on public surface |
| Stale `web/` scan | zero hits on public surface |
| Live-target framing scan | zero hits outside prohibition lists |
| Secret name scan | env-var names only; no values |

## 16. Skipped Checks and Why

| Skipped | Why |
|---|---|
| Archival fork tests (`forge test`) | Out of scope for this phase. No `ETH_RPC_URL` configured locally. Verification milestones are a separate release type. |
| `gh repo edit ... --apply` | Not autonomous. Manual confirmation required per the GitHub surface setup spec. |
| Social-preview PNG upload | Cannot be automated through `gh`; Repository Settings UI required. |
| Tag and push | Out of scope. This phase ends at "ready to commit". |
| New PoC additions | Out of scope. Corpus-growth is a corpus-milestone release type. |
| Solidity-test edits | Explicitly forbidden by phase scope. |

## 17. Remaining Risks

- **Lint warnings in PoC source.** `forge build` reports
  `erc20-unchecked-transfer` and `unsafe-typecast` warnings on existing
  PoC tests. These are not regressions introduced this phase, but the
  release notes should mention them or the next assertion-hardening
  release should resolve them.
- **Verification reports remain skeletons.** All 18 reports under
  `reports/verification/` retain placeholder verifier handles,
  meaning maturity index correctly reports L4=0. This is honest, not
  a bug. The first archival verification milestone resolves it.
- **Public-RPC smoke coverage is partial.** Only 2 of 18 entries have
  any `latest_public_rpc_status` recorded. Most historical mainnet
  PoCs cannot smoke-test on public endpoints anyway, so this is more
  a documentation completeness gap than a research gap.
- **Banned-phrase CI scan is heuristic.** It catches the phrases
  enumerated in the regex; it does not catch hype framings written in
  novel wording. The PR template's no-overclaiming gate is the
  qualitative backstop.
- **Manual GitHub steps are still required** before the public
  release feels finished — see section 18.

## 18. Manual GitHub Steps

These cannot be automated by this phase. Run them in order, after the
release branch is merged to `main`.

1. **Apply the GitHub surface.** From the repo root:
   ```sh
   bash scripts/github_surface_setup.sh --apply
   ```
   Confirms the description and the 12 topics are set on the
   repository.

2. **Upload the social preview.** Convert
   `.github/assets/social-preview.svg` to a `1280x640` PNG and upload
   via Repository Settings → Social preview → Upload image. The PNG is
   not committed; the SVG and asset README are.

3. **Set GitHub profile name / bio / avatar.** Maintainer profile
   should match the README attribution (Yudistira Putra / `arkheionx`).
   Bio should reference defensive DeFi research; avoid claimed
   affiliations the maintainer does not have.

4. **Pin the repo on the GitHub profile.** So the archive is the first
   thing visitors see.

5. **Open the release PR** (if the branch is not yet merged):
   ```sh
   gh pr create --base main --head arkheionx/research-grade-rebuild \
     --title "feat(repo): finalize Arkheionx Vault authority layer" \
     --body-file <release-pr-body.md>
   ```
   PR body should include the corpus snapshot, the file list, and a
   link to this report.

6. **Review CI.** All three workflows (`metadata`, `evm`, `docs`)
   must be green. The `evm` fork-test job is expected to skip with
   the clarified notice; that is correct, not a regression.

7. **Merge** only after every checklist box in
   `docs/RELEASE_CHECKLIST.md` is honestly ticked.

8. **Tag from `main`** (do not tag from a feature branch):
   ```sh
   git checkout main && git pull
   git tag -a v1.0.0 -m "Arkheionx Vault v1.0.0 — research-grade rebuild"
   git push origin v1.0.0
   ```

9. **Publish the GitHub release** using
   `docs/launch/GITHUB_RELEASE_NOTES.md` instantiated against the
   tagged corpus.

10. **Decide announcement.** If announcing, follow
    `docs/LAUNCH_PLAN.md`. If not, stay quiet.

## 19. Recommended Commit Groups

Splitting the final phase into reviewable commits makes the PR easier
to read. Suggested groups:

1. `feat(maturity): add PoC maturity model and index generator`
   - `docs/POC_MATURITY_MODEL.md`
   - `scripts/poc_maturity_index.py`
   - `reports/poc_maturity_index.md`

2. `feat(reports): add research dashboard generator`
   - `scripts/research_dashboard.py`
   - `reports/research_dashboard.md`

3. `feat(intake): add research candidate, hardening, and unsafe-content templates`
   - `.github/ISSUE_TEMPLATE/research_candidate.md`
   - `.github/ISSUE_TEMPLATE/assertion_hardening.md`
   - `.github/ISSUE_TEMPLATE/unsafe_content_report.md`

4. `feat(expansion): add priority lanes and rejection criteria`
   - `metadata/backlog/priority-lanes.md`
   - `metadata/backlog/rejection-criteria.md`
   - `docs/EXPANSION_PLAN.md` (intake-rubric reference)

5. `feat(release): add release process, checklist, and launch plan`
   - `docs/RELEASE_PROCESS.md`
   - `docs/RELEASE_CHECKLIST.md`
   - `docs/LAUNCH_PLAN.md`
   - `docs/launch/GITHUB_RELEASE_NOTES.md`
   - `docs/launch/LINKEDIN_LAUNCH_POST.md`
   - `docs/launch/X_THREAD.md`

6. `chore(ci): tighten metadata, docs, and evm workflows`
   - `.github/workflows/metadata.yml`
   - `.github/workflows/docs.yml`
   - `.github/workflows/evm.yml`

7. `chore(repo): harden PR template and refresh README status`
   - `.github/pull_request_template.md`
   - `README.md`
   - `scripts/github_surface_setup.sh`

8. `docs(internal): add final release orchestration log and report`
   - `docs/internal/FINAL_RELEASE_ORCHESTRATION_LOG.md`
   - `docs/internal/FINAL_RELEASE_CANDIDATE_REPORT.md`

The Phase 10 working log
(`docs/internal/PHASE_10_AUTHORITY_LAYER.md`) — already in the working
tree from a prior session — is committed alongside group 1 if it
documents the maturity model rollout.

A single bundle commit is also acceptable:

```
feat(repo): finalize Arkheionx Vault authority layer
```

Choice between split and bundle is a maintainer call.

## 20. Recommended Push / PR Steps

```sh
# from the working branch, after committing the groups above
git status --short
git log --oneline -10

# push the branch (no force)
git push -u origin arkheionx/research-grade-rebuild

# create the PR
gh pr create --base main --head arkheionx/research-grade-rebuild \
  --title "feat(repo): finalize Arkheionx Vault authority layer" \
  --body-file docs/internal/FINAL_RELEASE_CANDIDATE_REPORT.md

# wait for CI; only merge after green
gh pr checks
```

Do not force-push. Do not skip hooks. Do not merge with failing CI.

## 21. Recommended Next 30 Days

Order matters; later items depend on earlier ones.

1. Configure an archival mainnet RPC (and Base, for `2025-11-moonwell`).
2. Run the existing 11 assertion-hardened PoCs against the archival
   fork. Fill `reports/verification/<id>.md` with the real run
   transcript, the verifier handle, the date, and the commit SHA.
3. For PoCs whose archival run passes, flip
   `reproducibility: deterministic-confirmed` and
   `verification_status: verified`. Regenerate dashboard and maturity
   index. Confirm L4 count moves above zero.
4. Cut the first verification milestone release (`v1.1.0`) when the
   first batch reaches L4.
5. Lift the 7 weak-assertion PoCs to medium / strong using
   `.github/ISSUE_TEMPLATE/assertion_hardening.md` as the per-PoC PR
   driver. One PoC per PR.
6. Resolve the lint warnings (`erc20-unchecked-transfer`,
   `unsafe-typecast`) on existing PoC code as part of those PRs.
7. Open backlog candidate files for the next 5–7 incidents, one per
   priority lane, before adding any. Treat the backlog as the queue,
   not a private list.

## 22. Recommended Next 100 Days

1. Reach M1 (25 assertion-hardened PoCs) per
   `docs/EXPANSION_PLAN.md`.
2. Reach M1b (25 archival-verified PoCs) when archival RPC quota
   allows. This is the milestone where the archive transitions from
   "structured corpus" to "verified corpus".
3. Write the first L5 case study. Pick the cleanest L4 entry and
   produce: long-form write-up, patch lesson, auditor checklist
   walkthrough, root-cause playbook reference. The case-study release
   type exists for this.
4. Open the backlog for external candidates. Until the rejection
   rubric is exercised against real submissions, the rubric has not
   been tested.
5. Decide whether SVM or MoveVM warrants a real PoC. The scaffolds
   should not stay scaffolds indefinitely; either ship a real PoC per
   VM or note the deprecation in `docs/VM_SUPPORT.md`.
6. Re-evaluate the public-facing surface. The README, the dashboard,
   and the maturity model should still feel honest after another
   quarter of work; if any of them drifts toward overclaiming, fix
   that before adding more PoCs.

End of report.

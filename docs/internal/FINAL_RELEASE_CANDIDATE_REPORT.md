# Arkheionx Vault Final Release Candidate Report

Date: 2026-05-23
Branch: `agent/03-release-redteam`
Maintainer: Yudistira Putra (`arkheionx`)

## 1. Summary

The repository is push-ready as an open-source DeFi exploit PoC
research archive. This phase added the maturity ladder, maturity index,
research dashboard, expanded contributor system, release process,
launch kit, GitHub surface assets, and CI gates. No PoC source was
modified. No verification claim was upgraded. No fake affiliations,
counts, or credentials were introduced.

## 2. Current Repository Truth

- 18 historical DeFi exploit PoCs.
- 0 entries promoted to deterministic-confirmed.
- Maturity distribution: L0:0 · L1:7 · L2:10 · L3:1 · L4:0 · L5:0.
- 7 strong, 4 medium, 7 weak/none static assertion entries.
- 1 entry has `latest_public_rpc_status=public-rpc-pass` (Moonwell).
- Archival mainnet RPC remains the primary L3 → L4 blocker.

## 3. Final Public Surface

- `README.md` — current-state table, maturity ladder, links to
  dashboards, registry table.
- `docs/` — standards, taxonomy, maturity model, release process,
  launch plan, brand, ethics, security.
- `docs/launch/` — LinkedIn, GitHub release notes, X thread drafts.
- `metadata/` — registry, schema, backlog with priority lanes and
  rejection criteria.
- `reports/` — quality matrix, maturity index, research dashboard,
  per-PoC verification reports.
- `scripts/` — validate, generate, score, maturity-index, dashboard,
  GitHub surface setup.
- `.github/` — issue templates, PR template, workflows, social preview
  asset.

## 4. README Status

- Hero, thesis, current-status table, maturity ladder, what-this-is /
  is-not, research standard, layout, verification model, assertion
  quality, severity, run instructions, ethics, researcher identity,
  roadmap, generated registry table.
- Numbers reconciled to `metadata/registry.json` and
  `reports/poc_maturity_index.md`.
- No banned hype phrases on public surface; only defensive references
  to such phrases (in `docs/BRAND.md`, `RELEASE_CHECKLIST.md`, etc.).

## 5. Maturity Model

`docs/POC_MATURITY_MODEL.md` defines L0..L5 with strict gating: L4
requires `verification_status=verified` AND
`reproducibility=deterministic-confirmed` AND a verification report
with real run output. Public-RPC observations do not promote past L2.
L5 requires a case study under `reports/case-studies/`.

## 6. Maturity Index

`scripts/poc_maturity_index.py` writes
`reports/poc_maturity_index.md`. Deterministic; `--check` mode used
by CI. Current corpus runs cleanly through the script.

## 7. Research Dashboard

`scripts/research_dashboard.py` writes
`reports/research_dashboard.md` aggregating registry signals. Reads
the maturity index for a level distribution. Deterministic; `--check`
mode used by CI.

## 8. Contributor System

Issue templates in `.github/ISSUE_TEMPLATE/`:

- `research_candidate.md` — propose a new incident.
- `assertion_hardening.md` — propose strengthening assertions.
- `poc_verification_issue.md` — reproducibility divergence.
- `documentation_issue.md` — doc / metadata correction.
- `unsafe_content_report.md` — promote unsafe content concerns.
- `bug_report.md` — broken-PoC reports.
- `config.yml` — disables blank issues, points at ethics.

`pull_request_template.md` enforces one-PoC-per-patch, scope rules,
verification claims discipline, generated-artifacts checks, EVM build
checks, safety review.

## 9. Expansion Engine

`docs/EXPANSION_PLAN.md` defines milestones M1..M5 with quality bars
and review processes. `metadata/backlog/` adds:

- `priority-lanes.md` — oracle, reentrancy, accounting, governance,
  lending, bridge, vault strategy, AMM, token-standard, historical
  high-impact, weird primitives.
- `rejection-criteria.md` — hard rejections (R1..R7), soft rejections
  (S1..S4), what does NOT justify rejection.
- Existing `candidates.template.json` and `README.md` retained.

## 10. Release System

- `docs/RELEASE_PROCESS.md` — principles, roles, types, validation
  sequence, branching/tagging, post-release.
- `docs/RELEASE_CHECKLIST.md` — explicit checkboxes for repo state,
  metadata, EVM, docs, GitHub surface, safety, launch, push readiness.

## 11. Launch Kit

- `docs/LAUNCH_PLAN.md` — goal, channels, tone, follow-ups, what not
  to claim, manual launch steps.
- `docs/launch/LINKEDIN_LAUNCH_POST.md`,
  `GITHUB_RELEASE_NOTES.md`, `X_THREAD.md` — drafts with poster
  notes. Numbers placeholders are tied to README counts.

## 12. GitHub Surface Setup

- `scripts/github_surface_setup.sh` — dry-run by default, `--apply`
  required to mutate. Sets repo description and 12 topics. No
  visibility / deletion / push behaviour.
- `.github/assets/social-preview.svg` — 1280x640 dark technical SVG.
- `.github/assets/README.md` — conversion / upload instructions.

## 13. CI and Validation Gates

- `metadata.yml` — runs validate + 5 generated-artifact `--check`
  scripts on PR.
- `evm.yml` — `forge fmt --check` + `forge build`; optional fork
  test gated on `ETH_RPC_URL` secret with explicit skip notice.
- `docs.yml` — required-doc presence + no-stale-web-references +
  no-banned-hype-phrases checks.

No fake-green CI. Skipped fork tests are reported as skipped, not
passed.

## 14. Safety and Secret Scan

- `git grep` for credential patterns: only env var names in
  `foundry.toml`, `vm.envString("ETH_RPC_URL")` in test setup,
  documentation references in README. No real secrets.
- Hype-phrase scan on public surface: only defensive references
  (banned-phrase lists, brand guide, "Not the largest"). No claims.
- No live-target tooling, scanners, or drain helpers.
- No PoC source change.

## 15. Files Changed

New:

- `docs/POC_MATURITY_MODEL.md`
- `docs/RELEASE_PROCESS.md`
- `docs/RELEASE_CHECKLIST.md`
- `docs/LAUNCH_PLAN.md`
- `docs/launch/LINKEDIN_LAUNCH_POST.md`
- `docs/launch/GITHUB_RELEASE_NOTES.md`
- `docs/launch/X_THREAD.md`
- `docs/internal/FINAL_OPEN_SOURCE_PRODUCTIZATION_LOG.md`
- `docs/internal/FINAL_RELEASE_CANDIDATE_REPORT.md` (this file)
- `scripts/poc_maturity_index.py`
- `scripts/research_dashboard.py`
- `reports/poc_maturity_index.md`
- `reports/research_dashboard.md`
- `metadata/backlog/priority-lanes.md`
- `metadata/backlog/rejection-criteria.md`
- `.github/ISSUE_TEMPLATE/research_candidate.md`
- `.github/ISSUE_TEMPLATE/assertion_hardening.md`
- `.github/ISSUE_TEMPLATE/unsafe_content_report.md`
- `.github/assets/social-preview.svg`
- `.github/assets/README.md`
- `reports/case-studies/` (empty directory reserved)

Modified:

- `README.md` — added maturity ladder section, dashboard links,
  maturity row in status table.
- `docs/ROADMAP.md` — corrected stale Next.js mention.
- `metadata/backlog/README.md` — link priority lanes and rejection
  criteria.
- `.github/pull_request_template.md` — tightened scope/safety/verify.
- `.github/workflows/metadata.yml` — added 4 new --check steps.
- `.github/workflows/docs.yml` — added stale-web + hype-phrase gates,
  required new docs.

Untouched:

- `EVM/src/**`, `EVM/test/**/*.t.sol` — exploit code unchanged.
- `metadata/registry.json` — no entry was modified or promoted.
- `metadata/schema.json` — unchanged.

## 16. Commands Run

- `git status --short`, `git branch --show-current`, `git log --oneline -30`
- `python3 scripts/validate_metadata.py` → ok
- `python3 scripts/generate_registry.py --check` → ok
- `python3 scripts/score_pocs.py --check` → ok
- `python3 scripts/generate_verification_report.py --check` → ok
- `python3 scripts/poc_maturity_index.py` then `--check` → ok
- `python3 scripts/research_dashboard.py` then `--check` → ok
- `bash scripts/github_surface_setup.sh --dry-run` → ok
- `forge fmt --check` (in `EVM/`) → ok
- `forge build --root .../EVM` → ok (lint warnings only)

## 17. Passing Checks

- Schema validation
- README registry generation
- Quality matrix
- Verification report generation
- Maturity index
- Research dashboard
- GitHub surface dry-run
- forge fmt
- forge build

## 18. Skipped Checks and Why

- Fork tests: not run. Public RPC cannot serve historical state for
  most entries; archival RPC unavailable in this phase. Recorded
  honestly per entry; no entry was promoted to verified.
- `forge test`: not run for the same reason.
- `gh repo edit --apply`: explicitly forbidden by the brief.
- Social preview PNG export: not committed; SVG is source of truth.
- GitHub profile / pinned-repo edits: cannot be applied from inside
  the repo. Documented as manual steps.

## 19. Remaining Risks

- The README's "Strong: 7 / Medium: 4 / Weak: 7" line will drift if
  more PoCs are hardened without updating the row. The figures match
  current `assertion_quality` distribution as of this commit.
- The social-preview SVG is committed; the PNG required by GitHub's
  upload UI is not. Documented in `.github/assets/README.md`.
- The launch material contains a hard-coded "18" in the LinkedIn
  draft; updating the count is part of the launch checklist.

## 20. Manual GitHub Steps

1. Commit final changes locally.
2. Push the branch to GitHub.
3. Open a PR (or merge to `main` if direct merging is the intended
   workflow).
4. Run `bash scripts/github_surface_setup.sh --apply` after
   `gh auth login`.
5. Convert `.github/assets/social-preview.svg` to PNG and upload via
   GitHub Settings → Social preview.
6. Update GitHub profile name, bio, avatar per
   `docs/internal/GITHUB_PROFILE_POLISH_CHECKLIST.md`.
7. Pin the repository on the GitHub profile.
8. Review the repo in incognito.
9. Cut a GitHub release from `docs/launch/GITHUB_RELEASE_NOTES.md`.
10. Post LinkedIn copy from `docs/launch/LINKEDIN_LAUNCH_POST.md`.
11. Post X thread from `docs/launch/X_THREAD.md`.

## 21. Recommended Commit Groups

Group A — research surface:

```
git add docs/POC_MATURITY_MODEL.md \
        scripts/poc_maturity_index.py \
        scripts/research_dashboard.py \
        reports/poc_maturity_index.md \
        reports/research_dashboard.md
git commit -m "feat(research): add PoC maturity ladder and research dashboard"
```

Group B — contributor and release infra:

```
git add .github/ISSUE_TEMPLATE/research_candidate.md \
        .github/ISSUE_TEMPLATE/assertion_hardening.md \
        .github/ISSUE_TEMPLATE/unsafe_content_report.md \
        .github/pull_request_template.md \
        .github/workflows/metadata.yml \
        .github/workflows/docs.yml \
        docs/RELEASE_PROCESS.md \
        docs/RELEASE_CHECKLIST.md \
        metadata/backlog/README.md \
        metadata/backlog/priority-lanes.md \
        metadata/backlog/rejection-criteria.md
git commit -m "chore(repo): add contributor and release infrastructure"
```

Group C — launch surface:

```
git add README.md \
        docs/ROADMAP.md \
        docs/LAUNCH_PLAN.md \
        docs/launch/ \
        .github/assets/
git commit -m "docs(launch): prepare Arkheionx Vault public release"
```

Group D — internal report:

```
git add docs/internal/FINAL_OPEN_SOURCE_PRODUCTIZATION_LOG.md \
        docs/internal/FINAL_RELEASE_CANDIDATE_REPORT.md
git commit -m "docs(internal): final release candidate report"
```

Or one combined commit if preferred:

```
git add -A
git commit -m "feat(repo): finalize Arkheionx Vault open-source release candidate"
```

## 22. Push Instructions

```
git push -u origin agent/03-release-redteam
```

Do NOT force-push. Do NOT push to `main` directly without review.

## 23. PR / Main Merge Instructions

```
gh pr create \
  --base main \
  --head agent/03-release-redteam \
  --title "Arkheionx Vault: open-source release candidate" \
  --body-file docs/launch/GITHUB_RELEASE_NOTES.md
```

Or, if direct main is intended:

```
git checkout main
git merge --no-ff agent/03-release-redteam
git push origin main
```

(The user controls the merge; this report does not push.)

## 24. Next 30 Days

- Configure an archival mainnet RPC; re-run public-rpc-not-archival
  entries to clear L3.
- Promote a first entry past L4 with a real verification report.
- Open the first research-candidate issue using the new template.
- Begin the first L4 entry's case study under
  `reports/case-studies/`.

## 25. Next 100 Days

- Reach 25 PoCs at L2+ with an even distribution across priority
  lanes.
- Reach 5 PoCs at L4 with verification reports containing real run
  output.
- Publish a follow-up post on the assertion-patch pattern (one of
  the recent strong-assertion entries) once an L4 case study is
  ready.
- Begin SVM and MoveVM coverage only when there is a real PoC to
  merge — not as scaffolding expansion.

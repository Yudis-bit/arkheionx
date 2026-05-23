# Release Checklist

Run this checklist before pushing a release branch or merging to main.
Every item is honestly checked or explicitly N/A.

## Repository state

- [ ] `git status --short` is clean (or contains only the staged
      release changes).
- [ ] On a feature or release branch, not directly on `main`.
- [ ] No `web/` directory present.
- [ ] No leftover frontend artifacts (`node_modules`, `.next`, etc.).
- [ ] No real RPC URLs, private keys, or `.env` content committed.
- [ ] `.env.example` contains only variable names, no values.

## Metadata and registry

- [ ] `python scripts/validate_metadata.py` passes.
- [ ] `python scripts/generate_registry.py --check` passes.
- [ ] `python scripts/score_pocs.py --check` passes.
- [ ] `python scripts/generate_verification_report.py --check` passes.
- [ ] `python scripts/poc_maturity_index.py --check` passes.
- [ ] `python scripts/research_dashboard.py --check` passes.
- [ ] No PoC was promoted to `deterministic-confirmed` without a
      verification report containing real run output.
- [ ] No `verification_status` was set to `verified` without a real
      run.

## EVM build

- [ ] `forge fmt --check` passes from `EVM/`.
- [ ] `forge build` passes from `EVM/`.
- [ ] If a fork test was run, the chain alias and block are recorded
      in the relevant verification report.

## Documentation

- [ ] README current-status table matches the registry counts.
- [ ] README does not contain banned phrases (`largest`, `world-class`,
      `industry-leading`, `military-grade`, `AI-powered`, `trusted by`,
      `verified archive`, `drain framework`).
- [ ] README does not imply affiliation with any audit firm, contest
      platform, or bounty program.
- [ ] `docs/POC_MATURITY_MODEL.md`, `docs/POC_STANDARD.md`,
      `docs/RESEARCH_STANDARD.md`, `docs/ASSERTION_STANDARD.md`,
      `docs/REPRODUCIBILITY_STANDARD.md`,
      `docs/EXPLOIT_TAXONOMY.md`, `docs/EXPANSION_PLAN.md`,
      `docs/RELEASE_PROCESS.md`, and `docs/RELEASE_CHECKLIST.md` all
      present.
- [ ] Generated reports exist:
      `reports/poc_quality_matrix.md`,
      `reports/poc_maturity_index.md`,
      `reports/research_dashboard.md`.

## GitHub surface

- [ ] `bash scripts/github_surface_setup.sh --dry-run` runs cleanly.
- [ ] `.github/assets/social-preview.svg` exists and is current.
- [ ] `.github/ISSUE_TEMPLATE/research_candidate.md`,
      `assertion_hardening.md`, `unsafe_content_report.md`,
      `poc_verification_issue.md`, `documentation_issue.md`,
      and `bug_report.md` are all present.
- [ ] `.github/pull_request_template.md` enforces the safety checklist.
- [ ] `.github/workflows/metadata.yml`, `evm.yml`, and `docs.yml`
      reference the correct scripts and required files.

## Safety

- [ ] No live-target tooling, scanners, or drain helpers added.
- [ ] No PoC source change in this release without an explicit note.
- [ ] No new affiliation, bounty win, audit credit, or contest claim
      that is not backed by a public source already cited in the
      relevant entry.
- [ ] Personal information limited to the maintainer's own GitHub
      handle and stated identity (`Yudistira Putra` /
      `arkheionx` / `@Yudis-bit`).

## Launch (only for launch releases)

- [ ] `docs/LAUNCH_PLAN.md` reviewed.
- [ ] `docs/launch/LINKEDIN_LAUNCH_POST.md` numbers match the README.
- [ ] `docs/launch/GITHUB_RELEASE_NOTES.md` numbers match the README.
- [ ] `docs/launch/X_THREAD.md` numbers match the README.
- [ ] No launch copy claims affiliation, bounty wins, or "verified
      archive" status the registry does not back.
- [ ] Social preview asset exported / uploaded as PNG (manual step,
      see `.github/assets/README.md`).

## Push readiness

- [ ] Branch named `agent/...` or `release/...` (not `main`).
- [ ] PR description references the release type and the validation
      output above.
- [ ] If this is a major release, a release tag is prepared.
- [ ] No `--no-verify` was used in any commit.

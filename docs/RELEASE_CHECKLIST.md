# Release Checklist

A release is not cut until every applicable box is checked or marked N/A with a
written reason in the release PR.

## Scope

- [ ] Release type identified: scanner, rule pack, archive, verification,
      docs, or service surface.
- [ ] Version named in `CHANGELOG.md`.
- [ ] No unsupported claims added to README, docs, reports, or release notes.
- [ ] Current archive truth preserved: 18 structured PoCs, 0 L4+ archival
      confirmed entries unless regenerated artifacts prove otherwise.

## v3.8.0 Protocol Intelligence Core Machine Leverage — Agent 13 Final Local Release Checks

Release prep (Agent 12) is complete (decision `READY_FOR_V3_8_FINAL_LOCAL_RELEASE`).
Agent 13 finalized the local release on 2026-06-05: metadata set to `3.8.0`
(current milestone `v3.8.0`, next milestone `v3.9.0`, latest stable `v3.1.0`
unchanged), the release notes and changelog finalized and dated, the version-lock
test literals updated, and validation re-run before the commit. The items
completed before the final commit are checked below; the final commit, the local
annotated `v3.8.0` tag, and the backup bundle are created at finalization and
confirmed in `docs/dev/AGENT13_V3_8_FINAL_LOCAL_RELEASE.md`. Push, publication,
GitHub Release, and post-release cleanup remain not done and require explicit
approval.

- [x] Confirm the Agent 12 decision is `READY_FOR_V3_8_FINAL_LOCAL_RELEASE` and
      the release-prep commit (`docs(release): prepare Arkheionx v3.8.0`) is
      present.
- [x] Confirm the branch is `feat/v3.8.0-protocol-intelligence-core`.
- [x] Confirm the worktree is clean (no staged files, no merge conflicts, no
      untracked tooling artifact such as a `.kiro/` directory).
- [x] Confirm the `v3.7.0` tag is present.
- [x] Confirm the `v3.8.0` tag is absent before finalization.
- [x] Confirm metadata is still `3.7.0` / stable `v3.1.0` / current `v3.7.0` /
      next `v3.8.0` before the bump.
- [x] Run the protocol intelligence core smoke (role / value-path / assumption /
      test-gap / graph / coverage modules import side-effect free, deterministic
      IDs, `manual_review_required` true, `ready_for_submission` false).
- [x] Run the graph context smoke (evidence/report `protocol_graph_context` is
      optional, builds from supplied objects, and does not change evidence
      readiness or the report draft/manual-review behavior).
- [x] Run the review-package graph smoke (artifact count rises with graph
      artifacts, the seven optional kinds are included, the required kinds are
      unchanged, malformed JSON and overclaim are caught, and the export is
      deterministic).
- [x] Run the JSON purity checks for `local-validate --json --no-write`,
      `local-validate --json`, `review-package --json`, and
      `review-package --export zip --json`.
- [x] Run the no-overclaim checks over generated temp artifacts
      (`manual_review_required` true, `ready_for_submission` false, no automatic
      `HUMAN_REVIEWED`, no confirmed-vulnerability / final-severity / audit-passed
      / bounty-eligibility wording).
- [x] Run `python3 scripts/check_docs_links.py --check`.
- [x] Run `python3 scripts/check_safety_wording.py --strict`.
- [x] Run `python3 scripts/check_version_consistency.py --check`.
- [x] Run `python3 scripts/check_release_readiness.py --check`.
- [x] Run the full suite: `python3 -m unittest discover -s tests -p "test_*.py"`.
- [x] Run writable `make validate` with `/tmp` `PYTHONUSERBASE` and
      `PIP_CACHE_DIR`.
- [x] Finalize `release-notes/v3.8.0.md`: set the release date and replace the
      DRAFT / Release Prep status with the final local release status only after
      validation passes.
- [x] Finalize the `CHANGELOG.md` v3.8.0 section: set the date and replace the
      `## v3.8.0 — DRAFT / Release Prep` heading with the final dated heading.
- [x] Only during final release, bump metadata in `arkheionx/version.py` and
      `pyproject.toml`: package version `3.8.0`, current milestone `v3.8.0`, next
      milestone `v3.9.0`; keep the latest stable release at `v3.1.0` unless
      project policy explicitly changes it.
- [x] Update version-lock tests if the metadata bump requires it (frozen version
      / milestone literals only; no test logic change).
- [x] Re-run the full validation matrix after the metadata bump (repository
      checks, full suite, and writable `make validate`).
- [x] Preserve safety wording: local/static only, no new graph CLI, no
      protocol-graph writer, no RPC, no fork-url, no private keys, no seed
      phrases, no live-chain calls, no transaction broadcasting, no exploit
      automation, no auto-submit, no automatic `HUMAN_REVIEWED`, no confirmed
      vulnerabilities, no final severity, no audit-passed claim, no bounty
      eligibility, graph consistency does not prove safety, graph warnings do not
      prove a vulnerability, manual review required, `ready_for_submission` false.
- [x] Confirm v3.8 stays additive: no new public command, exact-only linking,
      deterministic IDs, no public schema-breaking migration, and no existing
      artifact shape changed.
- [ ] Create the final local release commit.
- [ ] Create the local annotated tag `v3.8.0`.
- [ ] Create the local backup bundle:
      `~/Documents/Arkheionx-backups/arkheionx-v3.8.0-local.bundle`.
- [ ] Verify the backup bundle with `git bundle verify`.
- [ ] Do not push.
- [ ] Do not publish.
- [ ] Do not create a GitHub Release.
- [ ] Do not run post-release cleanup unless explicitly approved.

## v3.7.0 Foundry / Local Validation Integration — Agent 12 Final Local Release Checks

Release prep (Agent 11) is complete (decision
`READY_FOR_V3_7_FINAL_LOCAL_RELEASE`). Agent 12 finalized the local release on
2026-06-04: metadata set to `3.7.0` (current milestone `v3.7.0`, next milestone
`v3.8.0`, latest stable `v3.1.0` unchanged), the release notes and changelog
finalized and dated, the version-lock test literals updated, and validation
re-run before the commit. The items completed before the final commit are checked
below; the final commit, the local annotated `v3.7.0` tag, and the backup bundle
are created at finalization and confirmed in
`docs/dev/AGENT12_V3_7_FINAL_LOCAL_RELEASE.md`. Push, publication, GitHub Release,
and post-release cleanup remain not done and require explicit approval.

- [x] Confirm the Agent 11 decision is `READY_FOR_V3_7_FINAL_LOCAL_RELEASE` and
      the release-prep commit (`docs(release): prepare Arkheionx v3.7.0`) is
      present.
- [x] Confirm the branch is `feat/v3.7.0-foundry-local-validation`.
- [x] Confirm the worktree is clean (no staged files, no merge conflicts, no
      untracked tooling artifact such as a `.kiro/` directory).
- [x] Confirm the `v3.6.0` tag is present.
- [x] Confirm the `v3.7.0` tag is absent before finalization.
- [x] Confirm metadata is still `3.6.0` / stable `v3.1.0` / current `v3.6.0` /
      next `v3.7.0` before the bump.
- [x] Run the local-validation smoke (no-write, write, and deterministic re-run)
      on a saved Foundry output fixture, confirming `manual_review_required` true,
      `ready_for_submission` false, repo-relative paths, and a stable checksum
      map.
- [x] Run the review-package integration smoke, confirming the local-validation
      artifacts are included (manifest, checksums, deterministic export) and that
      there is no safety failure.
- [x] Run the evidence/report support tests
      (`tests.test_evidence_local_validation`,
      `tests.test_report_local_validation`), confirming support is context only,
      a tested-only signal does not create `EVIDENCE_READY`, and the report stays
      a draft requiring manual review.
- [x] Run the JSON purity checks for `local-validate --json --no-write`,
      `local-validate --json`, `review-package --json`, and
      `review-package --export zip --json`.
- [x] Run `python3 scripts/check_docs_links.py --check`.
- [x] Run `python3 scripts/check_safety_wording.py --strict`.
- [x] Run `python3 scripts/check_version_consistency.py --check`.
- [x] Run `python3 scripts/check_release_readiness.py --check`.
- [x] Run the full suite: `python3 -m unittest discover -s tests -p "test_*.py"`.
- [x] Run writable `make validate` with `/tmp` `PYTHONUSERBASE` and
      `PIP_CACHE_DIR`.
- [x] Finalize `release-notes/v3.7.0.md`: set the release date and replace the
      DRAFT / Release Prep status with the final local release status only after
      validation passes.
- [x] Finalize the `CHANGELOG.md` v3.7.0 section: set the date and replace the
      `## v3.7.0 — DRAFT / Release Prep` heading with the final dated heading.
- [x] Only during final release, bump metadata in `arkheionx/version.py` and
      `pyproject.toml`: package version `3.7.0`, current milestone `v3.7.0`, next
      milestone `v3.8.0`; keep the latest stable release at `v3.1.0` unless
      project policy explicitly changes it.
- [x] Update version-lock tests if the metadata bump requires it (frozen version
      / milestone literals only; no test logic change).
- [x] Re-run the full validation matrix after the metadata bump (repository
      checks, full suite, and writable `make validate`).
- [x] Preserve safety wording: local/static only, saved Foundry output only, no
      live forge runner, no subprocess runner, no Foundry runtime requirement, no
      RPC, no fork-url, no private keys, no seed phrases, no live-chain calls, no
      transaction broadcasting, no exploit automation, no auto-submit, no
      automatic `HUMAN_REVIEWED`, no confirmed vulnerabilities, no final severity,
      no audit-passed claim, no bounty eligibility, manual review required,
      `ready_for_submission` false.
- [x] Confirm v3.7 stays additive: `local-validate` is the only new command, no
      public schema-breaking migration, and no existing artifact shape changed.
- [ ] Create the final local release commit.
- [ ] Create the local annotated tag `v3.7.0`.
- [ ] Create the local backup bundle:
      `~/Documents/Arkheionx-backups/arkheionx-v3.7.0-local.bundle`.
- [ ] Verify the backup bundle with `git bundle verify`.
- [ ] Do not push.
- [ ] Do not publish.
- [ ] Do not create a GitHub Release.
- [ ] Do not run post-release cleanup unless explicitly approved.

## v3.6.0 Review Package Workspace — Agent 11 Final Local Release Checks

Release prep (Agent 10) is complete: `release-notes/v3.6.0.md` drafted as
release prep, the `## v3.6.0` CHANGELOG section added as a draft, this checklist
updated, and `docs/dev/AGENT10_V3_6_RELEASE_PREP.md` written. Agent 11 finalized
the local release on 2026-06-04: metadata set to `3.6.0`, release notes and
changelog dated, and validation re-run before the commit. The items completed
before the final commit are checked below; the final commit, the local annotated
`v3.6.0` tag, and the backup bundle are created at finalization and confirmed in
`docs/dev/AGENT11_V3_6_FINAL_LOCAL_RELEASE.md`. Push, publication, GitHub
Release, and post-release cleanup remain not done and require explicit approval.

- [x] Confirm the Agent 10 decision is `READY_FOR_V3_6_FINAL_LOCAL_RELEASE` and
      the release-prep commit (`docs(release): prepare Arkheionx v3.6.0`) is
      present.
- [x] Rerun preflight: branch `feat/v3.6.0-review-package-workspace`, no staged
      files, no merge conflicts, `v3.5.0` tag present, `v3.6.0` tag absent,
      metadata still `3.5.0` / `v3.1.0` / `v3.5.0` / `v3.6.0`.
- [x] Clean any untracked tooling artifacts (for example a `.kiro/` directory
      created by tooling); do not stage or commit them, and confirm the tracked
      worktree is clean before editing.
- [x] Rerun the review-package smoke workflow on the bundled `lending-vault`
      demo: `--no-write`, write, and `--export zip`, confirming
      `manual_review_required` true, `ready_for_submission` false, no absolute
      path in generated package metadata, the protocol-model sidecar, and a
      deterministic export checksum.
- [x] Rerun the review-package suites: `tests.test_review_package_ids`,
      `tests.test_review_package_model`, `tests.test_review_package_collector`,
      `tests.test_review_package_manifest`, `tests.test_review_package_checksums`,
      `tests.test_review_package_validation`, `tests.test_review_package_builder`,
      `tests.test_review_package_cli`, `tests.test_review_package_export`,
      `tests.test_review_package_cli_export`,
      `tests.test_review_package_intelligence`,
      `tests.test_review_package_crossref`,
      `tests.test_review_package_cli_intelligence`.
- [x] Rerun the v3.5 intelligence tests: `tests.test_intelligence_ids`,
      `tests.test_intelligence_model`, `tests.test_intelligence_build`,
      `tests.test_review_map_intelligence_ids`,
      `tests.test_intelligence_reasoning_links`,
      `tests.test_intelligence_artifact_links`,
      `tests.test_intelligence_compatibility`,
      `tests.test_intelligence_target_resolution`,
      `tests.test_intelligence_public_regression`.
- [x] Rerun the v3.4 contract / public tests: `tests.test_execution_proof`,
      `tests.test_evidence`, `tests.test_report`, `tests.test_evidence_links_cli`,
      `tests.test_evidence_status`, `tests.test_review_map_artifacts`,
      `tests.test_focused_review_commands_integration`,
      `tests.test_public_surface_contract`, `tests.test_public_workflow`,
      `tests.test_package_imports`.
- [x] Rerun repository checks: `check_docs_links.py --check`,
      `check_safety_wording.py --strict`, `check_version_consistency.py --check`,
      `check_release_readiness.py --check`.
- [x] Rerun the full suite: `python3 -m unittest discover -s tests -p "test_*.py"`.
- [x] Rerun writable `make validate` with `/tmp` `PYTHONUSERBASE` and
      `PIP_CACHE_DIR`.
- [x] Finalize `release-notes/v3.6.0.md`: set the release date and replace the
      draft / release-prep banner with the final local release status only after
      validation passes.
- [x] Finalize the `CHANGELOG.md` v3.6.0 section: set the date and replace the
      draft / release-prep heading with the final heading.
- [x] Only during final release, update metadata to `3.6.0`:
      `arkheionx/version.py` and `pyproject.toml`.
- [x] Only during final release, update the current milestone to `v3.6.0`.
- [x] Only during final release, update the next milestone to `v3.7.0`.
- [x] Keep the latest stable release at `v3.1.0` unless project policy requires
      otherwise.
- [x] Preserve safety wording: local/static only, no RPC, no private keys, no
      seed phrases, no live-chain calls, no transaction broadcasting, no exploit
      automation, no auto-submit, no automatic `HUMAN_REVIEWED`, no confirmed
      vulnerabilities, no final severity, no audit-passed claim, no bounty
      eligibility, manual review required, `ready_for_submission` false.
- [x] Confirm v3.6 stays additive: `review-package` is the only new command, no
      public schema-breaking migration, and no existing artifact shape changed.
- [ ] Create the final local release commit.
- [ ] Create the local annotated tag `v3.6.0`.
- [ ] Create the local backup bundle:
      `~/Documents/Arkheionx-backups/arkheionx-v3.6.0-local.bundle`.
- [ ] Do not push.
- [ ] Do not publish.
- [ ] Do not create a GitHub Release.
- [ ] Do not run post-release cleanup unless explicitly approved.

## v3.5.0 Protocol Intelligence Model — Agent 10 Final Local Release Checks

Release prep (Agent 9) is complete: `release-notes/v3.5.0.md` drafted, the
`## v3.5.0` CHANGELOG section added, docs aligned, and this checklist updated.
Agent 10 finalized the local release on 2026-06-03: metadata set to `3.5.0`,
release notes and changelog dated, validation re-run, final commit created, and
the local annotated `v3.5.0` tag created. Push, publication, GitHub Release, and
post-release cleanup remain pending and require explicit approval.

- [x] Final release starts from a clean `feat/v3.5.0-protocol-intelligence-model`
      worktree with the Agent 9 release-prep commit (`docs(release): prepare
      Arkheionx v3.5.0`) present and Agent 9 decision
      `READY_FOR_V3_5_FINAL_LOCAL_RELEASE`.
- [x] Rerun preflight: branch correct, worktree clean, no staged files, no merge
      conflicts, `v3.4.0` tag present, `v3.5.0` tag absent, metadata still
      `3.4.0` / `v3.1.0` / `v3.4.0` / `v3.5.0`.
- [ ] (N/A — deferred) The duplicate
      `docs(dev): plan v3.5 intelligence swarm execution` commit was left intact;
      reconciling it needs a history rewrite, out of scope for the final local
      release. All ten required v3.5 commits are present.
- [x] Rerun targeted intelligence tests:
      `tests.test_intelligence_ids`, `tests.test_intelligence_model`,
      `tests.test_intelligence_build`, `tests.test_review_map_intelligence_ids`,
      `tests.test_intelligence_reasoning_links`,
      `tests.test_intelligence_artifact_links`,
      `tests.test_intelligence_compatibility`,
      `tests.test_intelligence_target_resolution`,
      `tests.test_intelligence_public_regression`.
- [x] Rerun targeted v3.4 contract tests:
      `tests.test_execution_proof`, `tests.test_evidence`, `tests.test_report`,
      `tests.test_evidence_links_cli`, `tests.test_evidence_status`,
      `tests.test_review_map_artifacts`,
      `tests.test_focused_review_commands_integration`,
      `tests.test_public_surface_contract`, `tests.test_public_workflow`,
      `tests.test_package_imports`.
- [x] Rerun repository checks:
      `check_docs_links.py --check`, `check_safety_wording.py --strict`,
      `check_version_consistency.py --check`,
      `check_release_readiness.py --check`.
- [x] Rerun full suite: `python3 -m unittest discover -s tests -p "test_*.py"`.
- [x] Rerun writable `make validate` with `/tmp` `PYTHONUSERBASE` and
      `PIP_CACHE_DIR`.
- [x] Rerun smoke test: `demo --copy lending-vault` then the review/focused
      commands in `--json` mode, plus a deterministic
      `build_protocol_model_from_review_map` build.
- [x] Only during final release, update metadata to `3.5.0`:
      `arkheionx/version.py` and `pyproject.toml`.
- [x] Only during final release, update current milestone to `v3.5.0`.
- [x] Only during final release, update next milestone to `v3.6.0`.
- [x] Keep latest stable release at `v3.1.0` unless project policy requires
      otherwise.
- [x] Date and finalize `release-notes/v3.5.0.md`; remove the draft/release-prep
      banner only after final validation.
- [x] Date and finalize the `CHANGELOG.md` v3.5.0 section.
- [x] Preserve safety wording: local/static only, no RPC, no private keys, no
      live-chain calls, no transaction broadcasting, no exploit automation, no
      auto-submit, no automatic `HUMAN_REVIEWED`, no confirmed vulnerabilities,
      no final severity, no bounty eligibility, manual review required.
- [x] Confirm v3.5 stays additive: no new public CLI command, no public
      schema-breaking migration, no mandatory `protocol-model.json`, old IDs/
      fields preserved.
- [x] Create the final local release commit.
- [x] Create local annotated tag `v3.5.0`.
- [ ] Do not push.
- [ ] Do not publish.
- [ ] Do not create a GitHub Release.
- [ ] Do not run post-release cleanup unless explicitly approved later.

Final local v3.5.0 release was completed on 2026-06-03. Push, publication,
GitHub Release creation, and post-release cleanup remain pending and require
explicit approval.

## v3.4.0 Proof and Evidence Workflow Final Agent 8 Checks

- [x] Final release starts from a clean `feat/v3.4.0-proof-evidence-workflow`
      worktree with Agent 7 release-prep commit present.
- [x] `v3.3.0` local tag exists and `v3.4.0` tag does not exist before final
      release work begins.
- [x] Targeted v3.4 tests pass:
      `tests.test_execution_proof`, `tests.test_evidence`, `tests.test_report`,
      `tests.test_evidence_links_cli`,
      `tests.test_focused_review_commands_integration`,
      `tests.test_review_map_artifacts`, `tests.test_evidence_status`,
      `tests.test_proof_plan_cli`, `tests.test_cli_workbench`,
      `tests.test_public_workflow`, `tests.test_public_surface_contract`, and
      `tests.test_review_map_schema`.
- [x] Repository checks pass:
      `check_docs_links.py --check`, `check_safety_wording.py --strict`,
      `check_version_consistency.py --check`, and
      `check_release_readiness.py --check`.
- [x] Full suite passes: `python3 -m unittest discover -s tests -p "test_*.py"`.
- [x] Writable `make validate` passes with `/tmp` `PYTHONUSERBASE` and
      `PIP_CACHE_DIR`.
- [x] End-to-end smoke passes:
      `proof -> trace -> evidence package -> report draft -> evidence-links -> review-map`.
- [x] Only during final release, update metadata to `3.4.0`:
      `arkheionx/version.py` and `pyproject.toml`.
- [x] Only during final release, update stable/current/next milestones according
      to project policy.
- [x] Date and finalize `release-notes/v3.4.0.md`; remove draft/release-prep
      wording only after final validation.
- [x] Date and finalize the `CHANGELOG.md` v3.4.0 section.
- [x] Preserve safety wording: no RPC, no private keys, no live-chain calls, no
      transaction broadcasting, no exploit automation, no auto-submit, no final
      severity, no confirmed vulnerabilities, no bounty eligibility, and manual
      review required.
- [x] Create the final local release commit.
- [x] Create local annotated tag `v3.4.0`.
- [ ] Do not push.
- [ ] Do not publish.
- [ ] Do not run post-release cleanup unless explicitly approved later.

Final local v3.4.0 release was completed on 2026-06-03. Push, publication,
GitHub Release creation, and post-release cleanup remain pending and require
explicit approval.

## v3.3.0 Focused Review Commands Checks

- [ ] Version metadata remains pending until final release approval; release-prep
      docs do not update `arkheionx/version.py` or `pyproject.toml`.
- [ ] `CHANGELOG.md` has an undated `## v3.3.0 - Unreleased` section for
      Focused Review Commands.
- [ ] `release-notes/v3.3.0.md` is drafted with release date, tag, and final
      metadata marked pending.
- [ ] `arkheionx test-gap-map`, `arkheionx value-paths`,
      `arkheionx assumptions`, `arkheionx proof-plan`, and
      `arkheionx evidence-links` are listed in README, CLI reference, public
      surface, and Review Map docs.
- [ ] All five focused commands support `--json`, `--no-write`, `--out`,
      `--target`, `--top`, and `--include-low-confidence`.
- [ ] Focused commands read existing review-map artifacts when present, derive
      locally through the review-map builder when missing, preserve
      artifact-compatible JSON, and do not alter `review-map --json`.
- [ ] `proof-plan` remains planning-only with no `--run`; `evidence-links`
      remains read-only and does not create evidence or promote evidence levels.
- [ ] Full validation, writable `make validate`, and the five-command smoke test
      pass before final metadata/date/tag work.
- [ ] Final release agent dates the changelog, finalizes release notes, updates
      metadata, commits, and creates the annotated `v3.3.0` tag only after
      explicit human approval.

## v3.1.0 Protocol Review Map Checks

- [ ] Version finalized `3.1.0`; stable pointer moved `v3.0.0` → `v3.1.0` in post-release cleanup; current `v3.1.0`, next `v3.2.0`.
- [ ] `arkheionx review-map <repo>` works on all three bundled demos and writes the nine artifacts under `.arkheionx/out/review-map/`.
- [ ] `--json` emits valid JSON only (no ANSI, even with `ARKHEIONX_COLOR=always`); `--no-write` writes nothing; `--out <dir>` writes to the given dir; `--target` filters; unknown target errors cleanly.
- [ ] `docs/REVIEW_MAP.md` present and linked from README; `docs/PUBLIC_SURFACE.md` lists `arkheionx review-map`; `docs/CLI_REFERENCE.md` documents it.
- [ ] `schemas/review-map.schema.json` present; generated `review-map.json` satisfies it.
- [ ] `release-notes/v3.1.0.md` and `## v3.1.0` changelog section present; no published/PyPI/Homebrew/binary/audit/severity/bounty claims; review-map described as review guidance, not findings.
- [ ] `python3 scripts/check_release_readiness.py --check` passes (also run by `make validate`).
- [ ] Post-release: finalize `3.1.0`, tag `v3.1.0`, publish, then cleanup (`STABLE_RELEASE`→`v3.1.0`, README/Action/install.sh/arkup→v3.1.0, ROADMAP marks v3.1.0 shipped and v3.2.0 current).
- [ ] `tests/test_review_map*.py` cover data model, CLI, artifacts, and schema.

## v3.0.0 Public Stable Launch Checks

- [ ] Version finalized `3.0.0`; stable pointer moved `v2.10.0` → `v3.0.0` in post-release cleanup.
- [ ] `python3 scripts/check_release_readiness.py --check` passes (also run by `make validate`).
- [ ] README is the public-stable landing page; references all v3 visuals (architecture, public-surface, demo-fixtures, stability) and they parse as XML.
- [ ] `docs/PUBLIC_SURFACE.md`, `docs/STABILITY_CONTRACT.md`, `docs/V3_READINESS.md` are accurate and linked from README.
- [ ] `docs/ROADMAP.md` marks v3.0.0 shipped and v3.1.0 current.
- [ ] `release-notes/v3.0.0.md` and `## v3.0.0` changelog section present; no published/PyPI/Homebrew/binary/audit/severity/bounty claims.
- [ ] Post-release: finalize `3.0.0`, tag `v3.0.0`, publish, then cleanup (`STABLE_RELEASE`→`v3.0.0`, README/Action/install.sh/arkup→v3.0.0, ROADMAP shipped).

## v2.10.0 Pre-v3 Public Readiness & Stability Hardening Checks

- [ ] `python3 scripts/check_release_readiness.py --check` passes (also run by `make validate`).
- [ ] `docs/PUBLIC_SURFACE.md` lists every `arkheionx --help` command and the three shell scripts.
- [ ] `docs/STABILITY_CONTRACT.md` and `docs/V3_READINESS.md` present and linked from README/ROADMAP.
- [ ] Version metadata is `2.10.0`; stable pointer moved `v2.9.0` → `v2.10.0` in post-release cleanup (current `v2.10.0`, next `v3.0.0`).
- [ ] `release-notes/v2.10.0.md` and `## v2.10.0` changelog section present.

## v2.9.0 Multi-Fixture Demo Expansion & Public Workflow Hardening Checks

- [ ] `arkheionx demo --list` lists `oracle-staking`, `amm-swap`, `lending-vault` with categories.
- [ ] `arkheionx demo --show <id>` prints category, risk theme, target, and safety notice.
- [ ] `arkheionx demo --commands <id>` uses the correct per-demo target.
- [ ] `arkheionx demo --copy <id> DEST` works (from a non-repo cwd) for every demo; source-only.
- [ ] Package resources exist for every demo (README, foundry.toml, src/*.sol, test/*.sol).
- [ ] No fixture bundles `out/`/`cache/`/`.arkheionx/`, RPC URLs, private keys, or live addresses.
- [ ] `docs/DEMO_WORKFLOW.md` selection table + `docs/PACKAGE_DATA.md` list all demos.
- [ ] `release-notes/v2.9.0.md` and `## v2.9.0` changelog section present.
- [ ] `tests/test_demo_workflow.py` + `tests/test_package_data.py` cover all demos.

## v2.8.0 Package Data & Distribution Hardening Checks

- [ ] Demo fixture bundled under `arkheionx/demo/fixtures/oracle-staking/`.
- [ ] `importlib.resources.files("arkheionx.demo.fixtures").joinpath("oracle-staking")` resolves.
- [ ] `pyproject.toml` has `[tool.setuptools.package-data]` for `arkheionx.demo.fixtures` (md/toml/sol only).
- [ ] `arkheionx demo --show oracle-staking` reports `Source: bundled package fixture`.
- [ ] `arkheionx demo --copy oracle-staking DEST` works from a non-repo cwd.
- [ ] Copy excludes `out/`, `cache/`, `.arkheionx/`; bundled fixture has no secrets/RPC/keys.
- [ ] Non-editable venv install can run `demo --copy` (no source checkout present).
- [ ] `docs/PACKAGE_DATA.md` present; `release-notes/v2.8.0.md` and `## v2.8.0` changelog present.
- [ ] `tests/test_package_data.py` passes; no generated demo artifacts tracked.

## v2.7.0 Guided Demo Fixtures & First Real Workflow Checks

- [ ] `arkheionx demo --list` lists `oracle-staking`.
- [ ] `arkheionx demo --show oracle-staking` prints target + safety notice.
- [ ] `arkheionx demo --commands oracle-staking` prints heuristic + Foundry commands.
- [ ] `arkheionx demo --copy oracle-staking DEST` copies source entries only.
- [ ] Copy refuses a non-empty destination without `--force`; never writes outside DEST.
- [ ] Unknown demo id fails with valid options (exit 2).
- [ ] Demo fixture has no RPC URLs, private keys, secrets, or live-chain instructions.
- [ ] `docs/DEMO_WORKFLOW.md` present; `demo` documented in CLI reference and README.
- [ ] `release-notes/v2.7.0.md` and `## v2.7.0` changelog section present.
- [ ] `tests/test_demo_workflow.py` passes; no generated demo artifacts tracked.

## v2.6.0 arkup & Version-Manager MVP Checks

- [ ] `sh -n install.sh`, `sh -n uninstall.sh`, `sh -n arkup` pass.
- [ ] `sh arkup --help`, `--version`, `--check` work (check works with no receipt).
- [ ] `arkup --check` and `arkheionx doctor --install` agree on install state.
- [ ] `install.sh` writes `~/.arkheionx/install.json` with required fields.
- [ ] Source model verified: stable/main/ref/local resolve correctly.
- [ ] `arkup --update` keeps the recorded source kind (no silent channel change).
- [ ] `uninstall.sh` shows and removes the receipt; path guard still enforced.
- [ ] Dry-run flows change nothing (`install`, `update`, `uninstall`).
- [ ] No sudo, no shell-profile edits, no secrets, no RPC anywhere.
- [ ] No PyPI / Homebrew / binary / domain-installer claims.
- [ ] `schemas/install-receipt.schema.json` present; no runtime receipt committed.
- [ ] `docs/ARKUP.md`, `docs/UPDATE_FLOW.md`, `release-notes/v2.6.0.md`,
      and `## v2.6.0` changelog section present.
- [ ] `tests/test_arkup.py` passes.

## v2.5.0 Installer & Onboarding Checks

- [ ] `sh -n install.sh` and `sh -n uninstall.sh` pass.
- [ ] `sh install.sh --help` and `sh uninstall.sh --help` print usage.
- [ ] `ARKHEIONX_DRY_RUN=1 sh install.sh` prints actions without changes.
- [ ] Local install verified: `ARKHEIONX_LOCAL_PATH="$PWD" sh install.sh` then
      `arkheionx version`.
- [ ] `sh uninstall.sh --dry-run` removes nothing; full run removes only
      `~/.arkheionx`-managed paths.
- [ ] Installer uses no root, edits no shell profile, asks for no secrets, and
      makes no RPC or live-chain calls.
- [ ] No PyPI, domain installer, standalone binary, or Homebrew claims.
- [ ] `arkheionx doctor` unchanged; `arkheionx doctor --install` exits `0`.
- [ ] `docs/INSTALLER.md`, `docs/UNINSTALL.md`, `docs/ONBOARDING.md`,
      `docs/TROUBLESHOOTING.md` present and linked.
- [ ] `release-notes/v2.5.0.md` and `## v2.5.0` changelog section present.
- [ ] `tests/test_installer.py` passes.

## v1.7 Config Stabilization Checks

- [ ] `schemas/arkheionx_config.schema.json` exists and parses.
- [ ] `python3 scripts/validate_config.py --config examples/arkheionx.config.example.json`
- [ ] Every `examples/configs/*.config.json` validates.
- [ ] Dangerous config keys are rejected.
- [ ] Rule-pack registry helpers map finding IDs to rule packs.
- [ ] Scanner accepts `--config` and reports config summary in Markdown/JSON.
- [ ] CLI `--protocol-type` overrides config protocol hints.
- [ ] Suppressions require a written reason.
- [ ] Config safety docs explain rejected keys and local/static boundaries.

## v1.8 Report UX Checks

- [ ] Markdown reports include `Fix First`.
- [ ] JSON reports include `fix_first`.
- [ ] JSON reports include `findings_by_rule_family`.
- [ ] JSON reports include `findings_by_confidence`.
- [ ] Markdown reports include `Suppression Summary`.
- [ ] Markdown reports include compact config and generated artifact settings.
- [ ] CI profile scan produces a compact report.
- [ ] Full profile scan preserves detailed evidence.
- [ ] Issue plans include Fix First ordering and rule family.
- [ ] SARIF includes defensive readiness help text and rule-family metadata.

## Scanner And Product Validation

- [ ] `python3 -m py_compile scripts/pre_audit_scan.py scripts/generate_search_index.py`
- [ ] `python3 -m py_compile scripts/post_pr_comment.py scripts/create_github_issues.py`
- [ ] `python3 -m unittest discover -s tests -p "test_*.py"`
- [ ] Mini-vault scan regenerated:

  ```sh
  python3 scripts/pre_audit_scan.py \
    --root examples/mini-vault \
    --protocol-type auto \
    --output examples/reports/mini-vault-pre-audit-report.md \
    --json-output examples/reports/mini-vault-pre-audit-report.json \
    --sarif-output examples/reports/mini-vault.sarif.json \
    --baseline-output examples/reports/mini-vault.baseline.json \
    --summary-output examples/reports/mini-vault-action-summary.md \
    --comment-output examples/reports/mini-vault-pr-comment.md \
    --issue-checklist-output examples/reports/mini-vault-issue-checklist.md \
    --generate-invariant-skeletons
  ```

- [ ] Vault-risk fixture scan regenerated:

  ```sh
  python3 scripts/pre_audit_scan.py \
    --root examples/vault-risk-fixture \
    --protocol-type vault \
    --output examples/reports/vault-risk-fixture-pre-audit-report.md \
    --json-output examples/reports/vault-risk-fixture-pre-audit-report.json \
    --sarif-output examples/reports/vault-risk-fixture.sarif.json \
    --baseline-output examples/reports/vault-risk-fixture.baseline.json \
    --summary-output examples/reports/vault-risk-fixture-action-summary.md \
    --comment-output examples/reports/vault-risk-fixture-pr-comment.md \
    --issue-checklist-output examples/reports/vault-risk-fixture-issue-checklist.md \
    --generate-invariant-skeletons
  ```

- [ ] Baseline diff scan regenerated:

  ```sh
  python3 scripts/pre_audit_scan.py \
    --root examples/vault-risk-fixture \
    --protocol-type vault \
    --compare-baseline examples/reports/vault-risk-fixture.baseline.json \
    --output examples/reports/vault-risk-fixture-diff-report.md \
    --json-output examples/reports/vault-risk-fixture-diff-report.json \
    --diff-output examples/reports/vault-risk-fixture-diff.md \
    --diff-json-output examples/reports/vault-risk-fixture-diff.json \
    --sarif-output examples/reports/vault-risk-fixture-diff.sarif.json \
    --summary-output examples/reports/vault-risk-fixture-diff-summary.md \
    --comment-output examples/reports/vault-risk-fixture-diff-comment.md \
    --issue-checklist-output examples/reports/vault-risk-fixture-diff-checklist.md
  ```

- [ ] Config suppression scan regenerated:

  ```sh
  python3 scripts/pre_audit_scan.py \
    --root examples/vault-risk-fixture \
    --protocol-type vault \
    --config examples/arkheionx.config.example.json \
    --output examples/reports/vault-risk-fixture-config-report.md \
    --json-output examples/reports/vault-risk-fixture-config-report.json \
    --summary-output examples/reports/vault-risk-fixture-config-summary.md \
    --comment-output examples/reports/vault-risk-fixture-config-comment.md \
    --issue-checklist-output examples/reports/vault-risk-fixture-config-checklist.md
  ```

- [ ] JSON outputs parse successfully.
- [ ] JSON outputs include canonical `findings`.
- [ ] SARIF outputs parse successfully and use SARIF `2.1.0`.
- [ ] SARIF outputs include rules, results, and readiness/not-vulnerability
      properties.
- [ ] Baseline JSON includes finding fingerprints.
- [ ] Diff JSON includes new, resolved, unchanged, changed, and suppressed
      counts.
- [ ] Diff report includes `Baseline Diff`.
- [ ] Markdown reports include the disclaimer.
- [ ] Vault report includes `Vault Rule Pack Coverage`.
- [ ] PR comment output contains `<!-- arkheionx-pre-audit-comment -->`.
- [ ] Summary output contains `Score:`.
- [ ] Generated issue checklist contains Markdown checkboxes.
- [ ] Config suppression output shows `Suppressed Readiness Gaps`.

## v0.5 Issue Workflow And Rule Pack Checks

- [ ] Issue plan JSON generated and parses successfully.
- [ ] Issue plan contains deterministic `<!-- arkheionx-issue:* -->` markers.
- [ ] Issue plan contains defensive disclaimers.
- [ ] `scripts/create_github_issues.py --mode dry-run` makes no API calls and
      writes dry-run output.
- [ ] Real issue creation is not used in CI.
- [ ] Rule pack coverage includes vault, oracle, access/upgradeability,
      reentrancy/value-flow, and reward accounting when relevant.
- [ ] SARIF output includes new rule-pack finding IDs as readiness gaps.
- [ ] Baseline/diff output supports new rule-pack findings.
- [ ] `docs/GITHUB_ISSUE_WORKFLOW.md` documents permissions, dry-run, create,
      update, duplicate prevention, and safety boundaries.

## v0.6 Semantic-Lite And False-Positive Checks

- [ ] JSON reports include `analysis_quality`.
- [ ] JSON reports include `semantic_lite` contracts/functions when enabled.
- [ ] Findings include `evidence`, `confidence_reason`, and
      `detection_sources`.
- [ ] Low-confidence keyword-only findings are visible but downgraded.
- [ ] Issue plans include confidence reasons and top evidence.
- [ ] SARIF locations prefer semantic-lite or Slither evidence where available.
- [ ] Slither absence is graceful unless strict mode is explicitly enabled.
- [ ] `--slither-json` works with a local mock/provided JSON file.
- [ ] `docs/SEMANTIC_LITE_ANALYSIS.md`, `docs/SLITHER_INTEGRATION.md`, and
      `docs/FALSE_POSITIVE_REDUCTION.md` are linked from README.

## v0.7 Delivery Artifact Checks

- [ ] Launch Report Markdown generated and includes `Executive Summary`.
- [ ] Pre-Audit Sprint Plan generated and includes the selected day schedule.
- [ ] Contest Readiness Report generated and includes the scope checklist.
- [ ] Executive Summary generated and fits a short stakeholder handoff format.
- [ ] Remediation Roadmap generated and groups tasks by phase.
- [ ] All delivery artifacts include defensive disclaimers.
- [ ] JSON output includes `delivery_outputs` and `delivery_summary`.
- [ ] GitHub Action exposes delivery output inputs.
- [ ] `docs/LAUNCH_REPORT_OS.md`, `docs/PRE_AUDIT_SPRINT_WORKFLOW.md`,
      `docs/CONTEST_READINESS_MODE.md`, and `docs/DELIVERY_ARTIFACTS.md` are
      linked from README.
- [ ] `SERVICES.md` and `docs/business/MONETIZATION.md` describe delivery artifacts as
      readiness support, not formal audit services.

## v0.8 Demo And Validation Checks

- [ ] `docs/TRY_IN_5_MINUTES.md` exists and the command runs locally.
- [ ] `docs/PUBLIC_DEMO_WORKFLOW.md` explains local and GitHub Action demos.
- [ ] `.github/workflows/arkheionx-demo.yml` is manual-only and creates no
      GitHub issues.
- [ ] Demo artifacts generated under `examples/reports/demo-*`.
- [ ] Demo issue dry-run says no GitHub API calls were made.
- [ ] `docs/case-studies/ORACLE_STAKING_FIXTURE_CASE_STUDY.md` exists.
- [ ] Before/after case study or template exists.
- [ ] `docs/RULE_CALIBRATION.md` and `reports/rule_calibration_summary.md`
      explain confidence, evidence, and false-positive handling.
- [ ] False-positive calibration and external validation issue templates exist.
- [ ] Launch/outreach posts avoid unsupported traction, user, or audit claims.

## Search And Registry

- [ ] `python3 scripts/generate_search_index.py --check`
- [ ] `python3 scripts/generate_registry.py --check`
- [ ] `python3 scripts/validate_metadata.py`
- [ ] `python3 scripts/score_pocs.py --check`
- [ ] `python3 scripts/generate_verification_report.py --check`
- [ ] `python3 scripts/poc_maturity_index.py --check`
- [ ] `python3 scripts/research_dashboard.py --check`

## README And Docs

- [ ] README renders cleanly on GitHub.
- [ ] README top section includes Start Here paths for builders and
      researchers.
- [ ] Latest release section names the current stable release accurately.
- [ ] Stable GitHub Action examples use the latest released tag.
- [ ] `@main` examples are labeled as development usage.
- [ ] Quick Start YAML is valid.
- [ ] Sample commands are readable.
- [ ] Registry table remains between generated markers.
- [ ] `docs/VAULT_RULE_PACK.md` linked from README and search index.
- [ ] `docs/GITHUB_ACTION_USAGE.md` matches action inputs.
- [ ] `docs/PR_COMMENT_MODE.md` documents permissions and update mode.
- [ ] `docs/GENERATED_ISSUE_CHECKLIST.md` documents manual issue workflow.
- [ ] `docs/ARKHEIONX_CONFIG.md` documents suppression behavior.
- [ ] `docs/SARIF_OUTPUT.md` documents Code Scanning upload and severity
      mapping.
- [ ] `docs/BASELINE_DIFF_MODE.md` documents baseline and diff usage.
- [ ] `docs/CI_GATING.md` documents fail thresholds and false-positive
      caution.
- [ ] `docs/READINESS_SCORE.md` matches scanner scoring categories.
- [ ] `SERVICES.md`, `docs/business/MONETIZATION.md`, and `docs/business/SPONSORSHIP.md` avoid
      formal-audit or guarantee claims.
- [ ] Stale release phrases are absent:

  ```sh
  python3 - <<'PY'
  from pathlib import Path

  version = "v0" + ".4" + ".0"
  phrases = [
      version + " - " + "Unreleased",
      "until " + version + " is tagged",
      "prepared, " + "not tagged",
      "prepared, " + "not released",
      "upcoming " + version,
      "planned " + version,
  ]
  for root in [Path("README.md"), Path("CHANGELOG.md"), Path("docs")]:
      files = [root] if root.is_file() else root.rglob("*.md")
      for path in files:
          text = path.read_text(encoding="utf-8", errors="ignore")
          for phrase in phrases:
              if phrase.lower() in text.lower():
                  raise SystemExit(f"stale release phrase: {path}: {phrase}")
  PY
  ```

- [ ] v0.7.0 or the next active milestone is visible in roadmap and release
      notes.

## v0.9.0 Security Memory Checks

- [ ] `metadata/security_memory_graph.json` exists and parses.
- [ ] `metadata/finding_knowledge_map.json` exists and parses.
- [ ] `metadata/rule_calibration_matrix.json` exists and parses.
- [ ] `reports/security_memory_graph.md` exists.
- [ ] `python3 scripts/generate_knowledge_graph.py --check` passes.
- [ ] `python3 scripts/search_knowledge.py "oracle stale price"` returns
      `ARK-ORC-001`.
- [ ] `python3 scripts/search_knowledge.py "missing invariant" --json`
      returns valid JSON.
- [ ] Generated reports include `Related Knowledge`.
- [ ] Generated issue plans include `Related Knowledge`.
- [ ] Search index and search metadata include v0.9 knowledge graph paths.
- [ ] Docs explain that historical similarity is not vulnerability
      confirmation.

## v0.9.2 Self-Ingestion Checks

- [ ] Generated Arkheionx artifacts inside `reports/` are ignored by default.
- [ ] JSON reports include `scan_sources.generated_artifacts_ignored`.
- [ ] Markdown reports include `Scan Source Summary`.
- [ ] Negative evidence does not come from generated report text.
- [ ] Repeated scans with previous outputs keep score and finding IDs stable
      unless source files changed.
- [ ] `tests/test_generated_artifact_ignore.py` passes.

## v1.0.0 Stable Public Release Checks

- [ ] README names v1.0.0 as the latest stable release.
- [ ] README documents what Arkheionx is, who it is for, what it produces, and
      how to try it in five minutes.
- [ ] Stable GitHub Action examples use the latest v1.0.x stable tag.
- [ ] `docs/CLI_REFERENCE.md` exists and matches `scripts/pre_audit_scan.py --help`.
- [ ] `docs/GITHUB_ACTION_USAGE.md` documents stable v1.0.0 inputs.
- [ ] `docs/SCHEMA_REFERENCE.md` exists.
- [ ] JSON schemas exist under `schemas/` and parse successfully.
- [ ] `docs/OUTPUT_ARTIFACTS.md` documents recommended names and generated
      artifact ignore behavior.
- [ ] `docs/V1_0_RELEASE_NOTES_DRAFT.md` exists.
- [ ] Generated artifacts are ignored by default.
- [ ] Negative evidence fixture passes.
- [ ] Self-ingestion fixture passes.
- [ ] `python3 scripts/generate_knowledge_graph.py --check` passes.
- [ ] `python3 scripts/check_docs_links.py --check` passes.
- [ ] `python3 scripts/check_version_consistency.py --check` passes.
- [ ] `python3 scripts/check_safety_wording.py` runs.
- [ ] Unit tests pass.
- [ ] Search index is up to date.
- [ ] Registry and metadata checks pass.
- [ ] `git diff --check` passes.
- [ ] No live-chain/RPC behavior added.
- [ ] No exploit automation added.
- [ ] No fake adoption, customer, or external-validation claims added.
- [ ] Release notes drafted but no tag/release/push performed.

## v1.1.0 Feedback Loop And External Calibration Checks

- [ ] Feedback issue templates exist.
- [ ] `metadata/feedback_schema.json` parses.
- [ ] `metadata/feedback_examples.json` parses and examples are synthetic or
      explicitly sourced.
- [ ] `metadata/rule_calibration_backlog.json` parses.
- [ ] `python3 scripts/generate_feedback_dashboard.py --check` passes.
- [ ] `reports/feedback_dashboard.md` exists.
- [ ] `reports/rule_calibration_backlog.md` exists.
- [ ] `docs/FEEDBACK_LOOP.md` exists.
- [ ] `docs/PUBLIC_FEEDBACK_GUIDE.md` exists.
- [ ] `docs/FEEDBACK_TRIAGE_WORKFLOW.md` exists.
- [ ] `docs/VALIDATION_LEVELS.md` exists.
- [ ] Feedback templates warn against secrets/private keys.
- [ ] Feedback templates warn against public disclosure of unpatched
      vulnerabilities.
- [ ] External validation docs distinguish toy/internal examples from public
      validation.
- [ ] No fake adoption or customer claims added.
- [ ] Docs link check passes.
- [ ] Version consistency check passes.
- [ ] Safety wording check passes.
- [ ] Unit tests pass.

## v1.2.0 Paid Offer Refinement Checks

- [ ] `docs/business/PAID_OFFER.md` exists.
- [ ] `docs/business/PRICING_LADDER.md` exists.
- [ ] `docs/business/SERVICE_PACKAGES.md` exists.
- [ ] `docs/business/CLIENT_INTAKE.md` exists.
- [ ] `docs/business/SAMPLE_SCOPE_OF_WORK.md` exists.
- [ ] `docs/business/SALES_FAQ.md` exists.
- [ ] `docs/business/PAID_WORK_BOUNDARIES.md` exists.
- [ ] `metadata/paid_offer_catalog.json` parses.
- [ ] `python3 scripts/generate_paid_offer_index.py --check` passes.
- [ ] `reports/paid_offer_index.md` exists.
- [ ] `templates/client_intake.md` exists.
- [ ] Readiness Snapshot, Pre-Audit Sprint, and Contest Readiness scope
      templates exist.
- [ ] Paid docs clearly say paid work is not a formal audit.
- [ ] Paid docs clearly say there are no security or bounty guarantees.
- [ ] README links to paid readiness support.
- [ ] Search index includes paid-offer docs and catalog.
- [ ] No customer, adoption, auditor-trust, platform-affiliation, or official
      certification claims added.
- [ ] No payment processing, CRM, email automation, live-chain, RPC, or
      offensive behavior added.
- [ ] Docs link check passes.
- [ ] Version consistency check passes.
- [ ] Safety wording check passes in strict mode.
- [ ] Unit tests pass.

## v1.3.0 Ecosystem Pack Checks

- [ ] `docs/ecosystem/ECOSYSTEM_PACK.md` exists.
- [ ] `docs/ecosystem/MULTI_REPO_READINESS_WORKFLOW.md` exists.
- [ ] `docs/ecosystem/ANONYMIZED_REPORTING.md` exists.
- [ ] `docs/ecosystem/ECOSYSTEM_READINESS_PILOT.md` exists.
- [ ] `metadata/ecosystem_pack_schema.json` parses.
- [ ] `metadata/ecosystem_pilot_example.json` parses and is clearly synthetic.
- [ ] `templates/ecosystem_intake.md` exists.
- [ ] `templates/ecosystem_readiness_pilot_scope.md` exists.
- [ ] `templates/ecosystem_manifest.example.json` exists.
- [ ] `python3 scripts/generate_ecosystem_report.py --check` passes.
- [ ] `reports/ecosystem_readiness_summary.md` exists.
- [ ] `reports/ecosystem_common_gaps.md` exists.
- [ ] Paid offer docs mention Ecosystem Readiness Pilot.
- [ ] README links ecosystem readiness workflow.
- [ ] Search index includes ecosystem readiness docs and reports.
- [ ] No remote cloning, external APIs, unauthorized repo workflow, live-chain,
      RPC, or offensive behavior added.
- [ ] No customer, adoption, partnership, endorsement, or certification claims
      added.
- [ ] Docs link check passes.
- [ ] Version consistency check passes.
- [ ] Safety wording check passes in strict mode.
- [ ] Unit tests pass.

## v1.4.0 AMM + Lending Protocol Pack Checks

- [ ] `docs/AMM_RULE_PACK.md` exists.
- [ ] `docs/LENDING_RULE_PACK.md` exists.
- [ ] `examples/amm-fixture/README.md` exists.
- [ ] `examples/lending-fixture/README.md` exists.
- [ ] `examples/amm-lending-hybrid-fixture/README.md` exists.
- [ ] AMM fixture scan emits `ARK-AMM-*` findings.
- [ ] Lending fixture scan emits `ARK-LEND-*` findings.
- [ ] Hybrid fixture scan emits both AMM and Lending rule-pack signals.
- [ ] AMM/Lending JSON reports parse.
- [ ] AMM/Lending SARIF outputs parse and include stable rule IDs.
- [ ] AMM/Lending issue plans include Related Knowledge.
- [ ] `metadata/finding_knowledge_map.json` maps `ARK-AMM-*` and `ARK-LEND-*`.
- [ ] `metadata/security_memory_graph.json` regenerated and check mode passes.
- [ ] Search index includes AMM/Lending docs, fixtures, and terms.
- [ ] No live-chain, RPC, remote cloning, liquidation automation, or exploit
      payload behavior added.
- [ ] No vulnerability-confirmation or bounty-claim language added.
- [ ] Docs link check passes.
- [ ] Version consistency check passes.
- [ ] Safety wording check passes in strict mode.
- [ ] Unit tests pass.

## v1.5.0 Invariant/Test Plan Generator Checks

- [ ] `docs/INVARIANT_TEST_PLAN_GENERATOR.md` exists.
- [ ] `docs/FOUNDRY_INVARIANT_SKELETONS.md` exists.
- [ ] `docs/INVARIANT_SAFETY_BOUNDARIES.md` exists.
- [ ] `metadata/finding_test_plan_map.json` parses.
- [ ] `scripts/generate_test_plan.py --check` passes.
- [ ] AMM fixture test plan Markdown and JSON exist.
- [ ] Lending fixture test plan Markdown and JSON exist.
- [ ] Hybrid fixture test plan Markdown and JSON exist.
- [ ] Generated Foundry skeletons include TODO placeholders and safety notices.
- [ ] Generated skeletons avoid production endpoints, credentials, real
      deployment assumptions, and unsafe payload language.
- [ ] Scanner JSON findings include `suggested_tests` and
      `invariant_candidates` where mappings exist.
- [ ] Issue plans include suggested test and invariant-candidate content.
- [ ] `schemas/test_plan.schema.json` exists and parses.
- [ ] Search index includes invariant/test-plan generator surfaces.
- [ ] No live-chain, RPC, deployed-contract testing, attack automation, or
      complete-coverage claims added.
- [ ] Docs link check passes.
- [ ] Version consistency check passes.
- [ ] Safety wording check passes in strict mode.
- [ ] Unit tests pass.

## v1.6.0 Internal Engine Split Checks

- [ ] `arkheionx/` package scaffold exists.
- [ ] `arkheionx/version.py` exposes `1.6.0-dev`, `v1.5.0`, `v1.6.0`, and
      `v1.7.0` milestone metadata for the v1.6 release branch.
- [ ] Core helper modules exist under `arkheionx/core/`.
- [ ] Rule registry exists under `arkheionx/rules/`.
- [ ] Generator extraction starts under `arkheionx/generators/`.
- [ ] `python3 -m arkheionx.cli.main version` exits 0.
- [ ] `python3 -m arkheionx.cli.main doctor` exits 0.
- [ ] Existing script entrypoints still run.
- [ ] `scripts/generate_test_plan.py --check` passes.
- [ ] Ecosystem, paid-offer, and feedback generator checks pass.
- [ ] Search index includes internal engine, package architecture, and CLI
      roadmap surfaces.
- [ ] No scanner capability expansion, RPC/live-chain behavior, exploit
      automation, or formal-audit claims added.
- [ ] Docs link check passes.
- [ ] Version consistency check passes.
- [ ] Safety wording check passes in strict mode.
- [ ] Unit tests pass.

## v1.7.0 Config And Rule-Pack Checks

- [ ] `arkheionx/version.py` exposes `1.7.0-dev`, `v1.6.0`, `v1.7.0`, and
      `v1.8.0` milestone metadata.
- [ ] `scripts/validate_config.py --config examples/arkheionx.config.example.json` exits 0.
- [ ] All `examples/configs/*.config.json` files validate.
- [ ] Dangerous config keys fail validation.
- [ ] Scanner JSON and Markdown include config summary.
- [ ] Rule-pack registry helpers map known IDs and reject unknown rule packs.
- [ ] Config docs, suppression docs, rule-pack config docs, and config safety
      docs exist.
- [ ] No RPC/live-chain, remote clone, secret-handling, or exploit-mode config
      behavior added.

## v1.8.0 Report UX And Noise Reduction Checks

- [ ] `arkheionx/version.py` exposes `1.8.0-dev`, `v1.7.0`, `v1.8.0`, and
      `v1.9.0` milestone metadata.
- [ ] `arkheionx/reports/ux.py`, `summary.py`, and `profiles.py` compile.
- [ ] Markdown fixture reports include Fix First, Finding Groups, Config
      Summary, and Suppression Summary.
- [ ] JSON fixture reports include `fix_first`, `report_ux`,
      `findings_by_rule_family`, and `findings_by_confidence`.
- [ ] CI and full profile fixture reports are generated and parseable.
- [ ] Issue plans include Fix First ordering, rule family, confidence reason,
      suggested tests, and invariant candidates.
- [ ] SARIF remains valid and includes rule-family readiness metadata.
- [ ] No report wording claims confirmed vulnerabilities, exploitability,
      formal audit status, or security guarantees.

## v1.9.0 Pre-v2 CLI Candidate Checks

- [ ] `arkheionx/version.py` exposes `1.9.0-dev`, `v1.8.0`, `v1.9.0`, and
      `v2.0.0` milestone metadata.
- [ ] `arkheionx/cli/main.py`, `commands.py`, and `exit_codes.py` compile.
- [ ] `python3 -m arkheionx.cli.main version` exits 0.
- [ ] `python3 -m arkheionx.cli.main doctor` exits 0.
- [ ] `python3 -m arkheionx.cli.main scan ...` writes Markdown, JSON, SARIF,
      and issue-plan outputs.
- [ ] `python3 -m arkheionx.cli.main validate-config --config ...` validates
      safe local configs and rejects dangerous config keys.
- [ ] `python3 -m arkheionx.cli.main test-plan ...` writes Markdown, JSON, and
      safe Foundry skeleton outputs.
- [ ] `python3 -m arkheionx.cli.main search "oracle stale price"` works locally.
- [ ] Existing script entrypoints still work.
- [ ] CLI docs and migration-to-v2 docs exist.
- [ ] No package publishing, pyproject, network behavior, RPC behavior, remote
      cloning, or exploit automation added.

## v2.0.0 Installable CLI / Package Checks

- [ ] `pyproject.toml` exists.
- [ ] Editable install succeeds with `python3 -m pip install -e .`.
- [ ] `arkheionx` console command resolves.
- [ ] `arkheionx --help`, `version`, `doctor`, `scan`, `validate-config`,
      `test-plan`, and `search` work locally.
- [ ] Package-data/path helpers resolve metadata, schemas, and templates.
- [ ] Module CLI still works.
- [ ] Old scripts still work.
- [ ] JSON, SARIF, issue-plan, and test-plan outputs generated by the console
      command parse.
- [ ] No `dist/`, `build/`, `.eggs/`, or `*.egg-info/` artifacts are committed.
- [ ] No PyPI publishing workflow, PyPI token, or trusted publishing config is
      added.
- [ ] Package docs do not claim PyPI availability and do not ask for secrets or
      RPC keys.

## v2.0.1 Packaging + Product Repositioning Hotfix Checks

- [ ] README uses value-flow workbench positioning.
- [ ] `Map the money flow. Find the missing tests.` appears in public docs.
- [ ] Audit-prep is framed as an advanced workflow.
- [ ] `docs/VALUE_FLOW_WORKBENCH.md` exists.
- [ ] `docs/VALUE_FLOW_ROADMAP.md` exists.
- [ ] `docs/DEVELOPER_RESEARCHER_WORKFLOW.md` exists.
- [ ] GitHub About recommendation uses the value-flow workbench description.
- [ ] No future `flow` commands are documented as available commands.
- [ ] No feature claims are made for an unimplemented flow engine.
- [ ] Installable CLI still works.
- [ ] Module CLI still works.
- [ ] Old scripts still work.
- [ ] No package publishing workflow added.
- [ ] No `dist/`, `build/`, `.eggs/`, or `*.egg-info/` artifacts are
      committed.
- [ ] Version consistency check names v2.0.0 as latest stable, v2.0.1 as
      current milestone, and v2.1.0 as next milestone.
- [ ] Safety wording check passes in strict mode.

## Safety Scan

- [ ] No live-target workflow added.
- [ ] No RPC requirement added to scanner or action.
- [ ] No transaction submission, key handling, or deployed-contract testing.
- [ ] No private keys, mnemonics, RPC credentials, or secrets in the diff.
- [ ] No banned/suspicious marketing phrases from the CI safety list.

## GitHub Surface

- [ ] Issue templates render correctly.
- [ ] GitHub Action path is correct.
- [ ] CI workflow runs scanner tests and fixture scans.
- [ ] Recommended topics reviewed in README/search guide.
- [ ] Discussions/categories updated manually if part of release.

## Release Steps

- [ ] Commit changes.
- [ ] Open release PR.
- [ ] Wait for CI green.
- [ ] Merge to `main`.
- [ ] Tag from `main` only after approval.
- [ ] Publish GitHub release from `CHANGELOG.md`.
- [ ] Announce only with honest, bounded language.

Releases are checkpoints, not finish lines.


## v2.2.0 — Execution Proof & Trace Workbench

Prepared locally. Do not push/tag/release without maintainer approval.

### Validate

- [ ] `python3 -m unittest discover -s tests -p "test_*.py"` passes.
- [ ] `make validate` passes.
- [ ] CLI smoke: `arkheionx doctor`, `arkheionx open .`, `arkheionx map . --top 5`,
      `arkheionx flow .`, `arkheionx hunt . --top 5`.
- [ ] Proof/trace smoke on a Foundry fixture:
      `arkheionx prove examples/oracle-staking-fixture --target OracleRewardFixture.stake --run`
      then `arkheionx trace examples/oracle-staking-fixture --target OracleRewardFixture.stake`.

### Inspect

- [ ] README names current commands (incl. `trace`) and evidence levels.
- [ ] CHANGELOG dates the `## v2.2.0` section (no longer "Unreleased").
- [ ] `release-notes/v2.2.0.md` matches implemented behavior.
- [ ] `arkheionx version` reports `2.2.0`, `v2.2.0`, `v2.3.0`.
- [ ] `git status` clean (no generated `.arkheionx/` output tracked).

### Release commands (run only after approval)

```sh
git status
git log --oneline -n 3
git tag -a v2.2.0 -m "Arkheionx v2.2.0 — Execution Proof & Trace Workbench"
git push origin pivot/value-flow-workbench-v2.0.1
git push origin v2.2.0
gh release create v2.2.0 \
  --title "Arkheionx v2.2.0 — Execution Proof & Trace Workbench" \
  --notes-file release-notes/v2.2.0.md
```

- [ ] Verify the GitHub release page renders the notes correctly.


## v2.3.0 — Evidence & Report Package

Prepared locally (dev). Do not push/tag/release without maintainer approval.

### Validate

- [ ] `python3 -m unittest discover -s tests -p "test_*.py"` passes.
- [ ] `make validate` passes.
- [ ] CLI smoke: `arkheionx evidence . --target <t>` / `arkheionx report . --target <t>`
      give useful next commands when no proof/evidence exists.
- [ ] Full chain on a Foundry fixture:
      `prove --run` → `trace` → `evidence` → `report` produces evidence.json + report.md.

### Inspect

- [ ] README lists `evidence` and `report` and the full workflow.
- [ ] CHANGELOG dates the `## v2.3.0` section (no longer "Unreleased").
- [ ] `release-notes/v2.3.0.md` matches implemented behavior.
- [ ] `arkheionx version` reports `2.3.0`, `v2.3.0`, `v2.4.0`.
- [ ] Reports contain no final-severity / live-chain / auto-submit language.

### Final cut (after approval)

- [ ] Set `__version__`/pyproject to `2.3.0`, date the CHANGELOG section.
- [ ] `git tag -a v2.3.0`, push branch + tag, create the GitHub release.


## v2.4.0 — Evidence Workflow Hardening

Prepared locally (dev). Do not push/tag/release without maintainer approval.

### Validate

- [ ] `python3 -m unittest discover -s tests -p "test_*.py"` passes.
- [ ] `make validate` passes.
- [ ] `arkheionx evidence-status .` and `arkheionx validate-artifacts .` exit
      gracefully on an empty repo and on a full Foundry-fixture loop.
- [ ] Malformed artifacts are reported as invalid, not ignored.

### Inspect

- [ ] README lists `evidence-status` and `validate-artifacts`.
- [ ] CHANGELOG dates the `## v2.4.0` section (no longer "Unreleased").
- [ ] `release-notes/v2.4.0.md` matches implemented behavior.
- [ ] `arkheionx version` reports `2.4.0`, `v2.4.0`, `v2.5.0`.
- [ ] Reports keep NEEDS_HUMAN_REVIEW, no final severity, no live-chain steps.

### Final cut (after approval)

- [ ] Set `__version__`/pyproject to `2.4.0`, date the CHANGELOG section.
- [ ] `git tag -a v2.4.0`, push branch + tag, create the GitHub release.

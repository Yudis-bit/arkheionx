# Test Expectation Alignment

## Summary

Initial full run used the repository virtualenv because `python` is not installed globally and `python3` lacks pytest:

```text
.venv/bin/python -m pytest -q 2>&1 | tee notes/pytest-phase3-failures.txt
33 failed, 2914 passed, 7 skipped, 1 warning
```

The failures are expectation drift after the public-surface cleanup. Core engine tests are not failing.

## Failure groups

### Group 1: Version expectation
- failing tests:
  - `tests/test_cli_commands.py::CliCommandTests::test_help_version_and_doctor_exit_zero`
  - `tests/test_cli_commands.py::CliCommandTests::test_version_includes_package_version_and_next_step`
  - `tests/test_cli_preview.py::CliPreviewTests::test_version_command`
  - `tests/test_demo_workflow.py::DemoDocsAndMetadataTests::test_version_metadata`
  - `tests/test_fixture_harness_public_contract.py::SchemaAndMetadataContractTests::test_version_metadata_unchanged`
  - `tests/test_installer.py::OnboardingSurfaceTests::test_version_metadata`
  - `tests/test_intelligence_public_regression.py::MetadataUnchangedTests::test_version_metadata_is_frozen`
  - `tests/test_package_contains_lens.py::PackagingConfigTests::test_version_consistent_between_version_py_and_pyproject`
  - `tests/test_package_imports.py::PackageImportTests::test_package_imports_and_version_metadata`
  - `tests/test_package_installable.py::PackageInstallableTests::test_editable_install_and_console_version`
  - `tests/test_package_installable.py::PackageInstallableTests::test_pyproject_declares_console_entrypoint`
  - `tests/test_release_readiness.py::ReleaseReadinessTests::test_version_metadata`
  - `tests/test_review_map.py::VersionMetadataTests::test_version_metadata_is_v34_final`
  - `tests/test_v3_launch_candidate.py::VersionMetadataTests::test_version_metadata`
- expected old value:
  - package/dev version: `9.1.0.dev0`
  - current milestone: `v9.1.0-dev`
  - next milestone: `v9.1.0`
- current intentional value:
  - package/dev version: `10.1.0.dev0`
  - latest stable public release: `v8.0.1`
  - current milestone: `v10.1.0-dev`
  - next planned release: `v10.1.0`
- action:
  - Update test expectations to the version context they are actually guarding. Keep stable release assertions pinned to `v8.0.1`.

### Group 2: README/site wording
- failing tests:
  - `tests/test_public_surface.py::PublicSurfaceTests::test_readme_front_page_positioning`
  - `tests/test_readme_is_clean.py::ReadmeIsCleanTests::test_clean_headings_present`
  - `tests/test_readme_is_clean.py::ReadmeIsCleanTests::test_core_story_and_command_present`
  - `tests/test_release_readiness.py::ReleaseReadinessTests::test_no_fake_proof_language`
  - `tests/test_release_readiness_gate.py::ReleaseReadinessGateTests::test_gate_passes`
  - `tests/test_release_readiness_gate.py::ReleaseReadinessGateTests::test_main_check_exits_zero`
  - `tests/test_site_is_clean.py::SiteIsCleanTests::test_homepage_has_clear_hero`
  - `tests/test_site_is_clean.py::SiteIsCleanTests::test_homepage_has_exactly_seven_sections`
  - `tests/test_site_is_clean.py::SiteIsCleanTests::test_homepage_has_safety_boundary`
  - `tests/test_v1_stability.py::V1StabilityTests::test_public_docs_name_stable_surface`
  - `tests/test_v3_launch_candidate.py::ReadmeSurfaceTests::test_clean_product_positioning`
  - `tests/test_v3_launch_candidate.py::DocsTests::test_roadmap_marks_current_and_history`
  - `tests/test_v3_launch_candidate.py::StableTagTests::test_install_and_arkup_track_stable`
  - `tests/test_value_flow_positioning.py::ValueFlowPositioningTests::test_readme_uses_value_flow_positioning`
  - `tests/test_value_flow_positioning.py::ValueFlowPositioningTests::test_roadmap_and_changelog_name_current_direction`
- old expected wording:
  - `# Arkheionx`
  - `Local-first Ethereum security research workflow for Solidity and DeFi repositories.`
  - v8/v3 README sections such as `Core workflow`, `Protocol Lens Packs`, `Release status`, and `License`
  - homepage with exactly seven sections and the older “security research workflow” hero
  - README-level GitHub Action example
  - roadmap current milestone `v8.0.1` / next milestone `v8.1.0`
- new intended wording:
  - `# ArkheionX`
  - `ArkheionX is local-first review infrastructure for smart contract security.`
  - `It does not replace auditors.`
  - `It gives auditors a better map.`
  - latest stable release `v8.0.1` remains distinct from development milestone `v10.1.0-dev`
  - README no longer carries the GitHub Action example; `docs/GITHUB_ACTION_USAGE.md` remains the stable action surface while repository identity migration is in progress.
- action:
  - Update tests and readiness gate expectations to the new public positioning without weakening checks for local-only behavior, human review, no auto-submit, no bounty guarantee, no endorsement, and no auditor replacement.

### Group 3: Archived docs path
- failing tests:
  - `tests/test_cli_commands.py::CliCommandTests::test_cli_docs_exist`
  - `tests/test_internal_engine_split.py::InternalEngineSplitTests::test_package_docs_exist`
  - `tests/test_value_flow_positioning.py::ValueFlowPositioningTests::test_advanced_flow_submodes_are_marked_planned`
- old path:
  - `docs/CLI_CANDIDATE.md`
  - `docs/CLI_COMMANDS.md`
  - `docs/CLI_INSTALLABLE.md`
  - `docs/CLI_MIGRATION_TO_V2.md`
  - `docs/CLI_ROADMAP.md`
- new path:
  - `docs/archive/legacy-workflows/CLI_CANDIDATE.md`
  - `docs/archive/legacy-workflows/CLI_COMMANDS.md`
  - `docs/archive/legacy-workflows/CLI_INSTALLABLE.md`
  - `docs/archive/legacy-workflows/CLI_MIGRATION_TO_V2.md`
  - `docs/archive/legacy-workflows/CLI_ROADMAP.md`
- action:
  - Point legacy workflow tests at the archive path when they intentionally validate historical docs. Keep canonical CLI checks pointed at `docs/CLI_REFERENCE.md`.

### Group 4: Real regression
- failing tests:
  - `tests/test_public_surface_is_generic.py::PublicSurfaceIsGenericTests::test_no_unnegated_marketing_claims`
  - release-readiness gate safety disclaimer check
- suspected cause:
  - The shared safety wording script passes. The duplicate generic-surface test uses a narrower negation window and does not recognize section-level “what this is not” contexts.
  - The release-readiness gate checks one exact README sentence from the older surface even though the README already states the equivalent no-automatic-discovery boundary.
- action:
  - Keep safety strict by reusing shared safety context handling in the duplicate test and by making the release-readiness gate check boundary concepts instead of one stale exact sentence.

## Final result
- pytest: `.venv/bin/python -m pytest -q` -> `2947 passed, 7 skipped, 1 warning, 112 subtests passed`
- docs links: `python3 scripts/check_docs_links.py --check` -> passed
- safety wording: `python3 scripts/check_safety_wording.py` -> passed
- version consistency: `python3 scripts/check_version_consistency.py` -> passed
- search index: `python3 scripts/generate_search_index.py --check` -> passed
- diff whitespace: `git diff --check` -> passed
- site build: `cd site && npm run build` -> passed
- remaining failures, if any: none

## Files changed
- `notes/test-expectation-alignment.md`
- `scripts/check_release_readiness.py`
- `tests/test_cli_commands.py`
- `tests/test_cli_preview.py`
- `tests/test_demo_workflow.py`
- `tests/test_fixture_harness_public_contract.py`
- `tests/test_installer.py`
- `tests/test_intelligence_public_regression.py`
- `tests/test_internal_engine_split.py`
- `tests/test_package_contains_lens.py`
- `tests/test_package_imports.py`
- `tests/test_package_installable.py`
- `tests/test_public_surface.py`
- `tests/test_public_surface_is_generic.py`
- `tests/test_readme_is_clean.py`
- `tests/test_release_readiness.py`
- `tests/test_review_map.py`
- `tests/test_site_is_clean.py`
- `tests/test_v1_stability.py`
- `tests/test_v3_launch_candidate.py`
- `tests/test_value_flow_positioning.py`

## Tests updated
- Version metadata assertions now distinguish package development version `10.1.0.dev0`, stable release `v8.0.1`, current milestone `v10.1.0-dev`, and next release `v10.1.0`.
- Legacy CLI workflow documentation tests now read `docs/archive/legacy-workflows/`.
- README and site surface tests now enforce the ArkheionX public positioning: local-first review infrastructure, auditor support rather than auditor replacement, human review required, and no unsupported public claims.
- The duplicate generic-surface marketing scanner now recognizes the shared safety prohibition context used by `scripts/check_safety_wording.py`.
- The release-readiness gate now checks safety boundary concepts and keeps the GitHub Action stable tag assertion in `docs/GITHUB_ACTION_USAGE.md` rather than requiring that example on the README front page.

## Why updates are valid
- The source version metadata and `pyproject.toml` already intentionally say `10.1.0.dev0`; the failing tests were pinned to old v9.1 development labels.
- The canonical public docs architecture intentionally moved old CLI transition docs into `docs/archive/legacy-workflows/`; tests now validate the archive rather than forcing those files back to the top level.
- The README/site tests now match the post-cleanup public surface while preserving strict checks for local-only workflow, no RPC by default, no auto-submit, no auditor replacement, no bounty guarantee, no severity guarantee, and human review.
- The safety updates do not allow positive claims. They only allow forbidden phrases when they appear in explicit negative contexts such as "does not", "not an", "What it is not", or "What not to imply".

## What was intentionally not changed
- No core engine logic.
- No tests deleted, skipped, or xfailed.
- No archived docs moved back to top level.
- No Ethereum Foundation endorsement language added.
- No public identity rollback to `DeFi-Exploit-PoCs`.
- No generated junk staged or committed.

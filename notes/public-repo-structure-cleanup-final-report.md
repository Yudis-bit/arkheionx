# Public Repository Structure Cleanup Final Report

## Summary

Phase 2 cleaned the public interpretation layer of the repository without rewriting engine logic. The repo still contains the full ArkheionX project, but generated/local output is ignored more clearly, public docs subtrees have boundaries, historical VM folders are framed as validation fixtures, output directories explain what they are, and the repo rename risk is documented instead of hidden.

No commits were made.

## What was already good from Phase 1

- Root `README.md` was already repositioned around ArkheionX as local-first review infrastructure.
- Canonical docs existed and were linked from `docs/README.md`.
- Case studies, external validation docs, versioning docs, and public positioning metadata were already created.
- Website source had already moved away from the old repo identity and old hero language.
- Historical version docs had already been moved under `docs/archive/`.

## What was still noisy

- Local/generated directories were visible in the working tree: `.arkheionx/`, `.codex/`, `.agents/`, caches, build outputs, and `full-tree.txt`.
- `docs/business/`, `docs/marketing/`, `docs/private/`, and `docs/launch/` had no boundary READMEs.
- `EVM/`, `MoveVM/`, and `SVM/` still read like exploit-reproduction folders at first glance.
- `artifacts/`, `examples/reports/`, and `reports/verification/` had no public explanation.
- GitHub issue templates were broad and partly duplicated.
- Old `DeFi-Exploit-PoCs` links remain in installer/action/historical surfaces.

## Generated/local junk status

Removed locally after confirming zero tracked files:

- `.arkheionx/`
- `.codex/`
- `.agents/`
- `full-tree.txt`
- `.pytest_cache/`
- `__pycache__/`
- `arkheionx.egg-info/`
- `build/`
- `dist/`
- `site/dist/`
- `site/.astro/`

Left in place:

- `site/node_modules/` because it is ignored, untracked, and useful for rebuilding the site without reinstalling dependencies.
- Generated smoke artifacts under `artifacts/smoke-*`; they remain ignored.

## `.gitignore` updates

Updated `.gitignore` to cover:

- local agent state: `.codex/`, `.agents/`;
- local tree dumps: `full-tree.txt`, `repo-tree.txt`;
- Python bytecode: `*.py[cod]`;
- site build/dependency output: `site/dist/`, `site/node_modules/`, `site/.astro/`;
- generated artifact directories while keeping only `/artifacts/README.md` trackable.

The root artifact exception initially exposed a nested test fixture artifact. The rule was corrected so nested `artifacts/` directories remain ignored.

## Docs tree cleanup

Created:

- `notes/public-docs-risk-inventory.md`
- `docs/business/README.md`
- `docs/marketing/README.md`
- `docs/private/README.md`
- `docs/launch/README.md`
- `docs/ecosystem/README.md`
- `docs/internal/README.md`

No docs subtree was moved in Phase 2 because tests, workflows, scripts, metadata, or release checklists still reference the current paths.

## Business/marketing/private docs decision

Decision: keep in place for now, add boundaries, and keep out of canonical navigation.

Reason:

- `docs/business/` is referenced by tests and scripts.
- `docs/marketing/` is referenced by tests and workflows.
- `docs/private/` is referenced by public-surface docs.
- `docs/launch/` is referenced by tests and metadata.

Moving those directories now would create broad churn. A later cleanup can move them to `metadata/` or `docs/archive/` after tests and workflows are updated deliberately.

## EVM/MoveVM/SVM historical fixture decision

Decision: keep paths stable and reframe them.

Updated:

- `EVM/README.md`
- `MoveVM/README.md`
- `SVM/README.md`
- `docs/VM_SUPPORT.md`
- `docs/INCIDENT_INTAKE.md`
- selected issue templates that referred to "Broken PoC" or "Target PoC"

Reason:

`EVM/`, `MoveVM/`, `SVM/`, `ExploitTemplate`, `exploit.move`, and `exploit.ts` are referenced across docs, metadata, scripts, reports, workflows, and issue templates. Renaming them now would be high-risk. The READMEs now explain that these are historical vulnerable-case or validation fixtures, not live exploit tooling.

## Artifacts/examples/reports boundary docs

Created:

- `artifacts/README.md`
- `examples/reports/README.md`
- `reports/verification/README.md`

These explain that generated outputs, sample reports, and historical verification reports are safe to inspect as review/regression context, not as claims of live exploitable targets or automatic vulnerability confirmation.

## Repository structure doc

Created:

- `docs/REPOSITORY_STRUCTURE.md`

Linked from:

- `README.md`
- `docs/README.md`
- `docs/START_HERE.md`

It explains the source tree, docs/archive boundary, examples, artifacts, schemas, site, metadata, templates, reports, VM fixtures, notes, and local generated directories.

## GitHub issue template inventory

Created:

- `notes/github-surface-inventory.md`

No issue templates were deleted. Small wording updates were made to selected templates to use "validation fixture" language. Remaining recommendations:

- merge duplicate false-positive templates;
- merge external evaluation and external validation templates;
- decide whether launch/business request templates should stay visible in the default public issue picker;
- update `.github/ISSUE_TEMPLATE/config.yml` links only after the repo rename is confirmed.

## Old slug / repo rename compatibility

Created:

- `docs/REPO_RENAME_COMPATIBILITY.md`

Linked from:

- `docs/REPO_IDENTITY_MIGRATION.md`
- `docs/README.md`

Current state:

- public project identity is ArkheionX;
- recommended future repo slug is `arkheionx`;
- old slug links remain in installer/action/generated/historical surfaces until the GitHub rename is real;
- this is a documented migration risk, not a hidden contradiction.

## Commands run

- `pwd`
- `git status --short`
- `git branch --show-current`
- `git log --oneline -5`
- `tree -a -L 3 > notes/current-tree-before-phase2.txt`
- filtered tree snapshot to `notes/current-tree-filtered-before-phase2.txt`
- generated path tracking checks with `git ls-files`, `git status --ignored`, and `git check-ignore`
- docs subtree inspection with `find` and `grep`
- EVM/MoveVM/SVM inspection with `find`, `sed`, and `grep`
- artifacts/examples/reports inspection with `find`
- GitHub issue template inspection
- repo-link scans for `github.com/Yudis-bit` and `DeFi-Exploit-PoCs`
- `git diff --check`
- `python3 -m arkheionx.cli.main version || true`
- `python3 -m arkheionx.cli.main doctor || true`
- `python3 scripts/check_docs_links.py --check || true`
- `python3 scripts/check_safety_wording.py || true`
- `python3 scripts/check_safety_wording.py --strict`
- `python3 scripts/check_version_consistency.py || true`
- `python3 scripts/check_version_consistency.py --check`
- `python3 -m pytest -q`
- local `.venv` setup, editable install, `pytest`, and `setuptools`
- `. .venv/bin/activate && python -m pytest -q`
- targeted pytest checks for README/site safety boundaries
- `npm run build` from `site/`
- `python scripts/generate_search_index.py`
- `python scripts/generate_search_index.py --check`

## Test results

Passed:

- `git diff --check`
- `python3 -m arkheionx.cli.main version`
- `python3 -m arkheionx.cli.main doctor` with expected dirty/non-Foundry warnings
- `python3 scripts/check_docs_links.py --check`
- `python3 scripts/check_safety_wording.py --strict`
- `python3 scripts/check_version_consistency.py --check`
- `python scripts/generate_search_index.py --check`
- `npm run build` in `site/`
- targeted README/site safety tests after final copy fixes: `3 passed`

Pytest:

- Base interpreter initially had no `pytest`.
- Created `.venv`, installed editable ArkheionX, installed `pytest`, then installed missing `setuptools`.
- First full run after dependency setup: `44 failed, 2903 passed, 7 skipped`.
- After updating the version gate and search-index generator: `37 failed, 2910 passed, 7 skipped`.
- Remaining failures are dominated by stale tests asserting `9.1.0.dev0`, old README/site wording, old top-level CLI doc paths, old stable installer/action expectations, and older release-surface contracts.
- A final full run was not repeated after the last README/site copy fixes; targeted tests covering those fixes passed.

No full pytest pass is claimed.

## Files changed

Phase 2-specific changes include:

- `.gitignore`
- `EVM/README.md`
- `MoveVM/README.md`
- `SVM/README.md`
- `README.md`
- `docs/REPOSITORY_STRUCTURE.md`
- `docs/REPO_RENAME_COMPATIBILITY.md`
- boundary READMEs under `docs/business`, `docs/marketing`, `docs/private`, `docs/launch`, `docs/ecosystem`, `docs/internal`
- `artifacts/README.md`
- `examples/reports/README.md`
- `reports/verification/README.md`
- selected `.github/ISSUE_TEMPLATE/*`
- `docs/VM_SUPPORT.md`
- `docs/INCIDENT_INTAKE.md`
- `scripts/check_version_consistency.py`
- `scripts/generate_search_index.py`
- `reports/search_index.md`
- notes under `notes/`
- `site/src/pages/index.astro`

The working tree also still contains the uncommitted Phase 1 changes.

## Files intentionally not changed

- Core engine logic under `arkheionx/`.
- Actual folder names `EVM/`, `MoveVM/`, and `SVM/`.
- Legacy fixture file names such as `ExploitTemplate.t.sol`, `exploit.move`, and `exploit.ts`.
- Root `install.sh`, `arkup`, and action usage docs that still depend on the old repository slug.
- Generated PDFs and historical paper artifacts with old URLs.
- `site/node_modules/`.
- Ignored generated smoke artifacts under `artifacts/smoke-*`.

## Remaining risks

- The GitHub repository has not actually been renamed to `arkheionx`.
- Some public-visible files still include `DeFi-Exploit-PoCs` because they are installer/action/historical compatibility surfaces.
- Full pytest still fails due stale version and public-surface assertions.
- Top-level CLI docs were archived, but some tests still assert old paths.
- Site source and docs source are aligned, but ignored `site/dist/` is regenerated locally and not staged.
- Business/marketing/private docs remain in `docs/`, but now with boundaries.

## Recommended commit plan

Do not stage everything blindly. Suggested grouping:

```bash
git add .gitignore README.md docs/REPOSITORY_STRUCTURE.md docs/REPO_RENAME_COMPATIBILITY.md \
  docs/business/README.md docs/marketing/README.md docs/private/README.md \
  docs/launch/README.md docs/ecosystem/README.md docs/internal/README.md \
  artifacts/README.md examples/reports/README.md reports/verification/README.md \
  EVM/README.md MoveVM/README.md SVM/README.md docs/VM_SUPPORT.md docs/INCIDENT_INTAKE.md \
  .github/ISSUE_TEMPLATE/assertion_hardening.md .github/ISSUE_TEMPLATE/bug_report.md \
  .github/ISSUE_TEMPLATE/poc_verification_issue.md .github/ISSUE_TEMPLATE/research_candidate.md \
  scripts/check_version_consistency.py scripts/generate_search_index.py reports/search_index.md \
  site/src/pages/index.astro notes/public-repo-structure-cleanup.md \
  notes/public-docs-risk-inventory.md notes/github-surface-inventory.md \
  notes/current-tree-before-phase2.txt notes/current-tree-filtered-before-phase2.txt \
  notes/public-repo-structure-cleanup-final-report.md

git status --short
git commit -m "docs: clarify public repository structure and fixture boundaries"
```

Phase 1 changes should probably be committed separately or squashed into a larger readiness commit before this Phase 2 commit, depending on maintainer preference.

## Next maintainer decisions

1. Decide whether to rename the GitHub repository to `Yudis-bit/arkheionx`.
2. If renamed, update installer/action URLs and generated public assets deliberately.
3. Decide whether to move `docs/business`, `docs/marketing`, and `docs/private` after updating tests/workflows.
4. Decide whether to add compatibility stubs for archived CLI docs or update tests to use archive paths.
5. Update stale tests from `9.1.0.dev0` expectations to the current `10.1.0.dev0` version truth.
6. Consolidate duplicate issue templates.
7. Re-run full pytest after test-surface updates.

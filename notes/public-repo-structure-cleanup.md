# Public Repository Structure Cleanup Session

## Safety snapshot

- Working directory: `/home/arkheionx/Documents/DeFi-Exploit-PoCs`
- Branch: `private/v10-godeye-war-engine`
- Recent commits:
  - `3e66d02 chore: bump Arkheionx milestone metadata to v10.1`
  - `4dff033 fix(warrun): normalize scoped include paths against target roots`
  - `b4adaf4 feat(ingest): harden real solidity discovery and stale artifact filtering`
  - `a12203b feat(v10): add generic reality engine`
  - `210905a docs(v10): add Ancient GodEye ascension report (local, no push)`

## Current mission

Phase 2 focuses on public repository structure cleanup after the Phase 1 docs and messaging pass.

Scope:

- repo structure clarity;
- generated/local junk hygiene;
- naming and old-slug risk;
- public docs tree risk classification;
- EVM/MoveVM/SVM fixture framing;
- artifacts/examples/reports boundary docs;
- GitHub issue template inventory;
- final quality gates and reporting.

Non-scope:

- core engine rewrites;
- CLI behavior changes unless metadata/docs consistency requires a tiny fix;
- deleting valuable files blindly;
- committing changes automatically.

## Current git status

The working tree already contains the uncommitted Phase 1 readiness changes, including README/docs/site/metadata/template updates, archived historical docs, and new notes. This Phase 2 pass must preserve that work and avoid broad rewrites of files that were already aligned unless a small structure or link fix is necessary.

Notable current signal:

- `full-tree.txt` is untracked and appears to be local tree/debug output.
- No generated-looking tracked path has been removed yet.

## Phase 1 tree inspection

Created:

- `notes/current-tree-before-phase2.txt`
- `notes/current-tree-filtered-before-phase2.txt`

Generated/local path tracking check:

| path | exists during inspection | tracked files | ignored before cleanup | decision |
|---|---:|---:|---:|---|
| `.arkheionx/` | yes | 0 | yes | removed locally; keep ignored |
| `.codex/` | yes | 0 | no | add ignore; removed locally |
| `.agents/` | yes | 0 | no | add ignore; removed locally |
| `full-tree.txt` | yes | 0 | no | add ignore; removed locally |
| `.pytest_cache/` | yes | 0 | yes | removed locally |
| `__pycache__/` | yes | 0 | yes | removed locally |
| `arkheionx.egg-info/` | yes | 0 | yes | removed locally |
| `build/` | yes | 0 | yes | removed locally |
| `dist/` | yes | 0 | yes | removed locally |
| `site/dist/` | yes | 0 | yes | removed locally; build may regenerate ignored output |
| `site/node_modules/` | yes | 0 | yes | left in place to avoid forcing reinstall |
| `site/.astro/` | yes | 0 | yes | removed locally |

The cleanup used only untracked/generated paths. `site/node_modules/` was not removed.

## `.gitignore` updates

Added or clarified:

- `.codex/`
- `.agents/`
- `full-tree.txt`
- `repo-tree.txt`
- `*.py[cod]`
- `site/dist/`
- `site/node_modules/`
- `site/.astro/`
- root artifact handling that keeps only `artifacts/README.md` trackable

Important correction: the root artifact exception initially exposed a nested test fixture artifact. The ignore rules were tightened so nested `artifacts/` directories remain ignored while `/artifacts/README.md` can be tracked.

## Public docs tree findings

`docs/business`, `docs/marketing`, `docs/private`, and `docs/launch` are public-surface risks but are still referenced by tests, workflows, scripts, metadata, or release checklists. Moving them in Phase 2 would create avoidable churn. The chosen action is boundary README files plus keeping them out of canonical docs navigation.

Detailed classification: `notes/public-docs-risk-inventory.md`.

## VM fixture findings

`EVM/`, `MoveVM/`, and `SVM/` are heavily referenced by docs, metadata, scripts, workflows, issue templates, and reports. Renaming these folders or legacy files in Phase 2 would be high risk.

Chosen action:

- keep paths stable;
- reframe folder READMEs as historical vulnerable-case and validation fixtures;
- document that legacy `Exploit_*`, `exploit.move`, and `exploit.ts` names are compatibility names, not public product claims.

## Output directory findings

- `artifacts/`: ignored generated smoke/sample artifacts; new boundary README is trackable.
- `examples/reports/`: tracked sample outputs and expected report examples; boundary README added.
- `reports/verification/`: tracked historical verification reports; boundary README added.

## GitHub surface findings

The issue template surface is broad but mostly useful. No templates were deleted. Duplicate false-positive and external-validation templates should be consolidated after the repo rename/public surface decision.

Detailed classification: `notes/github-surface-inventory.md`.

## Repo rename compatibility findings

The repository is in a mixed-link state:

- canonical/public identity points toward ArkheionX and the recommended `Yudis-bit/arkheionx` slug;
- installer/action/generated/historical surfaces still use `Yudis-bit/DeFi-Exploit-PoCs`;
- changing every URL before the actual GitHub rename could break installs or rewrite historical artifacts.

Created `docs/REPO_RENAME_COMPATIBILITY.md` to document this explicitly.

# Repository Rename Completion

## Remote status

- Current branch: `private/v10-godeye-war-engine`.
- Legacy public remote slug: `Yudis-bit/DeFi-Exploit-PoCs`.
- Legacy public remote URL: `https://github.com/Yudis-bit/DeFi-Exploit-PoCs.git`.
- Observed `origin` at the start of this phase: `https://github.com/Yudis-bit/arkheionx.git` for fetch and push.
- No `git remote set-url` command was needed in this phase because `origin` already pointed at the canonical repository.

## Rename status

The public repository has been renamed to `Yudis-bit/arkheionx`.

New users should use:

```text
https://github.com/Yudis-bit/arkheionx
https://github.com/Yudis-bit/arkheionx.git
```

The old `DeFi-Exploit-PoCs` slug may remain in historical documents, archived
material, generated artifacts, migration notes, compatibility notes, or local
folder cleanup instructions.

## Files checked

The requested old-slug scan was run across:

- `README.md`
- `docs`
- `site/src`
- `metadata`
- `templates`
- `.github`
- `scripts`
- `pyproject.toml`
- `install.sh`
- `uninstall.sh`
- `SECURITY.md`
- `SERVICES.md`
- `CONTRIBUTING.md`
- `reports`
- `release-notes`

Additional rename-sensitive checks were run across:

- `tests`
- `site/public`
- `arkheionx`

## Public references updated

- `README.md`
- `docs/STYLEGUIDE.md`
- `docs/marketing/BRAND.md`
- `docs/REPO_IDENTITY_MIGRATION.md`
- `docs/REPO_RENAME_COMPATIBILITY.md`
- `docs/GITHUB_REPO_SURFACE.md`
- `docs/INSTALLATION.md`
- `docs/ROADMAP.md`
- `docs/PUBLIC_ALPHA_READINESS.md`
- `metadata/global-positioning.md`
- `metadata/grant-feedback-notes.md`
- `site/src/pages/install.astro`

## Installer/action references updated

- `install.sh`
- `site/public/install.sh`
- `docs/INSTALLER.md`
- `docs/GITHUB_ACTION_USAGE.md`
- `docs/GITHUB_ISSUE_WORKFLOW.md`
- `docs/SLITHER_INTEGRATION.md`
- `docs/SARIF_OUTPUT.md`
- `docs/WEBSITE_DEPLOYMENT.md`
- `.github/ISSUE_TEMPLATE/config.yml`
- `scripts/github_surface_setup.sh`
- `scripts/check_version_consistency.py`
- `scripts/pre_audit_scan.py`
- `tests/test_installer.py`
- `tests/test_site_installer_public.py`
- `tests/test_public_surface.py`
- `tests/test_v1_stability.py`
- `tests/test_arkup.py`

## Historical references intentionally kept

The remaining old slug references are intentionally retained only in these categories:

- Compatibility and migration policy:
  - `README.md`
  - `docs/STYLEGUIDE.md`
  - `docs/marketing/BRAND.md`
  - `docs/REPO_IDENTITY_MIGRATION.md`
  - `docs/REPO_RENAME_COMPATIBILITY.md`
  - `docs/INSTALLATION.md`
  - `docs/ROADMAP.md`
- Local folder cleanup instruction:
  - `docs/REPO_IDENTITY_MIGRATION.md`
- Old technical paper and generated legacy artifacts:
  - `docs/papers/arkheionx-v4-technical-paper.md`
  - `docs/papers/arkheionx-v4-technical-paper.html`
  - `docs/papers/arkheionx-v4-technical-paper.pdf`
  - `site/public/arkheionx-v4-technical-paper.pdf`

The technical paper source and generated HTML/PDF were not changed in this phase
because they are legacy publication artifacts. Updating them safely should happen
only in a deliberate paper regeneration/publication pass.

# Repository Identity Migration

The public project name is **ArkheionX**.

The public repository has been renamed to `Yudis-bit/arkheionx`.

The old `DeFi-Exploit-PoCs` slug may remain in historical documents, archived
material, generated artifacts, migration notes, compatibility notes, or local
folder cleanup instructions.

This page documents the completed public migration and remaining local cleanup
guidance. Do not run local folder rename commands automatically.

## Why this matters

A serious reviewer should see ArkheionX as review infrastructure, not as an
exploit dump.

The name creates the wrong first impression for:

- protocol teams;
- auditors;
- security researchers;
- audit firms;
- grant reviewers;
- ecosystem infrastructure reviewers.

ArkheionX should be framed as review infrastructure, not an exploit collection.

## Public identity

Use:

```text
ArkheionX
```

Current public GitHub repository name:

```text
arkheionx
```

Current repository URL:

```text
https://github.com/Yudis-bit/arkheionx
```

## What not to imply

Do not treat ArkheionX as:

- an exploit dump;
- an exploit generator;
- a bounty automation toolkit;
- an AI auditor;
- a replacement for auditors;
- an endorsed ecosystem grant project.

## Completed public repository rename

The public GitHub repository has been renamed:

```text
Yudis-bit/DeFi-Exploit-PoCs -> Yudis-bit/arkheionx
```

Local remotes should point at the canonical repository:

```bash
git remote -v
git remote set-url origin https://github.com/Yudis-bit/arkheionx.git
git remote -v
```

## Recommended local folder rename

Local rename only, after closing editors and shells that depend on the path:

```bash
cd ~/Documents
mv DeFi-Exploit-PoCs arkheionx
cd arkheionx
pwd
```

Do not run this from an automated docs-cleanup session. It is a local maintainer action.

## Reference maintenance policy

Active public references should use `Yudis-bit/arkheionx`:

- `README.md`;
- `pyproject.toml`;
- `install.sh`;
- `uninstall.sh`;
- `arkup`;
- `site/src/**`;
- `site/public/install.sh`;
- `docs/GITHUB_ACTION_USAGE.md`;
- `docs/GITHUB_REPO_SURFACE.md`;
- `docs/INSTALLER.md`;
- release/version consistency scripts;
- tests that assert the old URL;
- generated examples and SARIF metadata where appropriate.

The old `DeFi-Exploit-PoCs` slug may remain in:

- historical documents;
- archived release material;
- generated legacy artifacts;
- compatibility notes;
- local folder cleanup instructions;
- old technical papers or generated PDFs that are preserved deliberately.

Use a reviewed diff, not blind replacement:

```bash
grep -rIn "Yudis-bit/DeFi-Exploit-PoCs\|DeFi-Exploit-PoCs" \
  --exclude-dir=.git \
  --exclude-dir=node_modules \
  --exclude-dir=build \
  --exclude-dir=dist \
  .
```

## Compatibility notes

For the post-rename compatibility state, see
[`REPO_RENAME_COMPATIBILITY.md`](REPO_RENAME_COMPATIBILITY.md).

## Validation after migration

```bash
python3 -m arkheionx.cli.main version
python3 -m arkheionx.cli.main doctor
python3 scripts/check_docs_links.py --check
python3 scripts/check_safety_wording.py --strict
python3 scripts/check_version_consistency.py --check
python3 scripts/check_release_readiness.py --check
pytest -q
( cd site && npm run build )
```

Expect tests and release gates to fail until hard-coded old repository references are updated intentionally.

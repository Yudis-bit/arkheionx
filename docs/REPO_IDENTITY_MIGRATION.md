# Repository identity migration

This is a **founder-only, external action plan**. Nothing here is run by the
agent; the destructive and remote steps must be performed by the maintainer.

## The hard truth

ArkheionX cannot honestly be called "ready for everyone" while it lives at
`github.com/Yudis-bit/DeFi-Exploit-PoCs` and ships the legacy `EVM/`, `MoveVM/`,
and `SVM/` exploit proof-of-concept folders at the repository root.

A first-time visitor sees a repository literally named "DeFi-Exploit-PoCs" with
exploit material, which directly contradicts the product's safety story
(local/static, no exploit automation, not an exploit tool, human review
required). Documentation can soften this, but it cannot resolve it. The
repository name and root contents are part of the public first impression.

**Verdict: repository identity is a blocker for broad public readiness. It is an
external action and is not resolved inside the source tree.**

## Why this is not a simple find-and-replace

The current identity is referenced in **dozens of files**, including some that
are asserted by tests and enforced by release gates. Changing the name without
updating these together will break `make validate`. Get the full live list with:

```sh
grep -rIl "Yudis-bit/DeFi-Exploit-PoCs" \
  --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=build .
```

High-priority surfaces (group them and change atomically):

| Surface | Files |
|---|---|
| Package metadata | `pyproject.toml` (`[project.urls]`) |
| Installers | `install.sh`, `site/public/install.sh`, `arkup` |
| Website | `site/src/pages/install.astro`, `site/src/pages/index.astro`, `site/src/components/Header.astro`, `site/src/components/Footer.astro` |
| Docs | `README.md`, `docs/GITHUB_ACTION_USAGE.md`, `docs/GITHUB_REPO_SURFACE.md`, `docs/INSTALLER.md`, `docs/WEBSITE_DEPLOYMENT.md`, others |
| GitHub config | `.github/ISSUE_TEMPLATE/config.yml`, `.github/workflows/evm.yml` (legacy) |
| Release gates (enforced) | `scripts/check_version_consistency.py` (`STABLE_ACTION`), `scripts/pre_audit_scan.py` |
| Tests (asserted) | `tests/test_installer.py`, `tests/test_arkup.py`, `tests/test_site_installer_public.py`, `tests/test_public_surface.py`, `tests/test_v1_stability.py` |
| Schema `$id` URLs | several files under `schemas/` |
| Example SARIF `informationUri` | several files under `examples/reports/` |

The GitHub Action reference `Yudis-bit/DeFi-Exploit-PoCs/.github/actions/pre-audit@v3.1.0`
is required by `check_version_consistency.py` and must be updated in the gate,
`README.md`, and `docs/GITHUB_ACTION_USAGE.md` at the same time.

## Option A — rename / split to a clean ArkheionX repo (preferred)

Goal: a clean public repository named `arkheionx` whose root is the tool, with
the legacy exploit-PoC corpus archived separately.

1. **Create the destination.** Either rename the GitHub repository to
   `arkheionx`, or create a new `Yudis-bit/arkheionx` and push a clean branch.
   Renaming preserves stars/issues; a new repo gives a clean root.
2. **Decide on history.** To preserve history, push the existing history to the
   new remote. To start clean, create a fresh history from the current tree.
3. **Archive the legacy corpus.** Move `EVM/`, `MoveVM/`, `SVM/` (and the
   `evm.yml` workflow) to a separate archive repository, or keep the old repo as
   the archive and remove that material from the ArkheionX repo.
4. **Update every reference** found by the `grep` above, including the enforced
   gate constants and the tests that assert the old URL.
5. **Update release tags / GitHub Action** references to the new path.
6. **Re-run the full validation matrix** (below) until green.
7. **Push** the clean ArkheionX repository and only then invite external users.

Example remote commands (founder runs manually; review each first):

```sh
# Preserve history into a new remote:
git remote add arkheionx git@github.com:Yudis-bit/arkheionx.git
git push arkheionx main

# Or set the new origin after a GitHub rename:
git remote set-url origin git@github.com:Yudis-bit/arkheionx.git
```

In-tree reference update (run, then review the diff before committing):

```sh
grep -rIl "Yudis-bit/DeFi-Exploit-PoCs" \
  --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=build . \
  | xargs sed -i 's#Yudis-bit/DeFi-Exploit-PoCs#Yudis-bit/arkheionx#g'
git diff   # review every change, especially gates and tests
```

Then run the validation matrix and fix anything the rename touched.

## Option B — stay in place with a disclaimer (temporary, not recommended)

If a rename is not yet possible, reduce the contradiction without claiming it is
solved:

- Make the ArkheionX product the unmistakable top of `README.md`.
- Add a prominent note that the legacy `EVM/`, `MoveVM/`, and `SVM/` folders are
  archived exploit-research material, not part of the tool.
- Keep the safety boundaries and "what this is not" wording prominent.

This is a mitigation for a limited audience. It is **not** sufficient for a broad
public launch, because the repository name itself still misrepresents the tool.

## Validation after migration

```sh
python3 scripts/check_docs_links.py --check
python3 scripts/check_safety_wording.py --strict
python3 scripts/check_version_consistency.py --check
python3 scripts/check_release_readiness.py --check
python3 -m unittest discover -s tests -p "test_*.py"
make validate
( cd site && npm ci && npm run build )
```

See [`PUBLIC_ALPHA_READINESS.md`](PUBLIC_ALPHA_READINESS.md) for how this blocker
gates broad public readiness, and [`WEBSITE_DEPLOYMENT.md`](WEBSITE_DEPLOYMENT.md)
for the related DNS/site step.

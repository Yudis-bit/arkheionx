# Arkheionx v4.0.0 — Release checklist

Run from the repository root. Every box must be green before the founder tags
and pushes. This release is **prepared locally**; tagging and pushing are
founder actions.

## Validation gates

- [ ] `git status --short` is clean.
- [ ] `python3 scripts/check_version_consistency.py --check`
- [ ] `python3 scripts/check_release_readiness.py --check`
- [ ] `python3 scripts/check_docs_links.py --check`
- [ ] `python3 scripts/check_safety_wording.py --strict`
- [ ] `python3 -m unittest discover -s tests -p "test_*.py"` (full suite passes)
- [ ] `make validate`

## Build and site

- [ ] `( cd site && npm ci && npm run build )` builds with no errors.
- [ ] `python3 -m build` succeeds (or the inability to build is documented).
- [ ] `python3 -m twine check dist/*` passes (if `dist/` was produced).
- [ ] `bash -n install.sh` and `bash -n site/public/install.sh` pass.

## Smokes

- [ ] Non-editable install smoke: `pip install .` then `arkheionx version`,
      `arkheionx doctor`, `arkheionx review-map examples/vault-strategy-oracle-fixture`.
- [ ] Fresh archive smoke: `git archive HEAD | tar -x` into a temp dir, install,
      and run the demo.
- [ ] `scripts/smoke_v4_release.sh` passes.

## Demo commands

- [ ] `arkheionx review-map examples/vault-strategy-oracle-fixture`
- [ ] `arkheionx test-gap-map examples/vault-strategy-oracle-fixture` shows
      `Source: <file>:<line>` references.
- [ ] `arkheionx proof-plan examples/vault-strategy-oracle-fixture`

## Docs and release artifacts

- [ ] `CHANGELOG.md` has a `## v4.0.0` section with an honest status.
- [ ] `docs/releases/V4_RELEASE_NOTES.md` is current.
- [ ] `docs/V4_STABLE_SCOPE.md` matches the shipped command surface.
- [ ] No unresolved P0 public-surface blocker.

## Release (founder only)

- [ ] Decide whether to bump the package version to `4.0.0` (updates
      `arkheionx/version.py`, `pyproject.toml`, and the version-locked tests
      together) or keep `3.9.0` and tag the milestone only.
- [ ] `git push origin main`
- [ ] `git tag -a v4.0.0 -m "Arkheionx v4.0.0 — stable local review-map workflow"`
- [ ] `git push origin v4.0.0`
- [ ] Draft the GitHub Release from `V4_RELEASE_NOTES.md`.

Nothing in this checklist performs RPC, live-chain, or exploit actions, and none
of it requires secrets.

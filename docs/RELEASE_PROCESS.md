# Release Process

How a release of Arkheionx Vault is prepared, validated, and shipped.

A "release" is any time the public surface of the repository materially
changes — new PoC, new docs section, new tooling, README rewrite,
launch event. This document describes the process for any of those.

## Principles

1. **Honest counts.** Every number in the README, dashboards, and
   launch material must match `metadata/registry.json` and the
   generated reports at the moment of release.
2. **No fake green.** A skipped CI job is reported as skipped, not as
   passed. A `verification_status=verified` claim requires a real run.
3. **One source of truth.** Generated files come from scripts. They
   are not hand-edited.
4. **Reversibility.** Releases are pushed to a branch first, reviewed,
   then merged or tagged. No force-push, no direct edit on `main`.

## Roles

- **Maintainer.** Yudistira Putra (`arkheionx`). Sole approver for
  registry changes and verification claims.
- **Reviewer.** Optional second reviewer for PRs. May be the
  maintainer's future self.
- **Contributor.** Anyone opening a research-candidate or
  assertion-hardening issue / PR.

## Release types

| Type | Branch | Validation | Tag |
|---|---|---|---|
| Patch (typo, doc fix, small metadata edit) | feature → main | metadata workflow | none |
| Minor (new PoC, new docs, new script) | feature → main | full validation gate | optional |
| Major (release-grade snapshot, launch) | release/x.y → main | full + launch checklist | recommended |

## Pre-release validation

Run, in order, from the repo root:

1. `git status --short` — must be clean (or only contain the staged
   release changes).
2. `python scripts/validate_metadata.py`
3. `python scripts/generate_registry.py --check`
4. `python scripts/score_pocs.py --check`
5. `python scripts/generate_verification_report.py --check`
6. `python scripts/poc_maturity_index.py --check`
7. `python scripts/research_dashboard.py --check`
8. `bash scripts/github_surface_setup.sh --dry-run`
9. From `EVM/`: `forge fmt --check` and `forge build`.

Any failure stops the release. Failures are fixed, generated files are
regenerated, and the validation gate is rerun. The sequence is
deterministic — running it twice in a row should produce no diff.

## Verification claims at release time

A release **must not** raise any entry's verification level unless:

- The entry's verification report contains real run output.
- `verification_status` is `verified`.
- `reproducibility` is `deterministic-confirmed`.
- The fork was archival, not public.

If those conditions are not all met, the entry stays where it was.

## CI

- `metadata.yml` runs on every PR. It validates the registry and
  checks that generated artifacts are up to date.
- `evm.yml` runs `forge fmt --check` + `forge build` on every PR.
  Optional fork-test job runs only when an `ETH_RPC_URL` secret is
  configured. A skipped fork-test job is reported as skipped.
- `docs.yml` checks required documentation files exist.

A release with a red CI run is not a release.

## Branching and tagging

- Work happens on a feature branch. Direct edits on `main` are not
  allowed.
- A release-grade snapshot uses a `release/x.y` branch.
- Tagging is optional. When used, tags follow `vYYYY.MM.DD` for date
  releases or `vMAJOR.MINOR.PATCH` for semver-style snapshots.
- No force-push to `main`. No `--no-verify`. No bypass of pre-commit
  hooks.

## Launch releases

A "launch release" is one accompanied by external posts (LinkedIn,
GitHub release notes, X thread). Launch releases follow the regular
process plus the launch checklist in `docs/RELEASE_CHECKLIST.md`.

The launch material under `docs/launch/` is reviewed at release time.
If the README's current-status numbers changed, the launch material is
updated to match before posting. Public posts referencing this archive
must not invent counts that the README does not state.

## Post-release

- Verify the registry table renders correctly on the GitHub web UI.
- Verify the GitHub repo About panel shows the description and topics
  set by `scripts/github_surface_setup.sh`.
- Confirm in incognito: a first-time visitor sees the README, the
  research thesis, and the honest-status table above the fold.
- Open the next milestone's planning issue if applicable.

## When something goes wrong

- Discovered a fake claim post-release: open a correction PR,
  reference the offending content, fix, ship a patch release. Do not
  rewrite history.
- Discovered an unsafe-content concern: redact, ship a patch release,
  acknowledge the reporter privately.
- Discovered CI was green on a skipped step that should have run:
  treat the previous release as not-validated, fix CI, rerun
  validation, ship a patch release.

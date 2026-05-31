# v3.0 Readiness Checklist

The readiness criteria for cutting Arkheionx **v3.0.0 — DeFi Value Flow
Workbench** (public stable). v3.0.0 has shipped as the public stable launch;
this remains as the record of what the launch required.

**Status: shipped.** All readiness items below were satisfied for the v3.0.0
public stable release. The current active milestone is **v3.1.0** (incremental
workbench improvements after the v3.0.0 cut).

## 1. Public command surface
- [x] Command inventory documented ([`PUBLIC_SURFACE.md`](PUBLIC_SURFACE.md)).
- [x] Contract test guards the documented surface against drift.
- [x] Stability labels reviewed for the v3.0 candidate.

## 2. Install / update lifecycle
- [x] `install.sh` / `uninstall.sh` / `arkup` syntax-checked and documented.
- [x] Install receipt schema present and read by `doctor --install` / `arkup`.
- [x] No sudo, no profile edits, no secrets, no RPC.

## 3. Demo workflow
- [x] Three bundled demos (`oracle-staking`, `amm-swap`, `lending-vault`).
- [x] `demo --copy` works from an installed package and outside the repo.
- [x] End-to-end open/hunt/evidence-status/validate-artifacts smoke tests.

## 4. Package data
- [x] Fixtures bundled via `[tool.setuptools.package-data]`; source-only.
- [x] No generated artifacts, secrets, RPC URLs, or live addresses bundled.

## 5. Output consistency
- [x] Shared `ARKHEIONX <COMMAND>` / `Status:` / `Next` shape.
- [x] Restrained TTY-gated color; JSON and artifacts stay plain.

## 6. Evidence model
- [x] Explicit ladder; heuristics are not presented as confirmed bugs.
- [x] Evidence/report draft wording reviewed for the v3.0 candidate.

## 7. Artifact validation
- [x] `validate-artifacts` checks required fields and safe transitions.

## 8. Docs and README
- [x] README landing page with visuals and current stable line.
- [x] Docs map links public surface, stability contract, and this checklist.
- [x] Docs audit completed for the v3.0 public stable launch.

## 9. Safety boundaries
- [x] Consistent safety wording; `check_safety_wording --strict` passes.

## 10. Release process
- [x] Release readiness gate (`scripts/check_release_readiness.py`).
- [x] Versioned changelog + per-release notes; finalize/post-release flow.

## 11. Known limitations accepted for v3.0
- Heuristic-first; Foundry optional; local-only; not a formal audit.
- Not on PyPI; no Homebrew, standalone binary, or domain installer.

## 12. What v3.0 will not claim
- No guaranteed vulnerability discovery, no final severity, no bounty
  eligibility, no live-chain testing, no auto-submission, no PyPI/Homebrew/
  binary/domain-installer availability unless actually implemented.

See [`STABILITY_CONTRACT.md`](STABILITY_CONTRACT.md) and [`ROADMAP.md`](ROADMAP.md).

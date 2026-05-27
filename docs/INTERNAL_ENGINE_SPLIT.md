# Arkheionx Internal Engine Split

Arkheionx v1.6.0 begins moving shared internals out of standalone scripts and
into a small `arkheionx/` package. This is structural release preparation for a
future installable CLI/package, not a new scanner capability release.

Existing script entrypoints remain supported:

```sh
python3 scripts/pre_audit_scan.py --root . --protocol-type auto
python3 scripts/generate_test_plan.py --check
python3 scripts/generate_search_index.py --check
```

## What Moved

- Shared version metadata now lives in `arkheionx/version.py`.
- Shared safety wording lives in `arkheionx/core/safety.py`.
- Small file/path helpers live in `arkheionx/core/files.py` and
  `arkheionx/core/paths.py`.
- Rule-pack metadata lives in `arkheionx/rules/registry.py`.
- Test-plan, ecosystem, paid-offer, and feedback generator logic now has
  package modules behind the existing scripts.
- A pre-v2 CLI candidate lives at `arkheionx/cli/main.py`.

## What Stays In Scripts

`scripts/pre_audit_scan.py` remains the primary scanner entrypoint. v1.6.0 only
extracts low-risk constants and helpers from the scanner path. Scoring,
finding generation, report rendering, SARIF output, and issue-plan behavior
remain script-owned for now.

## Compatibility

The internal package supports the old scripts; it does not replace them yet.
Documentation, GitHub Action examples, Makefile targets, and validation checks
continue to call `scripts/*.py`.

v1.9.0 adds `scan`, `validate-config`, `test-plan`, and `search` module
commands as wrappers around the existing scripts/modules. The script surface
remains supported until the v2 package release.

## Safety Boundary

The split adds no RPC calls, live-chain behavior, transaction execution,
deployed-contract scanning, external APIs, exploit automation, or secret
handling. Outputs remain readiness planning artifacts, not formal audits,
formal verification, proof of safety, or security guarantees.

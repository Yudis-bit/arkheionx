# Release Checklist

A release is not cut until every applicable box is checked or marked N/A with a
written reason in the release PR.

## Scope

- [ ] Release type identified: scanner, rule pack, archive, verification,
      docs, or service surface.
- [ ] Version named in `CHANGELOG.md`.
- [ ] No unsupported claims added to README, docs, reports, or release notes.
- [ ] Current archive truth preserved: 18 structured PoCs, 0 L4+ archival
      confirmed entries unless regenerated artifacts prove otherwise.

## Scanner And Product Validation

- [ ] `python3 -m py_compile scripts/pre_audit_scan.py scripts/generate_search_index.py`
- [ ] `python3 -m unittest discover -s tests -p "test_*.py"`
- [ ] Mini-vault scan regenerated:

  ```sh
  python3 scripts/pre_audit_scan.py \
    --root examples/mini-vault \
    --protocol-type auto \
    --output examples/reports/mini-vault-pre-audit-report.md \
    --json-output examples/reports/mini-vault-pre-audit-report.json \
    --generate-invariant-skeletons
  ```

- [ ] Vault-risk fixture scan regenerated:

  ```sh
  python3 scripts/pre_audit_scan.py \
    --root examples/vault-risk-fixture \
    --protocol-type vault \
    --output examples/reports/vault-risk-fixture-pre-audit-report.md \
    --json-output examples/reports/vault-risk-fixture-pre-audit-report.json \
    --generate-invariant-skeletons
  ```

- [ ] JSON outputs parse successfully.
- [ ] Markdown reports include the disclaimer.
- [ ] Vault report includes `Vault Rule Pack Coverage`.

## Search And Registry

- [ ] `python3 scripts/generate_search_index.py --check`
- [ ] `python3 scripts/generate_registry.py --check`
- [ ] `python3 scripts/validate_metadata.py`
- [ ] `python3 scripts/score_pocs.py --check`
- [ ] `python3 scripts/generate_verification_report.py --check`
- [ ] `python3 scripts/poc_maturity_index.py --check`
- [ ] `python3 scripts/research_dashboard.py --check`

## README And Docs

- [ ] README renders cleanly on GitHub.
- [ ] Quick Start YAML is valid.
- [ ] Sample commands are readable.
- [ ] Registry table remains between generated markers.
- [ ] `docs/VAULT_RULE_PACK.md` linked from README and search index.
- [ ] `docs/GITHUB_ACTION_USAGE.md` matches action inputs.
- [ ] `docs/READINESS_SCORE.md` matches scanner scoring categories.
- [ ] `SERVICES.md`, `docs/MONETIZATION.md`, and `docs/SPONSORSHIP.md` avoid
      formal-audit or guarantee claims.

## Safety Scan

- [ ] No live-target workflow added.
- [ ] No RPC requirement added to scanner or action.
- [ ] No transaction submission, key handling, or deployed-contract testing.
- [ ] No private keys, mnemonics, RPC credentials, or secrets in the diff.
- [ ] No banned/suspicious marketing phrases from the CI safety list.

## GitHub Surface

- [ ] Issue templates render correctly.
- [ ] GitHub Action path is correct.
- [ ] CI workflow runs scanner tests and fixture scans.
- [ ] Recommended topics reviewed in README/search guide.
- [ ] Discussions/categories updated manually if part of release.

## Release Steps

- [ ] Commit changes.
- [ ] Open release PR.
- [ ] Wait for CI green.
- [ ] Merge to `main`.
- [ ] Tag from `main` only after approval.
- [ ] Publish GitHub release from `CHANGELOG.md`.
- [ ] Announce only with honest, bounded language.

Releases are checkpoints, not finish lines.

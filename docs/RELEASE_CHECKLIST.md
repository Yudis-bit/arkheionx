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
- [ ] `python3 -m py_compile scripts/post_pr_comment.py`
- [ ] `python3 -m unittest discover -s tests -p "test_*.py"`
- [ ] Mini-vault scan regenerated:

  ```sh
  python3 scripts/pre_audit_scan.py \
    --root examples/mini-vault \
    --protocol-type auto \
    --output examples/reports/mini-vault-pre-audit-report.md \
    --json-output examples/reports/mini-vault-pre-audit-report.json \
    --sarif-output examples/reports/mini-vault.sarif.json \
    --baseline-output examples/reports/mini-vault.baseline.json \
    --summary-output examples/reports/mini-vault-action-summary.md \
    --comment-output examples/reports/mini-vault-pr-comment.md \
    --issue-checklist-output examples/reports/mini-vault-issue-checklist.md \
    --generate-invariant-skeletons
  ```

- [ ] Vault-risk fixture scan regenerated:

  ```sh
  python3 scripts/pre_audit_scan.py \
    --root examples/vault-risk-fixture \
    --protocol-type vault \
    --output examples/reports/vault-risk-fixture-pre-audit-report.md \
    --json-output examples/reports/vault-risk-fixture-pre-audit-report.json \
    --sarif-output examples/reports/vault-risk-fixture.sarif.json \
    --baseline-output examples/reports/vault-risk-fixture.baseline.json \
    --summary-output examples/reports/vault-risk-fixture-action-summary.md \
    --comment-output examples/reports/vault-risk-fixture-pr-comment.md \
    --issue-checklist-output examples/reports/vault-risk-fixture-issue-checklist.md \
    --generate-invariant-skeletons
  ```

- [ ] Baseline diff scan regenerated:

  ```sh
  python3 scripts/pre_audit_scan.py \
    --root examples/vault-risk-fixture \
    --protocol-type vault \
    --compare-baseline examples/reports/vault-risk-fixture.baseline.json \
    --output examples/reports/vault-risk-fixture-diff-report.md \
    --json-output examples/reports/vault-risk-fixture-diff-report.json \
    --diff-output examples/reports/vault-risk-fixture-diff.md \
    --diff-json-output examples/reports/vault-risk-fixture-diff.json \
    --sarif-output examples/reports/vault-risk-fixture-diff.sarif.json \
    --summary-output examples/reports/vault-risk-fixture-diff-summary.md \
    --comment-output examples/reports/vault-risk-fixture-diff-comment.md \
    --issue-checklist-output examples/reports/vault-risk-fixture-diff-checklist.md
  ```

- [ ] Config suppression scan regenerated:

  ```sh
  python3 scripts/pre_audit_scan.py \
    --root examples/vault-risk-fixture \
    --protocol-type vault \
    --config examples/arkheionx.config.example.json \
    --output examples/reports/vault-risk-fixture-config-report.md \
    --json-output examples/reports/vault-risk-fixture-config-report.json \
    --summary-output examples/reports/vault-risk-fixture-config-summary.md \
    --comment-output examples/reports/vault-risk-fixture-config-comment.md \
    --issue-checklist-output examples/reports/vault-risk-fixture-config-checklist.md
  ```

- [ ] JSON outputs parse successfully.
- [ ] JSON outputs include canonical `findings`.
- [ ] SARIF outputs parse successfully and use SARIF `2.1.0`.
- [ ] SARIF outputs include rules, results, and readiness/not-vulnerability
      properties.
- [ ] Baseline JSON includes finding fingerprints.
- [ ] Diff JSON includes new, resolved, unchanged, changed, and suppressed
      counts.
- [ ] Diff report includes `Baseline Diff`.
- [ ] Markdown reports include the disclaimer.
- [ ] Vault report includes `Vault Rule Pack Coverage`.
- [ ] PR comment output contains `<!-- arkheionx-pre-audit-comment -->`.
- [ ] Summary output contains `Score:`.
- [ ] Generated issue checklist contains Markdown checkboxes.
- [ ] Config suppression output shows `Suppressed Readiness Gaps`.

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
- [ ] README top section includes Start Here paths for builders and
      researchers.
- [ ] Latest release section names the current stable release accurately.
- [ ] Stable GitHub Action examples use the latest released tag.
- [ ] `@main` examples are labeled as development usage.
- [ ] Quick Start YAML is valid.
- [ ] Sample commands are readable.
- [ ] Registry table remains between generated markers.
- [ ] `docs/VAULT_RULE_PACK.md` linked from README and search index.
- [ ] `docs/GITHUB_ACTION_USAGE.md` matches action inputs.
- [ ] `docs/PR_COMMENT_MODE.md` documents permissions and update mode.
- [ ] `docs/GENERATED_ISSUE_CHECKLIST.md` documents manual issue workflow.
- [ ] `docs/ARKHEIONX_CONFIG.md` documents suppression behavior.
- [ ] `docs/SARIF_OUTPUT.md` documents Code Scanning upload and severity
      mapping.
- [ ] `docs/BASELINE_DIFF_MODE.md` documents baseline and diff usage.
- [ ] `docs/CI_GATING.md` documents fail thresholds and false-positive
      caution.
- [ ] `docs/READINESS_SCORE.md` matches scanner scoring categories.
- [ ] `SERVICES.md`, `docs/MONETIZATION.md`, and `docs/SPONSORSHIP.md` avoid
      formal-audit or guarantee claims.
- [ ] Stale release phrases are absent:

  ```sh
  python3 - <<'PY'
  from pathlib import Path

  version = "v0" + ".4" + ".0"
  phrases = [
      version + " - " + "Unreleased",
      "until " + version + " is tagged",
      "prepared, " + "not tagged",
      "prepared, " + "not released",
      "upcoming " + version,
      "planned " + version,
  ]
  for root in [Path("README.md"), Path("CHANGELOG.md"), Path("docs")]:
      files = [root] if root.is_file() else root.rglob("*.md")
      for path in files:
          text = path.read_text(encoding="utf-8", errors="ignore")
          for phrase in phrases:
              if phrase.lower() in text.lower():
                  raise SystemExit(f"stale release phrase: {path}: {phrase}")
  PY
  ```

- [ ] v0.5.0 next milestone is visible in roadmap and release notes.

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

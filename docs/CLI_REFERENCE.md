# Arkheionx CLI Reference

Arkheionx v1.0.0 treats the flags below as the stable public CLI surface for
`scripts/pre_audit_scan.py`.

The scanner is local/static. It does not require RPC, private keys, mnemonics,
or live-chain access.

## Core

| Flag | Default | Purpose |
|---|---|---|
| `--root PATH` | `.` | Repository root to scan. |
| `--protocol-type TYPE` | `auto` | Protocol hint: `auto`, `vault`, `amm`, `lending`, `staking`, `oracle`, or `generic`. |
| `--output PATH` | `ARKHEIONX_PRE_AUDIT_REPORT.md` | Markdown pre-audit readiness report. |
| `--json-output PATH` | empty | Machine-readable JSON report. |

## Reports

| Flag | Purpose |
|---|---|
| `--summary-output PATH` | GitHub Actions summary Markdown. |
| `--comment-output PATH` | Pull request comment body. |
| `--issue-checklist-output PATH` | Markdown remediation checklist. |
| `--issue-plan-output PATH` | JSON remediation issue plan. |
| `--launch-report-output PATH` | Launch Readiness Report Markdown. |
| `--sprint-plan-output PATH` | Pre-Audit Sprint Plan Markdown. |
| `--sprint-days N` | Sprint length: `3`, `5`, `7`, or `10`. |
| `--contest-readiness-output PATH` | Contest Readiness Report Markdown. |
| `--executive-summary-output PATH` | Short executive summary Markdown. |
| `--remediation-roadmap-output PATH` | Remediation roadmap Markdown. |

## Security Output

| Flag | Purpose |
|---|---|
| `--sarif-output PATH` | SARIF 2.1.0 readiness output for GitHub Code Scanning upload. |
| `--baseline-output PATH` | Compact baseline snapshot. |
| `--compare-baseline PATH` | Previous baseline for diff mode. |
| `--diff-output PATH` | Markdown diff report. |
| `--diff-json-output PATH` | JSON diff output. |

## Behavior

| Flag | Purpose |
|---|---|
| `--config PATH` | Optional `.arkheionx.json` configuration. |
| `--generate-invariant-skeletons` | Generate safe local Foundry invariant skeletons. |
| `--fail-score-below N` | Exit with readiness failure if score is below threshold. |
| `--fail-on-new-high` | Exit with readiness failure when diff mode finds new high/critical gaps. |
| `--fail-on-unsuppressed-high` | Exit with readiness failure when unsuppressed high/critical gaps exist. |
| `--fail-on-critical-readiness-gap` | Exit with readiness failure when critical readiness gaps exist. |

## Advanced

| Flag | Purpose |
|---|---|
| `--semantic-lite` | Enable semantic-lite Solidity extraction. Enabled by default. |
| `--no-semantic-lite` | Disable semantic-lite extraction. |
| `--slither` | Enable optional local Slither enrichment if available. |
| `--slither-json PATH` | Use an existing local Slither JSON output. |
| `--slither-output PATH` | Write normalized Arkheionx Slither summary. |
| `--slither-timeout SECONDS` | Timeout for optional Slither execution. |
| `--slither-strict` | Fail if requested Slither evidence is unavailable or warns. |
| `--min-confidence-for-issue-plan LEVEL` | Include issue-plan findings at `low`, `medium`, or `high` confidence. |
| `--create-issues` | Reserved local compatibility flag. It does not create remote issues. |
| `--verbose` | Print additional scanner details. |

## Stability Policy

Patch releases may add optional fields or flags, but v1.0.0 flags should remain
backward compatible unless a future changelog explicitly marks a breaking
change. Findings remain readiness signals, not formal audit findings or
vulnerability confirmations.

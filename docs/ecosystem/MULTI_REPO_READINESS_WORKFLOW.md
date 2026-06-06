# Multi-Repo Readiness Workflow

This workflow explains how to use Arkheionx across multiple authorized
repositories without adding remote cloning, external APIs, or live-chain
behavior.

## Safe Local Flow

Run Arkheionx separately on each authorized repository:

```sh
python3 scripts/pre_audit_scan.py \
  --root /path/to/repo-alpha \
  --protocol-type auto \
  --output repo-alpha/reports/ARKHEIONX_PRE_AUDIT_REPORT.md \
  --json-output repo-alpha/reports/arkheionx-report.json \
  --issue-plan-output repo-alpha/reports/ARKHEIONX_ISSUE_PLAN.json
```

Repeat for each authorized repository, then collect JSON report paths in a
local manifest.

Example report locations:

- `repo-alpha/reports/arkheionx-report.json`
- `repo-beta/reports/arkheionx-report.json`
- `repo-gamma/reports/arkheionx-report.json`

## Manifest Pattern

Use [`../../templates/ecosystem_manifest.example.json`](../../templates/ecosystem_manifest.example.json)
as a starting point.

Each entry should use a safe alias such as `Repo Alpha`, not a private project
name, unless public permission exists.

## What Not To Do

- Do not scan repositories without authorization.
- Do not clone remote repositories automatically.
- Do not fetch from network as part of ecosystem summary generation.
- Do not include private code snippets in public summaries.
- Do not publish unpatched vulnerability details.

## Output

The ecosystem report generator currently uses local metadata and synthetic
examples. It writes:

- [`../../reports/ecosystem_readiness_summary.md`](../../reports/ecosystem_readiness_summary.md)
- [`../../reports/ecosystem_common_gaps.md`](../../reports/ecosystem_common_gaps.md)

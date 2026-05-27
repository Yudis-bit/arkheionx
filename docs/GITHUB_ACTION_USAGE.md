# GitHub Action Usage

The Arkheionx pre-audit action is a GitHub-native readiness check for
authorized repositories. Default scans require no secrets, no RPC endpoint, and
no live-chain access.

Stable examples use:

```yaml
uses: Yudis-bit/DeFi-Exploit-PoCs/.github/actions/pre-audit@v1.2.0
```

Use `@main` only for development/testing of unreleased changes.

## Minimal Workflow

```yaml
name: Arkheionx Pre-Audit Readiness

on:
  pull_request:
  workflow_dispatch:

permissions:
  contents: read

jobs:
  readiness:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: Yudis-bit/DeFi-Exploit-PoCs/.github/actions/pre-audit@v1.2.0
        with:
          root: "."
          protocol-type: "auto"
          output: "reports/ARKHEIONX_PRE_AUDIT_REPORT.md"
          json-output: "reports/arkheionx-report.json"
```

## Advanced Workflow

This workflow generates SARIF, a baseline, an issue plan, and delivery
artifacts. PR comments and real issue creation remain disabled by default.

```yaml
name: Arkheionx Advanced Readiness

on:
  pull_request:
  workflow_dispatch:

permissions:
  contents: read
  security-events: write

jobs:
  readiness:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: Yudis-bit/DeFi-Exploit-PoCs/.github/actions/pre-audit@v1.2.0
        with:
          root: "."
          protocol-type: "auto"
          output: "reports/ARKHEIONX_PRE_AUDIT_REPORT.md"
          json-output: "reports/arkheionx-report.json"
          sarif-output: "reports/arkheionx.sarif.json"
          baseline-output: "reports/arkheionx.baseline.json"
          issue-plan-output: "reports/ARKHEIONX_ISSUE_PLAN.json"
          issue-checklist-output: "reports/ARKHEIONX_ISSUE_CHECKLIST.md"
          launch-report-output: "reports/ARKHEIONX_LAUNCH_REPORT.md"
          sprint-plan-output: "reports/ARKHEIONX_SPRINT_PLAN.md"
          contest-readiness-output: "reports/ARKHEIONX_CONTEST_READINESS.md"
          executive-summary-output: "reports/ARKHEIONX_EXECUTIVE_SUMMARY.md"
          remediation-roadmap-output: "reports/ARKHEIONX_REMEDIATION_ROADMAP.md"
          pr-comment: "false"
          create-github-issues: "false"

      - uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: reports/arkheionx.sarif.json
```

SARIF results are readiness gaps, not confirmed vulnerabilities.

## Stable v1.2.x Inputs

| Input | Default | Stable | Purpose |
|---|---|---|---|
| `root` | `.` | Yes | Repository root to scan. |
| `protocol-type` | `auto` | Yes | Protocol hint. |
| `output` | `ARKHEIONX_PRE_AUDIT_REPORT.md` | Yes | Markdown report path. |
| `json-output` | empty | Yes | JSON report path. |
| `sarif-output` | empty | Yes | SARIF output path. |
| `upload-sarif` | `false` | Yes | Documentation flag; upload with CodeQL action. |
| `baseline-output` | empty | Yes | Baseline JSON path. |
| `compare-baseline` | empty | Yes | Previous baseline for diff mode. |
| `diff-output` | empty | Yes | Markdown diff path. |
| `diff-json-output` | empty | Yes | JSON diff path. |
| `summary` | `true` | Yes | Write GitHub step summary. |
| `summary-output` | `ARKHEIONX_ACTION_SUMMARY.md` | Yes | Local summary Markdown path. |
| `pr-comment` | `false` | Yes | Opt-in PR comment mode. |
| `github-token` | empty | Yes | Token for optional PR comment/issue workflows. |
| `comment-output` | `ARKHEIONX_PR_COMMENT.md` | Yes | PR comment body path. |
| `comment-mode` | `update` | Yes | PR comment behavior. |
| `create-issue-checklist` | `true` | Yes | Generate Markdown issue checklist. |
| `issue-checklist-output` | `ARKHEIONX_ISSUE_CHECKLIST.md` | Yes | Issue checklist path. |
| `issue-plan-output` | empty | Yes | Issue plan JSON path. |
| `create-github-issues` | `false` | Yes | Opt-in remote issue workflow. |
| `issue-create-mode` | `dry-run` | Yes | `dry-run`, `create`, or `update`. |
| `issue-grouping` | `one-per-finding` | Yes | Issue grouping mode. |
| `issue-max` | `5` | Yes | Maximum issue operations. |
| `issue-only-priority` | `high` | Yes | Priority filter. |
| `issue-labels` | empty | Yes | Extra labels. |
| `issue-assignees` | empty | Yes | Assignees. |
| `issue-dry-run-output` | `ARKHEIONX_ISSUE_DRY_RUN.md` | Yes | Dry-run Markdown path. |
| `launch-report-output` | empty | Yes | Launch Report path. |
| `sprint-plan-output` | empty | Yes | Sprint Plan path. |
| `sprint-days` | `5` | Yes | `3`, `5`, `7`, or `10`. |
| `contest-readiness-output` | empty | Yes | Contest Readiness path. |
| `executive-summary-output` | empty | Yes | Executive Summary path. |
| `remediation-roadmap-output` | empty | Yes | Remediation Roadmap path. |
| `semantic-lite` | `true` | Yes | Semantic-lite extraction. |
| `slither` | `false` | Yes | Optional local Slither enrichment. |
| `slither-json` | empty | Yes | Existing Slither JSON path. |
| `slither-output` | empty | Yes | Normalized Slither summary path. |
| `slither-timeout` | `60` | Yes | Slither timeout in seconds. |
| `slither-strict` | `false` | Yes | Fail if Slither evidence is unavailable/warns. |
| `min-confidence-for-issue-plan` | `low` | Yes | Minimum issue-plan confidence. |
| `config` | `.arkheionx.json` | Yes | Config path. |
| `generate-invariant-skeletons` | `false` | Yes | Generate safe invariant skeletons. |
| `fail-on-critical-readiness-gap` | `false` | Yes | CI readiness gate. |
| `fail-on-new-high` | `false` | Yes | Diff-mode CI gate. |
| `fail-score-below` | empty | Yes | Numeric score gate. |
| `fail-on-unsuppressed-high` | `false` | Yes | Unsuppressed high/critical gate. |
| `create-issues` | `false` | Legacy | Local compatibility flag; no remote issues. |
| `verbose` | `false` | Yes | Print scanner details. |

## Pull Request Comment Mode

PR comment mode is off by default. Enable it only when you want Arkheionx to
post or update a pull request comment:

```yaml
permissions:
  contents: read
  pull-requests: write
  issues: write

steps:
  - uses: actions/checkout@v4
  - uses: Yudis-bit/DeFi-Exploit-PoCs/.github/actions/pre-audit@v1.2.0
    with:
      protocol-type: "auto"
      json-output: "reports/arkheionx-report.json"
      pr-comment: "true"
      github-token: ${{ secrets.GITHUB_TOKEN }}
      comment-mode: "update"
```

## Optional Issue Workflow

Issue creation is disabled by default. Start with dry-run mode:

```yaml
with:
  issue-plan-output: "reports/ARKHEIONX_ISSUE_PLAN.json"
  create-github-issues: "true"
  issue-create-mode: "dry-run"
  issue-dry-run-output: "reports/ARKHEIONX_ISSUE_DRY_RUN.md"
  issue-max: "5"
```

To create or update GitHub issues, explicitly set `issue-create-mode` to
`create` or `update`, provide `github-token`, and grant `issues: write` in a
repository you own or are authorized to manage.

Generated issues are readiness tasks, not formal audit findings.

## Semantic-Lite And Optional Slither

Semantic-lite extraction is enabled by default. Slither enrichment is optional
and local; Arkheionx does not install Slither automatically.

```yaml
steps:
  - uses: actions/checkout@v4
  - run: pipx install slither-analyzer
  - uses: Yudis-bit/DeFi-Exploit-PoCs/.github/actions/pre-audit@v1.2.0
    with:
      protocol-type: "auto"
      slither: "true"
      slither-output: "reports/arkheionx-slither-summary.json"
```

If Slither is unavailable, Arkheionx continues unless `slither-strict: "true"`
is explicitly set.

## Local CLI Equivalent

```sh
python3 scripts/pre_audit_scan.py \
  --root . \
  --protocol-type auto \
  --output reports/ARKHEIONX_PRE_AUDIT_REPORT.md \
  --json-output reports/arkheionx-report.json \
  --sarif-output reports/arkheionx.sarif.json \
  --baseline-output reports/arkheionx.baseline.json \
  --issue-checklist-output reports/ARKHEIONX_ISSUE_CHECKLIST.md \
  --issue-plan-output reports/ARKHEIONX_ISSUE_PLAN.json
```

Arkheionx ignores its own generated reports and artifacts by default during
future scans. This prevents old reports, issue plans, SARIF, baselines, and
delivery outputs from influencing readiness scores or evidence.

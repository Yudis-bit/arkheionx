# GitHub Action Usage

The Arkheionx pre-audit action is a GitHub-native readiness check for
authorized repositories. It scans local files, writes Markdown/JSON artifacts,
can generate a job summary, and can optionally post a concise pull request
comment.

Default scans require no secrets, no RPC endpoint, and no live-chain access.

## Minimal Workflow

Use this in an external repository when you only want a manual readiness scan:

```yaml
name: Arkheionx Pre-Audit Scan

on:
  workflow_dispatch:

permissions:
  contents: read

jobs:
  pre-audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: Yudis-bit/DeFi-Exploit-PoCs/.github/actions/pre-audit@v0.7.0
        with:
          protocol-type: auto
```

Use `@main` only if you intentionally want the latest development branch.

Development usage:

```yaml
- uses: Yudis-bit/DeFi-Exploit-PoCs/.github/actions/pre-audit@main
  with:
    protocol-type: auto
```

## Public Demo Workflow

This repository includes `.github/workflows/arkheionx-demo.yml`. It is
`workflow_dispatch` only, scans `examples/oracle-staking-fixture`, uploads demo
artifacts, and does not create GitHub issues.

For local demo commands, see [`TRY_IN_5_MINUTES.md`](TRY_IN_5_MINUTES.md).

## Pull Request Summary Workflow

This workflow writes a report, JSON, generated issue checklist, and GitHub
Actions job summary without commenting on the pull request:

```yaml
name: Arkheionx Pre-Audit Scan

on:
  pull_request:
    branches: [main]

permissions:
  contents: read

jobs:
  pre-audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: Yudis-bit/DeFi-Exploit-PoCs/.github/actions/pre-audit@v0.7.0
        with:
          root: "."
          protocol-type: "auto"
          output: "ARKHEIONX_PRE_AUDIT_REPORT.md"
          json-output: "arkheionx-report.json"
          summary: "true"
          create-issue-checklist: "true"
```

## Pull Request Comment Workflow

PR comment mode is off by default. Enable it only when you want Arkheionx to
post or update a pull request comment containing the score and top readiness
gaps.

```yaml
name: Arkheionx PR Readiness

on:
  pull_request:
    branches: [main]

permissions:
  contents: read
  pull-requests: write
  issues: write

jobs:
  pre-audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: Yudis-bit/DeFi-Exploit-PoCs/.github/actions/pre-audit@v0.7.0
        with:
          protocol-type: "auto"
          json-output: "arkheionx-report.json"
          pr-comment: "true"
          github-token: ${{ secrets.GITHUB_TOKEN }}
          comment-mode: "update"
```

Update mode searches for:

```html
<!-- arkheionx-pre-audit-comment -->
```

If a matching comment exists, Arkheionx updates it instead of posting a new
comment.

## SARIF And Code Scanning Workflow

Arkheionx can generate SARIF for GitHub Code Scanning-compatible workflows.
Use a separate upload step:

```yaml
permissions:
  contents: read
  security-events: write

steps:
  - uses: actions/checkout@v4
  - uses: Yudis-bit/DeFi-Exploit-PoCs/.github/actions/pre-audit@v0.7.0
    with:
      protocol-type: "auto"
      output: "ARKHEIONX_PRE_AUDIT_REPORT.md"
      json-output: "arkheionx-report.json"
      sarif-output: "arkheionx.sarif.json"
  - uses: github/codeql-action/upload-sarif@v3
    if: always()
    with:
      sarif_file: arkheionx.sarif.json
```

SARIF results are readiness gaps, not confirmed vulnerabilities.

## Baseline Diff Workflow

Generate a baseline:

```yaml
with:
  baseline-output: "arkheionx.baseline.json"
```

Compare against a committed or downloaded baseline:

```yaml
with:
  compare-baseline: "arkheionx.baseline.json"
  diff-output: "ARKHEIONX_DIFF.md"
  diff-json-output: "arkheionx-diff.json"
```

Diff mode classifies readiness gaps as new, resolved, unchanged, or changed.

## Generated Issue Plan Workflow

Arkheionx can generate a machine-readable issue plan without creating any
GitHub issues:

```yaml
with:
  issue-plan-output: "ARKHEIONX_ISSUE_PLAN.json"
  issue-checklist-output: "ARKHEIONX_ISSUE_CHECKLIST.md"
```

The issue plan contains deterministic markers, labels, titles, disclaimers, and
defensive remediation tasks for each selected readiness gap.

## Dry-Run Issue Creation

Issue creation is disabled by default. Start with dry-run mode:

```yaml
with:
  create-github-issues: "true"
  issue-create-mode: "dry-run"
  issue-plan-output: "ARKHEIONX_ISSUE_PLAN.json"
  issue-dry-run-output: "ARKHEIONX_ISSUE_DRY_RUN.md"
  issue-max: "5"
```

Dry-run mode makes no GitHub API calls.

## Create Or Update Arkheionx Issues

Only enable this in repositories you own or are authorized to manage:

```yaml
permissions:
  contents: read
  issues: write

steps:
  - uses: actions/checkout@v4
  - uses: Yudis-bit/DeFi-Exploit-PoCs/.github/actions/pre-audit@v0.7.0
    with:
      protocol-type: "auto"
      create-github-issues: "true"
      issue-create-mode: "create"
      issue-plan-output: "ARKHEIONX_ISSUE_PLAN.json"
      issue-max: "5"
      issue-only-priority: "high"
      github-token: ${{ secrets.GITHUB_TOKEN }}
```

Use `issue-create-mode: "update"` to update existing Arkheionx issues that
contain deterministic markers such as `<!-- arkheionx-issue:ARK-VLT-001 -->`.
Generated issues are readiness tasks, not formal audit findings.

## Optional CI Gates

All gates are disabled by default:

```yaml
with:
  fail-score-below: "70"
  fail-on-new-high: "true"
  fail-on-unsuppressed-high: "false"
```

Use these as readiness gates only. They are not formal vulnerability
confirmations.

## Vault Builder Workflow

For ERC4626-like vaults, strategy vaults, and share/accounting systems:

```yaml
name: Arkheionx Vault Readiness

on:
  workflow_dispatch:
  pull_request:
    branches: [main]

permissions:
  contents: read
  pull-requests: write
  issues: write

jobs:
  vault-readiness:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: Yudis-bit/DeFi-Exploit-PoCs/.github/actions/pre-audit@v0.7.0
        with:
          protocol-type: "vault"
          output: "ARKHEIONX_VAULT_READINESS_REPORT.md"
          json-output: "arkheionx-vault-report.json"
          generate-invariant-skeletons: "true"
          create-issue-checklist: "true"
          pr-comment: "true"
          github-token: ${{ secrets.GITHUB_TOKEN }}
```

## Workflow With Config

Create `.arkheionx.json` in your repository to ignore paths, add local search
tags, and document suppressions:

```yaml
with:
  config: ".arkheionx.json"
```

Suppressed findings are still shown under `Suppressed Readiness Gaps` in the
report and in `suppressed_findings` in JSON. Suppression is not proof of
safety.

## Semantic-Lite And Optional Slither

Semantic-lite extraction is enabled by default. It attaches evidence,
confidence reasons, detection sources, and affected functions to readiness
findings.

```yaml
with:
  semantic-lite: "true"
  min-confidence-for-issue-plan: "low"
```

Slither enrichment is optional and local. Arkheionx does not install Slither
automatically:

```yaml
steps:
  - uses: actions/checkout@v4
  - run: pipx install slither-analyzer
  - uses: Yudis-bit/DeFi-Exploit-PoCs/.github/actions/pre-audit@v0.7.0
    with:
      protocol-type: "auto"
      slither: "true"
      slither-output: "arkheionx-slither-summary.json"
```

If Slither is unavailable, Arkheionx continues unless `slither-strict: "true"`
is explicitly set. You can also pass an existing local Slither JSON file:

```yaml
with:
  slither-json: "slither-report.json"
```

## Delivery Artifact Workflow

v0.7.0 and later builds can generate client-ready delivery artifacts:

```yaml
with:
  launch-report-output: "ARKHEIONX_LAUNCH_REPORT.md"
  sprint-plan-output: "ARKHEIONX_SPRINT_PLAN.md"
  sprint-days: "5"
  contest-readiness-output: "ARKHEIONX_CONTEST_READINESS.md"
  executive-summary-output: "ARKHEIONX_EXECUTIVE_SUMMARY.md"
  remediation-roadmap-output: "ARKHEIONX_REMEDIATION_ROADMAP.md"
```

These files are readiness deliverables. They are not formal audit reports and
do not guarantee security.

## Local CLI Equivalent

```sh
python3 scripts/pre_audit_scan.py \
  --root . \
  --protocol-type auto \
  --output ARKHEIONX_PRE_AUDIT_REPORT.md \
  --json-output arkheionx-report.json \
  --sarif-output arkheionx.sarif.json \
  --baseline-output arkheionx.baseline.json \
  --summary-output ARKHEIONX_ACTION_SUMMARY.md \
  --comment-output ARKHEIONX_PR_COMMENT.md \
  --issue-checklist-output ARKHEIONX_ISSUE_CHECKLIST.md \
  --issue-plan-output ARKHEIONX_ISSUE_PLAN.json \
  --launch-report-output ARKHEIONX_LAUNCH_REPORT.md \
  --sprint-plan-output ARKHEIONX_SPRINT_PLAN.md \
  --sprint-days 5 \
  --contest-readiness-output ARKHEIONX_CONTEST_READINESS.md \
  --executive-summary-output ARKHEIONX_EXECUTIVE_SUMMARY.md \
  --remediation-roadmap-output ARKHEIONX_REMEDIATION_ROADMAP.md \
  --min-confidence-for-issue-plan medium
```

## Inputs

| Input | Default | Purpose |
|---|---|---|
| `root` | `.` | Repository path to scan. |
| `protocol-type` | `auto` | `auto`, `vault`, `amm`, `lending`, `staking`, `oracle`, or `generic`. |
| `output` | `ARKHEIONX_PRE_AUDIT_REPORT.md` | Markdown report path. |
| `json-output` | empty | Optional JSON report path. |
| `sarif-output` | empty | Optional SARIF report path. |
| `upload-sarif` | `false` | Documentation flag. Add `upload-sarif` as a separate workflow step. |
| `baseline-output` | empty | Optional compact baseline JSON output. |
| `compare-baseline` | empty | Optional baseline JSON path for diff mode. |
| `diff-output` | empty | Optional standalone Markdown diff report. |
| `diff-json-output` | empty | Optional standalone JSON diff report. |
| `summary` | `true` | Write generated summary to the GitHub Actions job summary. |
| `summary-output` | `ARKHEIONX_ACTION_SUMMARY.md` | Local summary Markdown path. |
| `pr-comment` | `false` | Generate and optionally post/update a PR comment. |
| `github-token` | empty | Token used only for optional PR comment and issue workflows. |
| `comment-output` | `ARKHEIONX_PR_COMMENT.md` | Local PR comment body path. |
| `comment-mode` | `update` | `update` existing marker comment or `append`. |
| `create-issue-checklist` | `true` | Generate a copyable Markdown issue checklist. |
| `issue-checklist-output` | `ARKHEIONX_ISSUE_CHECKLIST.md` | Checklist output path. |
| `issue-plan-output` | empty | Optional generated GitHub issue plan JSON path. |
| `create-github-issues` | `false` | Run the optional issue workflow. Defaults to no issue creation. |
| `issue-create-mode` | `dry-run` | `dry-run`, `create`, or `update`. |
| `issue-grouping` | `one-per-finding` | `one-per-finding` or `summary`. |
| `issue-max` | `5` | Maximum issues selected for create/update/dry-run. |
| `issue-only-priority` | `high` | `critical`, `high`, `medium`, `low`, `informational`, or `all`. |
| `issue-labels` | empty | Comma-separated extra labels. |
| `issue-assignees` | empty | Comma-separated assignees. |
| `issue-dry-run-output` | `ARKHEIONX_ISSUE_DRY_RUN.md` | Optional dry-run Markdown output. |
| `launch-report-output` | empty | Optional Launch Readiness Report Markdown output. |
| `sprint-plan-output` | empty | Optional Pre-Audit Sprint Plan Markdown output. |
| `sprint-days` | `5` | Sprint length: `3`, `5`, `7`, or `10`. |
| `contest-readiness-output` | empty | Optional Contest Readiness Report Markdown output. |
| `executive-summary-output` | empty | Optional one-page executive summary Markdown output. |
| `remediation-roadmap-output` | empty | Optional remediation roadmap Markdown output. |
| `semantic-lite` | `true` | Enable semantic-lite Solidity structure extraction. |
| `slither` | `false` | Enable optional local Slither integration if available. |
| `slither-json` | empty | Optional pre-generated Slither JSON file. |
| `slither-output` | empty | Optional normalized Arkheionx Slither summary output path. |
| `slither-timeout` | `60` | Slither timeout in seconds. |
| `slither-strict` | `false` | Fail if Slither is requested but unavailable or fails. |
| `min-confidence-for-issue-plan` | `low` | Minimum confidence included in generated issue plans. |
| `config` | `.arkheionx.json` | Optional config path. |
| `generate-invariant-skeletons` | `false` | Create safe Foundry invariant skeletons. |
| `fail-on-critical-readiness-gap` | `false` | Fail only when explicitly enabled. |
| `fail-on-new-high` | `false` | Fail when diff mode finds new high/critical readiness gaps. |
| `fail-score-below` | empty | Fail when score is below this threshold. |
| `fail-on-unsuppressed-high` | `false` | Fail on unsuppressed high/critical readiness gaps. |
| `create-issues` | `false` | Legacy scanner flag. Use `create-github-issues` for the opt-in issue workflow. |
| `verbose` | `false` | Print scanner details. |

## JSON Output

v0.7.0 and later JSON includes the v0.4/v0.5/v0.6 fields plus delivery
metadata when delivery outputs are requested:

- canonical `findings` with stable IDs;
- stable finding fingerprints;
- `fingerprint_version`;
- `analysis_quality`;
- `semantic_lite`;
- `slither`;
- `diff` data when `compare-baseline` is used;
- `suppressed_findings`;
- `summary` counts;
- `generated_outputs`;
- `delivery_outputs`;
- `delivery_summary`;
- legacy-compatible `readiness_gaps`;
- score, score band, score breakdown, signals, historical patterns, suggested
  invariants, and disclaimer.

## Troubleshooting

If the PR comment does not appear:

- confirm `pr-comment: "true"`;
- confirm `github-token: ${{ secrets.GITHUB_TOKEN }}`;
- confirm workflow permissions include `pull-requests: write` and
  `issues: write`;
- remember fork PRs may restrict token permissions.

If the report exists but is not committed:

- this action writes artifacts into the workflow workspace;
- upload them with `actions/upload-artifact` if you want to keep them after the
  job.

If the config is invalid:

- the scanner continues;
- the report includes `Configuration Warnings`;
- fix `.arkheionx.json` before relying on suppressions.

If no Solidity files are found:

- check the `root` input;
- confirm contracts are committed;
- confirm files are not only inside ignored build/cache folders.

## Security Notes

The default action path does not:

- call RPC endpoints;
- inspect deployed contracts;
- submit transactions;
- collect secrets;
- prove a repository is secure.

PR comment mode uses the GitHub API only when explicitly enabled and only to
write a comment on the pull request running the workflow.

GitHub issue creation uses the GitHub API only when `create-github-issues` is
enabled and `issue-create-mode` is set to `create` or `update`. Dry-run mode
makes no API calls.

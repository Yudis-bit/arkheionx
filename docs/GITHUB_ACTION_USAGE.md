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
      - uses: Yudis-bit/DeFi-Exploit-PoCs/.github/actions/pre-audit@v0.4.0
        with:
          protocol-type: auto
```

Until `v0.4.0` is tagged, use `@main` only if you intentionally want the
current development branch.

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
      - uses: Yudis-bit/DeFi-Exploit-PoCs/.github/actions/pre-audit@main
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
      - uses: Yudis-bit/DeFi-Exploit-PoCs/.github/actions/pre-audit@main
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
  - uses: Yudis-bit/DeFi-Exploit-PoCs/.github/actions/pre-audit@main
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
      - uses: Yudis-bit/DeFi-Exploit-PoCs/.github/actions/pre-audit@main
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
  --issue-checklist-output ARKHEIONX_ISSUE_CHECKLIST.md
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
| `github-token` | empty | Token used only for optional PR comment mode. |
| `comment-output` | `ARKHEIONX_PR_COMMENT.md` | Local PR comment body path. |
| `comment-mode` | `update` | `update` existing marker comment or `append`. |
| `create-issue-checklist` | `true` | Generate a copyable Markdown issue checklist. |
| `issue-checklist-output` | `ARKHEIONX_ISSUE_CHECKLIST.md` | Checklist output path. |
| `config` | `.arkheionx.json` | Optional config path. |
| `generate-invariant-skeletons` | `false` | Create safe Foundry invariant skeletons. |
| `fail-on-critical-readiness-gap` | `false` | Fail only when explicitly enabled. |
| `fail-on-new-high` | `false` | Fail when diff mode finds new high/critical readiness gaps. |
| `fail-score-below` | empty | Fail when score is below this threshold. |
| `fail-on-unsuppressed-high` | `false` | Fail on unsuppressed high/critical readiness gaps. |
| `create-issues` | `false` | Reserved. No remote issues are created. |
| `verbose` | `false` | Print scanner details. |

## JSON Output

v0.4.0 JSON includes:

- canonical `findings` with stable IDs;
- stable finding fingerprints;
- `fingerprint_version`;
- `diff` data when `compare-baseline` is used;
- `suppressed_findings`;
- `summary` counts;
- `generated_outputs`;
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
- create remote GitHub issues;
- prove a repository is secure.

PR comment mode uses the GitHub API only when explicitly enabled and only to
write a comment on the pull request running the workflow.

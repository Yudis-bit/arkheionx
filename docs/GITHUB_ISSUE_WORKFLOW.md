# GitHub Issue Workflow

Arkheionx v0.7.0 can convert readiness findings into a GitHub-native issue
plan. Optional issue creation is disabled by default and should be used only in
repositories you own or are authorized to manage.

Generated issues are remediation tasks. They are not formal audit findings and
do not confirm vulnerabilities. v0.6 issue plans include confidence reasons,
top evidence, detection sources, and affected functions when semantic-lite or
optional Slither evidence is available.

## Recommended Flow

1. Run the scanner and generate an issue plan.
2. Review the issue plan JSON and Markdown checklist.
3. Run `scripts/create_github_issues.py` in dry-run mode.
4. If the output is acceptable, opt in to `create` or `update` mode.
5. Re-run Arkheionx after remediation and compare against a baseline.

## Generate An Issue Plan

```sh
python3 scripts/pre_audit_scan.py \
  --root . \
  --protocol-type auto \
  --json-output arkheionx-report.json \
  --issue-plan-output ARKHEIONX_ISSUE_PLAN.json \
  --issue-checklist-output ARKHEIONX_ISSUE_CHECKLIST.md \
  --min-confidence-for-issue-plan medium
```

The default issue-plan threshold is conservative: low-confidence,
keyword-only findings remain in the report but are listed as excluded
low-confidence findings in the issue plan.

## Dry Run

```sh
python3 scripts/create_github_issues.py \
  --issue-plan ARKHEIONX_ISSUE_PLAN.json \
  --mode dry-run \
  --dry-run-output ARKHEIONX_ISSUE_DRY_RUN.md \
  --max-issues 5
```

Dry-run mode makes no GitHub API calls.

## Create Or Update Issues

Real issue creation requires explicit mode, a token, and `issues: write`
permissions.

```sh
python3 scripts/create_github_issues.py \
  --issue-plan ARKHEIONX_ISSUE_PLAN.json \
  --mode create \
  --repo OWNER/REPO \
  --github-token "$GITHUB_TOKEN" \
  --max-issues 5
```

Update mode updates matching Arkheionx issues when deterministic markers are
present:

```sh
python3 scripts/create_github_issues.py \
  --issue-plan ARKHEIONX_ISSUE_PLAN.json \
  --mode update \
  --repo OWNER/REPO \
  --github-token "$GITHUB_TOKEN"
```

## Duplicate Prevention

Each generated issue contains a hidden marker:

```html
<!-- arkheionx-issue:ARK-VLT-001 -->
```

The issue workflow searches open issues labeled `arkheionx` for this marker
before creating a new issue.

## GitHub Action Example

```yaml
permissions:
  contents: read
  issues: write

steps:
  - uses: actions/checkout@v4
  - uses: Yudis-bit/DeFi-Exploit-PoCs/.github/actions/pre-audit@v1.0.0
    with:
      protocol-type: auto
      issue-plan-output: ARKHEIONX_ISSUE_PLAN.json
      create-github-issues: "true"
      issue-create-mode: "dry-run"
      issue-max: "5"
      github-token: ${{ secrets.GITHUB_TOKEN }}
```

Use `dry-run` first. Switch to `create` or `update` only after reviewing the
generated plan.

## Launch Report And Pre-Audit Sprint Use

A Launch Report can review the issue plan and convert it into a prioritized
readiness plan. A Pre-Audit Sprint can help a team work through the generated
tasks, inspect evidence/confidence reasons, and compare progress with baseline
diff mode.

In v0.7 workflows, the same issue plan can feed a generated Launch Report,
Pre-Audit Sprint Plan, Contest Readiness Report, executive summary, and
remediation roadmap. These artifacts are planning aids for authorized
maintainers, not formal audit findings.

## Safety Boundaries

- issue creation is off by default,
- dry-run makes no API calls,
- token is required for create/update,
- max issue limits reduce noise,
- generated issues include disclaimers,
- no exploit steps or live-chain behavior are added.

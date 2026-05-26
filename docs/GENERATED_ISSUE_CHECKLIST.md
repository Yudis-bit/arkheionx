# Generated Issue Checklist

Arkheionx can generate a copyable Markdown checklist from readiness findings.
The checklist can also reference a structured issue plan used by the optional
GitHub issue workflow.

Default output:

```text
ARKHEIONX_ISSUE_CHECKLIST.md
```

## What It Contains

- Score and protocol type.
- High, medium, and low priority readiness gaps.
- Stable finding IDs such as `ARK-VLT-001`.
- Suggested defensive tests.
- Confidence and evidence context through linked issue-plan output.
- Documentation tasks.
- Suggested issue titles and labels when an issue plan is generated.
- A reminder that the checklist is not a formal audit.

When baseline diff mode is enabled, the checklist puts new findings first,
then existing unchanged findings, with resolved findings shown as informational
completed items.

## How Teams Use It

Indie teams can paste the checklist into a GitHub Issue, project board, launch
tracking issue, or internal remediation plan. This is useful before formal
audit intake because it turns scanner output into concrete engineering tasks.

## Convert This Checklist Into GitHub Issues

Generate an issue plan:

```sh
python3 scripts/pre_audit_scan.py \
  --root . \
  --protocol-type auto \
  --issue-plan-output ARKHEIONX_ISSUE_PLAN.json \
  --issue-checklist-output ARKHEIONX_ISSUE_CHECKLIST.md
```

Dry run:

```sh
python3 scripts/create_github_issues.py \
  --issue-plan ARKHEIONX_ISSUE_PLAN.json \
  --mode dry-run
```

Create issues only after reviewing the plan:

```sh
python3 scripts/create_github_issues.py \
  --issue-plan ARKHEIONX_ISSUE_PLAN.json \
  --mode create \
  --max-issues 5
```

Only run issue creation in repositories you own or are authorized to manage.

## Why Arkheionx Does Not Create Issues By Default

Automatic issue creation can be noisy and may expose private planning context.
Arkheionx generates the checklist and issue plan first. Real issue creation is
explicitly opt-in, token-based, capped by `--max-issues`, and marker-based to
avoid duplicates.

## Paid Service Bridge

For Launch Reports and Pre-Audit Sprints, the generated checklist and issue plan
can become the first draft of a prioritized remediation plan. Manual review can
review confidence reasons, remove false positives, clarify priority, add
context, and align the work with a formal audit scope.

## Limitations

The checklist is generated from local/static readiness signals. It does not
prove safety, confirm exploitability, or replace a formal audit.

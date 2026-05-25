# Generated Issue Checklist

Arkheionx v0.3.0 can generate a copyable Markdown checklist from readiness
findings.

Default output:

```text
ARKHEIONX_ISSUE_CHECKLIST.md
```

## What It Contains

- Score and protocol type.
- High, medium, and low priority readiness gaps.
- Stable finding IDs such as `ARK-VLT-001`.
- Suggested defensive tests.
- Documentation tasks.
- A reminder that the checklist is not a formal audit.

When baseline diff mode is enabled, the checklist puts new findings first,
then existing unchanged findings, with resolved findings shown as informational
completed items.

## How Teams Use It

Indie teams can paste the checklist into a GitHub Issue, project board, launch
tracking issue, or internal remediation plan. This is useful before formal
audit intake because it turns scanner output into concrete engineering tasks.

## Why Arkheionx Does Not Create Issues By Default

Automatic issue creation can be noisy and may expose private planning context.
For v0.3.0, Arkheionx generates the checklist file and leaves issue creation to
the repository maintainers.

## Paid Service Bridge

For Launch Reports and Pre-Audit Sprints, the generated checklist can become
the first draft of a prioritized remediation plan. Manual review can remove
false positives, clarify severity, add context, and align the checklist with a
formal audit scope.

## Limitations

The checklist is generated from local/static readiness signals. It does not
prove safety, confirm exploitability, or replace a formal audit.

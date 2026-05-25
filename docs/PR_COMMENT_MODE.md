# PR Comment Mode

Arkheionx v0.3.0 can generate a concise pull request comment with the readiness
score, protocol type, top readiness gaps, report path, and generated issue
checklist path.

PR comment mode is off by default.

## What It Does

- Generates `ARKHEIONX_PR_COMMENT.md`.
- Adds the marker `<!-- arkheionx-pre-audit-comment -->`.
- Optionally posts the body to the current pull request.
- Updates the existing Arkheionx marker comment in `update` mode.
- Includes baseline diff counts when `compare-baseline` is provided.

## Required Workflow Permissions

```yaml
permissions:
  contents: read
  pull-requests: write
  issues: write
```

Use:

```yaml
with:
  pr-comment: "true"
  github-token: ${{ secrets.GITHUB_TOKEN }}
  comment-mode: "update"
```

## Why Update Mode Exists

Update mode avoids comment spam. The posting script lists pull request issue
comments, finds the Arkheionx marker, and patches that comment when possible.
If no marker comment exists, it creates one.

## Fork Pull Request Behavior

GitHub may restrict token permissions for forked pull requests. In that case
the scanner still generates reports and local comment bodies, but the API
posting step may be skipped or fail gracefully.

## Safety Boundaries

PR comment mode does not call chains, inspect deployed contracts, submit
transactions, or send code to third-party services. It only uses the GitHub API
for the repository pull request when explicitly enabled.

## Limitations

- Comment posting depends on token permissions.
- The comment is a summary, not the full report.
- Diff counts are readiness-diff signals, not proof that a finding is fixed.
- The output is a readiness signal, not a formal audit or security guarantee.

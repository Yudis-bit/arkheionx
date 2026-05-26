# Try Arkheionx In 5 Minutes

This guide runs Arkheionx against the built-in oracle/staking demo fixture and
generates the same GitHub-native artifacts a builder would inspect before a
formal audit.

The demo is local and static. It does not call RPC, inspect deployed
contracts, submit transactions, or create GitHub issues.

## Prerequisites

- Python 3.11 or newer.
- A local clone of this repository.
- No API key, private key, RPC URL, or GitHub token.

## Run The Demo Scan

```sh
python3 scripts/pre_audit_scan.py \
  --root examples/oracle-staking-fixture \
  --protocol-type auto \
  --output examples/reports/demo-pre-audit-report.md \
  --json-output examples/reports/demo-report.json \
  --sarif-output examples/reports/demo.sarif.json \
  --baseline-output examples/reports/demo.baseline.json \
  --issue-plan-output examples/reports/demo-issue-plan.json \
  --issue-checklist-output examples/reports/demo-issue-checklist.md \
  --launch-report-output examples/reports/demo-launch-report.md \
  --sprint-plan-output examples/reports/demo-sprint-plan.md \
  --sprint-days 5 \
  --contest-readiness-output examples/reports/demo-contest-readiness.md \
  --executive-summary-output examples/reports/demo-executive-summary.md \
  --remediation-roadmap-output examples/reports/demo-remediation-roadmap.md
```

## Optional Dry-Run Issue Workflow

```sh
python3 scripts/create_github_issues.py \
  --issue-plan examples/reports/demo-issue-plan.json \
  --mode dry-run \
  --dry-run-output examples/reports/demo-issue-dry-run.md
```

Dry-run mode makes no GitHub API calls.

## Search The Security Memory Graph

```sh
python3 scripts/search_knowledge.py "oracle stale price"
python3 scripts/search_knowledge.py "missing invariant" --json
```

These commands show related finding IDs, historical pattern categories,
suggested defensive tests, and local docs for the demo findings. They do not
confirm vulnerabilities.

## Expected Output Files

| Output | Purpose |
|---|---|
| `demo-pre-audit-report.md` | Technical readiness report. |
| `demo-report.json` | Machine-readable score, findings, evidence, and outputs. |
| `demo.sarif.json` | Code Scanning-compatible readiness output. |
| `demo.baseline.json` | Baseline snapshot for future comparison. |
| `demo-issue-plan.json` | Structured remediation issue plan. |
| `demo-issue-checklist.md` | Copyable Markdown checklist. |
| `demo-launch-report.md` | Client-facing launch readiness report. |
| `demo-sprint-plan.md` | Five-day Pre-Audit Sprint plan. |
| `demo-contest-readiness.md` | Scope and researcher onboarding readiness report. |
| `demo-executive-summary.md` | Short founder/stakeholder summary. |
| `demo-remediation-roadmap.md` | Phase-based remediation plan. |
| `demo-issue-dry-run.md` | Dry-run summary of issues that would be created. |

## How To Read The Results

Start with:

1. `demo-executive-summary.md` for the short stakeholder view.
2. `demo-pre-audit-report.md` for technical findings and evidence.
3. `demo-issue-plan.json` for owner-ready remediation tasks.
4. `demo-launch-report.md` for a client-facing readiness artifact.
5. `demo-contest-readiness.md` for scope and reviewer onboarding gaps.

## Common Errors

- `python3: command not found`: install Python 3 or use the Python binary name
  available on your system.
- `No Solidity files found`: confirm the `--root` path points at a repository
  or fixture with `.sol` files.
- `Invalid sprint-days`: use `3`, `5`, `7`, or `10`.
- `GitHub token missing`: expected unless you intentionally use real issue
  creation. The demo uses dry-run mode.

## What To Do Next

- Run the same command against a repository you own or are authorized to
  review.
- Compare the original demo fixture with
  `examples/oracle-staking-fixture-fixed`.
- Read the demo case studies in `docs/case-studies/`.
- Report noisy findings through the false-positive calibration template.

Arkheionx output is not a formal audit and not a security guarantee. It helps
teams prepare for review.

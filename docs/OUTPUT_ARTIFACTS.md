# Output Artifacts

Arkheionx supports custom output paths, but v1.0.0 recommends the names below
for stable CI and local workflows.

| Artifact | Recommended Name |
|---|---|
| Pre-Audit Report | `ARKHEIONX_PRE_AUDIT_REPORT.md` |
| JSON Report | `arkheionx-report.json` |
| SARIF | `arkheionx.sarif.json` |
| Baseline | `arkheionx.baseline.json` |
| Diff Markdown | `ARKHEIONX_DIFF.md` |
| Diff JSON | `arkheionx-diff.json` |
| Issue Plan | `ARKHEIONX_ISSUE_PLAN.json` |
| Issue Checklist | `ARKHEIONX_ISSUE_CHECKLIST.md` |
| Issue Dry Run | `ARKHEIONX_ISSUE_DRY_RUN.md` |
| Launch Report | `ARKHEIONX_LAUNCH_REPORT.md` |
| Sprint Plan | `ARKHEIONX_SPRINT_PLAN.md` |
| Contest Readiness | `ARKHEIONX_CONTEST_READINESS.md` |
| Executive Summary | `ARKHEIONX_EXECUTIVE_SUMMARY.md` |
| Remediation Roadmap | `ARKHEIONX_REMEDIATION_ROADMAP.md` |
| Action Summary | `ARKHEIONX_ACTION_SUMMARY.md` |
| PR Comment Body | `ARKHEIONX_PR_COMMENT.md` |

## Reports Directory

It is safe to write outputs into a repository-local `reports/` directory:

```sh
python3 scripts/pre_audit_scan.py \
  --root . \
  --protocol-type auto \
  --output reports/ARKHEIONX_PRE_AUDIT_REPORT.md \
  --json-output reports/arkheionx-report.json \
  --sarif-output reports/arkheionx.sarif.json \
  --baseline-output reports/arkheionx.baseline.json
```

Arkheionx ignores its own generated reports, SARIF, baselines, issue plans,
dry-run outputs, and delivery artifacts by default on future scans. This
prevents previous outputs from influencing score, evidence, findings, negative
evidence, protocol detection, or issue plans.

## Custom Paths

Custom output paths are supported. Use names that make generated status obvious
and keep scanner outputs separate from protocol source files when possible.

Generated artifacts are local/static outputs. They are not formal audit reports
and do not confirm vulnerabilities.

## Protocol-Pack Examples

v1.4.0 adds AMM and lending fixture outputs that use the same artifact shapes:

- `examples/reports/amm-fixture-pre-audit-report.md`
- `examples/reports/amm-fixture-pre-audit-report.json`
- `examples/reports/amm-fixture.sarif.json`
- `examples/reports/amm-fixture-issue-plan.json`
- `examples/reports/lending-fixture-pre-audit-report.md`
- `examples/reports/lending-fixture-pre-audit-report.json`
- `examples/reports/lending-fixture.sarif.json`
- `examples/reports/lending-fixture-issue-plan.json`

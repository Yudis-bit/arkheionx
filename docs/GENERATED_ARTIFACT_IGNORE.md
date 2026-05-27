# Generated Artifact Ignore

Arkheionx ignores its own generated artifacts by default during repository
scans. This prevents previous scan outputs from becoming source evidence in a
later scan.

## Why This Exists

Generated reports contain finding titles, recommendations, checklist items,
and negative phrases such as "without role-boundary tests." If those files are
scanned as protocol evidence, they can pollute signals, findings, and
`negative_evidence`.

v0.9.2 adds a self-ingestion guard so generated artifacts remain outputs, not
inputs.

## Ignored By Default

Arkheionx ignores generated-looking files such as:

- `ARKHEIONX_PRE_AUDIT_REPORT.md`
- `ARKHEIONX_PR_COMMENT.md`
- `ARKHEIONX_ISSUE_CHECKLIST.md`
- `ARKHEIONX_ISSUE_PLAN.json`
- `arkheionx-report.json`
- `arkheionx.sarif.json`
- `reports/*-pre-audit-report.md`
- `reports/*-pre-audit-report.json`
- `reports/*.sarif.json`
- `reports/*.baseline.json`
- `reports/*-issue-plan.json`
- `reports/*-issue-checklist.md`
- `reports/*-launch-report.md`
- `reports/*-contest-readiness.md`
- `reports/*-executive-summary.md`
- `reports/*-remediation-roadmap.md`
- `reports/*-sprint-plan.md`

Files with clear generated headings, such as `# Arkheionx Pre-Audit Readiness
Report`, are also ignored even if the filename is custom.

## Scan Source Accounting

Markdown and JSON reports include `scan_sources` so users can see:

- files considered;
- files scanned;
- files ignored;
- generated Arkheionx artifacts ignored;
- ignored generated artifact paths.

v1.5.0 extends the default ignore set to generated test plans and Foundry
invariant skeleton outputs, so starter scaffolds do not become source evidence
in later scans.

## Config

Default behavior:

```json
{
  "scan": {
    "ignore_generated_artifacts": true,
    "include_generated_artifacts": false
  }
}
```

For debugging only, users can include generated artifacts:

```json
{
  "scan": {
    "include_generated_artifacts": true
  }
}
```

This is advanced behavior. Normal scans should leave generated artifacts
ignored so previous outputs do not influence future readiness scores.

## Safety Boundary

This feature is local/static. It does not add RPC, live-chain calls, deployed
contract scanning, exploit automation, or external services.

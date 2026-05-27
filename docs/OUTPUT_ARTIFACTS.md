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
| Test Plan | `ARKHEIONX_TEST_PLAN.md` |
| Test Plan JSON | `ARKHEIONX_TEST_PLAN.json` |
| Foundry Invariant Skeleton | `ArkheionxReadinessInvariants.t.sol` |
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
dry-run outputs, delivery artifacts, test plans, and invariant skeletons by
default on future scans. This prevents previous outputs from influencing score,
evidence, findings, negative evidence, protocol detection, or issue plans.

v1.8.0 scanner reports include Fix First, grouped finding summaries, compact
suppression summaries, and config summaries in Markdown and JSON. Config
summary fields include config source, effective protocol type, enabled rule
packs, minimum confidence, suppression count, output profile, and generated
artifact handling.

See [`OUTPUT_PROFILES.md`](OUTPUT_PROFILES.md), [`FIX_FIRST.md`](FIX_FIRST.md),
and [`REPORT_UX.md`](REPORT_UX.md).

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

## Test Plan Examples

v1.5.0 adds defensive test-plan artifacts generated from report JSON:

- `examples/reports/amm-fixture-test-plan.md`
- `examples/reports/amm-fixture-test-plan.json`
- `examples/reports/ArkheionxAMMInvariants.t.sol`
- `examples/reports/lending-fixture-test-plan.md`
- `examples/reports/lending-fixture-test-plan.json`
- `examples/reports/ArkheionxLendingInvariants.t.sol`
- `examples/reports/amm-lending-hybrid-fixture-test-plan.md`
- `examples/reports/amm-lending-hybrid-fixture-test-plan.json`
- `examples/reports/ArkheionxHybridInvariants.t.sol`

These skeletons are starter scaffolds with TODO placeholders. They are not
formal verification and require project-specific review.

## Internal Engine Split

v1.6.0 does not add new public output artifact shapes. It adds the internal
`arkheionx/` package scaffold and begins moving generator internals behind the
same script entrypoints and output paths.

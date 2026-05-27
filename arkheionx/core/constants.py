"""Shared constants for the Arkheionx internal engine split."""
from __future__ import annotations

PROTOCOL_TYPES = ("auto", "vault", "amm", "lending", "staking", "oracle", "generic")

DEFAULT_CONFIG = ".arkheionx.json"
COMMENT_MARKER = "<!-- arkheionx-pre-audit-comment -->"
ISSUE_MARKER_PREFIX = "<!-- arkheionx-issue:"

DEFAULT_GENERATED_ARTIFACT_IGNORE_PATTERNS = [
    "reports/ARKHEIONX_*.md",
    "reports/ARKHEIONX_*.json",
    "reports/arkheionx-*.json",
    "reports/*.sarif.json",
    "reports/*.baseline.json",
    "reports/*-baseline.json",
    "reports/*-diff*.md",
    "reports/*-diff*.json",
    "reports/*-issue-plan.json",
    "reports/*-issue-checklist.md",
    "reports/*-issue-dry-run.md",
    "reports/*-pre-audit-report.md",
    "reports/*-pre-audit-report.json",
    "reports/*-launch-report.md",
    "reports/*-contest-readiness.md",
    "reports/*-executive-summary.md",
    "reports/*-remediation-roadmap.md",
    "reports/*-sprint-plan.md",
    "reports/*-test-plan.md",
    "reports/*-test-plan.json",
    "reports/Arkheionx*Invariants.t.sol",
    "reports/*action-summary.md",
    "reports/*pr-comment.md",
    "ARKHEIONX_PRE_AUDIT_REPORT.md",
    "ARKHEIONX_ACTION_SUMMARY.md",
    "ARKHEIONX_PR_COMMENT.md",
    "ARKHEIONX_ISSUE_CHECKLIST.md",
    "ARKHEIONX_ISSUE_PLAN.json",
    "ARKHEIONX_ISSUE_DRY_RUN.md",
    "ARKHEIONX_LAUNCH_REPORT.md",
    "ARKHEIONX_CONTEST_READINESS.md",
    "ARKHEIONX_EXECUTIVE_SUMMARY.md",
    "ARKHEIONX_REMEDIATION_ROADMAP.md",
    "ARKHEIONX_SPRINT_PLAN.md",
    "ARKHEIONX_TEST_PLAN.md",
    "ARKHEIONX_TEST_PLAN.json",
    "Arkheionx*Invariants.t.sol",
    "arkheionx-report.json",
    "arkheionx.sarif.json",
    "arkheionx.baseline.json",
    "arkheionx-diff.json",
    "ARKHEIONX_DIFF.md",
]

ARKHEIONX_GENERATED_CONTENT_MARKERS = [
    "# Arkheionx Pre-Audit Readiness Report",
    "# Arkheionx Launch Readiness Report",
    "# Arkheionx Contest Readiness Report",
    "# Arkheionx Pre-Audit Sprint Plan",
    "# Arkheionx Executive Summary",
    "# Arkheionx Remediation Roadmap",
    "# Arkheionx Defensive Test Plan",
    "# Arkheionx Generated Issue Checklist",
    "# Arkheionx Baseline Diff Report",
    "<!-- arkheionx-pre-audit-comment -->",
    "<!-- arkheionx-issue:",
    "Arkheionx-generated defensive invariant skeleton",
    "arkheionx_generated",
    "\"scanner\": \"arkheionx\"",
    "\"generated_by\": \"arkheionx\"",
    "\"tool\": \"Arkheionx Pre-Audit Scanner\"",
]

"""Canonical generated artifact names used across Arkheionx docs and scripts."""
from __future__ import annotations

from arkheionx.core.models import OutputArtifact
from arkheionx.core.paths import PACKAGE_ROOT


OUTPUT_ARTIFACTS = [
    OutputArtifact("Pre-Audit Report", PACKAGE_ROOT / "ARKHEIONX_PRE_AUDIT_REPORT.md", "Markdown readiness report"),
    OutputArtifact("JSON Report", PACKAGE_ROOT / "arkheionx-report.json", "Machine-readable readiness report"),
    OutputArtifact("SARIF", PACKAGE_ROOT / "arkheionx.sarif.json", "SARIF 2.1.0 readiness output"),
    OutputArtifact("Issue Plan", PACKAGE_ROOT / "ARKHEIONX_ISSUE_PLAN.json", "GitHub-native remediation plan"),
    OutputArtifact("Test Plan", PACKAGE_ROOT / "ARKHEIONX_TEST_PLAN.md", "Defensive test-plan starter artifact"),
]

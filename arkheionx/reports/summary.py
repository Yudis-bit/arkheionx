"""Summary helpers for Arkheionx report outputs."""
from __future__ import annotations

from typing import Any

from arkheionx.reports.ux import finding_summary_tables, fix_first_items, summarize_suppressions


def report_ux_summary(
    findings: list[Any],
    suppressed_findings: list[Any],
    suppressions_loaded: int,
    fix_first_limit: int = 5,
) -> dict[str, object]:
    """Build backward-compatible report UX summary metadata."""

    summary = finding_summary_tables(findings, suppressed_findings)
    summary["fix_first"] = fix_first_items(findings, fix_first_limit)
    summary["suppression_summary"] = summarize_suppressions(suppressions_loaded, suppressed_findings)
    return summary

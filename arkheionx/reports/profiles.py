"""Report output profile settings for Arkheionx readiness reports."""
from __future__ import annotations

from copy import deepcopy


REPORT_PROFILES: dict[str, dict[str, object]] = {
    "concise": {
        "label": "Concise",
        "summary_limit": 3,
        "fix_first_limit": 5,
        "top_gap_limit": 5,
        "evidence_limit": 1,
        "negative_evidence_limit": 3,
        "suggested_test_limit": 3,
        "related_knowledge_limit": 2,
        "all_findings_limit": 5,
        "include_analysis_quality": False,
        "include_signal_summary": False,
        "include_historical_patterns": False,
        "include_rule_pack_details": False,
        "include_all_finding_details": True,
        "include_generated_outputs": True,
        "include_scan_sources": True,
    },
    "standard": {
        "label": "Standard",
        "summary_limit": 5,
        "fix_first_limit": 5,
        "top_gap_limit": 5,
        "evidence_limit": 3,
        "negative_evidence_limit": 5,
        "suggested_test_limit": 5,
        "related_knowledge_limit": 3,
        "all_findings_limit": 12,
        "include_analysis_quality": True,
        "include_signal_summary": True,
        "include_historical_patterns": True,
        "include_rule_pack_details": True,
        "include_all_finding_details": True,
        "include_generated_outputs": True,
        "include_scan_sources": True,
    },
    "full": {
        "label": "Full",
        "summary_limit": 8,
        "fix_first_limit": 8,
        "top_gap_limit": 10,
        "evidence_limit": 10,
        "negative_evidence_limit": 10,
        "suggested_test_limit": 8,
        "related_knowledge_limit": 6,
        "all_findings_limit": 0,
        "include_analysis_quality": True,
        "include_signal_summary": True,
        "include_historical_patterns": True,
        "include_rule_pack_details": True,
        "include_all_finding_details": True,
        "include_generated_outputs": True,
        "include_scan_sources": True,
    },
    "ci": {
        "label": "CI",
        "summary_limit": 3,
        "fix_first_limit": 5,
        "top_gap_limit": 5,
        "evidence_limit": 1,
        "negative_evidence_limit": 3,
        "suggested_test_limit": 3,
        "related_knowledge_limit": 2,
        "all_findings_limit": 0,
        "include_analysis_quality": False,
        "include_signal_summary": False,
        "include_historical_patterns": False,
        "include_rule_pack_details": False,
        "include_all_finding_details": False,
        "include_generated_outputs": True,
        "include_scan_sources": True,
    },
}


def profile_settings(profile: str | None) -> dict[str, object]:
    """Return safe report settings for a known profile.

    Unknown profile names fall back to ``standard`` to keep config handling
    predictable and backward-compatible.
    """

    key = (profile or "standard").strip().lower()
    if key not in REPORT_PROFILES:
        key = "standard"
    settings = deepcopy(REPORT_PROFILES[key])
    settings["key"] = key
    return settings


def profile_keys() -> tuple[str, ...]:
    """Return stable output profile keys."""

    return tuple(REPORT_PROFILES.keys())

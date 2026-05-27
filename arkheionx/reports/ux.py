"""Small report UX helpers shared by Arkheionx scripts and tests."""
from __future__ import annotations

from collections import Counter
from typing import Any

from arkheionx.rules.registry import finding_id_to_rule_pack


def _text(value: object) -> str:
    return str(value or "")


def _get(finding: Any, name: str, default: Any = "") -> Any:
    if isinstance(finding, dict):
        return finding.get(name, default)
    return getattr(finding, name, default)


def priority_rank(finding: Any) -> int:
    text = f"{_get(finding, 'priority')} {_get(finding, 'severity')}".lower()
    if "critical" in text:
        return 0
    if "high" in text:
        return 1
    if "medium" in text:
        return 2
    if "low" in text:
        return 3
    return 4


def confidence_rank(finding: Any) -> int:
    confidence = _text(_get(finding, "confidence", "medium")).lower()
    return {"high": 0, "medium": 1, "low": 2}.get(confidence, 3)


def rule_family_for_finding(finding: Any) -> str:
    finding_id = _text(_get(finding, "id") or _get(finding, "finding_id"))
    family = finding_id_to_rule_pack(finding_id)
    if family != "generic":
        return family
    category = _text(_get(finding, "category", "generic")).lower()
    if "oracle" in category:
        return "oracle"
    if "vault" in category:
        return "vault"
    if "amm" in category:
        return "amm"
    if "lend" in category or "liquidation" in category:
        return "lending"
    if "reentrancy" in category:
        return "reentrancy-value-flow"
    if "reward" in category or "staking" in category:
        return "rewards"
    if "access" in category or "upgrade" in category:
        return "access-control"
    if "doc" in category:
        return "docs"
    if "test" in category:
        return "testing"
    return "generic"


def fix_first_reason(finding: Any) -> str:
    reasons: list[str] = []
    if priority_rank(finding) <= 1:
        reasons.append("higher-priority readiness blocker")
    if confidence_rank(finding) == 0:
        reasons.append("high-confidence local evidence")
    evidence = _get(finding, "evidence", []) or []
    affected_files = _get(finding, "affected_files", []) or []
    suggested_tests = _get(finding, "suggested_tests", []) or []
    if len(affected_files) > 1:
        reasons.append("appears across multiple files")
    if suggested_tests:
        reasons.append("clear defensive tests are available")
    if not reasons and evidence:
        reasons.append("local evidence is available for manual review")
    if not reasons:
        reasons.append("manual review can reduce report noise")
    return "; ".join(reasons) + "."


def recommended_next_action(finding: Any) -> str:
    tests = _get(finding, "suggested_tests", []) or []
    recommendation = _text(_get(finding, "recommendation", ""))
    if tests:
        return f"Add or review: {tests[0]}"
    if recommendation:
        return recommendation
    return "Review the finding, document the assumption, and add a targeted defensive test."


def _fix_first_sort_key(finding: Any) -> tuple[int, int, int, int, str]:
    evidence = _get(finding, "evidence", []) or []
    affected_files = _get(finding, "affected_files", []) or []
    negative_evidence = _get(finding, "negative_evidence", []) or []
    signal_strength = -min(5, len(evidence) + len(affected_files) + len(negative_evidence))
    return (
        priority_rank(finding),
        confidence_rank(finding),
        signal_strength,
        0 if _get(finding, "suggested_tests", []) else 1,
        _text(_get(finding, "id") or _get(finding, "finding_id")),
    )


def rank_fix_first(findings: list[Any], limit: int = 5) -> list[Any]:
    """Rank active findings into a compact fix-first ordering."""

    return sorted(findings, key=_fix_first_sort_key)[: max(0, limit)]


def fix_first_items(findings: list[Any], limit: int = 5) -> list[dict[str, object]]:
    items: list[dict[str, object]] = []
    for rank, finding in enumerate(rank_fix_first(findings, limit), 1):
        suggested_tests = list(_get(finding, "suggested_tests", []) or [])
        items.append(
            {
                "rank": rank,
                "id": _text(_get(finding, "id") or _get(finding, "finding_id")),
                "title": _text(_get(finding, "title")),
                "rule_family": rule_family_for_finding(finding),
                "priority": _text(_get(finding, "priority")),
                "confidence": _text(_get(finding, "confidence")),
                "why_fix_first": fix_first_reason(finding),
                "recommended_next_action": recommended_next_action(finding),
                "suggested_test": suggested_tests[0] if suggested_tests else "",
            }
        )
    return items


def group_findings_by_rule_family(findings: list[Any]) -> dict[str, int]:
    return dict(sorted(Counter(rule_family_for_finding(item) for item in findings).items()))


def group_findings_by_confidence(findings: list[Any]) -> dict[str, int]:
    return dict(sorted(Counter(_text(_get(item, "confidence", "unknown")).lower() for item in findings).items()))


def summarize_suppressions(loaded_count: int, suppressed_findings: list[Any]) -> dict[str, object]:
    return {
        "suppressions_loaded": loaded_count,
        "suppressions_applied": len(suppressed_findings),
        "suppressed_finding_ids": [_text(_get(item, "id") or _get(item, "finding_id")) for item in suppressed_findings],
        "requires_review": bool(loaded_count or suppressed_findings),
    }


def finding_summary_tables(findings: list[Any], suppressed_findings: list[Any]) -> dict[str, object]:
    return {
        "active_findings_count": len(findings),
        "suppressed_findings_count": len(suppressed_findings),
        "findings_by_rule_family": group_findings_by_rule_family(findings),
        "findings_by_confidence": group_findings_by_confidence(findings),
    }

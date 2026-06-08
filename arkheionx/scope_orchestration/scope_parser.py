"""Parse a markdown contest/audit/program scope note into structured rules.

Heuristic and local/static: the parser reads a markdown file, splits it into
heading-delimited sections, and routes each section's bullet/line items into the
matching :class:`~arkheionx.scope_orchestration.models.ScopeData` field by keyword.
It never executes anything and never leaves the local file. A missing scope file
yields a generic, clearly-labelled empty scope so task generation is never blocked.
"""
from __future__ import annotations

import re
from pathlib import Path

from . import models as m

# Ordered (most specific first) mapping of heading keywords -> ScopeData field.
_HEADING_ROUTES: tuple[tuple[tuple[str, ...], str], ...] = (
    (("out of scope", "out-of-scope", "not in scope", "excluded"), "out_of_scope"),
    (("scope summary", "overview", "summary", "about the", "introduction"), "summary"),
    (("in scope", "in-scope", "contracts in scope", "scoped contracts"), "in_scope"),
    (("severity", "valid impact", "impact requirement", "qualifying impact", "what qualifies"), "severity_conditions"),
    (("trusted role", "trusted actor", "privileged role", "trusted parties", "roles"), "trusted_roles"),
    (("trusted integration", "trusted external", "trusted protocol", "trusted dependenc"), "trusted_integrations"),
    (("known issue", "known bug", "known limitation"), "known_issues"),
    (("accepted risk", "acknowledged risk", "acceptable risk"), "accepted_risks"),
    (("prior audit", "previous audit", "past audit", "audit history"), "prior_audit_notes"),
    (("changed since", "changes since", "new since", "diff since", "recently changed"), "changed_since_audit"),
    (("design choice", "design decision", "intended behavior", "intended behaviour", "by design"), "design_choices"),
    (("invariant",), "invariants"),
    (("off-chain", "offchain", "off chain"), "off_chain_assumptions"),
    (("admin assumption", "admin", "owner assumption", "governance"), "admin_assumptions"),
    (("external dependency", "dependency assumption", "external assumption", "third-party"), "external_dependency_assumptions"),
    (("gas", "array", "unbounded", "loop bound"), "array_gas_limits"),
    (("eip", "erc", "standard", "interface"), "eip_expectations"),
    (("compliance", "sanction", "blocklist", "blacklist", "freeze", "kyc", "denylist"), "compliance_expectations"),
    (("focus", "recommended", "areas of concern", "please review", "attention", "priority area"), "focus_areas"),
    (("invalid", "will not be accepted", "not valid", "won't be valid", "out-of-scope finding"), "invalid_patterns"),
    (("low only", "low-only", "informational", "qa report", "gas optimization", "non-issue"), "low_only_patterns"),
    (("report", "submission requirement", "poc required", "what to submit", "qualif"), "report_candidate_requirements"),
)

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
_BULLET_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+(.*)$")


def _route(heading: str) -> str | None:
    low = heading.lower()
    for keywords, field in _HEADING_ROUTES:
        if any(k in low for k in keywords):
            return field
    return None


def _clean_item(text: str) -> str:
    text = text.strip()
    text = re.sub(r"[*_`]+", "", text)          # strip md emphasis/code marks
    text = re.sub(r"\s+", " ", text).strip()
    return text


def empty_scope() -> m.ScopeData:
    return m.ScopeData(scope_file_used=False)


def parse_scope_text(text: str) -> m.ScopeData:
    """Parse raw markdown scope text into a :class:`ScopeData`."""
    scope = m.ScopeData(scope_file_used=True)
    lines = text.splitlines()

    current_field: str | None = None
    summary_lines: list[str] = []
    preamble: list[str] = []
    saw_heading = False

    def add(field: str, item: str) -> None:
        item = _clean_item(item)
        if not item:
            return
        if field == "summary":
            summary_lines.append(item)
            return
        bucket = getattr(scope, field)
        if item not in bucket:
            bucket.append(item)

    for raw in lines:
        head = _HEADING_RE.match(raw)
        if head:
            saw_heading = True
            current_field = _route(head.group(2))
            continue
        stripped = raw.strip()
        if not stripped:
            continue
        bullet = _BULLET_RE.match(raw)
        content = bullet.group(1) if bullet else stripped
        if current_field is None:
            # Text before the first routed heading is treated as summary preamble.
            if not saw_heading:
                preamble.append(_clean_item(content))
            continue
        add(current_field, content)

    if summary_lines:
        scope.summary = " ".join(summary_lines[:6]).strip()
    elif preamble:
        scope.summary = " ".join(p for p in preamble[:4] if p).strip()
    return scope


def parse_scope_file(path: Path | str | None) -> m.ScopeData:
    """Load and parse a markdown scope file. Missing/unreadable -> empty scope."""
    if not path:
        return empty_scope()
    p = Path(path).expanduser()
    if not p.is_file():
        return empty_scope()
    try:
        text = p.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return empty_scope()
    scope = parse_scope_text(text)
    scope.scope_file_path = str(p)
    return scope


def requires_medium_high(scope: m.ScopeData) -> bool:
    """Whether the scope restricts valid findings to Medium/High impact."""
    blob = " ".join(scope.severity_conditions + scope.report_candidate_requirements).lower()
    if not blob:
        return False
    mentions_mh = "medium" in blob or "high" in blob or "critical" in blob
    excludes_low = "low" in blob or "qualif" in blob or "valid" in blob or "only" in blob
    return mentions_mh and excludes_low

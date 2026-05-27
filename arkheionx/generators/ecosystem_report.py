"""Generate synthetic/local Arkheionx ecosystem readiness reports."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from arkheionx.core.files import load_json
from arkheionx.core.paths import PACKAGE_ROOT


ROOT = PACKAGE_ROOT
DEFAULT_INPUT = ROOT / "metadata" / "ecosystem_pilot_example.json"
SUMMARY_OUTPUT = ROOT / "reports" / "ecosystem_readiness_summary.md"
GAPS_OUTPUT = ROOT / "reports" / "ecosystem_common_gaps.md"


def load_payload(path: Path) -> dict[str, Any]:
    return load_json(path)


def render_disclaimer(payload: dict[str, Any]) -> list[str]:
    return [
        "## Important Notice",
        "",
        "This is a synthetic/internal ecosystem readiness example unless an",
        "operator has explicit public permission for a real summary.",
        "",
        "Arkheionx ecosystem reports are readiness planning artifacts, not formal",
        "audits, certifications, endorsements, security guarantees, or",
        "vulnerability confirmations.",
        "",
        "Do not include private code, secrets, or unpatched vulnerability details",
        "in public summaries. Use authorized repositories only.",
        "",
    ]


def score_distribution(entries: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for entry in entries:
        band = str(entry.get("score_band", "Unknown"))
        counts[band] = counts.get(band, 0) + 1
    return counts


def render_summary(payload: dict[str, Any]) -> str:
    entries = payload.get("repo_entries", [])
    lines: list[str] = [
        "# Arkheionx Ecosystem Readiness Summary",
        "",
    ]
    lines.extend(render_disclaimer(payload))
    lines.extend(
        [
            "## Ecosystem Overview",
            "",
            f"- Ecosystem: {payload.get('ecosystem_name_public', 'Unnamed ecosystem')}",
            f"- Ecosystem ID: `{payload.get('ecosystem_id', '')}`",
            f"- Arkheionx version: {payload.get('arkheionx_version', '')}",
            f"- Repository count: {payload.get('repo_count', len(entries))}",
            f"- Aggregate score band: {payload.get('aggregate_score_band', 'Unknown')}",
            f"- Anonymization: {payload.get('anonymization_level', 'unspecified')}",
            f"- Disclosure status: {payload.get('disclosure_status', 'unspecified')}",
            "",
            "## Repo-By-Repo Readiness Table",
            "",
            "| Repo alias | Protocol type | Score | Score band | Top findings | Public summary |",
            "|---|---|---:|---|---|---|",
        ]
    )
    for entry in entries:
        top = ", ".join(entry.get("top_findings", [])) or "-"
        public = "yes" if entry.get("public_summary_allowed") else "no"
        lines.append(
            "| {alias} | {protocol} | {score} | {band} | {top} | {public} |".format(
                alias=entry.get("repo_alias", ""),
                protocol=entry.get("protocol_type", ""),
                score=entry.get("score", ""),
                band=entry.get("score_band", ""),
                top=top,
                public=public,
            )
        )
    lines.extend(["", "## Readiness Distribution", ""])
    for band, count in sorted(score_distribution(entries).items()):
        lines.append(f"- {band}: {count}")
    lines.extend(["", "## Rule-Family Heatmap", ""])
    for family, count in sorted(payload.get("rule_family_counts", {}).items()):
        lines.append(f"- {family}: {count}")
    lines.extend(["", "## Recommended Ecosystem Actions", ""])
    for action in payload.get("recommended_actions", []):
        lines.append(f"- {action}")
    lines.extend(["", "## Safety Notes", ""])
    for note in payload.get("safety_notes", []):
        lines.append(f"- {note}")
    lines.append("")
    return "\n".join(lines)


def render_common_gaps(payload: dict[str, Any]) -> str:
    lines: list[str] = [
        "# Arkheionx Ecosystem Common Gaps",
        "",
    ]
    lines.extend(render_disclaimer(payload))
    lines.extend(["## Common Gap Families", ""])
    for family in payload.get("common_gap_families", []):
        lines.append(f"- {family}")
    lines.extend(["", "## Recurring Findings", ""])
    lines.append("| Finding ID | Count | Theme |")
    lines.append("|---|---:|---|")
    for finding in payload.get("recurring_findings", []):
        lines.append(
            "| `{id}` | {count} | {theme} |".format(
                id=finding.get("finding_id", ""),
                count=finding.get("count", ""),
                theme=finding.get("theme", ""),
            )
        )
    lines.extend(["", "## Remediation Themes", ""])
    themes = [
        "Standardize invariant and fuzz-test expectations before audit intake.",
        "Document oracle freshness, bounds, decimals, and failure assumptions.",
        "Require admin/role-boundary negative tests for privileged flows.",
        "Ask each participating repo to attach an Arkheionx issue plan.",
        "Use anonymized cohort summaries unless explicit public permission exists.",
    ]
    for theme in themes:
        lines.append(f"- {theme}")
    lines.extend(["", "## Disclosure Boundaries", ""])
    lines.extend(
        [
            "- Do not publish private code snippets.",
            "- Do not disclose unpatched vulnerability details publicly.",
            "- Do not name repositories without permission.",
            "- Do not describe readiness findings as confirmed vulnerabilities.",
            "",
        ]
    )
    return "\n".join(lines)


def write_reports(input_path: Path) -> None:
    payload = load_payload(input_path)
    SUMMARY_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_OUTPUT.write_text(render_summary(payload), encoding="utf-8")
    GAPS_OUTPUT.write_text(render_common_gaps(payload), encoding="utf-8")


def check_reports(input_path: Path) -> list[str]:
    payload = load_payload(input_path)
    expected = {
        SUMMARY_OUTPUT: render_summary(payload),
        GAPS_OUTPUT: render_common_gaps(payload),
    }
    failures: list[str] = []
    for path, content in expected.items():
        if not path.exists():
            failures.append(f"missing: {path.relative_to(ROOT)}")
        elif path.read_text(encoding="utf-8") != content:
            failures.append(f"stale: {path.relative_to(ROOT)}")
    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate Arkheionx ecosystem readiness reports.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Local ecosystem pilot JSON input.")
    parser.add_argument("--check", action="store_true", help="Exit nonzero if generated reports are stale.")
    args = parser.parse_args(argv)
    input_path = Path(args.input)
    if not input_path.is_absolute():
        input_path = ROOT / input_path
    if args.check:
        failures = check_reports(input_path)
        if failures:
            for failure in failures:
                print(failure)
            return 1
        print("ok: ecosystem reports up to date")
        return 0
    write_reports(input_path)
    print(f"updated: {SUMMARY_OUTPUT.relative_to(ROOT)}")
    print(f"updated: {GAPS_OUTPUT.relative_to(ROOT)}")
    return 0

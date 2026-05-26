#!/usr/bin/env python3
"""Generate Arkheionx feedback and calibration dashboards."""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
BACKLOG_PATH = ROOT / "metadata" / "rule_calibration_backlog.json"
FEEDBACK_PATH = ROOT / "metadata" / "feedback_examples.json"
MATRIX_PATH = ROOT / "metadata" / "rule_calibration_matrix.json"
FEEDBACK_OUTPUT = ROOT / "reports" / "feedback_dashboard.md"
BACKLOG_OUTPUT = ROOT / "reports" / "rule_calibration_backlog.md"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def markdown_table(headers: list[str], rows: list[list[str]]) -> list[str]:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(cell.replace("\n", " ") for cell in row) + " |")
    return lines


def render_feedback_dashboard() -> str:
    feedback = load_json(FEEDBACK_PATH)
    backlog = load_json(BACKLOG_PATH)
    matrix = load_json(MATRIX_PATH)
    examples = feedback.get("examples", [])
    entries = backlog.get("entries", [])

    by_source = defaultdict(list)
    for item in examples:
        by_source[item.get("source_type", "unknown")].append(item)

    status_counts = Counter(item.get("status", "unknown") for item in examples)
    backlog_counts = Counter(item.get("status", "unknown") for item in entries)

    lines: list[str] = [
        "# Arkheionx Feedback Dashboard",
        "",
        "This dashboard is generated from local metadata. Current entries are",
        "synthetic/internal unless a public source and permission are explicitly",
        "recorded.",
        "",
        "Arkheionx does not claim customers, adoption, production use, or broad",
        "external validation from synthetic examples.",
        "",
        "## Feedback Summary",
        "",
    ]
    lines.extend(
        markdown_table(
            ["Metric", "Value"],
            [
                ["Feedback examples", str(len(examples))],
                ["Calibration backlog entries", str(len(entries))],
                ["Rule calibration families", str(len(matrix.get("families", {})))],
                ["Public external feedback with permission", str(len(by_source.get("public_issue", [])))],
                ["Synthetic/internal examples", str(len(by_source.get("synthetic_internal", [])))],
            ],
        )
    )
    lines.extend(["", "## Feedback By Status", ""])
    lines.extend(markdown_table(["Status", "Count"], [[key, str(value)] for key, value in sorted(status_counts.items())]))
    lines.extend(["", "## Backlog By Status", ""])
    lines.extend(markdown_table(["Status", "Count"], [[key, str(value)] for key, value in sorted(backlog_counts.items())]))

    lines.extend(["", "## Synthetic/Internal Feedback", ""])
    synthetic_rows = []
    for item in by_source.get("synthetic_internal", []):
        synthetic_rows.append(
            [
                item.get("feedback_id", ""),
                item.get("type", ""),
                ", ".join(item.get("finding_ids", [])) or "-",
                item.get("status", ""),
                item.get("feedback_summary", ""),
            ]
        )
    lines.extend(markdown_table(["ID", "Type", "Findings", "Status", "Summary"], synthetic_rows or [["-", "-", "-", "-", "None"]]))

    lines.extend(["", "## External Feedback With Public Permission", ""])
    public_rows = []
    for source in ("public_issue", "public_demo"):
        for item in by_source.get(source, []):
            if item.get("public_permission") in {"anonymized", "public_source_allowed"}:
                public_rows.append(
                    [
                        item.get("feedback_id", ""),
                        source,
                        item.get("repo_type", ""),
                        item.get("public_permission", ""),
                        item.get("feedback_summary", ""),
                    ]
                )
    lines.extend(markdown_table(["ID", "Source", "Repo Type", "Permission", "Summary"], public_rows or [["-", "-", "-", "-", "None recorded"]]))

    lines.extend(["", "## External Feedback Without Public Permission", ""])
    private_rows = []
    for item in examples:
        if item.get("public_permission") in {"none", "No", "no"}:
            private_rows.append([item.get("feedback_id", ""), item.get("repo_type", ""), item.get("status", ""), "Private/anonymized only"])
    lines.extend(markdown_table(["ID", "Repo Type", "Status", "Notes"], private_rows or [["-", "-", "-", "None recorded"]]))

    lines.extend(
        [
            "",
            "## Calibration Backlog",
            "",
            "See [`rule_calibration_backlog.md`](rule_calibration_backlog.md).",
            "",
            "## Safety Notes",
            "",
            "- Do not store secrets, private keys, mnemonics, or RPC credentials.",
            "- Do not publish unpatched vulnerability details.",
            "- Do not describe synthetic/internal examples as external adoption.",
            "- Use public validation claims only when permission and evidence are committed.",
            "",
        ]
    )
    return "\n".join(lines)


def render_backlog() -> str:
    backlog = load_json(BACKLOG_PATH)
    entries = backlog.get("entries", [])
    lines: list[str] = [
        "# Arkheionx Rule Calibration Backlog",
        "",
        "Generated from `metadata/rule_calibration_backlog.json`.",
        "",
        "Initial entries are synthetic/internal and exist to track calibration",
        "work without claiming customers, adoption, or production validation.",
        "",
    ]
    rows = []
    for item in entries:
        rows.append(
            [
                item.get("id", ""),
                item.get("priority", ""),
                item.get("status", ""),
                item.get("rule_family", ""),
                item.get("title", ""),
                item.get("target_release", ""),
            ]
        )
    lines.extend(markdown_table(["ID", "Priority", "Status", "Rule Family", "Title", "Target"], rows))
    lines.extend(["", "## Details", ""])
    for item in entries:
        lines.extend(
            [
                f"### {item.get('id', '')} - {item.get('title', '')}",
                "",
                f"- Rule family: `{item.get('rule_family', '')}`",
                f"- Source: `{item.get('source', '')}`",
                f"- Status: `{item.get('status', '')}`",
                f"- Priority: `{item.get('priority', '')}`",
                f"- Target release: `{item.get('target_release', '')}`",
                f"- Problem: {item.get('problem', '')}",
                f"- Proposed action: {item.get('proposed_action', '')}",
                f"- Safety notes: {item.get('safety_notes', '')}",
                f"- Linked tests: {', '.join(item.get('linked_tests', [])) or '-'}",
                "",
            ]
        )
    return "\n".join(lines)


def write_outputs() -> None:
    FEEDBACK_OUTPUT.write_text(render_feedback_dashboard(), encoding="utf-8")
    BACKLOG_OUTPUT.write_text(render_backlog(), encoding="utf-8")
    print(f"updated: {FEEDBACK_OUTPUT.relative_to(ROOT)}")
    print(f"updated: {BACKLOG_OUTPUT.relative_to(ROOT)}")


def check_outputs() -> int:
    expected = {
        FEEDBACK_OUTPUT: render_feedback_dashboard(),
        BACKLOG_OUTPUT: render_backlog(),
    }
    stale = [path for path, content in expected.items() if not path.exists() or path.read_text(encoding="utf-8") != content]
    if stale:
        for path in stale:
            print(f"would update: {path.relative_to(ROOT)}")
        return 1
    print("ok: feedback dashboard up to date")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate Arkheionx feedback dashboards.")
    parser.add_argument("--check", action="store_true", help="Exit nonzero if generated dashboards are stale.")
    args = parser.parse_args(argv)
    if args.check:
        return check_outputs()
    write_outputs()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

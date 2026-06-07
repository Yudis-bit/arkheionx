"""Generate defensive Arkheionx test plans from readiness report JSON."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

from arkheionx.core.files import load_json, write_json, write_text
from arkheionx.core.paths import PACKAGE_ROOT, display_path
from arkheionx.version import SCANNER_VERSION, SCHEMA_VERSION


VERSION = SCANNER_VERSION
ROOT = PACKAGE_ROOT
MAP_PATH = ROOT / "metadata" / "finding_test_plan_map.json"

CHECK_TARGETS = [
    (
        ROOT / "examples/reports/amm-fixture-pre-audit-report.json",
        ROOT / "examples/reports/amm-fixture-test-plan.md",
        ROOT / "examples/reports/amm-fixture-test-plan.json",
        ROOT / "examples/reports/ArkheionxAMMInvariants.t.sol",
    ),
    (
        ROOT / "examples/reports/lending-fixture-pre-audit-report.json",
        ROOT / "examples/reports/lending-fixture-test-plan.md",
        ROOT / "examples/reports/lending-fixture-test-plan.json",
        ROOT / "examples/reports/ArkheionxLendingInvariants.t.sol",
    ),
    (
        ROOT / "examples/reports/amm-lending-hybrid-fixture-pre-audit-report.json",
        ROOT / "examples/reports/amm-lending-hybrid-fixture-test-plan.md",
        ROOT / "examples/reports/amm-lending-hybrid-fixture-test-plan.json",
        ROOT / "examples/reports/ArkheionxHybridInvariants.t.sol",
    ),
]

SAFETY_NOTES = [
    "Generated plans are starter scaffolds for authorized local repositories; human review required.",
    "They are not a formal audit, not formal verification, and not proof of safety.",
    "Replace TODO placeholders with project-specific contracts, handlers, and assertions.",
    "Use local mocks or test deployments only; do not wire production credentials or deployed systems.",
]


def clean_evidence_summary(summary: str) -> str:
    """Drop a leading location-less ": <reason>" colon so the rendered evidence
    reference reads cleanly even for older source reports."""
    return str(summary or "").strip().lstrip(":").strip()


def load_plan_map() -> dict[str, dict]:
    payload = load_json(MAP_PATH)
    entries = payload.get("findings", {})
    if not isinstance(entries, dict):
        return {}
    return {str(key): value for key, value in entries.items() if isinstance(value, dict)}


def dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for item in items:
        normalized = re.sub(r"\s+", " ", str(item).strip().lower())
        if normalized and normalized not in seen:
            seen.add(normalized)
            output.append(str(item).strip())
    return output


# Soft qualifier words that do not change the meaning of a defensive test idea.
# Collapsing them lets near-duplicate phrasings (e.g. "within fee and rounding
# bounds" vs "within expected fee and rounding bounds") fold into one line.
_SOFT_FILLER = frozenset({"the", "a", "an", "expected"})

# Rule-family overview caps: a concise digest, not the full per-finding set.
RULE_FAMILY_TEST_CAP = 6
RULE_FAMILY_INVARIANT_CAP = 5


def _semantic_signature(text: str) -> str:
    words = re.sub(r"[^a-z0-9\s]", " ", str(text).lower()).split()
    return " ".join(word for word in words if word not in _SOFT_FILLER)


def dedupe_semantic(items: list[str]) -> list[str]:
    """Deterministic near-duplicate dedup for suggested tests / invariant
    candidates: collapses lines that differ only by punctuation, casing, or soft
    qualifier words, keeping the first occurrence so ordering stays stable."""
    seen: set[str] = set()
    output: list[str] = []
    for item in items:
        signature = _semantic_signature(item)
        if signature and signature not in seen:
            seen.add(signature)
            output.append(str(item).strip())
    return output


# Invariant candidates should read as properties (declarative statements about
# what must always hold), not as suggested-test instructions. Sentences that open
# with an imperative testing verb are suggested tests, so they are filtered out of
# the invariant-candidate lists to avoid restating a test as a property.
INSTRUCTION_LEADING_VERBS = frozenset(
    {
        "assert",
        "test",
        "document",
        "add",
        "use",
        "simulate",
        "move",
        "reject",
        "check",
        "review",
        "pair",
        "cover",
        "run",
        "wire",
        "replace",
        "build",
    }
)


def looks_like_instruction(text: str) -> bool:
    first = re.split(r"[\s:]", str(text).strip(), maxsplit=1)[0].lower()
    return first in INSTRUCTION_LEADING_VERBS


def property_candidates(items: list[str]) -> list[str]:
    """Keep only declarative invariant properties, dropping suggested-test style
    instructions. If every candidate reads like an instruction, keep the original
    list so a finding is never left without any candidate."""
    properties = [item for item in items if not looks_like_instruction(item)]
    return properties if properties else items


def class_name_from_path(path: Path | None, protocol_type: str) -> str:
    if path:
        name = path.name
        if name.endswith(".t.sol"):
            name = name[: -len(".t.sol")]
        elif name.endswith(".sol"):
            name = name[: -len(".sol")]
        cleaned = re.sub(r"[^A-Za-z0-9_]", "", name)
        if cleaned and cleaned[0].isalpha():
            return cleaned
    suffix = re.sub(r"[^A-Za-z0-9]", "", protocol_type.title()) or "Readiness"
    return f"Arkheionx{suffix}Invariants"


def normalize_function_name(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_]", "", name.strip())
    if not cleaned:
        return "invariant_projectSpecificProperty"
    if not cleaned.startswith("invariant_"):
        cleaned = "invariant_" + cleaned
    return cleaned


def finding_priority_rank(finding: dict) -> int:
    text = f"{finding.get('priority', '')} {finding.get('severity', '')}".lower()
    if "critical" in text:
        return 0
    if "high" in text:
        return 1
    if "medium" in text:
        return 2
    if "low" in text:
        return 3
    return 4


def collect_plan(report: dict, plan_map: dict[str, dict], foundry_output: Path | None) -> dict:
    findings = [item for item in report.get("findings", []) if isinstance(item, dict)]
    planned_findings: list[dict] = []
    all_tests: list[str] = []
    all_invariants: list[str] = []
    skeleton_functions: list[str] = []
    required_bindings: list[str] = []
    families: dict[str, dict] = {}

    for finding in sorted(findings, key=finding_priority_rank):
        finding_id = str(finding.get("id", ""))
        mapping = plan_map.get(finding_id, {})
        suggested_tests = dedupe_semantic(
            [str(item) for item in mapping.get("suggested_tests", [])]
            + [str(item) for item in finding.get("suggested_tests", [])]
        )
        invariant_candidates = property_candidates(
            dedupe_semantic(
                [str(item) for item in mapping.get("invariant_candidates", [])]
                + [str(item) for item in finding.get("invariant_candidates", [])]
            )
        )
        functions = dedupe([str(item) for item in mapping.get("foundry_skeleton_functions", [])])
        bindings = dedupe([str(item) for item in mapping.get("required_project_bindings", [])])
        family = str(mapping.get("rule_family") or finding.get("category") or "generic")
        entry = {
            "finding_id": finding_id,
            "title": str(mapping.get("title") or finding.get("title", "")),
            "rule_family": family,
            "priority": str(finding.get("priority", "")),
            "confidence": str(finding.get("confidence", "")),
            "suggested_tests": suggested_tests,
            "invariant_candidates": invariant_candidates,
            "foundry_skeleton_functions": functions,
            "required_project_bindings": bindings,
            "safety_notes": mapping.get("safety_notes", []),
            "manual_review_notes": mapping.get("manual_review_notes", []),
            "source_report_evidence_summary": clean_evidence_summary(finding.get("evidence_summary", "")),
            "matched_signals": [str(s) for s in finding.get("detected_signals", []) if str(s).strip()][:6],
        }
        planned_findings.append(entry)
        all_tests.extend(suggested_tests)
        all_invariants.extend(invariant_candidates)
        skeleton_functions.extend(functions)
        required_bindings.extend(bindings)
        families.setdefault(
            family,
            {
                "rule_family": family,
                "finding_ids": [],
                "suggested_tests": [],
                "invariant_candidates": [],
            },
        )
        families[family]["finding_ids"].append(finding_id)
        families[family]["suggested_tests"].extend(suggested_tests)
        families[family]["invariant_candidates"].extend(invariant_candidates)

    # Rule-family overview is a curated digest, not a dump: dedup near-duplicates
    # and cap the lists. Per-finding detail below keeps the full set.
    for family in families.values():
        family["finding_ids"] = dedupe(family["finding_ids"])
        family["suggested_tests"] = dedupe_semantic(family["suggested_tests"])[:RULE_FAMILY_TEST_CAP]
        family["invariant_candidates"] = dedupe_semantic(family["invariant_candidates"])[:RULE_FAMILY_INVARIANT_CAP]

    protocol_type = str(report.get("protocol_type", "auto"))
    return {
        "tool": "Arkheionx Test Plan Generator",
        "version": VERSION,
        "schema_version": SCHEMA_VERSION,
        "source_report": str(report.get("repo_root", "")),
        "source_report_version": str(report.get("version", "")),
        "source_report_score": report.get("score"),
        "source_report_score_band": report.get("score_band", ""),
        "protocol_type": protocol_type,
        # Keep generated test-plan JSON deterministic across CI runs.
        # Source scanner reports may be regenerated with fresh timestamps during
        # workflow execution; inheriting that timestamp makes committed fixture
        # test-plan JSON appear stale even when the review content is unchanged.
        "generated_at": "1970-01-01T00:00:00+00:00",
        "rule_families": sorted(families.values(), key=lambda item: item["rule_family"]),
        "findings": planned_findings,
        "suggested_tests": dedupe_semantic(all_tests),
        "invariant_candidates": dedupe_semantic(all_invariants),
        "foundry_skeleton": {
            "path": display_path(foundry_output, ROOT),
            "contract_name": class_name_from_path(foundry_output, protocol_type),
            "functions": dedupe([normalize_function_name(item) for item in skeleton_functions]),
            "required_project_bindings": dedupe(required_bindings),
        },
        "safety_notes": SAFETY_NOTES,
        "manual_review_required": True,
        "disclaimer": "This is a defensive test-planning artifact, not a formal audit or formal verification.",
    }


def render_markdown(plan: dict) -> str:
    lines = [
        "# Arkheionx Defensive Test Plan",
        "",
        "This generated plan turns Arkheionx readiness findings into defensive local test ideas.",
        "",
        "## Important Notice",
        "",
    ]
    for note in plan["safety_notes"]:
        lines.append(f"- {note}")
    lines.extend(
        [
            "",
            "## Source Summary",
            "",
            f"- Source report root: `{plan.get('source_report', '')}`",
            f"- Source report version: `{plan.get('source_report_version', '')}`",
            f"- Protocol type: `{plan.get('protocol_type', '')}`",
            f"- Readiness score: `{plan.get('source_report_score')}`",
            f"- Score band: `{plan.get('source_report_score_band', '')}`",
            f"- Mapped findings: `{len(plan.get('findings', []))}`",
            "",
            "## Rule-Family Plan",
            "",
        ]
    )
    for family in plan.get("rule_families", []):
        lines.append(f"### {family['rule_family']}")
        lines.append("")
        lines.append(f"- Findings: `{', '.join(family.get('finding_ids', []))}`")
        lines.append("- Suggested tests:")
        for test in family.get("suggested_tests", [])[:10]:
            lines.append(f"  - {test}")
        if family.get("invariant_candidates"):
            lines.append("- Invariant candidates:")
            for candidate in family.get("invariant_candidates", [])[:8]:
                lines.append(f"  - {candidate}")
        lines.append("")
    lines.extend(["## Finding Details", ""])
    for finding in plan.get("findings", []):
        lines.append(f"### {finding['finding_id']} - {finding['title']}")
        lines.append("")
        lines.append(f"- Rule family: `{finding['rule_family']}`")
        lines.append(f"- Priority: `{finding['priority']}`")
        lines.append(f"- Confidence: `{finding['confidence']}`")
        if finding.get("source_report_evidence_summary"):
            lines.append(f"- Source evidence summary: {finding['source_report_evidence_summary']}")
        if finding.get("matched_signals"):
            lines.append(f"- Matched signals: {', '.join(finding['matched_signals'])}")
        lines.append("- Suggested tests:")
        for test in finding.get("suggested_tests", [])[:8]:
            lines.append(f"  - {test}")
        if finding.get("invariant_candidates"):
            lines.append("- Invariant candidates:")
            for candidate in finding.get("invariant_candidates", [])[:6]:
                lines.append(f"  - {candidate}")
        if finding.get("required_project_bindings"):
            lines.append("- Project bindings to fill in:")
            for binding in finding.get("required_project_bindings", [])[:6]:
                lines.append(f"  - {binding}")
        if finding.get("manual_review_notes"):
            lines.append("- Manual review notes:")
            for note in finding.get("manual_review_notes", [])[:4]:
                lines.append(f"  - {note}")
        lines.append("")
    skeleton = plan.get("foundry_skeleton", {})
    lines.extend(
        [
            "## Foundry Skeleton",
            "",
            f"- Suggested output: `{skeleton.get('path', '') or 'not requested'}`",
            f"- Contract name: `{skeleton.get('contract_name', '')}`",
            "- Skeleton functions:",
        ]
    )
    for function in skeleton.get("functions", [])[:30]:
        lines.append(f"  - `{function}`")
    lines.extend(
        [
            "",
            "## What To Do Next",
            "",
            "1. Wire TODO bindings to local project contracts and mocks.",
            "2. Replace placeholder assertions with project-specific properties.",
            "3. Run the project test suite locally.",
            "4. Re-run Arkheionx and compare the readiness report or baseline.",
            "",
            "## Limitations",
            "",
            "- This plan is generated from heuristic readiness findings.",
            "- Manual review is required before relying on any generated property.",
            "- A formal smart contract audit remains recommended before handling real user funds.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_foundry_skeleton(plan: dict, foundry_output: Path | None) -> str:
    skeleton = plan.get("foundry_skeleton", {})
    contract_name = class_name_from_path(foundry_output, str(plan.get("protocol_type", "readiness")))
    functions = dedupe([normalize_function_name(item) for item in skeleton.get("functions", [])])
    if not functions:
        functions = [
            "invariant_projectSpecificAccountingHolds",
            "invariant_projectSpecificAccessBoundariesHold",
        ]
    bindings = dedupe([str(item) for item in skeleton.get("required_project_bindings", [])])
    lines = [
        "// SPDX-License-Identifier: MIT",
        "pragma solidity ^0.8.20;",
        "",
        "/// @notice Arkheionx-generated defensive invariant skeleton.",
        "/// @dev Starter scaffold for authorized local repositories. Human review required.",
        "///      Replace TODO bindings with project-specific contracts, handlers, and assertions.",
        f"contract {contract_name} {{",
        "    // TODO: bind target contracts and local mocks.",
        "    // TODO: add handlers for allowed user actions.",
        "    // TODO: replace placeholder assertions with project-specific properties.",
    ]
    if bindings:
        lines.append("    // Suggested project bindings to review:")
        for binding in bindings[:12]:
            safe_binding = binding.replace("*/", "").replace("/*", "")
            lines.append(f"    // TODO: {safe_binding}.")
    lines.append("")
    for function in functions:
        lines.append(f"    function {function}() public {{")
        lines.append("        // TODO: implement a defensive property for the mapped readiness finding.")
        lines.append("    }")
        lines.append("")
    lines.append("}")
    return "\n".join(lines).rstrip() + "\n"


def generate(report_path: Path, output: Path | None, json_output: Path | None, foundry_output: Path | None) -> dict:
    report = load_json(report_path)
    plan = collect_plan(report, load_plan_map(), foundry_output)
    if output:
        write_text(output, render_markdown(plan))
    if json_output:
        write_json(json_output, plan)
    if foundry_output:
        write_text(foundry_output, render_foundry_skeleton(plan, foundry_output))
    return plan


def check_outputs() -> list[str]:
    failures: list[str] = []
    for report_path, md_path, json_path, sol_path in CHECK_TARGETS:
        if not report_path.exists():
            failures.append(f"missing source report: {report_path.relative_to(ROOT)}")
            continue
        report = load_json(report_path)
        plan = collect_plan(report, load_plan_map(), sol_path)
        expected = {
            md_path: render_markdown(plan),
            json_path: json.dumps(plan, indent=2, sort_keys=True) + "\n",
            sol_path: render_foundry_skeleton(plan, sol_path),
        }
        for path, text in expected.items():
            if not path.exists():
                failures.append(f"missing generated output: {path.relative_to(ROOT)}")
                continue
            actual = path.read_text(encoding="utf-8")
            if actual != text:
                failures.append(f"stale generated output: {path.relative_to(ROOT)}")
    return failures


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate defensive Arkheionx test plans from report JSON.")
    parser.add_argument("--report", default="", help="Arkheionx report JSON input path.")
    parser.add_argument("--output", default="", help="Markdown test plan output path.")
    parser.add_argument("--json-output", default="", help="Optional JSON test plan output path.")
    parser.add_argument("--foundry-output", default="", help="Optional Foundry invariant skeleton output path.")
    parser.add_argument("--check", action="store_true", help="Fail if committed fixture test plans are stale.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if args.check:
        failures = check_outputs()
        if failures:
            print("Test plan generation check failed:")
            for failure in failures:
                print(f"- {failure}")
            return 1
        print("ok: test plans up to date")
        return 0
    if not args.report:
        print("--report is required unless --check is used", file=sys.stderr)
        return 2
    report = Path(args.report)
    output = Path(args.output) if args.output else None
    json_output = Path(args.json_output) if args.json_output else None
    foundry_output = Path(args.foundry_output) if args.foundry_output else None
    if not any([output, json_output, foundry_output]):
        print("At least one output path is required.", file=sys.stderr)
        return 2
    generate(report, output, json_output, foundry_output)
    if output:
        print(f"Arkheionx test plan generated: {output}")
    if json_output:
        print(f"Arkheionx JSON test plan generated: {json_output}")
    if foundry_output:
        print(f"Arkheionx Foundry invariant skeleton generated: {foundry_output}")
    return 0

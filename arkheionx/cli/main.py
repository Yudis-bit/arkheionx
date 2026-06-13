"""Arkheionx local/static CLI command surface.

v2.0.1 keeps this parser available through the installed `arkheionx` console
command and the `python3 -m arkheionx.cli.main` module path. Existing scripts
remain supported and first-class.
"""
from __future__ import annotations

import argparse
import sys

from arkheionx.cli import commands, exit_codes, workbench
from arkheionx.core.safety import LOCAL_ONLY_DISCLAIMER


PROTOCOL_TYPES = [
    "auto",
    "generic",
    "vault",
    "oracle",
    "access-control",
    "rewards",
    "staking",
    "amm",
    "lending",
    "hybrid",
]


# First-run guidance shown at the end of `arkheionx --help`. Lists only existing
# commands and reuses the shared safety boundary verbatim (single source of truth).
FIRST_RUN_EPILOG = (
    "First run:\n"
    "  arkheionx version             Show package and release milestone metadata.\n"
    "  arkheionx doctor              Check local environment, Foundry, and project layout.\n"
    "  arkheionx review-map .        Map value paths, assumptions, and missing tests (start here).\n"
    "\n"
    "Try the bundled multi-contract demo:\n"
    "  arkheionx review-map examples/vault-strategy-oracle-fixture\n"
    "\n"
    "Go deeper:\n"
    "  arkheionx open .              Orient inside an authorized local repository.\n"
    "  arkheionx doctor --install    Check install health, PATH, and source state.\n"
    "\n"
    "Run 'arkheionx <command> --help' for command-specific options.\n"
    "\n"
    "Safety: " + LOCAL_ONLY_DISCLAIMER + "\n"
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="arkheionx",
        description="Arkheionx local/static DeFi value-flow workbench CLI.",
        epilog=FIRST_RUN_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command")

    version = subparsers.add_parser("version", help="Print package and release milestone metadata.")
    version.set_defaults(func=commands.version_command)

    doctor = subparsers.add_parser("doctor", help="Diagnose Arkheionx install, Foundry, and project layout.")
    doctor.add_argument("repo", nargs="?", default=".", help="Project root to diagnose (default: current dir).")
    doctor.add_argument("--install", action="store_true", help="Focus on install health: command path, Python, package import, PATH hint.")
    doctor.set_defaults(func=workbench.doctor_command)

    review = subparsers.add_parser(
        "review",
        help="One-command local review pack (start here): run context, scope map, value-flow map, interaction map, assumptions, review lanes, evidence tasks (with kill conditions), evidence rubric, report filter, agent input, review.json, and manifest.json. Add --lens for protocol-aware artifacts. Planning artifact, not a finding; human review required.",
    )
    review.add_argument("repo", nargs="?", default=".", help="Authorized local repository root.")
    review.add_argument("--scope-file", default="", help="Path to a markdown scope note (optional).")
    review.add_argument("--lens", default="", help="Optional protocol lens id (e.g. fixed-credit-market). Omit for a generic review.")
    review.add_argument("--out", default="", help="Artifact output directory (default: <repo>/.arkheionx/review/).")
    review.add_argument("--json", action="store_true", help="Print machine-readable manifest JSON to stdout only (no human text).")
    review.add_argument("--no-write", action="store_true", help="Build the pack in memory only; do not write artifact files.")
    review.set_defaults(func=workbench.review_command)

    scan = subparsers.add_parser("scan", help="Run a local Arkheionx value-flow/readiness scan.")
    scan.add_argument("root", help="Authorized local repository root to scan.")
    scan.add_argument("--protocol-type", default="auto", choices=PROTOCOL_TYPES, help="Protocol type hint.")
    scan.add_argument("--config", default="", help="Optional Arkheionx JSON config path.")
    scan.add_argument("--output", default="", help="Markdown report output path.")
    scan.add_argument("--json-output", default="", help="Optional JSON report output path.")
    scan.add_argument("--sarif-output", default="", help="Optional SARIF v2.1.0 output path.")
    scan.add_argument("--issue-plan-output", default="", help="Optional generated GitHub issue plan JSON path.")
    scan.add_argument("--summary-output", default="", help="Optional GitHub Actions summary Markdown path.")
    scan.add_argument("--comment-output", default="", help="Optional pull request comment Markdown path.")
    scan.add_argument("--baseline-output", default="", help="Optional compact baseline JSON output path.")
    scan.add_argument("--compare-baseline", default="", help="Optional previous Arkheionx baseline JSON path.")
    scan.add_argument("--diff-output", default="", help="Optional standalone Markdown diff report path.")
    scan.add_argument("--diff-json-output", default="", help="Optional standalone JSON diff output path.")
    scan.add_argument("--fail-under-score", type=int, default=None, help="Exit nonzero if readiness score is below this threshold.")
    scan.add_argument("--min-confidence", default="", choices=["", "low", "medium", "high"], help="Minimum confidence for issue-plan entries.")
    scan.add_argument("--output-profile", default="", choices=["", "concise", "standard", "full", "ci"], help="Temporary report output profile override.")
    scan.add_argument("--generate-invariant-skeletons", action="store_true", help="Generate safe local Foundry invariant skeletons.")
    scan.set_defaults(func=commands.scan_command)

    validate_config = subparsers.add_parser("validate-config", help="Validate a local Arkheionx JSON config.")
    validate_config.add_argument("--config", default=".arkheionx.json", help="Config path to validate.")
    validate_config.add_argument("--json", action="store_true", help="Write machine-readable validation output.")
    validate_config.set_defaults(func=commands.validate_config_command)

    test_plan = subparsers.add_parser("test-plan", help="Generate defensive test plans from Arkheionx report JSON.")
    test_plan.add_argument("--report", default="", help="Arkheionx report JSON input path.")
    test_plan.add_argument("--output", default="", help="Markdown test plan output path.")
    test_plan.add_argument("--json-output", default="", help="Optional JSON test plan output path.")
    test_plan.add_argument("--foundry-output", default="", help="Optional safe Foundry invariant skeleton output path.")
    test_plan.add_argument("--check", action="store_true", help="Fail if committed fixture test plans are stale.")
    test_plan.set_defaults(func=commands.test_plan_command)

    search = subparsers.add_parser("search", help="Search local Arkheionx security memory metadata.")
    search.add_argument("query", help="Search query, for example: oracle stale price")
    search.add_argument("--json", action="store_true", help="Output JSON.")
    search.add_argument("--limit", type=int, default=10, help="Maximum matches to return.")
    search.add_argument(
        "--type",
        choices=["finding", "historical_pattern", "poc", "doc", "rule_pack", "suggested_test", "all"],
        default="all",
        help="Filter by node type.",
    )
    search.set_defaults(func=commands.search_command)

    demo = subparsers.add_parser("demo", help="List, show, and copy safe local demo workflows.")
    demo.add_argument("--list", action="store_true", help="List available demos.")
    demo.add_argument("--show", metavar="ID", default="", help="Show details for a demo.")
    demo.add_argument("--commands", metavar="ID", default="", help="Print the demo workflow commands.")
    demo.add_argument("--copy", nargs=2, metavar=("ID", "DEST"), default=None, help="Copy a demo fixture to DEST.")
    demo.add_argument("--force", action="store_true", help="Allow copy into a non-empty destination.")
    demo.add_argument("--json", action="store_true", help="JSON output for --list/--show.")
    demo.set_defaults(func=commands.demo_command)

    _add_workbench_commands(subparsers)

    review_map = subparsers.add_parser(
        "review-map",
        help="Build a local protocol review map: contracts, value paths, assumptions, test gaps, proof suggestions, evidence links.",
    )
    review_map.add_argument("repo", nargs="?", default=".", help="Authorized local repository root.")
    review_map.add_argument("--out", default="", help="Artifact output directory (default: <repo>/.arkheionx/out/review-map/).")
    review_map.add_argument("--top", type=int, default=10, help="Number of top review targets to show.")
    review_map.add_argument("--json", action="store_true", help="Print machine-readable JSON to stdout (no human text).")
    review_map.add_argument("--no-write", action="store_true", help="Print the summary only; do not write artifact files.")
    review_map.add_argument("--include-low-confidence", action="store_true", help="Include low-confidence test gaps.")
    review_map.add_argument("--target", default="", help="Limit the map to a single Contract.function.")
    review_map.set_defaults(func=workbench.review_map_command)

    test_gap_map = subparsers.add_parser(
        "test-gap-map",
        help="Show the focused Test Gap Map from review-map artifacts or derive it locally.",
    )
    test_gap_map.add_argument("repo", nargs="?", default=".", help="Authorized local repository root.")
    test_gap_map.add_argument("--out", default="", help="Artifact output directory (default: <repo>/.arkheionx/out/review-map/).")
    test_gap_map.add_argument("--top", type=int, default=5, help="Number of top test gaps to show in human output.")
    test_gap_map.add_argument("--json", action="store_true", help="Print machine-readable Test Gap Map JSON to stdout only.")
    test_gap_map.add_argument("--no-write", action="store_true", help="Build in memory only; do not write artifact files.")
    test_gap_map.add_argument("--include-low-confidence", action="store_true", help="Include low-confidence test gaps when building.")
    test_gap_map.add_argument("--target", default="", help="Limit the map to a single Contract.function when building.")
    test_gap_map.set_defaults(func=workbench.test_gap_map_command)

    value_paths = subparsers.add_parser(
        "value-paths",
        help="Show focused value paths from review-map artifacts or derive them locally.",
    )
    value_paths.add_argument("repo", nargs="?", default=".", help="Authorized local repository root.")
    value_paths.add_argument("--out", default="", help="Artifact output directory (default: <repo>/.arkheionx/out/review-map/).")
    value_paths.add_argument("--top", type=int, default=5, help="Number of top value paths to show in human output.")
    value_paths.add_argument("--json", action="store_true", help="Print machine-readable value-paths JSON to stdout only.")
    value_paths.add_argument("--no-write", action="store_true", help="Build in memory only; do not write artifact files.")
    value_paths.add_argument("--include-low-confidence", action="store_true", help="Include low-confidence review-map signals when building.")
    value_paths.add_argument("--target", default="", help="Limit the map to a single Contract.function when building.")
    value_paths.set_defaults(func=workbench.value_paths_command)

    assumptions = subparsers.add_parser(
        "assumptions",
        help="Show focused assumptions from review-map artifacts or derive them locally.",
    )
    assumptions.add_argument("repo", nargs="?", default=".", help="Authorized local repository root.")
    assumptions.add_argument("--out", default="", help="Artifact output directory (default: <repo>/.arkheionx/out/review-map/).")
    assumptions.add_argument("--top", type=int, default=5, help="Number of top assumptions to show in human output.")
    assumptions.add_argument("--json", action="store_true", help="Print machine-readable assumptions JSON to stdout only.")
    assumptions.add_argument("--no-write", action="store_true", help="Build in memory only; do not write artifact files.")
    assumptions.add_argument("--include-low-confidence", action="store_true", help="Include low-confidence review-map signals when building.")
    assumptions.add_argument("--target", default="", help="Limit the map to a single Contract.function when building.")
    assumptions.set_defaults(func=workbench.assumptions_command)

    proof_plan = subparsers.add_parser(
        "proof-plan",
        help="Show focused proof suggestions from review-map artifacts or derive them locally.",
    )
    proof_plan.add_argument("repo", nargs="?", default=".", help="Authorized local repository root.")
    proof_plan.add_argument("--out", default="", help="Artifact output directory (default: <repo>/.arkheionx/out/review-map/).")
    proof_plan.add_argument("--top", type=int, default=5, help="Number of top proof suggestions to show in human output.")
    proof_plan.add_argument("--json", action="store_true", help="Print machine-readable proof-plan JSON to stdout only.")
    proof_plan.add_argument("--no-write", action="store_true", help="Build in memory only; do not write artifact files.")
    proof_plan.add_argument("--include-low-confidence", action="store_true", help="Include low-confidence proof suggestions when building.")
    proof_plan.add_argument("--target", default="", help="Limit the map to a single Contract.function when building.")
    proof_plan.set_defaults(func=workbench.proof_plan_command)

    evidence_links = subparsers.add_parser(
        "evidence-links",
        help="Show focused evidence links from review-map artifacts or derive them locally.",
    )
    evidence_links.add_argument("repo", nargs="?", default=".", help="Authorized local repository root.")
    evidence_links.add_argument("--out", default="", help="Artifact output directory (default: <repo>/.arkheionx/out/review-map/).")
    evidence_links.add_argument("--top", type=int, default=5, help="Number of top evidence links to show in human output.")
    evidence_links.add_argument("--json", action="store_true", help="Print machine-readable evidence-links JSON to stdout only.")
    evidence_links.add_argument("--no-write", action="store_true", help="Build in memory only; do not write artifact files.")
    evidence_links.add_argument("--include-low-confidence", action="store_true", help="Include low-confidence review-map signals when building.")
    evidence_links.add_argument("--target", default="", help="Limit the map to a single Contract.function when building.")
    evidence_links.set_defaults(func=workbench.evidence_links_command)

    review_package = subparsers.add_parser(
        "review-package",
        help="Build a local reviewer-ready review package (manifest, validation, README, copied artifacts) under .arkheionx/out/review-package/.",
    )
    review_package.add_argument("repo", nargs="?", default=".", help="Authorized local repository root.")
    review_package.add_argument("--output", default="", help="Package output directory (default: <repo>/.arkheionx/out/review-package/).")
    review_package.add_argument("--json", action="store_true", help="Print machine-readable JSON to stdout only (no human text).")
    review_package.add_argument("--no-write", action="store_true", help="Build and validate in memory only; write no package files.")
    review_package.add_argument("--strict", action="store_true", help="Exit nonzero (1) when validation is invalid or reports errors.")
    review_package.add_argument("--export", default="", choices=["", "zip"], help="Also write a deterministic local archive of the package (only 'zip').")
    review_package.add_argument("--export-output", default="", help="Export archive path (default: <package>/exports/arkheionx-review-package-<id>.zip).")
    review_package.add_argument("--exclude-unknown", action="store_true", help="Exclude unclassified (unknown) artifacts from the package.")
    review_package.add_argument("--no-copy-artifacts", action="store_true", help="Do not copy artifact files; write manifest/validation/README only.")
    review_package.add_argument("--include-protocol-model", action="store_true", help="Include a protocol-model.json sidecar when buildable (default on).")
    review_package.add_argument("--no-protocol-model", action="store_true", help="Do not include the protocol-model.json sidecar or cross-reference checks.")
    review_package.set_defaults(func=workbench.review_package_command)

    local_validate = subparsers.add_parser(
        "local-validate",
        help="Ingest a saved Foundry test output file into local validation artifacts (local/static; never runs forge).",
    )
    local_validate.add_argument("repo", help="Authorized local repository root.")
    local_validate.add_argument("--input", required=True, help="Path to a saved Foundry test output file (JSON or text).")
    local_validate.add_argument("--json", action="store_true", help="Print machine-readable JSON to stdout only (no human text).")
    local_validate.add_argument("--no-write", action="store_true", help="Parse and build in memory only; write no artifacts.")
    local_validate.add_argument("--output", default="", help="Output directory (default: <repo>/.arkheionx/out/local-validation/).")
    local_validate.add_argument("--format", default="auto", choices=["auto", "foundry-json", "foundry-text"], help="Saved-output format (default: auto).")
    local_validate.add_argument("--tool", default="foundry", help="Local validation tool label recorded in artifacts (default: foundry).")
    local_validate.add_argument("--command", default="forge test --json", help="Command string recorded for provenance only; never executed.")
    local_validate.set_defaults(func=workbench.cmd_local_validate)

    agent_brief = subparsers.add_parser(
        "agent-brief",
        help="Build an AI-agent-ready review brief (value paths, surfaces, hypotheses) from the review map.",
    )
    agent_brief.add_argument("repo", nargs="?", default=".", help="Authorized local repository root.")
    agent_brief.add_argument("--out", default="", help="Artifact output directory (default: <repo>/.arkheionx/research/).")
    agent_brief.add_argument("--top", type=int, default=10, help="Number of top review targets to consider.")
    agent_brief.add_argument("--json", action="store_true", help="Print machine-readable JSON to stdout only (no human text).")
    agent_brief.add_argument("--no-write", action="store_true", help="Build in memory only; do not write artifact files.")
    agent_brief.add_argument("--include-low-confidence", action="store_true", help="Include low-confidence review-map signals when building.")
    agent_brief.set_defaults(func=workbench.agent_brief_command)

    hypothesis_log = subparsers.add_parser(
        "hypothesis-log",
        help="Generate a structured hypothesis log and rejected-finding memory from review-map surfaces.",
    )
    hypothesis_log.add_argument("repo", nargs="?", default=".", help="Authorized local repository root.")
    hypothesis_log.add_argument("--out", default="", help="Artifact output directory (default: <repo>/.arkheionx/research/).")
    hypothesis_log.add_argument("--top", type=int, default=10, help="Number of top review targets to consider.")
    hypothesis_log.add_argument("--json", action="store_true", help="Print machine-readable JSON to stdout only (no human text).")
    hypothesis_log.add_argument("--no-write", action="store_true", help="Build in memory only; do not write artifact files.")
    hypothesis_log.add_argument("--include-low-confidence", action="store_true", help="Include low-confidence review-map signals when building.")
    hypothesis_log.set_defaults(func=workbench.hypothesis_log_command)

    case_study = subparsers.add_parser(
        "case-study",
        help="Generate a sanitized case-study / research-session report template from artifacts.",
    )
    case_study.add_argument("repo", nargs="?", default=".", help="Authorized local repository root.")
    case_study.add_argument("--out", default="", help="Output directory, or a .md file path for the Markdown case study.")
    case_study.add_argument("--from", dest="from_dir", default="", help="Directory holding a hypotheses.json log to incorporate statuses from.")
    case_study.add_argument("--top", type=int, default=10, help="Number of top review targets to consider.")
    case_study.add_argument("--json", action="store_true", help="Print machine-readable JSON to stdout only (no human text).")
    case_study.add_argument("--no-write", action="store_true", help="Build in memory only; do not write artifact files.")
    case_study.add_argument("--include-low-confidence", action="store_true", help="Include low-confidence review-map signals when building.")
    case_study.set_defaults(func=workbench.case_study_command)

    blind_spots = subparsers.add_parser(
        "blind-spots",
        help="Rank likely blind-spot candidates: high-impact surfaces with weak review evidence (v5).",
    )
    blind_spots.add_argument("repo", nargs="?", default=".", help="Authorized local repository root.")
    blind_spots.add_argument("--out", default="", help="Artifact output directory (default: <repo>/.arkheionx/blind-spots/).")
    blind_spots.add_argument("--top", type=int, default=10, help="Number of top review targets to consider.")
    blind_spots.add_argument("--limit", type=int, default=12, help="Maximum number of blind-spot candidates to surface.")
    blind_spots.add_argument("--json", action="store_true", help="Print machine-readable JSON to stdout only (no human text).")
    blind_spots.add_argument("--no-write", action="store_true", help="Build in memory only; do not write artifact files.")
    blind_spots.add_argument("--include-low-confidence", action="store_true", help="Include low-confidence review-map signals when building.")
    blind_spots.set_defaults(func=workbench.blind_spots_command)

    criticality_map = subparsers.add_parser(
        "criticality-map",
        help="Map criticality potential (heuristic blast radius, not severity) across protocol surfaces (v5).",
    )
    criticality_map.add_argument("repo", nargs="?", default=".", help="Authorized local repository root.")
    criticality_map.add_argument("--out", default="", help="Artifact output directory (default: <repo>/.arkheionx/criticality-map/).")
    criticality_map.add_argument("--top", type=int, default=10, help="Number of top review targets to consider.")
    criticality_map.add_argument("--json", action="store_true", help="Print machine-readable JSON to stdout only (no human text).")
    criticality_map.add_argument("--no-write", action="store_true", help="Build in memory only; do not write artifact files.")
    criticality_map.add_argument("--include-low-confidence", action="store_true", help="Include low-confidence review-map signals when building.")
    criticality_map.set_defaults(func=workbench.criticality_map_command)

    counterfactuals = subparsers.add_parser(
        "counterfactuals",
        help="Generate counterfactual research prompts by negating guarding assumptions (v5).",
    )
    counterfactuals.add_argument("repo", nargs="?", default=".", help="Authorized local repository root.")
    counterfactuals.add_argument("--out", default="", help="Artifact output directory (default: <repo>/.arkheionx/counterfactuals/).")
    counterfactuals.add_argument("--top", type=int, default=10, help="Number of top review targets to consider.")
    counterfactuals.add_argument("--json", action="store_true", help="Print machine-readable JSON to stdout only (no human text).")
    counterfactuals.add_argument("--no-write", action="store_true", help="Build in memory only; do not write artifact files.")
    counterfactuals.add_argument("--include-low-confidence", action="store_true", help="Include low-confidence review-map signals when building.")
    counterfactuals.set_defaults(func=workbench.counterfactuals_command)

    research_pack = subparsers.add_parser(
        "research-pack",
        help="Generate a complete local AI/human-ready bug bounty research pack (v5, headline). Writes by default.",
    )
    research_pack.add_argument("repo", nargs="?", default=".", help="Authorized local repository root.")
    research_pack.add_argument("--out", default="", help="Pack output directory (default: <repo>/.arkheionx/research-pack/).")
    research_pack.add_argument("--top", type=int, default=10, help="Number of top review targets to consider.")
    research_pack.add_argument("--json", action="store_true", help="Print the machine-readable manifest JSON to stdout only (no human text).")
    research_pack.add_argument("--no-write", action="store_true", help="Build the pack in memory only; do not write files.")
    research_pack.add_argument("--include-low-confidence", action="store_true", help="Include low-confidence review-map signals when building.")
    research_pack.set_defaults(func=workbench.research_pack_command)

    evidence_graph = subparsers.add_parser(
        "evidence-graph",
        help="Classify every important review surface into an evidence state (v6): tested, unresolved, needs-human-review, insufficient-evidence, unclassified.",
    )
    evidence_graph.add_argument("repo", nargs="?", default=".", help="Authorized local repository root.")
    evidence_graph.add_argument("--out", default="", help="Artifact output directory (default: <repo>/.arkheionx/evidence-graph/).")
    evidence_graph.add_argument("--top", type=int, default=10, help="Number of top review targets to consider.")
    evidence_graph.add_argument("--json", action="store_true", help="Print machine-readable JSON to stdout only (no human text).")
    evidence_graph.add_argument("--no-write", action="store_true", help="Build in memory only; do not write artifact files.")
    evidence_graph.add_argument("--only-unresolved", action="store_true", help="Show only surfaces in an open evidence state (unresolved/insufficient/needs-human-review/unclassified).")
    evidence_graph.add_argument("--include-low-confidence", action="store_true", help="Include low-confidence review-map signals when building.")
    evidence_graph.set_defaults(func=workbench.evidence_graph_command)

    interaction_matrix = subparsers.add_parser(
        "interaction-matrix",
        help="Detect meaningful combinations of surfaces that may hide bugs when tested together (v6). Interaction priority is not severity.",
    )
    interaction_matrix.add_argument("repo", nargs="?", default=".", help="Authorized local repository root.")
    interaction_matrix.add_argument("--out", default="", help="Artifact output directory (default: <repo>/.arkheionx/interaction-matrix/).")
    interaction_matrix.add_argument("--top", type=int, default=10, help="Number of top review targets to consider.")
    interaction_matrix.add_argument("--json", action="store_true", help="Print machine-readable JSON to stdout only (no human text).")
    interaction_matrix.add_argument("--no-write", action="store_true", help="Build in memory only; do not write artifact files.")
    interaction_matrix.add_argument("--only-unresolved", action="store_true", help="Show only high-impact interactions with weak or no evidence.")
    interaction_matrix.add_argument("--include-low-confidence", action="store_true", help="Include low-confidence review-map signals when building.")
    interaction_matrix.set_defaults(func=workbench.interaction_matrix_command)

    unresolved_map = subparsers.add_parser(
        "unresolved-map",
        help="Show everything important that local evidence does not yet close (v6): high-impact unresolved surfaces and interactions. Unresolved does not mean vulnerable.",
    )
    unresolved_map.add_argument("repo", nargs="?", default=".", help="Authorized local repository root.")
    unresolved_map.add_argument("--out", default="", help="Artifact output directory (default: <repo>/.arkheionx/unresolved-map/).")
    unresolved_map.add_argument("--top", type=int, default=10, help="Number of top review targets to consider.")
    unresolved_map.add_argument("--json", action="store_true", help="Print machine-readable JSON to stdout only (no human text).")
    unresolved_map.add_argument("--no-write", action="store_true", help="Build in memory only; do not write artifact files.")
    unresolved_map.add_argument("--include-low-confidence", action="store_true", help="Include low-confidence review-map signals when building.")
    unresolved_map.set_defaults(func=workbench.unresolved_map_command)

    complete_review = subparsers.add_parser(
        "complete-review",
        help="Generate a complete local V6 review package (review map, blind spots, criticality, counterfactuals, evidence graph, interaction matrix, unresolved map, agent input, human checklist, case-study template, manifest) (v6, headline). Writes by default.",
    )
    complete_review.add_argument("repo", nargs="?", default=".", help="Authorized local repository root.")
    complete_review.add_argument("--out", default="", help="Package output directory (default: <repo>/.arkheionx/complete-review/).")
    complete_review.add_argument("--top", type=int, default=10, help="Number of top review targets to consider.")
    complete_review.add_argument("--json", action="store_true", help="Print the machine-readable manifest JSON to stdout only (no human text).")
    complete_review.add_argument("--no-write", action="store_true", help="Build the package in memory only; do not write files.")
    complete_review.add_argument("--include-low-confidence", action="store_true", help="Include low-confidence review-map signals when building.")
    complete_review.set_defaults(func=workbench.complete_review_command)

    scope_map = subparsers.add_parser(
        "scope-map",
        help="Parse a contest/audit scope note into a structured scope map: trusted assumptions, known/accepted risks, invariants, focus areas, and do-not-waste-time filters (v7).",
    )
    scope_map.add_argument("repo", nargs="?", default=".", help="Authorized local repository root.")
    scope_map.add_argument("--scope-file", default="", help="Path to a markdown scope note (optional; generic map inferred if omitted).")
    scope_map.add_argument("--out", default="", help="Artifact output directory (default: <repo>/.arkheionx/scope-map/).")
    scope_map.add_argument("--top", type=int, default=10, help="Number of top review targets to consider.")
    scope_map.add_argument("--json", action="store_true", help="Print machine-readable JSON to stdout only (no human text).")
    scope_map.add_argument("--no-write", action="store_true", help="Build in memory only; do not write artifact files.")
    scope_map.add_argument("--include-low-confidence", action="store_true", help="Include low-confidence review-map signals when building.")
    scope_map.set_defaults(func=workbench.scope_map_command)

    scope_lanes = subparsers.add_parser(
        "scope-lanes",
        help="Generate scope-aware review lanes from repository surfaces plus scope rules (v7). Lanes are planning artifacts, not findings.",
    )
    scope_lanes.add_argument("repo", nargs="?", default=".", help="Authorized local repository root.")
    scope_lanes.add_argument("--scope-file", default="", help="Path to a markdown scope note (optional).")
    scope_lanes.add_argument("--out", default="", help="Artifact output directory (default: <repo>/.arkheionx/scope-lanes/).")
    scope_lanes.add_argument("--top", type=int, default=10, help="Number of top review targets to consider.")
    scope_lanes.add_argument("--json", action="store_true", help="Print machine-readable JSON to stdout only (no human text).")
    scope_lanes.add_argument("--no-write", action="store_true", help="Build in memory only; do not write artifact files.")
    scope_lanes.add_argument("--include-low-confidence", action="store_true", help="Include low-confidence review-map signals when building.")
    scope_lanes.set_defaults(func=workbench.scope_lanes_command)

    scope_tasks = subparsers.add_parser(
        "scope-tasks",
        help="Turn scope-aware lanes into precise, bounded, evidence-oriented tasks for a human reviewer or AI agent (v7). Tasks are not exploit instructions.",
    )
    scope_tasks.add_argument("repo", nargs="?", default=".", help="Authorized local repository root.")
    scope_tasks.add_argument("--scope-file", default="", help="Path to a markdown scope note (optional).")
    scope_tasks.add_argument("--out", default="", help="Artifact output directory (default: <repo>/.arkheionx/scope-tasks/).")
    scope_tasks.add_argument("--top", type=int, default=10, help="Number of top review targets to consider.")
    scope_tasks.add_argument("--json", action="store_true", help="Print machine-readable JSON to stdout only (no human text).")
    scope_tasks.add_argument("--no-write", action="store_true", help="Build in memory only; do not write artifact files.")
    scope_tasks.add_argument("--include-low-confidence", action="store_true", help="Include low-confidence review-map signals when building.")
    scope_tasks.set_defaults(func=workbench.scope_tasks_command)

    scope_pack = subparsers.add_parser(
        "scope-pack",
        help="Generate a complete local scope-aware research pack: scope map, lanes, tasks, do-not-waste-time, evidence template/rubric, report-filter checklist, agent input, and manifest (v7). Writes by default.",
    )
    scope_pack.add_argument("repo", nargs="?", default=".", help="Authorized local repository root.")
    scope_pack.add_argument("--scope-file", default="", help="Path to a markdown scope note (optional).")
    scope_pack.add_argument("--out", default="", help="Pack output directory (default: <repo>/.arkheionx/scope-pack/).")
    scope_pack.add_argument("--top", type=int, default=10, help="Number of top review targets to consider.")
    scope_pack.add_argument("--json", action="store_true", help="Print the machine-readable manifest JSON to stdout only (no human text).")
    scope_pack.add_argument("--no-write", action="store_true", help="Build the pack manifest in memory only; do not write files.")
    scope_pack.add_argument("--include-low-confidence", action="store_true", help="Include low-confidence review-map signals when building.")
    scope_pack.set_defaults(func=workbench.scope_pack_command)

    evidence_judge = subparsers.add_parser(
        "evidence-judge",
        help="Judge whether local tests/evidence actually prove the intended task (v7). Does not confirm vulnerabilities; candidate-with-evidence is not a confirmed vulnerability.",
    )
    evidence_judge.add_argument("repo", nargs="?", default=".", help="Authorized local repository root.")
    evidence_judge.add_argument("--scope-file", default="", help="Path to a markdown scope note (optional).")
    evidence_judge.add_argument("--tasks-file", default="", help="Optional scope-tasks.json to align judged evidence with tasks.")
    evidence_judge.add_argument("--evidence-dir", default="", help="Optional evidence directory (default: scans .arkheionx/scope-pack, .arkheionx/evidence, .arkheionx/private, test, tests).")
    evidence_judge.add_argument("--out", default="", help="Artifact output directory (default: <repo>/.arkheionx/evidence-judge/).")
    evidence_judge.add_argument("--top", type=int, default=10, help="Number of top review targets to consider.")
    evidence_judge.add_argument("--json", action="store_true", help="Print machine-readable JSON to stdout only (no human text).")
    evidence_judge.add_argument("--no-write", action="store_true", help="Build in memory only; do not write artifact files.")
    evidence_judge.add_argument("--include-low-confidence", action="store_true", help="Include low-confidence review-map signals when building.")
    evidence_judge.set_defaults(func=workbench.evidence_judge_command)

    report_filter = subparsers.add_parser(
        "report-filter",
        help="Classify report candidates against the scope before submission (v7): potentially-reportable, needs-more-evidence, likely-known/accepted/trusted/out-of-scope/low-only, duplicate-prone, needs-human-review. Not final triage.",
    )
    report_filter.add_argument("repo", nargs="?", default=".", help="Authorized local repository root.")
    report_filter.add_argument("--scope-file", default="", help="Path to a markdown scope note (optional).")
    report_filter.add_argument("--out", default="", help="Artifact output directory (default: <repo>/.arkheionx/report-filter/).")
    report_filter.add_argument("--top", type=int, default=10, help="Number of top review targets to consider.")
    report_filter.add_argument("--json", action="store_true", help="Print machine-readable JSON to stdout only (no human text).")
    report_filter.add_argument("--no-write", action="store_true", help="Build in memory only; do not write artifact files.")
    report_filter.add_argument("--include-low-confidence", action="store_true", help="Include low-confidence review-map signals when building.")
    report_filter.set_defaults(func=workbench.report_filter_command)

    _add_lens_commands(subparsers)

    help_command = subparsers.add_parser("help", help="Print CLI help.")
    help_command.set_defaults(func=lambda _args: _print_help(parser))
    return parser


def _print_help(parser: argparse.ArgumentParser) -> int:
    parser.print_help()
    return exit_codes.SUCCESS


def _add_workbench_commands(subparsers) -> None:
    """Register the Foundry-powered workbench commands: open/map/flow/hunt/prove."""

    def _common(sub) -> None:
        sub.add_argument("repo", nargs="?", default=".", help="Authorized local repository root.")
        sub.add_argument("--from-report", default="", help="Reuse semantic_lite from an existing scan report JSON.")
        sub.add_argument("--foundry", action="store_true", help="Detect Foundry (no build) to label evidence.")
        sub.add_argument("--build", action="store_true", help="Run forge build for compiler-confirmed evidence.")
        sub.add_argument("--show-all", action="store_true", help="Include interfaces/tests/mocks/fixtures hidden by default.")
        sub.add_argument("--full", action="store_true", help="Detailed terminal output (tables, all edges).")
        sub.add_argument("--json", action="store_true", help="Print machine-readable JSON to stdout.")
        sub.add_argument("--no-artifacts", action="store_true", help="Do not write artifact files.")
        sub.add_argument("--artifacts-dir", default="", help="Base directory for .arkheionx/out (default: cwd).")
        sub.add_argument("--verbose", action="store_true", help="Verbose diagnostic output.")
        sub.add_argument("--raw", action="store_true", help="Include raw backend output.")
        sub.add_argument("--top", type=int, default=10, help="Number of top targets to consider/show.")

    opener = subparsers.add_parser("open", help="One-command project understanding (scan + orient).")
    _common(opener)
    opener.set_defaults(func=workbench.open_command)

    mapper = subparsers.add_parser("map", help="Draw the protocol: roles, journeys, money flow, hunter targets.")
    _common(mapper)
    mapper.set_defaults(func=workbench.map_command)

    flow = subparsers.add_parser("flow", help="Build the money-flow graph (compact summary + Mermaid).")
    _common(flow)
    flow.add_argument("--mermaid", action="store_true", help="Print Mermaid graph to stdout.")
    flow.set_defaults(func=workbench.flow_command)

    hunt = subparsers.add_parser("hunt", help="Rank bug-hunting surfaces for a solo researcher.")
    _common(hunt)
    hunt.set_defaults(func=workbench.hunt_command)

    prove = subparsers.add_parser("prove", help="Generate a local Foundry proof scaffold for a target.")
    _common(prove)
    prove.add_argument("--target", default="", help="Fully-qualified target, e.g. Vault.withdraw or src/Vault.sol:Vault.withdraw(uint256).")
    prove.add_argument("--run", action="store_true", help="Run targeted Foundry tests (never fakes proof).")
    prove.set_defaults(func=workbench.prove_command)

    trace = subparsers.add_parser("trace", help="Summarize the latest Foundry proof/trace for a target.")
    _common(trace)
    trace.add_argument("--target", default="", help="Fully-qualified target, e.g. Vault.withdraw.")
    trace.add_argument("--run", action="store_true", help="Run targeted Foundry tests, then summarize.")
    trace.set_defaults(func=workbench.trace_command)

    evidence = subparsers.add_parser("evidence", help="Build a compact evidence package from proof + trace artifacts.")
    _common(evidence)
    evidence.add_argument("--target", default="", help="Fully-qualified target, e.g. Vault.withdraw.")
    evidence.add_argument("--from-proof", default="", help="Build from a specific proof.json artifact.")
    evidence.set_defaults(func=workbench.evidence_command)

    report = subparsers.add_parser("report", help="Create a responsible local report draft from evidence.")
    _common(report)
    report.add_argument("--target", default="", help="Fully-qualified target, e.g. Vault.withdraw.")
    report.add_argument("--from-evidence", default="", help="Build from a specific evidence.json artifact.")
    report.set_defaults(func=workbench.report_command)

    ev_status = subparsers.add_parser("evidence-status", help="Inspect proof/evidence/report artifact state for a repo.")
    ev_status.add_argument("repo", nargs="?", default=".", help="Authorized local repository root.")
    ev_status.add_argument("--target", default="", help="Limit to a single target.")
    ev_status.add_argument("--artifacts-dir", default="", help="Base directory for .arkheionx/out (default: cwd).")
    ev_status.add_argument("--json", action="store_true", help="Print machine-readable JSON to stdout.")
    ev_status.set_defaults(func=workbench.evidence_status_command)

    validate = subparsers.add_parser("validate-artifacts", help="Validate generated proof/evidence/report artifacts.")
    validate.add_argument("repo", nargs="?", default=".", help="Authorized local repository root.")
    validate.add_argument("--artifacts-dir", default="", help="Base directory for .arkheionx/out (default: cwd).")
    validate.add_argument("--json", action="store_true", help="Print machine-readable JSON to stdout.")
    validate.set_defaults(func=workbench.validate_artifacts_command)


def _add_lens_commands(subparsers) -> None:
    """Register the v7.5 protocol-lens commands (lens-list/map/lanes/tasks/pack/evidence/report-filter)."""

    def _common(sub, *, with_out_default: str = "") -> None:
        sub.add_argument("repo", nargs="?", default=".", help="Authorized local repository root.")
        sub.add_argument("--lens", default="fixed-credit-market", help="Protocol lens id (default: fixed-credit-market).")
        sub.add_argument("--scope-file", default="", help="Path to a markdown scope note (optional).")
        sub.add_argument("--out", default="", help=f"Artifact output directory{with_out_default}.")
        sub.add_argument("--top", type=int, default=10, help="Number of top review targets to consider.")
        sub.add_argument("--json", action="store_true", help="Print machine-readable JSON to stdout only (no human text).")
        sub.add_argument("--no-write", action="store_true", help="Build in memory only; do not write artifact files.")
        sub.add_argument("--include-low-confidence", action="store_true", help="Include low-confidence review-map signals when building.")

    lens_list = subparsers.add_parser(
        "lens-list",
        help="List implemented (and planned) protocol lenses (v7.5).",
    )
    lens_list.add_argument("--json", action="store_true", help="Print machine-readable JSON to stdout only.")
    lens_list.set_defaults(func=workbench.lens_list_command)

    lens_map = subparsers.add_parser(
        "lens-map",
        help="Build a protocol-aware lens map (protocol model + scope + behavior promises + economic invariants) (v7.5). Planning artifact, not a finding.",
    )
    _common(lens_map, with_out_default=" (default: <repo>/.arkheionx/lens-map/)")
    lens_map.set_defaults(func=workbench.lens_map_command)

    lens_lanes = subparsers.add_parser(
        "lens-lanes",
        help="Generate protocol-aware review lanes from the lens plus repository surfaces and scope (v7.5). Lane priority is review order, not severity.",
    )
    _common(lens_lanes, with_out_default=" (default: <repo>/.arkheionx/lens-lanes/)")
    lens_lanes.set_defaults(func=workbench.lens_lanes_command)

    lens_tasks = subparsers.add_parser(
        "lens-tasks",
        help="Turn lens review lanes into precise, bounded, evidence-oriented scope tasks (v7.5). Tasks are research instructions, not exploit instructions.",
    )
    _common(lens_tasks, with_out_default=" (default: <repo>/.arkheionx/lens-tasks/)")
    lens_tasks.set_defaults(func=workbench.lens_tasks_command)

    lens_pack = subparsers.add_parser(
        "lens-pack",
        help="Generate a complete local lens pack: run context, scope map, protocol model, value-flow map, behavior promises, economic invariants, temporal windows, periphery bundle map, evidence map, review lanes, scope tasks, blind-spot ranking, evidence rubric, report filter, agent input, and lens-pack.json (v7.5). Writes by default.",
    )
    _common(lens_pack, with_out_default=" (default: <repo>/.arkheionx/lens-pack/)")
    lens_pack.set_defaults(func=workbench.lens_pack_command)

    lens_evidence = subparsers.add_parser(
        "lens-evidence",
        help="Classify local-test evidence for each lens economic invariant (v7.5). Evidence quality is not vulnerability validity.",
    )
    _common(lens_evidence, with_out_default=" (default: <repo>/.arkheionx/lens-evidence/)")
    lens_evidence.set_defaults(func=workbench.lens_evidence_command)

    lens_report_filter = subparsers.add_parser(
        "lens-report-filter",
        help="Classify lens report candidates against the scope before submission (v7.5). Not final triage; human decision required.",
    )
    _common(lens_report_filter, with_out_default=" (default: <repo>/.arkheionx/lens-report-filter/)")
    lens_report_filter.set_defaults(func=workbench.lens_report_filter_command)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    if argv is None:
        argv = sys.argv[1:]
    if not argv:
        parser.print_help()
        return exit_codes.SUCCESS
    args = parser.parse_args(argv)
    func = getattr(args, "func", None)
    if func is None:
        parser.print_help()
        return exit_codes.INVALID_ARGUMENTS
    return int(func(args))


if __name__ == "__main__":
    raise SystemExit(main())

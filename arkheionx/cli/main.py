"""Arkheionx local/static CLI command surface.

v2.0.1 keeps this parser available through the installed `arkheionx` console
command and the `python3 -m arkheionx.cli.main` module path. Existing scripts
remain supported and first-class.
"""
from __future__ import annotations

import argparse
import sys

from arkheionx.cli import commands, exit_codes, workbench


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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="arkheionx",
        description="Arkheionx local/static DeFi value-flow workbench CLI.",
    )
    subparsers = parser.add_subparsers(dest="command")

    version = subparsers.add_parser("version", help="Print package and release milestone metadata.")
    version.set_defaults(func=commands.version_command)

    doctor = subparsers.add_parser("doctor", help="Diagnose Arkheionx install, Foundry, and project layout.")
    doctor.add_argument("repo", nargs="?", default=".", help="Project root to diagnose (default: current dir).")
    doctor.add_argument("--install", action="store_true", help="Focus on install health: command path, Python, package import, PATH hint.")
    doctor.set_defaults(func=workbench.doctor_command)

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

    _add_workbench_commands(subparsers)

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

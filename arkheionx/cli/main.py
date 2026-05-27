"""Arkheionx local/static CLI command surface.

v2.0.0 exposes this parser through the installed `arkheionx` console command
and the `python3 -m arkheionx.cli.main` module path. Existing scripts remain
supported and first-class.
"""
from __future__ import annotations

import argparse
import sys

from arkheionx.cli import commands, exit_codes


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
        description="Arkheionx local/static pre-audit readiness CLI.",
    )
    subparsers = parser.add_subparsers(dest="command")

    version = subparsers.add_parser("version", help="Print package and release milestone metadata.")
    version.set_defaults(func=commands.version_command)

    doctor = subparsers.add_parser("doctor", help="Check local package imports, rule packs, and safety posture.")
    doctor.set_defaults(func=commands.doctor_command)

    scan = subparsers.add_parser("scan", help="Run a local Arkheionx readiness scan.")
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

    help_command = subparsers.add_parser("help", help="Print CLI help.")
    help_command.set_defaults(func=lambda _args: _print_help(parser))
    return parser


def _print_help(parser: argparse.ArgumentParser) -> int:
    parser.print_help()
    return exit_codes.SUCCESS


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

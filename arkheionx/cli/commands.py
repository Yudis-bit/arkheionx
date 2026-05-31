"""Command implementations for the Arkheionx local/static CLI."""
from __future__ import annotations

import importlib
import json
import platform
import sys
import tempfile
from argparse import Namespace
from pathlib import Path
from typing import Iterable

from arkheionx.cli import exit_codes
from arkheionx.config.loader import load_and_validate_config
from arkheionx.config.schema import normalize_config
from arkheionx.core.safety import LOCAL_ONLY_DISCLAIMER, READINESS_DISCLAIMER
from arkheionx.rules.registry import list_rule_packs
from arkheionx.version import CURRENT_MILESTONE, NEXT_MILESTONE, STABLE_RELEASE, __version__


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _module_main(module_name: str, argv: list[str]) -> int:
    module = importlib.import_module(module_name)
    main = getattr(module, "main", None)
    if main is None:
        print(f"error: module {module_name} does not expose main()", file=sys.stderr)
        return exit_codes.RUNTIME_ERROR
    try:
        return int(main(argv) or 0)
    except SystemExit as exc:
        code = exc.code
        if isinstance(code, int):
            return code
        return exit_codes.RUNTIME_ERROR


def _append_option(argv: list[str], name: str, value: object) -> None:
    if value is None or value == "":
        return
    argv.extend([name, str(value)])


def _append_flag(argv: list[str], name: str, enabled: bool) -> None:
    if enabled:
        argv.append(name)


def _read_json(path: str) -> tuple[dict[str, object], str | None]:
    if not path:
        return {}, None
    candidate = Path(path).expanduser()
    if not candidate.is_absolute():
        candidate = (Path.cwd() / candidate).resolve()
    if not candidate.exists():
        return {}, f"config file does not exist: {path}"
    try:
        payload = json.loads(candidate.read_text(encoding="utf-8"))
    except ValueError as exc:
        return {}, f"could not parse config {path}: {exc}"
    except OSError as exc:
        return {}, f"could not read config {path}: {exc}"
    if not isinstance(payload, dict):
        return {}, f"config {path} must be a JSON object"
    return payload, None


def _temporary_profile_config(config_path: str, output_profile: str) -> tuple[str | None, str | None]:
    raw, error = _read_json(config_path)
    if error:
        return None, error
    result = normalize_config(raw, source=config_path or "cli-output-profile")
    if not result.valid:
        return None, "; ".join(result.errors)
    config = result.normalized_config
    config["output_profile"] = output_profile
    handle = tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".arkheionx.json", delete=False)
    with handle:
        json.dump(config, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return handle.name, None


def _cleanup_paths(paths: Iterable[str | None]) -> None:
    for path in paths:
        if not path:
            continue
        try:
            Path(path).unlink(missing_ok=True)
        except OSError:
            pass


def version_command(_args: Namespace) -> int:
    from arkheionx.cli import colors

    lines = [
        f"Arkheionx package version: {__version__}",
        f"Latest stable release: {STABLE_RELEASE}",
        f"Current milestone: {CURRENT_MILESTONE}",
        f"Next milestone: {NEXT_MILESTONE}",
    ]
    print(colors.colorize_report("\n".join(lines)))
    return exit_codes.SUCCESS


def doctor_command(_args: Namespace) -> int:
    print("Arkheionx doctor")
    print(f"Python: {platform.python_version()}")
    print("Package imports: ok")
    print("Rule packs:")
    for info in list_rule_packs():
        print(f"- {info.key}: {info.display_name} ({info.prefix})")
    print(LOCAL_ONLY_DISCLAIMER)
    print(READINESS_DISCLAIMER)
    return exit_codes.SUCCESS


def validate_config_command(args: Namespace) -> int:
    config_path = Path(args.config).expanduser() if args.config else None
    result = load_and_validate_config(config_path, REPO_ROOT)
    payload = {
        "valid": result.valid,
        "source": result.source,
        "errors": result.errors,
        "warnings": result.warnings,
        "normalized_config": result.normalized_config,
    }
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        label = result.source or str(config_path or ".arkheionx.json")
        if result.valid:
            print(f"ok: Arkheionx config valid: {label}")
        else:
            print(f"error: Arkheionx config invalid: {label}", file=sys.stderr)
        for warning in result.warnings:
            print(f"warning: {warning}")
        for error in result.errors:
            print(f"error: {error}", file=sys.stderr)
    if result.valid:
        return exit_codes.SUCCESS
    if any("Dangerous config key" in error for error in result.errors):
        return exit_codes.SAFETY_REJECTION
    return exit_codes.INVALID_ARGUMENTS


def search_command(args: Namespace) -> int:
    argv = [args.query]
    _append_flag(argv, "--json", bool(args.json))
    _append_option(argv, "--limit", args.limit)
    if getattr(args, "type", "all") != "all":
        _append_option(argv, "--type", args.type)
    return _module_main("scripts.search_knowledge", argv)


def test_plan_command(args: Namespace) -> int:
    argv: list[str] = []
    _append_flag(argv, "--check", bool(args.check))
    _append_option(argv, "--report", args.report)
    _append_option(argv, "--output", args.output)
    _append_option(argv, "--json-output", args.json_output)
    _append_option(argv, "--foundry-output", args.foundry_output)
    return _module_main("scripts.generate_test_plan", argv)


def scan_command(args: Namespace) -> int:
    argv = ["--root", args.root]
    _append_option(argv, "--protocol-type", args.protocol_type)

    temp_config: str | None = None
    config_path = args.config
    if args.output_profile:
        if not config_path:
            cwd_default = Path(".arkheionx.json")
            root_default = Path(args.root) / ".arkheionx.json"
            if cwd_default.exists():
                config_path = str(cwd_default)
            elif root_default.exists():
                config_path = str(root_default)
        temp_config, error = _temporary_profile_config(config_path or "", args.output_profile)
        if error:
            print(f"error: {error}", file=sys.stderr)
            return exit_codes.SAFETY_REJECTION
        config_path = temp_config
    _append_option(argv, "--config", config_path)

    _append_option(argv, "--output", args.output)
    _append_option(argv, "--json-output", args.json_output)
    _append_option(argv, "--sarif-output", args.sarif_output)
    _append_option(argv, "--issue-plan-output", args.issue_plan_output)
    _append_option(argv, "--summary-output", args.summary_output)
    _append_option(argv, "--comment-output", args.comment_output)
    _append_option(argv, "--baseline-output", args.baseline_output)
    _append_option(argv, "--compare-baseline", args.compare_baseline)
    _append_option(argv, "--diff-output", args.diff_output)
    _append_option(argv, "--diff-json-output", args.diff_json_output)
    _append_option(argv, "--fail-score-below", args.fail_under_score)
    _append_option(argv, "--min-confidence-for-issue-plan", args.min_confidence)
    _append_flag(argv, "--generate-invariant-skeletons", bool(args.generate_invariant_skeletons))
    try:
        return _module_main("scripts.pre_audit_scan", argv)
    finally:
        _cleanup_paths([temp_config])


def demo_command(args: Namespace) -> int:
    """List, show, and copy safe local demo workflows."""
    from dataclasses import asdict

    from arkheionx import demo as demo_pkg
    from arkheionx.cli import colors

    def _unknown(demo_id: str) -> int:
        print(f"error: unknown demo: {demo_id}", file=sys.stderr)
        print(f"valid demos: {', '.join(demo_pkg.demo_ids())}", file=sys.stderr)
        return exit_codes.INVALID_ARGUMENTS

    show_id = getattr(args, "show", "") or ""
    commands_id = getattr(args, "commands", "") or ""
    copy_args = getattr(args, "copy", None)
    use_json = bool(getattr(args, "json", False))

    if show_id:
        demo = demo_pkg.get_demo(show_id)
        if demo is None:
            return _unknown(show_id)
        print(json.dumps(asdict(demo), indent=2) if use_json else colors.colorize_report(demo_pkg.render_show(demo)))
        return exit_codes.SUCCESS

    if commands_id:
        demo = demo_pkg.get_demo(commands_id)
        if demo is None:
            return _unknown(commands_id)
        print(colors.colorize_report(demo_pkg.render_commands(demo, "./arkheionx-demo")))
        return exit_codes.SUCCESS

    if copy_args:
        demo_id, dest = copy_args[0], copy_args[1]
        demo = demo_pkg.get_demo(demo_id)
        if demo is None:
            return _unknown(demo_id)
        try:
            target, copied, source_kind = demo_pkg.copy_demo(demo, dest, force=bool(getattr(args, "force", False)))
        except demo_pkg.DemoCopyError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return exit_codes.INVALID_ARGUMENTS
        summary = "\n".join([
            f"Copied demo '{demo.id}' to {target}",
            f"Source: {source_kind}",
            f"Entries: {', '.join(copied)}",
            "",
            "Next",
            f"  arkheionx open {target}",
            f"  arkheionx hunt {target} --top 5",
            f"  arkheionx demo --commands {demo.id}",
        ])
        print(colors.colorize_report(summary))
        return exit_codes.SUCCESS

    # Default action (including --list): list available demos.
    demos = demo_pkg.list_demos()
    if use_json:
        print(json.dumps([asdict(demo) for demo in demos], indent=2))
    else:
        print(colors.colorize_report(demo_pkg.render_list(demos)))
    return exit_codes.SUCCESS

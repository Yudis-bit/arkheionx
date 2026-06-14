"""CLI handler for `arkheionx war-run` (experimental, local-first).

Reconstructs the economic machine, derives invariants, ranks attack paths, and
tells the researcher which are worth proving. No report, no RPC by default, no
broadcast, fork support is a plan only. Human review required.
"""
from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path

from arkheionx.cli import exit_codes

from .orchestrator import WarRunError, run_war_run

SUCCESS = exit_codes.SUCCESS
WARNING = exit_codes.RUNTIME_ERROR
FAILED = exit_codes.INVALID_ARGUMENTS


def war_run_command(args: Namespace) -> int:
    target = getattr(args, "target", ".") or "."
    if not Path(target).expanduser().exists():
        print(f"ArkheionX error: target not found: {target}")
        print("Next: run `arkheionx war-run <path> --scope scope.yaml` on an authorized local repo.")
        return FAILED

    out = str(getattr(args, "out", "") or "").strip() or None
    write = not bool(getattr(args, "no_write", False))
    gen_poc = not bool(getattr(args, "no_poc_skeletons", False))
    allow_fork = not bool(getattr(args, "no_fork", False))

    try:
        result = run_war_run(
            target,
            scope_file=str(getattr(args, "scope", "") or "") or None,
            out_dir=out,
            max_candidates=int(getattr(args, "max_candidates", 10) or 10),
            gen_poc=gen_poc,
            allow_fork_plan=allow_fork,
            memory_dir=str(getattr(args, "memory", "") or "") or None,
            write=write,
            asset_decimals=int(getattr(args, "asset_decimals", 0) or 0),
        )
    except WarRunError as exc:
        print(f"ArkheionX error: {exc}")
        return FAILED
    except OSError as exc:
        print(f"ArkheionX error: could not run war-run: {exc}")
        return FAILED

    if getattr(args, "json", False):
        print(json.dumps(result["triage"], indent=2))
        return SUCCESS if result["counts"]["candidates"] else WARNING

    print("\n".join(result["console"]))
    return SUCCESS if result["counts"]["candidates"] else WARNING

"""CLI handler for `arkheionx triage` (private Senior Researcher mode).

Local-only by default. The optional ``--rpc-url`` endpoint is masked in all output
and is never called live in this pass; senior triage makes no live-chain calls and
never mutates chain.
"""
from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path

from arkheionx.cli import exit_codes

from . import models as M
from . import pack as pack_mod

SUCCESS = exit_codes.SUCCESS           # 0
WARNING = exit_codes.RUNTIME_ERROR     # 1 (heuristic warning, not a crash)
FAILED = exit_codes.INVALID_ARGUMENTS  # 2 (cannot complete)


def _resolve_root(repo: str) -> Path | None:
    root = Path(repo).expanduser().resolve()
    return root if root.is_dir() else None


def _rel(path: str, root: Path) -> str:
    try:
        return str(Path(path).resolve().relative_to(root))
    except (ValueError, OSError):
        return path


def triage_command(args: Namespace) -> int:
    repo = getattr(args, "repo", ".") or "."
    root = _resolve_root(repo)
    if root is None:
        print(f"ArkheionX error: input path not found or not a directory: {repo}")
        print("Next: run `arkheionx triage <repo>` with a local repository path you are authorized to review.")
        return FAILED

    out = str(getattr(args, "out", "") or "").strip()
    out_dir = Path(out).expanduser() if out else pack_mod.default_triage_dir(root)
    write = not bool(getattr(args, "no_write", False))
    # dest='rpc'; the endpoint is masked and never called live in this pass.
    rpc_endpoint = str(getattr(args, "rpc", "") or "")

    try:
        result = pack_mod.build_senior_triage_pack(
            root,
            scope_file=str(getattr(args, "scope_file", "") or ""),
            known_path=str(getattr(args, "known", "") or ""),
            audits_path=str(getattr(args, "audits", "") or ""),
            addresses_file=str(getattr(args, "addresses", "") or ""),
            baseline_ref=str(getattr(args, "baseline_ref", "") or ""),
            since_date=str(getattr(args, "since_date", "") or ""),
            rpc_endpoint=rpc_endpoint,
            out_dir=out_dir,
            command="triage",
            write=write,
        )
    except OSError as exc:
        print(f"ArkheionX error: could not build triage pack: {exc}")
        print("Next: check the repository path and the output directory permissions.")
        return FAILED

    triage = result["triage"]
    target = triage["target_decision"]
    exit_code = SUCCESS if target == M.TARGET_TOUCH else WARNING

    if getattr(args, "json", False):
        print(json.dumps(triage, indent=2))
        return exit_code

    counts = result["counts"]
    manifest = result["manifest"]
    top = result["pack"].top_leads()
    lines = [
        "ARKHEIONX TRIAGE (senior research mode — experimental, local-only)",
        "Decides what is worth reviewing before review. Not a finding, not severity. Human review required.",
        "",
        f"Repo    {repo}",
        f"Scope   {'provided' if triage['eligibility']['scope_provided'] else 'none (eligibility unconfirmed)'}",
        f"Target  {target} ({triage['target_confidence']})",
        f"Why     {triage['target_reason']}",
        f"Leads   {counts['leads']} total | pursue {counts['pursue']} | park {counts['park']} | kill {counts['kill']}",
        f"RPC     {triage['rpc_mode']} (no live-chain calls; endpoint masked)",
        "",
        "Top leads",
    ]
    if top:
        for i, lead in enumerate(top, 1):
            lines.append(f"  {i}. [{lead.decision} {lead.research_priority_score}] {lead.title} — {lead.surface}")
    else:
        lines.append("  NO_HIGH_PRIORITY_LEADS")
    if result["pack"].do_not_touch:
        lines += ["", "Do not touch"]
        for item in result["pack"].do_not_touch[:5]:
            lines.append(f"  - {item['title']} ({item['reason']})")
    lines.append("")
    if write:
        rel = _rel(result["out_dir"], root)
        lines.append(f"Wrote {manifest['artifact_count']} files to {rel}")
        for name in manifest["artifact_paths"]:
            lines.append(f"  {name}")
    else:
        lines.append("No-write: built the triage pack in memory only (nothing written).")
    lines += [
        "",
        "Next",
        "  Read 00-target-decision.md, then 06-top-3-leads.md and 07-do-not-touch.md.",
        "  Only after triage, run `arkheionx review` on the surviving lead(s).",
        "",
        "Boundary",
        "  Local/static only. No RPC by default, no live-chain calls, no auto-submit.",
        "  Not a finding, not severity, not a confirmed vulnerability. Human review required.",
    ]
    print("\n".join(lines))
    return exit_code

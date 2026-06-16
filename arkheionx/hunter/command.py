"""CLI handler for `arkheionx hunter` (and `arkheionx triage --hunter`).

Local-first. The optional ``--rpc-url`` endpoint is masked in all output, only
read-only methods are ever issued, no transaction is sent, and the chain is never
mutated. No report is auto-submitted. Human review is required.
"""
from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path

from arkheionx.cli import exit_codes

from . import models as M
from . import pack as pack_mod

SUCCESS = exit_codes.SUCCESS           # 0
WARNING = exit_codes.RUNTIME_ERROR     # 1 (heuristic "nothing to pursue", not a crash)
FAILED = exit_codes.INVALID_ARGUMENTS  # 2 (cannot complete)


def _resolve_root(repo: str) -> Path | None:
    root = Path(repo).expanduser().resolve()
    return root if root.is_dir() else None


def _rel(path: str, root: Path) -> str:
    try:
        return str(Path(path).resolve().relative_to(root))
    except (ValueError, OSError):
        return path


def _read_calls(path: str, key: str):
    if not path:
        return None
    data = json.loads(Path(path).expanduser().read_text(encoding="utf-8"))
    if isinstance(data, dict) and isinstance(data.get(key), list):
        return data[key]
    if isinstance(data, list):
        return data
    raise ValueError(f"expected a list or {{'{key}': [...]}}")


def _read_allowlist(value: str) -> list:
    if not value:
        return []
    p = Path(value).expanduser()
    try:
        if p.is_file():
            return [ln.strip() for ln in p.read_text(encoding="utf-8").splitlines() if ln.strip()]
    except OSError:
        pass
    return [tok.strip() for tok in value.split(",") if tok.strip()]


def hunter_command(args: Namespace) -> int:
    repo = getattr(args, "repo", ".") or "."
    root = _resolve_root(repo)
    if root is None:
        print(f"ArkheionX error: input path not found or not a directory: {repo}")
        print("Next: run `arkheionx hunter <repo>` with a local repository path you are authorized to review.")
        return FAILED

    out = str(getattr(args, "out", "") or "").strip()
    out_dir = Path(out).expanduser() if out else pack_mod.default_hunter_dir(root)
    write = not bool(getattr(args, "no_write", False))
    rpc_endpoint = str(getattr(args, "rpc", "") or "")

    source_mode = str(getattr(args, "source_recovery", "") or "auto")
    if bool(getattr(args, "no_source_recovery", False)):
        source_mode = "none"

    deployment_calls = registry_calls = None
    try:
        deployment_calls = _read_calls(str(getattr(args, "deployment_calls", "") or ""), "calls")
        registry_calls = _read_calls(str(getattr(args, "registry_calls", "") or ""), "registry_calls")
    except (OSError, ValueError) as exc:
        print(f"ArkheionX error: could not read calls JSON: {type(exc).__name__}: {exc}")
        return FAILED

    if (deployment_calls or registry_calls) and not rpc_endpoint:
        print("ArkheionX error: --deployment-calls / --registry-calls require a read-only --rpc-url.")
        return FAILED

    try:
        result = pack_mod.build_hunter_pack(
            root,
            scope_file=str(getattr(args, "scope_file", "") or ""),
            known_path=str(getattr(args, "known", "") or ""),
            audits_path=str(getattr(args, "audits", "") or ""),
            addresses_file=str(getattr(args, "addresses", "") or ""),
            source_dir=str(getattr(args, "source_dir", "") or ""),
            baseline_ref=str(getattr(args, "baseline_ref", "") or ""),
            since_date=str(getattr(args, "since_date", "") or ""),
            audit_date=str(getattr(args, "audit_date", "") or ""),
            fresh_allowlist=_read_allowlist(str(getattr(args, "fresh_allowlist", "") or "")),
            source_recovery_mode=source_mode,
            rpc_endpoint=rpc_endpoint,
            deployment_calls=deployment_calls,
            registry_calls=registry_calls,
            out_dir=out_dir,
            command=("triage --hunter" if getattr(args, "hunter", False) else "hunter"),
            write=write,
            strict_context=bool(getattr(args, "strict_context", False)),
            top=int(getattr(args, "top", 5) or 5),
            max_leads=int(getattr(args, "max_leads", 25) or 25),
        )
    except OSError as exc:
        print(f"ArkheionX error: could not build hunter pack: {exc}")
        return FAILED

    triage = result["triage"]
    counts = result["counts"]
    pursueable = counts.get("pursue_now", 0) + counts.get("needs_poc", 0)
    exit_code = SUCCESS if pursueable else WARNING

    if getattr(args, "json", False):
        print(json.dumps(triage, indent=2))
        return exit_code

    pack = result["pack"]
    manifest = result["manifest"]
    lines = [
        "ARKHEIONX HUNTER (universal senior exploit-hunter mode — local-first, experimental)",
        "Chooses the highest-EV bounty surface before review. Not a finding, not severity. Human review required.",
        "",
        f"Repo            {repo}",
        f"Scope           {pack.program_identity.scope_status} ({pack.program_identity.scope_confidence})",
        f"Source          {pack.source_provenance.overall_status}",
        f"Dedup quality   {pack.dedup_quality.status}",
        f"Deployment      {pack.deployment_reality.status} | mismatches {len(pack.deployment_reality.mismatches)} "
        f"| registry {pack.registry_diff.status}",
        f"Value/State     {len(pack.value_paths)} value paths | "
        f"{sum(1 for s in pack.state_machines if s.touches_value)} value-gating state machines",
        f"Leads           {counts['leads']} | pursue_now {counts['pursue_now']} | needs_poc {counts['needs_poc']} "
        f"| park {counts['park']} | kill {counts['kill']}",
        f"RPC             {triage['rpc_mode']} (read-only only; endpoint masked; no mutation)",
        "",
        "Top leads",
    ]
    top = pack.top_leads(counts.get("top", M.TOP_LEAD_LIMIT))
    if top:
        for i, lead in enumerate(top, 1):
            lines.append(f"  {i}. [{lead.decision} {lead.score}] {lead.title} — {lead.surface or lead.contract} "
                         f"({lead.lead_type})")
    else:
        lines.append("  NO_PURSUEABLE_LEADS")
    if pack.program_identity.scope_warnings:
        lines += ["", "Scope warnings", "  " + ", ".join(pack.program_identity.scope_warnings)]
    lines.append("")
    if write:
        lines.append(f"Wrote {manifest['artifact_count']} files to {_rel(result['out_dir'], root)}")
    else:
        lines.append("No-write: built the hunter pack in memory only (nothing written).")
    lines += [
        "",
        "Next",
        "  Read 00-run-context.md, then 08-top-leads.md, 09-poc-plans.md, 10-submission-risk.md, 11-report-filter.md.",
        "  Only pursue PURSUE_NOW / NEEDS_POC leads. Apply each kill condition aggressively.",
        "",
        "Boundary",
        "  Local-first. Read-only RPC only when provided (masked). No mutation, no auto-submit. Human review required.",
    ]
    print("\n".join(lines))
    return exit_code

"""War-run renderers: scope map (01), console verdict, triage.json, manifest.json."""
from __future__ import annotations

import datetime as dt

from arkheionx.version import PACKAGE_VERSION

MILESTONE = "v10.1.0-dev"
ARTIFACT_TYPE = "godeye_war_run"
MANIFEST_TYPE = "godeye_war_run_manifest"
BRANCH = "private/v10-godeye-war-engine"

SAFETY_FLAGS = {
    "local_only": True,
    "no_rpc_by_default": True,
    "no_live_chain_mutation": True,
    "no_broadcast": True,
    "no_signing_keys": True,
    "no_auto_submit": True,
    "no_report_generated": True,
    "fork_is_plan_only": True,
    "human_review_required": True,
}

SAFETY_BOUNDARIES = (
    "Reconstructs the economic machine, derives invariants, ranks attack paths, and",
    "tells the researcher which are worth proving. Not a finding, not a severity, not",
    "a confirmed vulnerability. No report is generated until an invariant is proven.",
    "Local/static; no RPC by default; fork support is a plan only; secrets are redacted.",
)


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def scope_map_md(scope, smap) -> str:
    lines = [
        "# 01 Scope Map",
        "",
    ]
    if scope.present:
        lines += [
            f"- Program: {scope.name or '(unnamed)'} | Platform: {scope.platform or 'n/a'}",
            f"- Chain: {scope.chain or 'unspecified'}",
            f"- In-scope paths: {', '.join(scope.in_scope_paths) or '(whole tree)'}",
            f"- In-scope contracts: {', '.join(scope.in_scope_contracts) or '(all parsed)'}",
            f"- Out-of-scope: {', '.join(scope.out_of_scope_text) or 'none stated'}",
            f"- Known reports: {', '.join(scope.known_reports) or 'none'}",
            f"- Rules: {', '.join(k for k, v in scope.rules.items() if v) or 'none'}",
        ]
    else:
        lines.append("- No scope file provided; running unscoped (all .sol under target).")
    lines += [
        "",
        f"- Contracts indexed: {len(smap.contracts)} (semantic confidence {smap.confidence})",
        f"- Files indexed: {smap.files_indexed}",
    ]
    if scope.warnings:
        lines += ["", "## Scope warnings"] + [f"- {w}" for w in scope.warnings]
    return "\n".join(lines) + "\n"


def _next_action(c) -> str:
    sev = c.economic_severity or ""
    if sev.startswith("KILL"):
        return "KILL"
    if sev.startswith("PARK"):
        return "PARK"
    if sev in ("NEEDS_FORK_PROOF", "NEEDS_REAL_ASSET_PROOF"):
        return "RUN_FORK_PLAN"
    if sev.startswith("SUBMIT"):
        return "WRITE_POC"
    return "INVESTIGATE"


def console_lines(target, smap, emap, tmap, invset, graph, out_dir, wrote, *,
                  ingest_summary=None, auth_analysis=None, reality_results=None,
                  gates=None) -> list:
    reality_results = reality_results or []
    gates = gates or []
    lines = [
        "Arkheionx V10.1 Reality Engine War Run",
        "",
        f"Target: {target}",
        f"Framework detected: {getattr(ingest_summary, 'framework', 'unknown')}",
        f"Solidity files indexed: {getattr(ingest_summary, 'solidity_files_indexed', smap.files_indexed)}",
        f"Contracts indexed: {getattr(ingest_summary, 'contracts_indexed', len(smap.contracts))}",
        f"Artifact mode: {getattr(ingest_summary, 'artifact_mode', smap.artifact_mode)}",
        f"Excluded dependency files: {getattr(ingest_summary, 'excluded_dependency_files', 0)}",
        f"Auth engine active: {'yes' if getattr(auth_analysis, 'active', False) else 'no'}",
        f"Root-cause memory matches: "
        f"{sum(c.duplicate_risk in ('SAME_ROOT_CAUSE', 'RELATED_BUT_DISTINCT') for c in graph.candidates)}",
        f"Bounty reality blocked candidates: {sum(result.blocked for result in reality_results)}",
        f"Quality gate warnings: {sum(g.status in ('warn', 'fail') for g in gates)}",
        f"Semantic confidence: {smap.confidence.lower()}",
        f"Entities found: {len(emap.entities)}",
        f"State transitions found: {len(tmap.transitions)}",
        f"Invariants generated: {len(invset.invariants)} "
        f"({len(invset.suspicious())} suspicious)",
        f"Attack candidates: {len(graph.candidates)}",
        "",
        "Top candidates:",
    ]
    if getattr(ingest_summary, "contracts_indexed", len(smap.contracts)) == 0:
        lines.insert(
            12,
            "ZERO_CONTRACTS_INDEXED: this war-run did not analyze Solidity contracts. "
            "Check target path, framework detection, or ingestion settings.",
        )
    if graph.candidates:
        for i, c in enumerate(graph.candidates[:5], 1):
            sev = c.economic_severity or "PENDING"
            lines.append(f"  {i}. {c.title} — {sev} / {_next_action(c)}")
    else:
        lines.append("  (no candidates: no invariant looked suspicious on this target)")
    lines += [""]
    if wrote:
        lines.append(f"Artifacts written: {out_dir}")
    else:
        lines.append("No-write: artifacts built in memory only.")
    lines += [
        "",
        "No report generated.",
        "Run PoC skeletons manually. Human review required.",
    ]
    return lines


def triage_json(target, scope, smap, emap, tmap, invset, graph, verdicts, fork_reqs,
                artifact_paths) -> dict:
    return {
        "schema_version": "v10-godeye",
        "artifact_type": ARTIFACT_TYPE,
        "arkheionx_version": PACKAGE_VERSION,
        "milestone": MILESTONE,
        "generated_at": now(),
        "command": "war-run",
        "target": target,
        "scope": scope.to_dict(),
        "semantic": {
            "mode": smap.mode, "confidence": smap.confidence,
            "artifact_mode": smap.artifact_mode,
            "files_indexed": smap.files_indexed, "contracts": len(smap.contracts),
            "call_edges": len(smap.call_edges), "external_calls": len(smap.external_calls),
            "dataflow_hints": len(smap.dataflow_hints),
        },
        "entities": [e.entity_type for e in emap.entities],
        "transitions": [t.to_dict() for t in tmap.transitions],
        "invariants": invset.to_dict(),
        "attack_candidates": [c.to_dict() for c in graph.candidates],
        "economic_severity": [v.to_dict() for v in verdicts],
        "fork_requirements": [r.to_dict() for r in fork_reqs],
        "counts": {
            "entities": len(emap.entities),
            "transitions": len(tmap.transitions),
            "invariants": len(invset.invariants),
            "suspicious_invariants": len(invset.suspicious()),
            "candidates": len(graph.candidates),
            "fork_required": len(fork_reqs),
        },
        "artifact_paths": artifact_paths,
        "safety_flags": dict(SAFETY_FLAGS),
        "safety_boundaries": list(SAFETY_BOUNDARIES),
        "human_review_required": True,
        "report_generated": False,
    }


def manifest_json(target, artifact_paths, counts) -> dict:
    return {
        "schema_version": "v10-godeye",
        "artifact_type": MANIFEST_TYPE,
        "arkheionx_version": PACKAGE_VERSION,
        "milestone": MILESTONE,
        "branch": BRANCH,
        "generated_at": now(),
        "command": "war-run",
        "target": target,
        "artifact_count": len(artifact_paths),
        "artifact_paths": artifact_paths,
        "counts": counts,
        "safety_flags": dict(SAFETY_FLAGS),
        "safety_boundaries": list(SAFETY_BOUNDARIES),
        "human_review_required": True,
        "local_only": True,
        "no_push": True,
        "no_remote_write": True,
        "report_generated": False,
    }

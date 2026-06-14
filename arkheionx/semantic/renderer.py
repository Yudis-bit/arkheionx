"""Renderers for semantic-core artifacts (02/03/04 of the war-run)."""
from __future__ import annotations

from . import models as M


def semantic_map_json(smap: M.SemanticMap) -> dict:
    return smap.to_dict()


def call_graph_json(smap: M.SemanticMap) -> dict:
    return {
        "schema_version": M.SCHEMA_VERSION,
        "artifact_type": "semantic_call_graph",
        "mode": smap.mode,
        "edges": [e.to_dict() for e in smap.call_edges],
        "edge_count": len(smap.call_edges),
    }


def storage_access_json(smap: M.SemanticMap) -> dict:
    return {
        "schema_version": M.SCHEMA_VERSION,
        "artifact_type": "semantic_storage_access_map",
        "mode": smap.mode,
        "accesses": [s.to_dict() for s in smap.storage_accesses],
        "access_count": len(smap.storage_accesses),
    }


def semantic_summary_md(smap: M.SemanticMap) -> str:
    lines = [
        "# 02 Semantic Map (summary)",
        "",
        f"- Mode: `{smap.mode}` (confidence {smap.confidence})",
        f"- Files indexed: {smap.files_indexed}",
        f"- Contracts: {len(smap.contracts)}",
        f"- Call edges: {len(smap.call_edges)}",
        f"- External calls: {len(smap.external_calls)}",
        f"- Storage accesses: {len(smap.storage_accesses)}",
        f"- Data-flow hints: {len(smap.dataflow_hints)}",
        "",
        "_Fallback semantic extraction. Every fact is heuristic and carries a",
        "confidence; this is review context, not a finding._",
        "",
        "## Contracts",
    ]
    for c in smap.contracts:
        inh = f" is {', '.join(c.inheritance)}" if c.inheritance else ""
        lines.append(f"- **{c.name}** ({c.kind}){inh} — {len(c.functions)} fns, "
                     f"{len(c.state_variables)} state vars [{c.file}]")
    flagged = [h for h in smap.dataflow_hints if h.tag]
    if flagged:
        lines += ["", "## Notable data-flow hints"]
        for h in flagged:
            lines.append(f"- `{h.function}`: {h.source_expr} -> {h.sink_expr} "
                         f"[{h.tag}] ({h.confidence})")
    if smap.warnings:
        lines += ["", "## Warnings"]
        lines += [f"- {w}" for w in smap.warnings]
    return "\n".join(lines) + "\n"

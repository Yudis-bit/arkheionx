"""Assemble a complete local lens pack (v7.5).

Writes the numbered human-readable Markdown files (00-run-context .. 13-report-filter),
a model-agnostic ``agent-input.md``, and a single machine-readable ``lens-pack.json``
that embeds all structured data for an AI agent. Everything is local/static and
vendor-agnostic. The pack never claims a vulnerability or a severity. Human review
is required.
"""
from __future__ import annotations

from pathlib import Path

from arkheionx.review_map.model import ReviewMap

from . import models as m
from . import render
from . import safety
from .base import ProtocolLens
from .blindspots import build_blind_spots
from .evidence_judge import judge_evidence
from .evidence_map import build_evidence_map
from .extractor import build_lens_context
from .json_output import _json, _write, default_lens_pack_dir
from .lane_builder import build_lens_map, build_review_lanes
from .leak_check import output_path_warning
from .report_filter import build_report_filter
from .task_builder import build_scope_tasks

PACK_FILES = (
    "00-run-context.md", "01-scope-map.md", "02-protocol-model.md", "03-value-flow-map.md",
    "04-behavior-promises.md", "05-economic-invariants.md", "06-temporal-windows.md",
    "07-periphery-bundle-map.md", "08-evidence-map.md", "09-review-lanes.md",
    "10-scope-tasks.md", "11-blindspot-ranking.md", "12-evidence-rubric.md",
    "13-report-filter.md", "agent-input.md", "lens-pack.json",
)


def build_lens_pack(lens: ProtocolLens, rm: ReviewMap, root: Path | str,
                    scope_file: str | None = None, out_dir: Path | str | None = None, *,
                    source_files: int = 0, test_files: int = 0, write: bool = True) -> dict:
    root = Path(root)
    out = Path(out_dir).expanduser() if out_dir else default_lens_pack_dir(root)
    # Lens packs are namespaced by lens id so multiple lenses can coexist.
    out = out / lens.lens_id

    ctx = build_lens_context(lens, rm, root, scope_file, source_files=source_files, test_files=test_files)
    lens_map = build_lens_map(ctx)
    lanes = build_review_lanes(ctx)
    tasks = build_scope_tasks(ctx)
    evidence = build_evidence_map(ctx, root)
    blind = build_blind_spots(ctx, root, evidence_data=evidence)
    judge = judge_evidence(ctx, root, tasks_data=tasks)
    report = build_report_filter(ctx, root, judge_data=judge)

    contents: dict[str, str] = {
        "00-run-context.md": render.render_run_context_md(lens_map),
        "01-scope-map.md": render.render_scope_map_md(lens_map),
        "02-protocol-model.md": render.render_protocol_model_md(lens_map.get("protocol_model", {})),
        "03-value-flow-map.md": render.render_value_flow_md(lens_map.get("value_flow_paths", [])),
        "04-behavior-promises.md": render.render_behavior_promises_md(lens_map.get("behavior_promises", [])),
        "05-economic-invariants.md": render.render_economic_invariants_md(lens_map.get("economic_invariants", [])),
        "06-temporal-windows.md": render.render_temporal_windows_md(lens_map.get("temporal_windows", [])),
        "07-periphery-bundle-map.md": render.render_periphery_bundle_map_md(lens_map.get("protocol_model", {})),
        "08-evidence-map.md": render.render_evidence_map_md(evidence),
        "09-review-lanes.md": render.render_review_lanes_md(lanes),
        "10-scope-tasks.md": render.render_scope_tasks_md(tasks),
        "11-blindspot-ranking.md": render.render_blindspot_ranking_md(blind),
        "12-evidence-rubric.md": render.render_evidence_rubric_md(judge),
        "13-report-filter.md": render.render_report_filter_md(report),
        "agent-input.md": render.render_agent_input_md(lens_map),
    }

    manifest = {
        "schema_version": m.SCHEMA_VERSION,
        "lens_layer": m.LENS_LAYER,
        "arkheionx_version": lens_map.get("arkheionx_version", ""),
        "kind": m.KIND_LENS_PACK_MANIFEST,
        "command": "lens-pack",
        "lens": lens.meta().to_dict(),
        "generated_at": ctx["generated_at"],
        "scope_file_used": lens_map.get("scope_file_used", False),
        "scope_status": lens_map.get("scope_status", ""),
        "generated_artifacts": list(PACK_FILES),
        "counts": {
            "behavior_promises": len(lens_map.get("behavior_promises", [])),
            "economic_invariants": len(lens_map.get("economic_invariants", [])),
            "review_lanes": lanes.get("lane_count", 0),
            "scope_tasks": tasks.get("task_count", 0),
            "blind_spots": blind.get("candidate_count", 0),
            "evidence_items": evidence.get("summary", {}).get("invariants", 0),
            "report_candidates": report.get("candidate_count", 0),
            "terms_discovered": len(lens_map.get("protocol_model", {}).get("discovered_terms", [])),
            "terms_unknown": len(lens_map.get("protocol_model", {}).get("unknown_terms", [])),
        },
        "data": {
            "lens_map": lens_map,
            "review_lanes": lanes,
            "scope_tasks": tasks,
            "evidence_map": evidence,
            "blind_spots": blind,
            "evidence_judge": judge,
            "report_filter": report,
        },
        "safety_flags": safety.safety_flags(),
        "safety": safety.safety_block(),
        "human_review_required": True,
        "safety_boundary": safety.SAFETY_BOUNDARY,
    }

    warning = output_path_warning(root, out, scope_file)

    written: dict[str, str] = {}
    if write:
        for name, text in contents.items():
            written[name] = _write(out / name, text)
        written["lens-pack.json"] = _write(out / "lens-pack.json", _json(manifest))

    return {
        "manifest": manifest,
        "out_dir": str(out),
        "artifacts": written,
        "leak_warning": warning,
        "lens_map": lens_map,
        "lanes": lanes,
        "tasks": tasks,
        "evidence": evidence,
        "blind_spots": blind,
        "judge": judge,
        "report": report,
    }

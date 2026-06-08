"""Evidence Graph builder (v6).

Builds a deterministic, JSON-ready evidence graph from a review map and the
v4.1 research surfaces: one classified :class:`EvidenceNode` per reviewable
surface, an evidence-state summary, the high-impact unresolved surfaces, the
aggregate evidence gaps, and a human review checklist.

Everything is heuristic and local/static. An evidence state is not a
vulnerability claim. Human review is required.
"""
from __future__ import annotations

import json
from pathlib import Path

from arkheionx.blind_spots.counterfactuals import build_counterfactuals
from arkheionx.blind_spots.models import SurfaceRecord
from arkheionx.blind_spots.signals import build_surface_records
from arkheionx.core.safety import LOCAL_ONLY_DISCLAIMER
from arkheionx.research.surfaces import ResearchSurfaces, build_research_surfaces
from arkheionx.review_map.model import ReviewMap

from . import classifier, models as m


def _safety() -> dict:
    return {
        "disclaimer": LOCAL_ONLY_DISCLAIMER,
        "boundary": list(m.BOUNDARY_LINES),
        "do_not_claim": list(m.DO_NOT_CLAIM),
        "human_review_required": True,
    }


def _split_source(source: str) -> tuple[str, int]:
    if not source:
        return "", 0
    path, sep, line = source.rpartition(":")
    if sep and line.isdigit():
        return path, int(line)
    return source, 0


def load_research_memory(path: Path) -> dict[str, str]:
    """Read a local hypotheses.json log and map target -> recorded status.

    Only statuses that are explicitly recorded by a human alongside a local test
    are honored (``rejected``/``confirmed``/``needs-human-review``/``testing``).
    Returns an empty mapping when no log is present. This is the only path to the
    ``rejected-with-evidence`` and ``confirmed-candidate`` states.
    """
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    entries = payload.get("hypotheses") if isinstance(payload, dict) else None
    if not isinstance(entries, list):
        return {}
    memory: dict[str, str] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        target = entry.get("target") or entry.get("surface") or ""
        status = (entry.get("status") or "").strip().lower()
        recorded = entry.get("test_command") or entry.get("result") or entry.get("evidence")
        if not target or status not in ("rejected", "confirmed", "needs-human-review", "testing"):
            continue
        # rejected/confirmed require recorded local evidence; never inferred.
        if status in ("rejected", "confirmed") and not recorded:
            continue
        memory.setdefault(target, status)
    return memory


def _repo_summary(rm: ReviewMap, surfaces: ResearchSurfaces, nodes: list[m.EvidenceNode],
                  source_files: int, test_files: int) -> dict:
    s = rm.summary
    high_impact = sum(1 for n in nodes if n.criticality_potential in (m.CRIT_VERY_HIGH, m.CRIT_HIGH))
    unresolved = sum(1 for n in nodes if n.evidence_state in m.OPEN_STATES)
    return {
        "repo_path": rm.repo_path,
        "mode": rm.mode,
        "protocol_types": list(s.protocol_types),
        "contracts": s.contracts_analyzed,
        "functions": s.functions_mapped,
        "source_files": source_files,
        "test_files": test_files,
        "value_paths": s.value_paths,
        "assumptions": s.assumptions,
        "test_gaps": s.test_gaps,
        "blind_spot_candidates": _blind_spot_candidate_count(nodes),
        "counterfactuals": 0,  # filled by caller after counterfactuals built
        "authorization_surfaces": len(surfaces.authorization_surfaces),
        "periphery_surfaces": len(surfaces.periphery_surfaces),
        "behavior_mismatch_surfaces": len(surfaces.behavior_mismatch_surfaces),
        "high_impact_surfaces": high_impact,
        "evidence_nodes": len(nodes),
        "unresolved_surfaces": unresolved,
    }


def _blind_spot_candidate_count(nodes: list[m.EvidenceNode]) -> int:
    return sum(1 for n in nodes
               if n.evidence_state in m.OPEN_STATES
               and n.criticality_potential in (m.CRIT_VERY_HIGH, m.CRIT_HIGH, m.CRIT_MEDIUM))


def _detect_invariant_fuzz(test_references: list[str]) -> tuple[bool, bool]:
    blob = " ".join(test_references).lower()
    return ("invariant" in blob), ("fuzz" in blob)


def _build_node(record: SurfaceRecord, idx: int, *, fs_by_id: dict,
                cf_by_target: dict[str, list[str]], proof_by_target: dict[str, list[str]],
                memory: dict[str, str]) -> m.EvidenceNode:
    stype = classifier.surface_type(record)
    strength = classifier.evidence_strength(record)
    state, why_state, unresolved_reason = classifier.classify_state(
        record, strength, memory_status=memory.get(record.target))
    src_file, src_line = _split_source(record.source)
    fs = fs_by_id.get(record.target)
    test_refs = list(fs.test_references) if fs else []
    invariants, fuzz = _detect_invariant_fuzz(test_refs)
    hypothesis_links: list[str] = []
    if memory.get(record.target):
        hypothesis_links.append(f"local-hypothesis:{record.target}")
    return m.EvidenceNode(
        node_id=f"EV-{idx:03d}",
        surface_id=record.target,
        surface_name=f"{stype} surface",
        contract=record.contract,
        function=record.function,
        source_file=src_file,
        source_line=src_line,
        surface_type=stype,
        criticality_potential=record.criticality_potential,
        review_density=record.review_density,
        blind_spot_priority=record.blind_spot_priority,
        assumptions=list(record.assumptions),
        counterfactuals=cf_by_target.get(record.target, []),
        tests_detected=record.test_reference_count,
        invariants_detected=invariants,
        fuzz_detected=fuzz,
        proof_plan_links=proof_by_target.get(record.target, []),
        hypothesis_links=hypothesis_links,
        evidence_state=state,
        evidence_strength=strength,
        confidence=classifier.confidence_label(strength),
        why_state=why_state,
        unresolved_reason=unresolved_reason if state in m.OPEN_STATES else "",
        missing_evidence=classifier.missing_evidence(record, strength, stype),
        next_test_direction=record.suggested_local_test,
        human_review_required=True,
    )


def _state_summary(nodes: list[m.EvidenceNode]) -> dict:
    counts = {state: 0 for state in m.EVIDENCE_STATE_ORDER}
    for n in nodes:
        counts[n.evidence_state] = counts.get(n.evidence_state, 0) + 1
    return {state: counts[state] for state in m.EVIDENCE_STATE_ORDER}


def _high_impact_unresolved(nodes: list[m.EvidenceNode]) -> list[dict]:
    out = []
    for n in nodes:
        if n.criticality_potential in (m.CRIT_VERY_HIGH, m.CRIT_HIGH) and n.evidence_state in m.OPEN_STATES:
            out.append({
                "node_id": n.node_id,
                "surface_id": n.surface_id,
                "source": f"{n.source_file}:{n.source_line}" if n.source_line else n.source_file,
                "surface_type": n.surface_type,
                "criticality_potential": n.criticality_potential,
                "evidence_state": n.evidence_state,
                "evidence_strength": n.evidence_strength,
                "unresolved_reason": n.unresolved_reason,
                "missing_evidence": n.missing_evidence,
                "next_test_direction": n.next_test_direction,
                "human_review_required": True,
            })
    return out


def _evidence_gaps(nodes: list[m.EvidenceNode]) -> list[dict]:
    by_gap: dict[str, list[str]] = {}
    for n in nodes:
        for gap in n.missing_evidence:
            by_gap.setdefault(gap, []).append(n.surface_id)
    rows = []
    for gap in m.GAP_TYPES:
        if gap in by_gap:
            surfaces = sorted(set(by_gap[gap]))
            rows.append({"gap": gap, "count": len(surfaces), "example_surfaces": surfaces[:8]})
    return rows


def build_human_review_checklist() -> list[str]:
    return [
        "Review every high-impact unresolved surface before ending the review.",
        "Check whether each test actually reaches the target function (not just the contract).",
        "Check whether every value movement has a pre/post balance assertion.",
        "Check whether authorization paths include negative (must-revert) tests.",
        "Check whether periphery paths produce the same accounting as the equivalent direct call.",
        "Check whether callback / external-call ordering is covered by a test.",
        "Confirm oracle-dependent paths reject stale, zero, and extreme inputs.",
        "Do not submit evidence-graph output as a finding. Human review required.",
    ]


def build_evidence_graph(rm: ReviewMap, surfaces: ResearchSurfaces, *,
                         source_files: int = 0, test_files: int = 0,
                         memory: dict[str, str] | None = None,
                         package_version: str = "") -> dict:
    memory = memory or {}
    records = build_surface_records(rm, surfaces)
    counterfactuals = build_counterfactuals(rm, surfaces, records)
    cf_by_target: dict[str, list[str]] = {}
    for cf in counterfactuals:
        cf_by_target.setdefault(cf["target"], []).append(cf["id"])
    proof_by_target: dict[str, list[str]] = {}
    for ps in rm.proof_suggestions:
        if ps.target:
            proof_by_target.setdefault(ps.target, []).append(ps.id)
    fs_by_id = {f.display_id: f for f in rm.functions}

    nodes = [
        _build_node(r, i, fs_by_id=fs_by_id, cf_by_target=cf_by_target,
                    proof_by_target=proof_by_target, memory=memory)
        for i, r in enumerate(records, 1)
    ]

    repo = _repo_summary(rm, surfaces, nodes, source_files, test_files)
    repo["counterfactuals"] = len(counterfactuals)

    return {
        "schema_version": m.SCHEMA_VERSION,
        "package_version": package_version,
        "command": "evidence-graph",
        "kind": m.KIND_EVIDENCE_GRAPH,
        "generated_at": rm.generated_at,
        "repo_path": rm.repo_path,
        "mode": rm.mode,
        "repo_summary": repo,
        "evidence_state_summary": _state_summary(nodes),
        "evidence_strength_legend": {
            "strong": "Direct evidence addresses the relevant counterfactual or assumption.",
            "medium": "Evidence touches the surface but may not cover all important edges.",
            "weak": "Evidence exists but is indirect, shallow, or not focused.",
            "none": "No meaningful local evidence was found.",
            "unknown": "Could not classify evidence quality.",
        },
        "nodes": [n.to_dict() for n in nodes],
        "unresolved_surfaces": _high_impact_unresolved(nodes),
        "evidence_gaps": _evidence_gaps(nodes),
        "human_review_checklist": build_human_review_checklist(),
        "safety": _safety(),
        "human_review_required": True,
    }


def build_evidence_graph_from_review_map(rm: ReviewMap, root, *,
                                         source_files: int = 0, test_files: int = 0,
                                         memory: dict[str, str] | None = None,
                                         package_version: str = "") -> dict:
    surfaces = build_research_surfaces(rm, root)
    return build_evidence_graph(rm, surfaces, source_files=source_files, test_files=test_files,
                                memory=memory, package_version=package_version)

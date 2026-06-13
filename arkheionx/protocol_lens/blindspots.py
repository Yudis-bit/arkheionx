"""Rank lens blind-spot candidates (section 13): top-10 places to look.

A blind spot is a high-importance surface with weak local evidence. Each candidate
is built from a review lane and the lane's weakest-evidence invariant, scored with
:mod:`arkheionx.protocol_lens.scoring`. Output is "blind spot", never "confirmed
bug". Human review is required.
"""
from __future__ import annotations

import re
from pathlib import Path

from . import models as m
from . import scoring
from .common import bind_lane
from .evidence_map import build_evidence_map

_WEAKNESS_RATIONALE = {
    m.EV_UNKNOWN: "Evidence is unknown; the invariant is not clearly tested locally.",
    m.EV_UNTESTED: "No local test targets this invariant's functions or state.",
    m.EV_COMMENT_ONLY: "The invariant is mentioned only in comments, which is not evidence.",
    m.EV_HAPPY_PATH_ONLY: "Only a positive path is asserted; the breaking case is untested.",
    m.EV_INDIRECTLY_TESTED: "The functions are touched without a direct assertion on this invariant.",
    m.EV_FUZZED_BUT_NOT_TARGETED: "Fuzzing touches the symbols but does not explicitly target this property.",
    m.EV_DIRECTLY_TESTED_WEAK: "A test exercises the path but is not confirmed to target this invariant.",
    m.EV_DIRECTLY_TESTED_STRONG: "A test appears to target this invariant; revisit only for edge cases.",
    m.EV_FORMALLY_PROVEN: "A formal rule targets this property; revisit only outside its assumptions.",
}


def _camel(slug: str) -> str:
    return "".join(p.capitalize() for p in re.split(r"[^a-z0-9]+", slug) if p)


def _status_by_invariant(evidence_data: dict) -> dict[str, str]:
    return {it["invariant_id"]: it["status"] for it in evidence_data.get("items", [])}


def build_blind_spots(ctx: dict, root: Path | str, evidence_data: dict | None = None, limit: int = 10) -> dict:
    from .common import common_header  # local import to avoid cycle at module load
    from . import safety

    lens = ctx["lens"]
    if evidence_data is None:
        evidence_data = build_evidence_map(ctx, root)
    status_by_inv = _status_by_invariant(evidence_data)
    inv_by_id = lens.invariant_by_id()

    candidates: list[m.BlindSpotCandidate] = []
    for ld in lens.review_lanes():
        b = bind_lane(ctx, ld)
        matched = b["matched_records"]
        # Pick the lane's weakest-evidence invariant.
        weakest_id, weakest_status, weakest_w = "", m.EV_UNKNOWN, -1
        for iid in (ld.invariants_at_risk or ()):
            st = status_by_inv.get(iid, m.EV_UNKNOWN)
            w = scoring.evidence_weakness(st)
            if w > weakest_w:
                weakest_id, weakest_status, weakest_w = iid, st, w
        cross_count = len({t for r in matched for t in r.cross_contract_targets})
        value_out = any("value" in s.lower() for r in matched for s in r.risk_signals)
        dims = scoring.score_dimensions(
            lane_id=ld.lane_id,
            priority=ld.default_priority,
            status=weakest_status,
            matched_count=len(matched),
            cross_count=cross_count,
            value_out=value_out,
        )
        total = scoring.blind_spot_score(dims)
        inv = inv_by_id.get(weakest_id)
        camel = _camel(ld.slug)
        cand = m.BlindSpotCandidate(
            title=f"{ld.title} — {weakest_id or 'invariant'} weakly evidenced",
            why_blind_spot=f"{ld.why_this_lane_matters} {_WEAKNESS_RATIONALE.get(weakest_status, '')}".strip(),
            source_files=b["source_files"],
            functions=b["functions"],
            state_variables=b["state_variables"],
            invariant_at_risk=f"{weakest_id}: {inv.statement}" if inv else (weakest_id or m.UNKNOWN_IN_LOCAL_REPO),
            existing_evidence=weakest_status,
            why_evidence_insufficient=_WEAKNESS_RATIONALE.get(weakest_status, "Evidence is insufficient."),
            impact_if_broken=(inv.impact_if_broken if inv else m.UNKNOWN_IN_LOCAL_REPO),
            duplicate_risk=(f"Duplicate-risk dimension {dims['duplicate_risk']}/5; compare to known families "
                            "and a patched-behavior model (INV-MM-12) before treating as novel."),
            poc_objective=ld.stop_condition,
            suggested_test_file=f"test/lens/{camel}.t.sol",
            suggested_test_name=f"test_blindspot_{ld.slug.replace('-', '_')}",
            expected_failure_condition=(
                f"A local test shows {weakest_id or 'the invariant'} can break with realistic actors and in-scope contracts."),
            scores=dims,
            blind_spot_score=total,
        )
        candidates.append(cand)

    candidates.sort(key=lambda c: (-c.blind_spot_score, c.title))
    top = candidates[:limit]

    data = common_header(m.KIND_LENS_EVIDENCE, "lens-blindspots", ctx)
    data["kind"] = "lens-blindspots"
    data.update({
        "candidate_count": len(top),
        "formula": "Importance * Evidence weakness * Cross-surface complexity * Exploitability plausibility * Potential severity - Duplicate risk",
        "blind_spots": [c.to_dict() for c in top],
        "note": "These are blind spots (places to look), not confirmed bugs. Human review is required.",
        "safety": safety.safety_block(),
    })
    return data

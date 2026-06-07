"""Surface-signal aggregation for the v5 Blind Spot Intelligence layer.

Builds one :class:`~arkheionx.blind_spots.models.SurfaceRecord` per reviewable
surface by joining the review map and the v4.1 research-surface engine. No source
file is re-scanned here: every signal is derived from data the review map and
``build_research_surfaces`` already produced, so v5 stays consistent with v4.1.
"""
from __future__ import annotations

from arkheionx.review_map.model import ReviewMap
from arkheionx.research.surfaces import ResearchSurfaces

from . import models as m
from . import scoring


def _assumptions_by_target(rm: ReviewMap) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for asm in rm.assumptions:
        if asm.status == "verified":
            continue
        for target in asm.used_by:
            out.setdefault(target, []).append(asm.id)
    for target in out:
        out[target] = sorted(set(out[target]))
    return out


def _behavior_by_target(surfaces: ResearchSurfaces) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for row in surfaces.behavior_mismatch_surfaces:
        target = row.get("target", "")
        signal = row.get("signal", "")
        if target and signal:
            out.setdefault(target, []).append(signal)
    for target in out:
        out[target] = sorted(set(out[target]))
    return out


def _cross_contract_by_target(surfaces: ResearchSurfaces) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for row in surfaces.periphery_surfaces:
        target = row.get("target", "")
        cores = row.get("core_targets", []) or []
        if target and cores:
            out.setdefault(target, []).extend(cores)
    for target in out:
        out[target] = sorted(set(out[target]))
    return out


def build_surface_records(rm: ReviewMap, surfaces: ResearchSurfaces) -> list[m.SurfaceRecord]:
    """Build a scored SurfaceRecord for every surface in the coverage ranking.

    The coverage ranking is the canonical value-relevant surface set (it already
    drops pure low-priority views with no value/auth/periphery relevance).
    """
    fs_by_id = {f.display_id: f for f in rm.functions}
    assumptions_by_target = _assumptions_by_target(rm)
    behavior_by_target = _behavior_by_target(surfaces)
    cross_by_target = _cross_contract_by_target(surfaces)

    records: list[m.SurfaceRecord] = []
    for row in surfaces.coverage_ranking:
        target = row["surface"]
        fs = fs_by_id.get(target)
        contract, _, function = target.partition(".")
        auth_kinds = sorted(surfaces.auth_by_function.get(target, set()))
        periphery = sorted(surfaces.periphery_by_function.get(target, set()))
        record = m.SurfaceRecord(
            target=target,
            contract=fs.contract if fs else contract,
            function=fs.name if fs else function,
            source=row.get("source", ""),
            review_priority=row.get("review_priority", "low"),
            coverage_signal=row.get("coverage_signal", "unknown"),
            risk_signals=list(row.get("risk_signals", [])),
            auth_kinds=auth_kinds,
            periphery_interactions=periphery,
            behavior_signals=behavior_by_target.get(target, []),
            cross_contract_targets=cross_by_target.get(target, []),
            assumptions=assumptions_by_target.get(target, []),
            test_reference_count=len(fs.test_references) if fs else 0,
        )
        scoring.score_surface(record)
        _annotate(record)
        records.append(record)

    # Deterministic order: blind spot score desc, then priority, then target.
    records.sort(key=lambda r: (-r.blind_spot_score, m.blind_spot_rank(r.blind_spot_priority), r.target))
    return records


# --------------------------------------------------------------------------
# Narrative annotations (why skipped / why it matters / guidance)
# --------------------------------------------------------------------------
def _annotate(record: m.SurfaceRecord) -> None:
    record.why_it_may_be_skipped = _why_skipped(record)
    record.why_it_may_matter = _why_matters(record)
    record.suggested_local_test = _suggested_test(record)
    record.evidence_needed = (
        "A local Foundry test that exercises this surface and asserts the "
        "guarding invariant holds (or records exactly how it fails)."
    )


def _why_skipped(record: m.SurfaceRecord) -> str:
    bits: list[str] = []
    if record.review_density in (m.DENSITY_NONE, m.DENSITY_UNKNOWN):
        bits.append("no direct local test was observed")
    elif record.review_density == m.DENSITY_WEAK:
        bits.append("only partial local test evidence was observed")
    if record.periphery_interactions:
        bits.append("it sits behind a periphery route that is easy to treat as a thin wrapper")
    if record.auth_kinds:
        bits.append("authorization code is easy to assume correct without negative tests")
    if "try-catch" in record.periphery_interactions or "try-catch" in record.behavior_signals:
        bits.append("partial-failure handling is easy to read past")
    if not bits:
        bits.append("it is value-relevant but easy to deprioritize against louder surfaces")
    return "; ".join(bits) + "."


def _why_matters(record: m.SurfaceRecord) -> str:
    if record.impact_dimensions:
        dims = ", ".join(d["dimension"] for d in record.impact_dimensions[:3])
        return (
            f"If a bug existed here the blast radius is heuristically {record.criticality_potential} "
            f"({dims}). This is criticality potential, not severity."
        )
    return "Value-relevant surface; criticality potential is heuristic, not severity."


def _suggested_test(record: m.SurfaceRecord) -> str:
    name = record.function.lower()
    auth = set(record.auth_kinds)
    if auth & {"signature", "domain", "replay"}:
        return ("Assert a signature/authorization for one action cannot authorize a different "
                "action, signer, nonce, deadline, chain, or verifying contract.")
    if "merkle" in record.auth_kinds:
        return ("Assert a proof for one leaf, a different root, and a malformed-length proof are "
                "all rejected, and that the leaf binds every value-relevant field.")
    if record.periphery_interactions:
        return ("Assert the periphery path produces the same core accounting as the equivalent "
                "direct call, including the partial-failure / skip path.")
    if "value exit" in record.risk_signals or "value-out" in record.risk_signals:
        return ("Round-trip the value path (entry then exit) and assert accounting is conserved "
                "for first, last, and dust amounts.")
    if any(k in name for k in ("borrow", "liquidate", "health", "collateral")):
        return ("Assert the liquidation / health boundary behaves as documented at the exact "
                "just-healthy vs just-unhealthy boundary.")
    if "oracle" in " ".join(record.risk_signals):
        return ("Drive a stale, zero, and extreme price through this surface and assert it is "
                "rejected or bounded before it reaches accounting.")
    return ("Exercise this surface with edge inputs and assert the guarding invariant holds.")

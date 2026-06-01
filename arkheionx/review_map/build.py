"""Build a Protocol Review Map from a local repository (static, heuristic)."""
from __future__ import annotations

import datetime as dt
from pathlib import Path

from arkheionx.core.safety import LOCAL_ONLY_DISCLAIMER
from arkheionx.protocol.detector import Analysis, analyze

from . import assumptions as _assumptions
from . import detect, proof_plan
from . import tests as _tests
from .evidence_links import generate_evidence_links
from .model import (
    COMPILER_CONFIRMED,
    HEURISTIC,
    HIGH,
    LOW,
    MEDIUM,
    Assumption,
    ContractSurface,
    EvidenceLink,
    FunctionSurface,
    ProofSuggestion,
    ReviewerNote,
    ReviewMap,
    ReviewMapSummary,
    SafetyInfo,
    TestGap,
    ValuePath,
    priority_rank,
)

SAFETY_BOUNDARIES = [
    "Local/static repository analysis only.",
    "No RPC, no live-chain calls, no deployed-contract scanning.",
    "No private keys, seed phrases, or secrets.",
    "No exploit automation and no transaction broadcasting.",
    "Review guidance only — not confirmed vulnerabilities, severity, or audit.",
]

_CONDITION_BY_SIGNAL = {
    "value-out": "caller entitlement / balance check",
    "oracle-dependent": "fresh, in-range price check",
    "external-call": "reentrancy guard / checks-effects-interactions ordering",
    "debt-or-liquidation": "health-factor / solvency check",
    "privileged": "access-control guard",
}


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def _conditions(fs: FunctionSurface) -> list[str]:
    return [text for sig, text in _CONDITION_BY_SIGNAL.items() if sig in fs.risk_signals]


def _value_paths(contract: str, surfaces: list[FunctionSurface], assumptions: list[Assumption]) -> list[ValuePath]:
    value_out = [fs for fs in surfaces if fs.value_direction in ("out", "both")]
    value_in = [fs for fs in surfaces if fs.value_direction in ("in", "both")]
    movement = sorted({fs.name for fs in surfaces if set(fs.value_keywords) & set(detect.MOVEMENT_KEYWORDS)})
    entry = value_in[0].name if value_in else "external caller"

    def _asm_for(name: str) -> list[str]:
        target = f"{contract}.{name}"
        return [a.id for a in assumptions if target in a.used_by]

    paths: list[ValuePath] = []
    if value_out:
        for fs in value_out:
            paths.append(ValuePath(
                id=f"vp-{_slug(contract)}-{_slug(fs.name)}",
                label=f"{contract}: {entry} -> {fs.name}",
                entry_function=f"{contract}.{entry}" if value_in else entry,
                movement=movement,
                exit_function=fs.display_id,
                assets=fs.value_keywords,
                conditions=_conditions(fs),
                assumptions=sorted(set(_asm_for(fs.name) + (_asm_for(entry) if value_in else []))),
                test_coverage_hint="referenced" if fs.test_references else "none",
                evidence_level=HEURISTIC,
                review_priority=fs.review_priority,
            ))
    elif value_in:
        fs = value_in[0]
        paths.append(ValuePath(
            id=f"vp-{_slug(contract)}-{_slug(fs.name)}",
            label=f"{contract}: {fs.name} (value-in)",
            entry_function=fs.display_id,
            movement=movement,
            exit_function="",
            assets=fs.value_keywords,
            conditions=_conditions(fs),
            assumptions=_asm_for(fs.name),
            test_coverage_hint="referenced" if fs.test_references else "none",
            evidence_level=HEURISTIC,
            review_priority=fs.review_priority,
        ))
    return paths


def _reviewer_notes(surfaces: list[FunctionSurface], top: int) -> list[ReviewerNote]:
    ranked = sorted(
        (fs for fs in surfaces
         if fs.review_priority in (HIGH, MEDIUM) and fs.visibility in ("external", "public", "unspecified")),
        key=lambda fs: (priority_rank(fs.review_priority), fs.value_direction != "out", fs.display_id),
    )
    notes: list[ReviewerNote] = []
    for i, fs in enumerate(ranked[:top], 1):
        why = ", ".join(fs.risk_signals) or "value-relevant surface"
        notes.append(ReviewerNote(
            id=f"note-{i}",
            title=fs.display_id,
            body=f"{why}. Value direction: {fs.value_direction}.",
            next_step=f"arkheionx prove . --target {fs.display_id} --run",
            priority=fs.review_priority,
        ))
    return notes


def _summary_text(types: list[str], surfaces: list[FunctionSurface], paths: list[ValuePath], gaps: list[TestGap]) -> str:
    high = sum(1 for fs in surfaces if fs.review_priority == HIGH)
    return (
        f"{'/'.join(types)} surface: {len(surfaces)} functions mapped, {high} high-priority. "
        f"{len(paths)} value path(s), {len(gaps)} test gap(s). Review guidance only."
    )


def _slug(text: str) -> str:
    import re
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def build_review_map(
    root: Path,
    *,
    top: int = 10,
    target: str = "",
    include_low_confidence: bool = False,
    analysis: Analysis | None = None,
) -> ReviewMap:
    """Build a ReviewMap for ``root``. Raises ValueError for an unknown target."""

    analysis = analysis or analyze(root, use_foundry=False, top=top)
    by_contract: dict[str, list] = {}
    for fr in analysis.functions:
        by_contract.setdefault(fr.contract_name, []).append(fr)

    surfaces: list[FunctionSurface] = []
    surfaces_by_contract: dict[str, list[FunctionSurface]] = {}
    for cname, frs in by_contract.items():
        cs = [detect.build_function_surface(fr) for fr in frs]
        surfaces_by_contract[cname] = cs
        surfaces.extend(cs)

    contracts: list[ContractSurface] = []
    roles_by_contract = {cr.contract_name: ([cr.role] if cr.role else []) for cr in analysis.contracts}
    assets_by_contract = {cr.contract_name: cr.value_state_vars for cr in analysis.contracts}
    for cr in analysis.contracts:
        frs = by_contract.get(cr.contract_name, [])
        cs = surfaces_by_contract.get(cr.contract_name, [])
        contracts.append(detect.build_contract_surface(
            cr.contract_name, cr.file_path, cr.source_kind or "contract",
            roles_by_contract.get(cr.contract_name, []), assets_by_contract.get(cr.contract_name, []), frs, cs,
        ))

    assumptions = _assumptions.generate_assumptions(surfaces)
    blobs = _tests.load_test_blobs(root)
    gaps = _tests.generate_test_gaps(surfaces, blobs)
    if not include_low_confidence:
        gaps = [g for g in gaps if g.confidence != LOW]
    value_paths: list[ValuePath] = []
    for cname in sorted(surfaces_by_contract):
        value_paths.extend(_value_paths(cname, surfaces_by_contract[cname], assumptions))
    proof_suggestions = proof_plan.generate_proof_suggestions(surfaces, gaps, assumptions)
    evidence_links = generate_evidence_links(root)
    _link_missing_tests(assumptions, gaps)

    if target:
        (surfaces, contracts, value_paths, assumptions, gaps, proof_suggestions, evidence_links) = _filter_target(
            target, surfaces, contracts, value_paths, assumptions, gaps, proof_suggestions, evidence_links
        )

    notes = _reviewer_notes(surfaces, top)
    types = analysis.snapshot.protocol_types
    summary = ReviewMapSummary(
        protocol_types=types,
        contracts_analyzed=len(contracts),
        functions_mapped=len(surfaces),
        value_paths=len(value_paths),
        assumptions=len(assumptions),
        test_gaps=len(gaps),
        proof_suggestions=len(proof_suggestions),
        evidence_links=len(evidence_links),
        text=_summary_text(types, surfaces, value_paths, gaps),
    )
    mode = "compiler-confirmed" if analysis.snapshot.evidence_level == COMPILER_CONFIRMED else "static-heuristic"
    return ReviewMap(
        schema_version="1.0.0",
        generated_at=_now(),
        repo_path=str(root),
        mode=mode,
        summary=summary,
        contracts=sorted(contracts, key=lambda c: (priority_rank(c.review_priority), c.name)),
        functions=sorted(surfaces, key=lambda f: (priority_rank(f.review_priority), f.display_id)),
        value_paths=sorted(value_paths, key=lambda p: (priority_rank(p.review_priority), p.id)),
        assumptions=assumptions,
        test_gaps=sorted(gaps, key=lambda g: g.id),
        proof_suggestions=sorted(proof_suggestions, key=lambda p: p.id),
        evidence_links=evidence_links,
        reviewer_notes=notes,
        safety=SafetyInfo(disclaimer=LOCAL_ONLY_DISCLAIMER, boundaries=list(SAFETY_BOUNDARIES)),
    )


def _link_missing_tests(assumptions: list[Assumption], gaps: list[TestGap]) -> None:
    for asm in assumptions:
        asm.missing_tests = sorted({g.id for g in gaps if g.related_function in asm.used_by})


def _filter_target(target, surfaces, contracts, value_paths, assumptions, gaps, proofs, links):
    t = target.lower()
    matched = [fs for fs in surfaces if fs.display_id.lower() == t or fs.name.lower() == t]
    if not matched:
        raise ValueError(target)
    ids = {fs.display_id for fs in matched}
    contract_names = {fs.contract for fs in matched}
    f_surfaces = [fs for fs in surfaces if fs.display_id in ids]
    f_contracts = [c for c in contracts if c.name in contract_names]
    f_paths = [p for p in value_paths if p.exit_function in ids or p.entry_function in ids]
    f_assumptions = [a for a in assumptions if set(a.used_by) & ids]
    f_gaps = [g for g in gaps if g.related_function in ids]
    f_proofs = [p for p in proofs if p.target in ids]
    f_links = [link for link in links if any(i.split(".")[-1] in link.related_target for i in ids)]
    return f_surfaces, f_contracts, f_paths, f_assumptions, f_gaps, f_proofs, f_links

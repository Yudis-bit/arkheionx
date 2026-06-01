"""Proof-plan suggestions for the Review Map.

Each suggestion is a local Foundry proof a reviewer could write next. It maps a
test gap (and the assumption it would check) to a concrete objective/action/
assertion outline plus a hint that reuses the existing `arkheionx prove`
workflow. Suggestions are guidance, not proof.
"""
from __future__ import annotations

from .model import HIGH, MEDIUM, Assumption, FunctionSurface, ProofSuggestion, TestGap


def _objective(fs: FunctionSurface) -> str:
    if "value-out" in fs.risk_signals:
        return f"Value leaving via {fs.name} is fully accounted and cannot exceed the caller's entitlement."
    if "oracle-dependent" in fs.risk_signals:
        return f"{fs.name} rejects stale or out-of-range oracle values before moving value."
    if "value-in" in fs.risk_signals:
        return f"{fs.name} credits exactly the value received and updates accounting consistently."
    return f"{fs.name} preserves its core invariant under adversarial inputs."


def _assertions(suggested_test: str) -> list[str]:
    scenarios = [s.strip() for s in suggested_test.split(";") if s.strip()]
    return [f"Assert behavior under: {s}" for s in scenarios[:4]] or ["Assert the core invariant holds."]


def _related_assumption(target: str, assumptions: list[Assumption]) -> str:
    for asm in assumptions:
        if target in asm.used_by:
            return asm.id
    return ""


def generate_proof_suggestions(
    surfaces: list[FunctionSurface], gaps: list[TestGap], assumptions: list[Assumption]
) -> list[ProofSuggestion]:
    by_id = {fs.display_id: fs for fs in surfaces}
    out: list[ProofSuggestion] = []
    for gap in gaps:
        fs = by_id.get(gap.related_function)
        if fs is None or fs.review_priority not in (HIGH, MEDIUM):
            continue
        if gap.confidence == "low" and fs.review_priority != HIGH:
            continue
        target = fs.display_id
        out.append(
            ProofSuggestion(
                id=f"proof-{gap.id[4:]}" if gap.id.startswith("gap-") else f"proof-{gap.id}",
                target=target,
                title=f"Prove {target} under value-sensitive scenarios",
                objective=_objective(fs),
                setup=[
                    "Open the repo in a local Foundry project.",
                    "Deploy the contract with mock tokens (and a mock price feed if oracle-dependent).",
                ],
                action=f"Exercise {target} across the suggested scenarios with adversarial inputs.",
                assertions=_assertions(gap.suggested_test),
                related_assumption=_related_assumption(target, assumptions),
                related_test_gap=gap.id,
                foundry_hint=f"arkheionx prove . --target {target} --run",
            )
        )
    return out

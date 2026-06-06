"""Proof-plan suggestions for the Review Map.

Each suggestion is a local Foundry proof a reviewer could write next. It maps a
test gap (and the assumption it would check) to a concrete objective/action/
assertion outline plus a hint that reuses the existing `arkheionx prove`
workflow. Suggestions are guidance, not proof.
"""
from __future__ import annotations

from .model import HIGH, MEDIUM, Assumption, FunctionSurface, ProofSuggestion, ReviewMap, TestGap, to_dict


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


def build_proof_plan_payload(rm: ReviewMap) -> dict:
    """Return the exact payload shape written to ``proof-plan.json``."""

    return {
        "schema_version": rm.schema_version,
        "generated_at": rm.generated_at,
        "repo_path": rm.repo_path,
        "proof_suggestions": to_dict(rm.proof_suggestions),
    }


def _proof_suggestions(data: object) -> list[dict]:
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    if isinstance(data, dict):
        suggestions = data.get("proof_suggestions", [])
        if isinstance(suggestions, list):
            return [item for item in suggestions if isinstance(item, dict)]
    return []


def _proof_target(proof: dict) -> str:
    target = str(proof.get("target") or "").strip()
    return target if "." in target else ""


def _one_line(values: object, fallback: str = "none") -> str:
    if isinstance(values, list):
        return "; ".join(str(value) for value in values if str(value).strip()) or fallback
    text = str(values or "").strip()
    return text or fallback


def _proof_command(repo: str, target: str) -> str:
    return f"arkheionx prove {repo} --target {target} --run" if target else ""


def render_proof_plan_cli(data: object, repo: str, *, top: int = 5, source: str = "", mode: str = "") -> str:
    """Render a concise human report for the focused proof-plan command."""

    suggestions = _proof_suggestions(data)
    ranked = sorted(suggestions, key=lambda item: (str(item.get("target", "")), str(item.get("id", ""))))
    top_items = ranked[:max(0, top)]
    with_test_gap = sum(1 for item in suggestions if item.get("related_test_gap"))
    with_assumption = sum(1 for item in suggestions if item.get("related_assumption"))
    display_mode = mode or (str(data.get("mode", "")) if isinstance(data, dict) else "") or "review-map proof-plan artifact"

    lines = [
        "ARKHEIONX PROOF PLAN",
        "View: Proof Plan",
        "Local/static review guidance only.",
        "Proof plans are suggested local proof outlines, not executed proofs.",
        "Proof plans are not confirmed bugs. Human review required.",
        "Priority is review order, not severity.",
        "",
        "Scope",
        f"  Repo: {repo}",
        f"  Mode: {display_mode}",
    ]
    if source:
        lines.append(f"  Source: {source}")
    lines += [
        "",
        "Summary",
        f"  Total proof suggestions: {len(suggestions)}",
        f"  Related test gaps: {with_test_gap}",
        f"  Related assumptions: {with_assumption}",
        "  Executed proofs: 0 (planning only)",
        "",
        "Top Proof Suggestions",
    ]

    if top_items:
        for index, proof in enumerate(top_items, 1):
            target = _proof_target(proof) or str(proof.get("target") or "unknown")
            title = str(proof.get("title") or proof.get("id") or "proof suggestion")
            lines.append(f"  {index}. {target} - {title}")
            lines.append(f"     Objective: {_one_line(proof.get('objective'))}")
            lines.append(f"     Setup: {_one_line(proof.get('setup'))}")
            lines.append(f"     Action: {_one_line(proof.get('action'))}")
            lines.append(f"     Assertions: {_one_line(proof.get('assertions'))}")
            related = ", ".join(
                value for value in (
                    str(proof.get("related_test_gap") or "").strip(),
                    str(proof.get("related_assumption") or "").strip(),
                )
                if value
            )
            lines.append(f"     Related: {related or 'none'}")
            command = _proof_command(repo, _proof_target(proof))
            if command:
                lines.append(f"     Next: {command}")
    else:
        lines.append("  No proof suggestions surfaced. Inspect the full review map for contract/function context.")

    lines += [
        "",
        "Next",
        f"  Full review map: arkheionx review-map {repo}",
        f"  Test gaps: arkheionx test-gap-map {repo}",
        f"  Value paths: arkheionx value-paths {repo}",
        f"  Assumptions: arkheionx assumptions {repo}",
    ]
    if top_items:
        command = _proof_command(repo, _proof_target(top_items[0]))
        if command:
            lines.append(f"  First local proof: {command}")
    lines += [
        "",
        "Boundary",
        "  Local/static only. No RPC, no private keys, no live-chain calls.",
        "  No exploit automation, no transaction broadcasting, no auto-submit.",
        "  Planning only. No proof was executed by this command.",
        "  Review guidance only. Human review required.",
    ]
    return "\n".join(lines) + "\n"

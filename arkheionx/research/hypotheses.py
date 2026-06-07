"""Hypothesis generation (v4.1).

Turns research surfaces + the review map into a deterministic set of *open*
hypotheses. A hypothesis is a testable review prompt, never a finding. ArkheionX
only ever emits ``open`` hypotheses; humans (or agents under human review) record
every later status after a local test.
"""
from __future__ import annotations

from arkheionx.review_map.model import ReviewMap, priority_rank

from .surfaces import ResearchSurfaces

# Bug-class metadata: why it matters + what local evidence would settle it +
# a default local-test direction. Heuristic prompts only.
BUG_CLASSES: dict[str, dict] = {
    "withdrawal/redeem accounting drift": {
        "why": "Value leaves the system here. Shares/balances burned must match assets paid out across edge amounts.",
        "evidence": "A local Foundry test asserting share<->asset accounting holds for first/last/dust withdrawals.",
        "test": "round-trip deposit then withdraw conserves accounting for first depositor, last depositor, and dust amounts",
    },
    "share inflation / donation": {
        "why": "First-deposit / donation rounding can let an early actor skew the share price for later depositors.",
        "evidence": "A local test of first-deposit share math and a direct asset donation before the second deposit.",
        "test": "first deposit of 1 wei then a direct asset donation does not let the first depositor capture later deposits",
    },
    "oracle stale/wrong value": {
        "why": "Accounting depends on an external price. A stale or wrong value propagates into balances.",
        "evidence": "A local test driving a stale/zero/extreme price through the dependent path.",
        "test": "a stale, zero, or extreme price is rejected or bounded before it reaches accounting",
    },
    "liquidation boundary": {
        "why": "Liquidation/seizure boundaries decide who loses value. Off-by-one health checks change outcomes.",
        "evidence": "A local test at the exact health-factor boundary (just-healthy vs just-unhealthy).",
        "test": "a position exactly at the health boundary liquidates as documented (no early/late seizure)",
    },
    "signature replay": {
        "why": "Signed authorization can be replayed if the digest does not bind nonce, deadline, and domain.",
        "evidence": "A local test replaying a used signature and reusing a consumed nonce.",
        "test": "a used signature/nonce cannot authorize a second action and an expired deadline is rejected",
    },
    "Merkle proof shape confusion": {
        "why": "A leaf that omits a field, or a proof of the wrong shape/root, can authorize an unintended claim.",
        "evidence": "A local test with a wrong-length proof, a different root, and a leaf missing a bound field.",
        "test": "a malformed/wrong-length proof, a different root, and a leaf missing a bound field are all rejected",
    },
    "authorization binding error": {
        "why": "Authorization must bind to the intended caller/account/action and reject everyone else.",
        "evidence": "A local test calling the gated path from an unauthorized caller and an alternate path.",
        "test": "an unauthorized caller is rejected and authorization for one account does not apply to another",
    },
    "periphery/core mismatch": {
        "why": "A periphery call should produce the same core accounting as the equivalent direct call.",
        "evidence": "A local test comparing core state after a periphery call vs the equivalent direct call.",
        "test": "core accounting after the periphery call equals accounting after the equivalent direct call",
    },
    "skip-on-revert behavior mismatch": {
        "why": "Documented skip/continue-on-error behavior can be defeated if earlier computation reverts first.",
        "evidence": "A local test feeding one malformed item among many and asserting the documented partial-failure path.",
        "test": "one malformed item among many behaves as documented (skipped/continued) and does not revert earlier",
    },
    "callback reentrancy / safety assumption": {
        "why": "Callbacks and low-level calls can re-enter or arrive from an unexpected caller.",
        "evidence": "A local test re-entering through the callback and calling it from an unexpected caller.",
        "test": "a reentrant callback and an unexpected caller are handled safely",
    },
    "rounding / precision loss": {
        "why": "Integer rounding in value math can accumulate or be steered across repeated operations.",
        "evidence": "A local test repeating the operation with adversarial amounts to detect drift.",
        "test": "repeated operations with dust/adversarial amounts do not let value drift in one direction",
    },
}

_AUTH_KIND_TO_CLASS = {
    "signature": "signature replay",
    "replay": "signature replay",
    "merkle": "Merkle proof shape confusion",
    "domain": "authorization binding error",
    "access-control": "authorization binding error",
}


def _related_value_path(rm: ReviewMap, target: str) -> str:
    for vp in rm.value_paths:
        if target in (vp.entry_function, vp.exit_function):
            return vp.id
    return ""


def _related_test_gap(rm: ReviewMap, target: str) -> str:
    for gap in rm.test_gaps:
        if gap.related_function == target:
            return gap.id
    return ""


def _candidate(rm: ReviewMap, target: str, contract: str, function: str, source: str,
               surface_label: str, bug_class: str, signals: list[str]) -> dict:
    meta = BUG_CLASSES.get(bug_class, {})
    return {
        "surface": surface_label,
        "contract": contract,
        "function": function,
        "target": target,
        "source": source,
        "value_path": _related_value_path(rm, target),
        "bug_class": bug_class,
        "why_it_matters": meta.get("why", ""),
        "current_evidence": "Static heuristic signal only: " + (", ".join(signals) or "value-flow signal") + ".",
        "test_gap": _related_test_gap(rm, target),
        "suggested_local_test": meta.get("test", ""),
        "evidence_required": meta.get("evidence", ""),
        "status": "open",
        "manual_review_required": True,
    }


def generate_hypotheses(rm: ReviewMap, surfaces: ResearchSurfaces, *, limit: int = 30) -> list[dict]:
    """Generate deterministic, open hypotheses from review map + surfaces."""
    fs_by_id = {f.display_id: f for f in rm.functions}
    seen: set[tuple] = set()
    candidates: list[dict] = []

    def add(target, contract, function, source, surface_label, bug_class, signals):
        key = (target, bug_class)
        if key in seen or function == "":
            return
        seen.add(key)
        candidates.append(_candidate(rm, target, contract, function, source, surface_label, bug_class, signals))

    # Value/oracle/liquidation/entry surfaces from the function set.
    for fs in rm.functions:
        src = f"{fs.path}:{fs.line}" if fs.path and fs.line > 0 else (fs.path or "")
        name = fs.name.lower()
        if fs.value_direction in ("out", "both"):
            add(fs.display_id, fs.contract, fs.name, src, "value-exit surface",
                "withdrawal/redeem accounting drift", fs.risk_signals)
        if "oracle-dependent" in fs.risk_signals:
            add(fs.display_id, fs.contract, fs.name, src, "oracle surface",
                "oracle stale/wrong value", fs.risk_signals)
        if "debt-or-liquidation" in fs.risk_signals:
            add(fs.display_id, fs.contract, fs.name, src, "liquidation surface",
                "liquidation boundary", fs.risk_signals)
        if any(k in name for k in ("deposit", "mint", "stake", "supply")) and fs.value_direction in ("in", "both"):
            add(fs.display_id, fs.contract, fs.name, src, "accounting surface",
                "share inflation / donation", fs.risk_signals)

    # Authorization surfaces.
    for row in surfaces.authorization_surfaces:
        if not row["function"]:
            continue
        bug_class = _AUTH_KIND_TO_CLASS.get(row["kind"], "authorization binding error")
        add(row["target"], row["contract"], row["function"], row["source"],
            "authorization surface", bug_class, [row["signal"]])

    # Periphery surfaces.
    for row in surfaces.periphery_surfaces:
        add(row["target"], row["contract"], row["function"], row["source"],
            "periphery surface", "periphery/core mismatch", row["interaction_type"])
        if {"try-catch", "loop-with-external-call"} & set(row["interaction_type"]):
            add(row["target"], row["contract"], row["function"], row["source"],
                "periphery surface", "skip-on-revert behavior mismatch", row["interaction_type"])
        if "callback" in " ".join(row["interaction_type"]) or "low-level-call" in row["interaction_type"]:
            add(row["target"], row["contract"], row["function"], row["source"],
                "callback/external-call surface", "callback reentrancy / safety assumption", row["interaction_type"])

    # Behavior-mismatch surfaces.
    for row in surfaces.behavior_mismatch_surfaces:
        if not row["function"]:
            continue
        add(row["target"], row["contract"], row["function"], row["source"],
            "behavior-mismatch surface", "skip-on-revert behavior mismatch", [row["signal"]])

    # Deterministic order: by target review priority, then target, then bug class.
    def _rank(c: dict) -> tuple:
        fs = fs_by_id.get(c["target"])
        return (priority_rank(fs.review_priority if fs else "low"), c["target"], c["bug_class"])

    candidates.sort(key=_rank)
    candidates = candidates[:limit]
    for i, c in enumerate(candidates, 1):
        c["id"] = f"HYP-{i:03d}"
    # Move id to the front for readability.
    return [{"id": c.pop("id"), **c} for c in candidates]

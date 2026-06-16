"""Step 5 (inputs) — generate a small, capped set of research leads.

Leads come from the existing local review map (value paths, value-sensitive
functions, oracle/adapter/registry/external-call surfaces). We deliberately cap the
number of raw leads so triage never produces a giant graveyard. Every lead is given
a kill condition here; a lead without a kill condition is invalid.
"""
from __future__ import annotations

from . import models as M

# Visibility considered reachable by an external attacker.
_REACHABLE_VIS = ("public", "external")


def _public_function_index(rm) -> dict:
    index: dict[str, object] = {}
    for fs in getattr(rm, "functions", []) or []:
        index[fs.display_id] = fs
    return index


def _contract_index(rm) -> dict:
    return {c.name: c for c in (getattr(rm, "contracts", []) or [])}


def _tags_for_path(vp, functions: dict) -> set[str]:
    tags: set[str] = set()
    endpoints = [vp.entry_function, vp.exit_function, *list(getattr(vp, "movement", []) or [])]
    for ep in endpoints:
        fs = functions.get(ep)
        if fs is None:
            continue
        for sig in getattr(fs, "risk_signals", []) or []:
            tags.add(sig)
    label = (getattr(vp, "label", "") or "").lower()
    for word, tag in (
        ("oracle", "oracle-dependent"),
        ("adapter", "adapter"),
        ("registry", "registry"),
        ("withdraw", "value-out"),
        ("redeem", "value-out"),
        ("migrat", "migration"),
    ):
        if word in label:
            tags.add(tag)
    return tags


def _kill_condition(tags: set[str]) -> str:
    if "oracle-dependent" in tags:
        return (
            "Kill this lead if the oracle path validates freshness and bounds and a local "
            "test shows stale or out-of-range input reverts before any value moves."
        )
    if "external-call" in tags:
        return (
            "Kill this lead if checks-effects-interactions ordering holds and a local "
            "reentrancy test cannot move value or corrupt accounting."
        )
    if "debt-or-liquidation" in tags:
        return (
            "Kill this lead if a local solvency/health-factor test shows the position "
            "cannot be drained or liquidated for attacker profit."
        )
    if "value-out" in tags:
        return (
            "Kill this lead if every value-out path enforces a caller-entitlement and "
            "balance check that a local test already covers."
        )
    if "privileged" in tags:
        return (
            "Kill this lead if the only way to trigger it is a trusted role the scope "
            "treats as out of scope."
        )
    return (
        "Kill this lead if a local test shows the guarded invariant holds and no value "
        "moves without authorization."
    )


def _reason_for(tags: set[str]) -> str:
    bits: list[str] = []
    if "value-out" in tags:
        bits.append("moves value out")
    if "oracle-dependent" in tags:
        bits.append("depends on an oracle/price input")
    if "external-call" in tags:
        bits.append("makes an external call")
    if "debt-or-liquidation" in tags:
        bits.append("touches debt/liquidation accounting")
    if "adapter" in tags:
        bits.append("routes through an adapter/integration")
    if "registry" in tags:
        bits.append("reads a registry entry")
    if "migration" in tags:
        bits.append("exercises a migration path")
    if "privileged" in tags:
        bits.append("is access-control gated")
    if not bits:
        bits.append("is value-sensitive")
    return "This surface " + ", ".join(bits) + "."


def _reachability(linked_functions: list[str], functions: dict, value_bearing: bool) -> int:
    saw = False
    for disp in linked_functions:
        fs = functions.get(disp)
        if fs is None:
            continue
        saw = True
        vis = (getattr(fs, "visibility", "") or "").lower()
        if vis in _REACHABLE_VIS:
            return 85
        if vis in ("internal", "private"):
            return 30
    # Visibility was unspecified/undetected: a value-bearing entry/exit is most
    # likely externally reachable; otherwise stay neutral.
    if value_bearing:
        return 75
    return 55 if saw else 50


def _materiality(tags: set[str], value_sensitive: bool) -> int:
    score = 35
    if "value-out" in tags:
        score = max(score, 85)
    if "debt-or-liquidation" in tags:
        score = max(score, 80)
    if "oracle-dependent" in tags:
        score = max(score, 70)
    if value_sensitive:
        score = max(score, 60)
    return min(score, 100)


def _proof_difficulty(tags: set[str]) -> int:
    score = 50
    if "oracle-dependent" in tags or "external-call" in tags:
        score += 20
    if "debt-or-liquidation" in tags:
        score += 10
    if "value-out" in tags and not ({"oracle-dependent", "external-call"} & tags):
        score -= 20
    return max(10, min(score, 90))


def _time_cost(tags: set[str]) -> int:
    score = 45
    if "external-call" in tags or "oracle-dependent" in tags:
        score += 20
    if "migration" in tags or "registry" in tags:
        score += 10
    return max(10, min(score, 90))


def _contract_paths(contract_name: str, contracts: dict) -> list[str]:
    cs = contracts.get(contract_name)
    return [cs.path] if cs is not None and getattr(cs, "path", "") else []


def generate_leads(rm) -> list[M.LeadCandidate]:
    functions = _public_function_index(rm)
    contracts = _contract_index(rm)
    leads: list[M.LeadCandidate] = []
    seen_surfaces: set[str] = set()
    counter = 0

    def _next_id() -> str:
        nonlocal counter
        counter += 1
        return f"LEAD-{counter:03d}"

    # 1) Value paths are the strongest material leads.
    for vp in getattr(rm, "value_paths", []) or []:
        entry = getattr(vp, "entry_function", "") or ""
        exit_ = getattr(vp, "exit_function", "") or ""
        # Prefer a real "Contract.func" surface (entry, else exit, else the label).
        if "." in entry:
            surface = entry
        elif "." in exit_:
            surface = exit_
        else:
            surface = getattr(vp, "label", "") or f"value-path:{vp.id}"
        if surface in seen_surfaces:
            continue
        seen_surfaces.add(surface)
        contract_name = surface.split(".")[0] if "." in surface else ""
        tags = _tags_for_path(vp, functions)
        linked_functions = [f for f in [entry, exit_] if "." in f]
        cs = contracts.get(contract_name)
        value_sensitive = bool(getattr(cs, "value_sensitive", False)) if cs else True
        linked_files = _contract_paths(contract_name, contracts)
        materiality = _materiality(tags, value_sensitive)
        value_bearing = materiality >= 60 or bool({"value-out", "value-in"} & tags)
        lead = M.LeadCandidate(
            id=_next_id(),
            title=getattr(vp, "label", "") or surface,
            surface=surface,
            reason=_reason_for(tags),
            linked_files=linked_files,
            linked_functions=linked_functions or [surface],
            attacker_reachability_score=_reachability(linked_functions or [surface], functions, value_bearing),
            materiality_score=materiality,
            proof_difficulty_score=_proof_difficulty(tags),
            time_cost_score=_time_cost(tags),
            kill_condition=_kill_condition(tags),
            notes=sorted(tags),
        )
        leads.append(lead)
        if len(leads) >= M.RAW_LEAD_LIMIT:
            return leads

    # 2) Value-sensitive / risky functions not already represented by a path.
    funcs = sorted(
        getattr(rm, "functions", []) or [],
        key=lambda f: (0 if (f.value_direction in ("out", "both")) else 1, f.display_id),
    )
    for fs in funcs:
        disp = fs.display_id
        if disp in seen_surfaces:
            continue
        risky = bool(getattr(fs, "risk_signals", []) or [])
        value_bearing = fs.value_direction in ("out", "both", "in")
        if not (risky or value_bearing):
            continue
        seen_surfaces.add(disp)
        tags = set(getattr(fs, "risk_signals", []) or [])
        if fs.value_direction in ("out", "both"):
            tags.add("value-out")
        cs = contracts.get(fs.contract)
        value_sensitive = bool(getattr(cs, "value_sensitive", False)) if cs else False
        materiality = _materiality(tags, value_sensitive)
        value_bearing = materiality >= 60 or value_bearing
        lead = M.LeadCandidate(
            id=_next_id(),
            title=f"{fs.contract}.{fs.name} ({fs.value_direction})",
            surface=disp,
            reason=_reason_for(tags),
            linked_files=[fs.path] if getattr(fs, "path", "") else _contract_paths(fs.contract, contracts),
            linked_functions=[disp],
            attacker_reachability_score=_reachability([disp], functions, value_bearing),
            materiality_score=materiality,
            proof_difficulty_score=_proof_difficulty(tags),
            time_cost_score=_time_cost(tags),
            kill_condition=_kill_condition(tags),
            notes=sorted(tags),
        )
        leads.append(lead)
        if len(leads) >= M.RAW_LEAD_LIMIT:
            break

    return leads

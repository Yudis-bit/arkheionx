"""Duplicate / dedup classifier (Layer 9)."""
from __future__ import annotations

from . import models as M
from . import families as F
from . import root_cause_hash as rch


def _sparse_legacy_match(candidate_components: dict, entry) -> bool:
    """Match pre-fingerprint memory that only stored family/role/attacker."""

    if getattr(entry, "root_cause", ""):
        return False
    entry_family = F.canonical(
        getattr(entry, "root_cause_family", "") or getattr(entry, "invariant_family", "")
    )
    if entry_family != F.canonical(candidate_components["invariant_family"]):
        return False
    entry_role = (
        getattr(entry, "affected_function", "")
        or getattr(entry, "function_role", "")
        or "unknown"
    )
    entry_attacker = (
        getattr(entry, "attacker_capability", "")
        or getattr(entry, "attacker_category", "")
        or "user"
    )
    return (
        rch.function_role(entry_role) == candidate_components["function_role"]
        and rch.attacker_category(entry_attacker) == candidate_components["attacker_category"]
    )


def classify_candidate(candidate, known_hashes, known_families=None) -> str:
    """Return SAME_ROOT_CAUSE / RELATED_BUT_DISTINCT / DISTINCT / UNKNOWN."""
    comps = rch.components_for_candidate(candidate)
    h = comps["root_cause_hash"]
    if not known_hashes:
        return M.DUP_UNKNOWN
    if h in known_hashes:
        return M.SAME_ROOT_CAUSE
    if any(_sparse_legacy_match(comps, e) for e in known_hashes.values()):
        return M.SAME_ROOT_CAUSE
    fams = known_families if known_families is not None else {
        e.invariant_family for e in known_hashes.values()}
    canonical_fams = {F.canonical(f) for f in fams}
    if F.canonical(candidate.invariant_family) in canonical_fams:
        return M.RELATED_BUT_DISTINCT
    return M.DISTINCT


def annotate(graph, store, scope=None):
    """Set duplicate_risk / scope_risk / root_cause_hash on each candidate."""
    known = store.known_hashes() if store else {}
    fams = {e.invariant_family for e in known.values()}
    oos = store.out_of_scope_contracts() if store else set()
    scope_oos = set((scope or {}).get("out_of_scope_contracts", []) or [])
    oos |= scope_oos
    results = []
    for c in graph.candidates:
        comps = rch.components_for_candidate(c)
        c.root_cause_hash = comps["root_cause_hash"]
        c.duplicate_risk = classify_candidate(c, known, fams)
        contract = c.entry_function.split(".")[0]
        if contract in oos:
            c.scope_risk = "OUT_OF_SCOPE"
        elif scope is not None:
            c.scope_risk = "IN_SCOPE"
        results.append((c.id, c.duplicate_risk, c.scope_risk, c.root_cause_hash))
    return results

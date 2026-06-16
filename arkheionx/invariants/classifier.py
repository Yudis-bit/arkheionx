"""Invariant classifier (Layer 4): group, count, and order invariants."""
from __future__ import annotations


def classify(invset) -> dict:
    by_family, by_testability = {}, {}
    for inv in invset.invariants:
        by_family.setdefault(inv.family, []).append(inv.id)
        by_testability.setdefault(inv.testability, []).append(inv.id)
    return {
        "by_family": {k: len(v) for k, v in by_family.items()},
        "by_testability": {k: len(v) for k, v in by_testability.items()},
        "suspicious_ids": [i.id for i in invset.suspicious()],
        "total": len(invset.invariants),
        "suspicious": len(invset.suspicious()),
    }


def ordered(invset) -> list:
    """Suspicious invariants first, then by family for stability."""
    return sorted(invset.invariants, key=lambda i: (not i.suspicious, i.family, i.id))

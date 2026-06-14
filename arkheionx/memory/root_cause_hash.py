"""Semantic root-cause hashing (Layer 9).

The hash is intentionally *semantic*, not the title: it keys on the invariant
family, the function role (lifecycle, contract-agnostic), and the attacker
category. So the same root cause on a different pool/contract hashes the same,
while a genuinely different bug hashes differently.
"""
from __future__ import annotations

import hashlib
import re

_ROLE_RULES = [
    (re.compile(r"repay|settle"), "repay"),
    (re.compile(r"borrow|originat"), "borrow"),
    (re.compile(r"liquidat"), "liquidate"),
    (re.compile(r"redeem|redemption"), "redeem"),
    (re.compile(r"withdraw|consume|claim"), "consume"),
    (re.compile(r"deposit|mint|supply"), "deposit"),
    (re.compile(r"swap|exchange|route"), "swap"),
    (re.compile(r"bridge|lzsend|lzreceive"), "bridge"),
    (re.compile(r"vote|propos|delegate"), "governance"),
    (re.compile(r"sweep|rescue|skim|withdrawfees"), "admin_value_move"),
]


def function_role(fn_name: str) -> str:
    n = (fn_name or "").split(".")[-1].lower()
    for rx, role in _ROLE_RULES:
        if rx.search(n):
            return role
    return n or "unknown"


def attacker_category(capability: str) -> str:
    c = (capability or "").lower()
    if "unprivileged" in c or "anyone" in c:
        return "unprivileged"
    if "borrow" in c:
        return "borrower"
    if "lend" in c:
        return "lender"
    if "depos" in c or "donor" in c or "first" in c:
        return "depositor"
    if "role" in c or "owner" in c or "admin" in c:
        return "role"
    return "user"


def root_cause_hash(invariant_family: str, fn_role: str, attacker_cat: str) -> str:
    seed = "|".join([(invariant_family or "").strip().upper(), fn_role, attacker_cat])
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()[:16]


def components_for_candidate(candidate) -> dict:
    role = function_role(candidate.entry_function)
    cat = attacker_category(candidate.attacker_capability)
    return {
        "invariant_family": candidate.invariant_family,
        "function_role": role,
        "attacker_category": cat,
        "root_cause_hash": root_cause_hash(candidate.invariant_family, role, cat),
    }

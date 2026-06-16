"""Factory deployment and initialization analysis."""
from __future__ import annotations

import re

from . import models as M


def analyze_factories(source_text: str, contract_names: list[str]) -> list[M.FactoryInitAnalysis]:
    lowered = source_text.lower()
    if "create2" not in lowered and "new " not in lowered and "initialize" not in lowered:
        return []
    initializer_callable = bool(re.search(
        r"function\s+initialize\s*\([^)]*\)\s+(?:external|public)", source_text, re.I
    ))
    guard = bool(re.search(
        r"function\s+initialize[\s\S]{0,300}(?:initializer|initialized|_initialized)",
        source_text,
        re.I,
    ))
    salt_match = re.search(r"(?:salt|create2)[\s\S]{0,300}keccak256\s*\(([^;]+)", source_text, re.I)
    salt_text = salt_match.group(1) if salt_match else ""
    owner_bound = bool(re.search(r"owner|signer", salt_text, re.I))
    parent_bound = bool(re.search(r"controller|parent|factory", salt_text, re.I))
    atomic = bool(re.search(r"(?:new\s+\w+|create2)[\s\S]{0,400}\.initialize\s*\(", source_text, re.I))
    takeover = initializer_callable and not guard and not atomic
    if not (initializer_callable or "create2" in lowered):
        return []
    contract = next((name for name in contract_names if "factory" in name.lower()), contract_names[0] if contract_names else "")
    return [M.FactoryInitAnalysis(
        contract=contract,
        function="initialize" if initializer_callable else "deploy",
        initializer_callable=initializer_callable,
        initializer_guard=guard,
        create2_salt_fields=[value for value, present in (
            ("owners", owner_bound),
            ("parent_or_controller", parent_bound),
        ) if present],
        signer_or_owner_bound_in_salt=owner_bound,
        parent_or_controller_bound_in_salt=parent_bound,
        atomic_init=atomic,
        takeover_risk=takeover,
        verdict="FACTORY_INITIALIZATION_TAKEOVER" if takeover else "FACTORY_INITIALIZATION_BOUND",
        evidence=["factory deployment and initialization sequence"],
    )]

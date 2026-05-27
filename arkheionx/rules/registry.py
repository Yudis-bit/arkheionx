"""Canonical rule-pack metadata for the Arkheionx internal engine split."""
from __future__ import annotations

from arkheionx.core.models import RulePackInfo


RULE_PACKS = {
    "vault": {
        "display_name": "Vault Rule Pack",
        "prefix": "ARK-VLT",
        "docs": "docs/VAULT_RULE_PACK.md",
        "description": "Vault, ERC4626-like, strategy, fee, and withdrawal lifecycle readiness.",
    },
    "oracle": {
        "display_name": "Oracle Rule Pack",
        "prefix": "ARK-ORC",
        "docs": "docs/ORACLE_RULE_PACK.md",
        "description": "Oracle freshness, normalization, bounds, and price-source assumptions.",
    },
    "access-control": {
        "display_name": "Access Control Rule Pack",
        "prefix": "ARK-ACC",
        "docs": "docs/ACCESS_CONTROL_RULE_PACK.md",
        "description": "Privileged role, setter, initializer, and upgrade boundary readiness.",
    },
    "reentrancy-value-flow": {
        "display_name": "Reentrancy Value Flow Rule Pack",
        "prefix": "ARK-REENT",
        "docs": "docs/REENTRANCY_VALUE_FLOW_RULE_PACK.md",
        "description": "External-call ordering, callback, and claimable-accounting readiness.",
    },
    "rewards": {
        "display_name": "Reward Accounting Rule Pack",
        "prefix": "ARK-RWD",
        "docs": "docs/REWARD_ACCOUNTING_RULE_PACK.md",
        "description": "Reward index, emission, claim, cooldown, and staking lifecycle readiness.",
    },
    "testing": {
        "display_name": "Testing Readiness",
        "prefix": "ARK-TST",
        "docs": "docs/READINESS_SCORE.md",
        "description": "Invariant, fuzz, property, and lifecycle test readiness.",
    },
    "docs": {
        "display_name": "Documentation Readiness",
        "prefix": "ARK-DOC",
        "docs": "docs/READINESS_SCORE.md",
        "description": "Assumption, scope, and operational documentation readiness.",
    },
    "amm": {
        "display_name": "AMM Rule Pack",
        "prefix": "ARK-AMM",
        "docs": "docs/AMM_RULE_PACK.md",
        "description": "Swap, reserve, LP share, slippage, fee, and price dependency readiness.",
    },
    "lending": {
        "display_name": "Lending Rule Pack",
        "prefix": "ARK-LEND",
        "docs": "docs/LENDING_RULE_PACK.md",
        "description": "Collateral, debt, liquidation, interest, and oracle-dependent lending readiness.",
    },
}


def rule_pack_infos() -> list[RulePackInfo]:
    return [
        RulePackInfo(
            key=key,
            display_name=str(value["display_name"]),
            prefix=str(value["prefix"]),
            docs=str(value["docs"]),
            description=str(value.get("description", "")),
        )
        for key, value in sorted(RULE_PACKS.items())
    ]

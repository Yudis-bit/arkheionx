"""Canonical rule-pack metadata for the Arkheionx internal engine split."""
from __future__ import annotations

from arkheionx.core.models import RulePackInfo


RULE_PACKS = {
    "vault": {
        "display_name": "Vault Rule Pack",
        "prefix": "ARK-VLT",
        "docs": "docs/VAULT_RULE_PACK.md",
        "description": "Vault, ERC4626-like, strategy, fee, and withdrawal lifecycle readiness.",
        "default_enabled": True,
        "related_protocol_types": ("auto", "vault", "hybrid"),
    },
    "oracle": {
        "display_name": "Oracle Rule Pack",
        "prefix": "ARK-ORC",
        "docs": "docs/ORACLE_RULE_PACK.md",
        "description": "Oracle freshness, normalization, bounds, and price-source assumptions.",
        "default_enabled": True,
        "related_protocol_types": ("auto", "oracle", "vault", "lending", "amm", "hybrid"),
    },
    "access-control": {
        "display_name": "Access Control Rule Pack",
        "prefix": "ARK-ACC",
        "secondary_prefixes": ("ARK-UPG",),
        "docs": "docs/ACCESS_CONTROL_RULE_PACK.md",
        "description": "Privileged role, setter, initializer, and upgrade boundary readiness.",
        "default_enabled": True,
        "related_protocol_types": ("auto", "access-control", "vault", "oracle", "rewards", "staking", "amm", "lending", "hybrid"),
    },
    "reentrancy-value-flow": {
        "display_name": "Reentrancy Value Flow Rule Pack",
        "prefix": "ARK-REENT",
        "docs": "docs/REENTRANCY_VALUE_FLOW_RULE_PACK.md",
        "description": "External-call ordering, callback, and claimable-accounting readiness.",
        "default_enabled": True,
        "related_protocol_types": ("auto", "vault", "rewards", "staking", "amm", "lending", "hybrid"),
    },
    "rewards": {
        "display_name": "Reward Accounting Rule Pack",
        "prefix": "ARK-RWD",
        "docs": "docs/REWARD_ACCOUNTING_RULE_PACK.md",
        "description": "Reward index, emission, claim, cooldown, and staking lifecycle readiness.",
        "default_enabled": True,
        "related_protocol_types": ("auto", "rewards", "staking", "hybrid"),
    },
    "testing": {
        "display_name": "Testing Readiness",
        "prefix": "ARK-TST",
        "docs": "docs/READINESS_SCORE.md",
        "description": "Invariant, fuzz, property, and lifecycle test readiness.",
        "default_enabled": True,
        "related_protocol_types": ("auto", "generic", "vault", "oracle", "access-control", "rewards", "staking", "amm", "lending", "hybrid"),
    },
    "docs": {
        "display_name": "Documentation Readiness",
        "prefix": "ARK-DOC",
        "docs": "docs/READINESS_SCORE.md",
        "description": "Assumption, scope, and operational documentation readiness.",
        "default_enabled": True,
        "related_protocol_types": ("auto", "generic", "vault", "oracle", "access-control", "rewards", "staking", "amm", "lending", "hybrid"),
    },
    "amm": {
        "display_name": "AMM Rule Pack",
        "prefix": "ARK-AMM",
        "docs": "docs/AMM_RULE_PACK.md",
        "description": "Swap, reserve, LP share, slippage, fee, and price dependency readiness.",
        "default_enabled": True,
        "related_protocol_types": ("auto", "amm", "hybrid"),
    },
    "lending": {
        "display_name": "Lending Rule Pack",
        "prefix": "ARK-LEND",
        "docs": "docs/LENDING_RULE_PACK.md",
        "description": "Collateral, debt, liquidation, interest, and oracle-dependent lending readiness.",
        "default_enabled": True,
        "related_protocol_types": ("auto", "lending", "hybrid"),
    },
}


def _prefixes_for(value: dict[str, object]) -> tuple[str, ...]:
    primary = str(value["prefix"])
    secondary = value.get("secondary_prefixes", ())
    if not isinstance(secondary, tuple):
        secondary = tuple(str(item) for item in secondary) if isinstance(secondary, list) else ()
    return (primary, *secondary)


def rule_pack_infos() -> list[RulePackInfo]:
    return [
        RulePackInfo(
            key=key,
            display_name=str(value["display_name"]),
            prefix=str(value["prefix"]),
            docs=str(value["docs"]),
            description=str(value.get("description", "")),
            default_enabled=bool(value.get("default_enabled", True)),
            related_protocol_types=tuple(str(item) for item in value.get("related_protocol_types", ())),
        )
        for key, value in sorted(RULE_PACKS.items())
    ]


def get_rule_pack(key: str) -> RulePackInfo | None:
    value = RULE_PACKS.get(key)
    if value is None:
        return None
    return RulePackInfo(
        key=key,
        display_name=str(value["display_name"]),
        prefix=str(value["prefix"]),
        docs=str(value["docs"]),
        description=str(value.get("description", "")),
        default_enabled=bool(value.get("default_enabled", True)),
        related_protocol_types=tuple(str(item) for item in value.get("related_protocol_types", ())),
    )


def list_rule_packs() -> list[RulePackInfo]:
    return rule_pack_infos()


def validate_rule_pack_keys(keys: list[str] | tuple[str, ...]) -> list[str]:
    return [key for key in keys if key not in RULE_PACKS]


def finding_id_to_rule_pack(finding_id: str) -> str:
    normalized = finding_id.upper()
    for key, value in RULE_PACKS.items():
        if normalized.startswith(_prefixes_for(value)):
            return key
    return "generic"


def is_known_finding_prefix(finding_id_or_prefix: str) -> bool:
    normalized = finding_id_or_prefix.upper()
    return any(normalized.startswith(_prefixes_for(value)) for value in RULE_PACKS.values())

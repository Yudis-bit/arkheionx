"""Finding ID helpers for Arkheionx rule families."""
from __future__ import annotations


ID_PREFIXES = {
    "vault": "ARK-VLT",
    "oracle": "ARK-ORC",
    "access-control": "ARK-ACC",
    "upgradeability": "ARK-UPG",
    "reentrancy-value-flow": "ARK-REENT",
    "rewards": "ARK-RWD",
    "testing": "ARK-TST",
    "docs": "ARK-DOC",
    "amm": "ARK-AMM",
    "lending": "ARK-LEND",
}


def prefix_for_family(family: str) -> str:
    return ID_PREFIXES.get(family, "ARK-GEN")


def family_for_finding_id(finding_id: str) -> str:
    normalized = finding_id.upper()
    for family, prefix in ID_PREFIXES.items():
        if normalized.startswith(prefix):
            return family
    return "generic"

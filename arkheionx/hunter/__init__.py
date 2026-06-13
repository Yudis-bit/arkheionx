"""Arkheionx V9 Universal Senior Exploit Hunter Mode (`arkheionx hunter`).

A local-first senior research *decision* engine. It helps a human researcher choose the
highest-EV bounty surfaces — fresh, in-scope, payable, non-duplicate, attacker-reachable
— and avoid known / out-of-scope / dead leads before writing PoCs.

It does not automatically find vulnerabilities, does not confirm bugs, does not assign
final severity, does not submit reports, and makes no live-chain mutation. Read-only RPC
is opt-in only and the endpoint is always masked. Human review is always required.
"""
from __future__ import annotations

from .command import hunter_command
from .models import (
    ARTIFACT_TYPE,
    SCHEMA_VERSION,
    TOP_LEAD_LIMIT,
    HunterLead,
    HunterPack,
)
from .pack import build_hunter_pack, default_hunter_dir

__all__ = [
    "hunter_command",
    "build_hunter_pack",
    "default_hunter_dir",
    "HunterPack",
    "HunterLead",
    "SCHEMA_VERSION",
    "ARTIFACT_TYPE",
    "TOP_LEAD_LIMIT",
]

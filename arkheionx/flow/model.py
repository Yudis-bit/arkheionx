"""Money-flow data model."""
from __future__ import annotations

from dataclasses import dataclass, field

from arkheionx.protocol.model import HEURISTIC

# Flow edge kinds.
FLOW_KINDS = (
    "token_in", "token_out", "mint", "burn", "state_write", "state_read",
    "oracle_read", "external_call", "admin_update", "strategy_move",
    "reward_claim", "queue_request", "queue_fulfill", "unknown",
)


@dataclass
class FlowEdge:
    source: str
    target: str
    kind: str = "unknown"
    label: str = ""
    asset_hint: str = ""
    confidence: str = "medium"
    evidence_level: str = HEURISTIC


@dataclass
class MoneyFlow:
    entrypoints: list[str] = field(default_factory=list)
    exits: list[str] = field(default_factory=list)
    value_holders: list[str] = field(default_factory=list)
    asset_movements: list[FlowEdge] = field(default_factory=list)
    accounting_surfaces: list[str] = field(default_factory=list)
    pricing_dependencies: list[str] = field(default_factory=list)
    privileged_movers: list[str] = field(default_factory=list)
    external_integrations: list[str] = field(default_factory=list)
    edges: list[FlowEdge] = field(default_factory=list)
    evidence_level: str = HEURISTIC

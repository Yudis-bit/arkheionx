"""Core data model for the Arkheionx Foundry-powered workbench.

These dataclasses are additive and decoupled from the legacy scanner. They
serialize deterministically via :func:`to_dict` for stable JSON artifacts.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field

# --- Evidence levels -------------------------------------------------------
# Every major result carries exactly one of these labels. They reflect how the
# conclusion was reached, never how severe a finding is.
HEURISTIC = "HEURISTIC"
COMPILER_CONFIRMED = "COMPILER_CONFIRMED"
EXECUTION_CONFIRMED = "EXECUTION_CONFIRMED"
REPORT_READY = "REPORT_READY"

_EVIDENCE_ORDER = {
    HEURISTIC: 0,
    COMPILER_CONFIRMED: 1,
    EXECUTION_CONFIRMED: 2,
    REPORT_READY: 3,
}


def max_evidence(a: str, b: str) -> str:
    """Return the stronger of two evidence levels."""

    return a if _EVIDENCE_ORDER.get(a, 0) >= _EVIDENCE_ORDER.get(b, 0) else b


# --- Role vocabularies (stable strings used in reports and schemas) --------
CONTRACT_ROLES = (
    "User Entry",
    "Value Holder",
    "Share Token",
    "Accounting",
    "Pricing / Oracle",
    "Strategy",
    "Reward Distributor",
    "Queue / Escrow",
    "Router",
    "Manager",
    "Token",
    "Privileged Controller",
    "External Adapter",
    "Test / Mock",
    "Unknown",
)

FUNCTION_ROLES = (
    "Money Entry",
    "Money Exit",
    "Asset Transfer",
    "Share Mint",
    "Share Burn",
    "Accounting Update",
    "Pricing Update",
    "Oracle Read",
    "Reward Claim",
    "Strategy Movement",
    "Privileged Movement",
    "External Call",
    "Pause / Emergency",
    "Config Change",
    "Unknown",
)


def to_dict(obj: object) -> object:
    """Deterministically serialize a workbench dataclass (or container)."""

    if hasattr(obj, "__dataclass_fields__"):
        return asdict(obj)
    if isinstance(obj, (list, tuple)):
        return [to_dict(item) for item in obj]
    return obj


@dataclass
class ContractRole:
    contract_name: str
    file_path: str
    role: str = "Unknown"
    confidence: str = "medium"
    evidence_level: str = HEURISTIC
    reasons: list[str] = field(default_factory=list)
    value_state_vars: list[str] = field(default_factory=list)
    line_range: list[int] = field(default_factory=list)
    source_kind: str = "production"


@dataclass
class FunctionRole:
    function_id: str
    contract_name: str
    function_name: str
    signature: str = ""
    visibility: str = "unspecified"
    modifiers: list[str] = field(default_factory=list)
    role: str = "Unknown"
    risk_score: int = 0
    evidence_level: str = HEURISTIC
    reasons: list[str] = field(default_factory=list)
    external_calls: list[str] = field(default_factory=list)
    oracle_calls: list[str] = field(default_factory=list)
    reads_state: list[str] = field(default_factory=list)
    writes_state: list[str] = field(default_factory=list)
    privileged: bool = False
    user_callable: bool = False
    line_range: list[int] = field(default_factory=list)
    source_kind: str = "production"
    file_path: str = ""
    display_id: str = ""
    qualified_id: str = ""
    stable_id: str = ""


@dataclass
class UserJourney:
    name: str
    actor: str = "User"
    steps: list[str] = field(default_factory=list)
    entry_functions: list[str] = field(default_factory=list)
    exit_functions: list[str] = field(default_factory=list)
    assets_involved: list[str] = field(default_factory=list)
    evidence_level: str = HEURISTIC


@dataclass
class ProtocolSnapshot:
    root: str
    protocol_types: list[str] = field(default_factory=list)
    foundry_status: str = "unavailable"
    contracts_analyzed: int = 0
    functions_analyzed: int = 0
    evidence_level: str = HEURISTIC
    summary: str = ""
    limitations: list[str] = field(default_factory=list)

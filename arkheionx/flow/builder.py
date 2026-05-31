"""Build a money-flow graph from classified functions and contracts."""
from __future__ import annotations

from arkheionx.protocol.model import ContractRole, FunctionRole
from arkheionx.protocol.roles import ACCOUNTING_STATE_TERMS

from .model import FlowEdge, MoneyFlow

_USER = "User"
_OWNER = "Owner / Admin"
_ORACLE = "Oracle / Rate Provider"

_ENTRY_ROLES = {"Money Entry"}
_EXIT_ROLES = {"Money Exit", "Reward Claim"}
_TRANSFER_CALLS = {"transfer", "safetransfer", "transferfrom", "safetransferfrom", "send"}


def _confidence_for(fr: FunctionRole, has_token: bool) -> str:
    if has_token:
        return "high"
    if fr.writes_state or fr.oracle_calls:
        return "medium"
    return "low"


def _token_out(fr: FunctionRole) -> bool:
    return any(c.lower().startswith(("transfer", "safetransfer", "send")) and "from" not in c.lower() for c in fr.external_calls)


def _token_in(fr: FunctionRole) -> bool:
    return any("from" in c.lower() for c in fr.external_calls)


def _writes_accounting(fr: FunctionRole) -> bool:
    return any(any(term in v.lower() for term in ACCOUNTING_STATE_TERMS) for v in fr.writes_state)


def build_money_flow(
    contract_roles: list[ContractRole],
    function_roles: list[FunctionRole],
    evidence_level: str,
) -> MoneyFlow:
    flow = MoneyFlow(evidence_level=evidence_level)
    flow.value_holders = sorted({
        cr.contract_name
        for cr in contract_roles
        if cr.value_state_vars or cr.role in {"Value Holder", "Share Token", "Reward Distributor"}
    })
    flow.external_integrations = sorted({
        f"{cr.contract_name} (price source, trust assumed)"
        for cr in contract_roles
        if cr.role == "Pricing / Oracle"
    })

    for fr in function_roles:
        contract = fr.contract_name
        token_out = _token_out(fr)
        token_in = _token_in(fr)

        if fr.role in _ENTRY_ROLES:
            flow.entrypoints.append(fr.function_id)
            edge = FlowEdge(_USER, fr.function_id, "token_in", "token in", "ERC20 token", _confidence_for(fr, token_in), evidence_level)
            flow.edges.append(edge)
            flow.asset_movements.append(edge)
            if fr.writes_state:
                flow.edges.append(FlowEdge(fr.function_id, contract, "state_write", "updates balances", "", "medium", evidence_level))
        if fr.role in _EXIT_ROLES:
            flow.exits.append(fr.function_id)
            kind = "reward_claim" if fr.role == "Reward Claim" else "token_out"
            edge = FlowEdge(fr.function_id, _USER, kind, "token out", "ERC20 token", _confidence_for(fr, token_out), evidence_level)
            flow.edges.append(edge)
            flow.asset_movements.append(edge)
        if fr.oracle_calls:
            flow.pricing_dependencies.append(fr.function_id)
            flow.edges.append(FlowEdge(fr.function_id, _ORACLE, "oracle_read", "price/rate read", "", "high", evidence_level))
        if _writes_accounting(fr):
            flow.accounting_surfaces.append(fr.function_id)
        if fr.privileged:
            flow.privileged_movers.append(fr.function_id)
            flow.edges.append(FlowEdge(_OWNER, fr.function_id, "admin_update", "configures", "", "medium", evidence_level))
        if {c.lower() for c in fr.external_calls} & _TRANSFER_CALLS and fr.role not in (_ENTRY_ROLES | _EXIT_ROLES):
            flow.asset_movements.append(FlowEdge(contract, "external", "external_call", "token movement", "ERC20 token", "medium", evidence_level))

    flow.entrypoints = sorted(set(flow.entrypoints))
    flow.exits = sorted(set(flow.exits))
    flow.accounting_surfaces = sorted(set(flow.accounting_surfaces))
    flow.pricing_dependencies = sorted(set(flow.pricing_dependencies))
    flow.privileged_movers = sorted(set(flow.privileged_movers))
    return flow

"""Heuristic contract and function role classification.

Classification starts at HEURISTIC evidence and is upgraded to
COMPILER_CONFIRMED by the orchestrator when ``forge build`` confirms a
contract compiled.
"""
from __future__ import annotations

from .model import HEURISTIC, ContractRole, FunctionRole

# Value-bearing state variable name fragments.
VALUE_STATE_TERMS = (
    "balanceof", "balance", "totalsupply", "totalassets", "totalstaked",
    "reserve", "reserves", "debt", "shares", "assets", "liquidity",
    "collateral", "deposits", "escrow", "pendingreward", "rewardpertoken",
    "accumulator", "klast",
)
ACCOUNTING_STATE_TERMS = (
    "index", "accumulator", "rewardpertoken", "exchangerate", "totalassets",
    "rate", "sharesper", "borrowindex",
)

_ENTRY_NAMES = ("deposit", "stake", "mint", "supply", "addliquidity", "request", "wrap")
_EXIT_NAMES = ("withdraw", "redeem", "unstake", "claim", "payout", "refund", "removeliquidity", "unwrap")
_TOKEN_OUT_CALLS = ("transfer", "safetransfer", "send")
_TOKEN_IN_CALLS = ("transferfrom", "safetransferfrom")
_ADMIN_PREFIXES = ("set", "update", "configure", "pause", "unpause", "upgrade", "rebalance", "execute", "migrate", "sweep", "rescue")
_ADMIN_MODIFIERS = ("onlyowner", "onlyrole", "onlyadmin", "onlygovernance", "auth", "restricted")


def _has(name: str, terms) -> bool:
    return any(term in name for term in terms)


def _value_state_vars(state_variables) -> list[str]:
    return [v for v in state_variables if _has(v.lower(), VALUE_STATE_TERMS)]


def is_privileged(function: dict) -> bool:
    name = str(function.get("name", "")).lower()
    mods = [str(m).lower() for m in function.get("modifiers", [])]
    if any(m in _ADMIN_MODIFIERS for m in mods):
        return True
    return name.startswith(_ADMIN_PREFIXES)


def classify_function(function: dict, contract_name: str) -> FunctionRole:
    name = str(function.get("name", ""))
    lname = name.lower()
    visibility = str(function.get("visibility", "unspecified"))
    external_calls = list(function.get("external_calls", []))
    oracle_calls = list(function.get("oracle_calls", []))
    writes_state = list(function.get("writes_state", []))
    reads_state = list(function.get("reads_state", []))
    modifiers = list(function.get("modifiers", []))
    payable = bool(function.get("payable", False))
    line_start = int(function.get("line_start", 0) or 0)
    line_end = int(function.get("line_end", 0) or 0)

    privileged = is_privileged(function)
    user_callable = visibility in {"public", "external"} and not privileged
    ext_lower = {c.lower().strip(".(") for c in external_calls}
    token_out = bool(ext_lower & set(_TOKEN_OUT_CALLS))
    token_in = bool(ext_lower & set(_TOKEN_IN_CALLS))
    writes_accounting = any(_has(v.lower(), ACCOUNTING_STATE_TERMS) for v in writes_state)

    reasons: list[str] = []
    role = "Unknown"
    # Order matters: most specific / highest-signal first.
    if lname.startswith(("pause", "unpause")) or "emergency" in lname or "freeze" in lname:
        role = "Pause / Emergency"
        reasons.append("pause/emergency control")
    elif "claim" in lname:
        role = "Reward Claim"
        reasons.append("reward claim path")
        if token_out:
            reasons.append("transfers tokens out")
    elif _has(lname, _EXIT_NAMES) and (token_out or not external_calls):
        role = "Money Exit"
        reasons.append(f"exit-style name `{name}`")
        if token_out:
            reasons.append("transfers tokens out")
    elif _has(lname, _ENTRY_NAMES) and (token_in or payable or writes_state):
        role = "Money Entry"
        reasons.append(f"entry-style name `{name}`")
        if token_in:
            reasons.append("pulls tokens in via transferFrom")
        if payable:
            reasons.append("payable")
    elif lname in {"mint"} or (lname.endswith("mint") and writes_state):
        role = "Share Mint"
        reasons.append("mints shares/tokens")
    elif lname in {"burn"} or (lname.endswith("burn") and writes_state):
        role = "Share Burn"
        reasons.append("burns shares/tokens")
    elif lname.startswith(("invest", "harvest", "rebalance", "migrate", "allocate")):
        role = "Strategy Movement"
        reasons.append("strategy movement")
    elif privileged and (token_in or token_out):
        role = "Privileged Movement"
        reasons.append("privileged + moves value")
    elif privileged:
        role = "Config Change"
        reasons.append("privileged setter/config")
    elif oracle_calls:
        role = "Oracle Read"
        reasons.append(f"reads price source ({', '.join(oracle_calls)})")
    elif writes_accounting:
        role = "Accounting Update"
        reasons.append("updates accounting state")
    elif token_in or token_out:
        role = "Asset Transfer"
        reasons.append("moves tokens")
    elif external_calls:
        role = "External Call"
        reasons.append("makes external calls")

    score = _risk_score(role, token_in, token_out, oracle_calls, writes_state, external_calls, user_callable, privileged)
    fid = f"{contract_name}.{name}#{line_start}"
    signature = str(function.get("signature", "")) or f"{name}()"
    return FunctionRole(
        function_id=fid,
        contract_name=contract_name,
        function_name=name,
        signature=signature,
        visibility=visibility,
        modifiers=modifiers,
        role=role,
        risk_score=score,
        evidence_level=HEURISTIC,
        reasons=reasons,
        external_calls=external_calls,
        oracle_calls=oracle_calls,
        reads_state=reads_state,
        writes_state=writes_state,
        privileged=privileged,
        user_callable=user_callable,
        line_range=[line_start, line_end],
    )


def _risk_score(role, token_in, token_out, oracle_calls, writes_state, external_calls, user_callable, privileged) -> int:
    score = 0
    if token_out:
        score += 35  # direct asset outflow is the highest-value surface
    if token_in:
        score += 15
    if role in {"Reward Claim", "Money Exit"}:
        score += 15
    if oracle_calls:
        score += 18
    if writes_state:
        score += 10
    if external_calls:
        score += 8
    if user_callable:
        score += 8
    if privileged and (token_in or token_out):
        score += 20
    elif privileged:
        score += 6
    if role in {"Accounting Update", "Pricing Update"}:
        score += 10
    return max(0, min(100, score))


_CONTRACT_ROLE_PRIORITY = (
    "Test / Mock",
    "Pricing / Oracle",
    "Reward Distributor",
    "Strategy",
    "Queue / Escrow",
    "Router",
    "Share Token",
    "Token",
    "Value Holder",
    "Accounting",
    "Manager",
    "External Adapter",
    "User Entry",
    "Privileged Controller",
    "Unknown",
)


def classify_contract(contract: dict, function_roles: list[FunctionRole]) -> ContractRole:
    name = str(contract.get("name", ""))
    lname = name.lower()
    kind = str(contract.get("kind", "contract"))
    inherits = [str(i).lower() for i in contract.get("inherits", [])]
    state_vars = [str(v) for v in contract.get("state_variables", [])]
    value_vars = _value_state_vars(state_vars)
    fnames = {fr.function_name.lower() for fr in function_roles}
    froles = {fr.role for fr in function_roles}
    candidates: set[str] = set()
    reasons: list[str] = []

    if kind == "interface":
        candidates.add("External Adapter")
        reasons.append("interface declaration")
    if _has(lname, ("mock", "harness")) or lname.endswith("test"):
        candidates.add("Test / Mock")
        reasons.append("mock/test naming")
    has_value_actions = bool(froles & {"Money Entry", "Money Exit", "Reward Claim"})
    if (_has(lname, ("oracle", "price", "feed", "aggregator")) and not has_value_actions) or (kind == "interface" and any(fr.oracle_calls for fr in function_roles)):
        candidates.add("Pricing / Oracle")
        reasons.append("price/oracle naming or oracle reads")
    if _has(lname, ("reward", "distributor", "staking", "gauge")) or _has(" ".join(state_vars).lower(), ("reward", "accumulator", "rewardpertoken")):
        candidates.add("Reward Distributor")
        reasons.append("reward/staking accounting")
    if _has(lname, ("strategy", "vault4626", "yield")):
        candidates.add("Strategy")
        reasons.append("strategy naming")
    if _has(lname, ("queue", "escrow", "cooldown", "timelock")):
        candidates.add("Queue / Escrow")
        reasons.append("queue/escrow naming")
    if _has(lname, ("router", "swap")) or "swap" in fnames:
        candidates.add("Router")
        reasons.append("router/swap surface")
    if _has(lname, ("share", "erc4626", "vault")) and _has(" ".join(state_vars).lower(), ("shares", "totalassets")):
        candidates.add("Share Token")
        reasons.append("share accounting")
    if any(i in {"erc20", "ierc20", "erc20upgradeable"} for i in inherits) or ({"transfer", "transferfrom", "approve"} <= fnames and _has(" ".join(state_vars).lower(), ("balanceof", "totalsupply"))):
        candidates.add("Token")
        reasons.append("ERC20-like token")
    if value_vars and (froles & {"Money Entry", "Money Exit", "Asset Transfer", "Reward Claim"}):
        candidates.add("Value Holder")
        reasons.append(f"holds value: {', '.join(value_vars[:4])}")
    if _has(lname, ("manager", "controller", "comptroller", "pool", "lend", "bank")):
        candidates.add("Manager")
        reasons.append("manager/controller naming")
    if _has(lname, ("adapter", "wrapper", "connector")):
        candidates.add("External Adapter")
        reasons.append("adapter naming")
    if froles & {"Money Entry"}:
        candidates.add("User Entry")
        reasons.append("exposes user entry points")
    privileged_fns = sum(1 for fr in function_roles if fr.privileged)
    if privileged_fns and not (froles & {"Money Entry", "Money Exit"}) and not value_vars:
        candidates.add("Privileged Controller")
        reasons.append("mostly privileged setters")

    role = "Unknown"
    for candidate in _CONTRACT_ROLE_PRIORITY:
        if candidate in candidates:
            role = candidate
            break

    return ContractRole(
        contract_name=name,
        file_path=str(contract.get("file", "")),
        role=role,
        confidence="medium" if role != "Unknown" else "low",
        evidence_level=HEURISTIC,
        reasons=reasons or ["no strong role signal detected"],
        value_state_vars=value_vars,
        line_range=[int(contract.get("line_start", 0) or 0), int(contract.get("line_end", 0) or 0)],
    )

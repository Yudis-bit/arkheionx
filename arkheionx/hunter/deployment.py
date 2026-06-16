"""Deployment reality engine (V9) for hunter mode.

Local-first and strictly read-only. Without ``--addresses`` it is RPC_NOT_PROVIDED.
With addresses but no endpoint it emits a static read-only verification plan. With an
explicit read-only ``--rpc-url`` it issues only the allowlisted read methods
(eth_chainId, eth_getCode, eth_getStorageAt, eth_call), detects EIP-1967 and beacon
proxies, compares the live implementation / admin / beacon against the expected
values from addresses.json, and records source-vs-deployed mismatches. It never
signs, never sends a transaction, never mutates chain, and masks the endpoint in all
output. A transport can be injected so tests never touch the network.
"""
from __future__ import annotations

from arkheionx.senior_triage.deployment_rpc import (
    EIP1967_ADMIN_SLOT,
    EIP1967_BEACON_SLOT,
    EIP1967_IMPLEMENTATION_SLOT,
    ReadOnlyRpc,
    RpcError,
    ZERO_ADDRESS,
    decode_return,
    mask_endpoint,
)

from . import models as M

# implementation() selector, used to resolve a beacon's current implementation.
_IMPLEMENTATION_SELECTOR = "0x5c60da1b"

# A small, well-known, read-only built-in selector set (stable 4-byte selectors).
_BUILTIN_SELECTORS = (
    ("owner", "0x8da5cb5b", "address"),
    ("paused", "0x5c975abb", "bool"),
    ("implementation", "0x5c60da1b", "address"),
    ("asset", "0x38d52e0f", "address"),
    ("totalSupply", "0x18160ddd", "uint256"),
    ("totalAssets", "0x01e1d114", "uint256"),
)

_RECOMMENDED_CHECKS = (
    "Chain id (eth_chainId) matches the in-scope chain.",
    "Code exists at every in-scope address (eth_getCode).",
    "EIP-1967 implementation slot for each proxy and compare to expected_implementation.",
    "EIP-1967 admin slot for each upgradeable contract.",
    "EIP-1967 beacon slot and the beacon's implementation() for beacon proxies.",
    "Registry routing entries vs the listed in-scope set (live registry diff).",
    "Oracle address, decimals, and staleness window.",
    "Paused / disabled state of value-bearing entry points.",
)

_SAFE_COMMANDS = (
    "cast chain-id                                  # confirm the chain (read-only)",
    "cast code <address>                            # confirm deployed bytecode exists (read-only)",
    "cast storage <proxy> " + EIP1967_IMPLEMENTATION_SLOT + "   # EIP-1967 implementation slot (read-only)",
    "cast storage <proxy> " + EIP1967_BEACON_SLOT + "   # EIP-1967 beacon slot (read-only)",
    "cast call <beacon> 'implementation()(address)'  # beacon implementation (read-only)",
    "cast call <oracle> 'decimals()(uint8)'          # read-only oracle metadata",
)


def _norm(addr: str) -> str:
    return (addr or "").strip().lower()


def _beacon_implementation(rpc: ReadOnlyRpc, beacon: str) -> str:
    try:
        raw = rpc.eth_call(beacon, _IMPLEMENTATION_SELECTOR)
        impl = decode_return("address", raw)
        return "" if impl in ("", ZERO_ADDRESS) else impl
    except RpcError:
        return ""


def _read_slot_address(rpc: ReadOnlyRpc, address: str, slot: str) -> str:
    try:
        word = rpc.storage_at(address, slot)
    except RpcError:
        return ""
    if not isinstance(word, str):
        return ""
    h = word[2:] if word.startswith("0x") else word
    addr = "0x" + h.rjust(64, "0")[-40:].lower()
    return "" if addr in ("", ZERO_ADDRESS) else addr


def _builtin_calls(rpc: ReadOnlyRpc, address: str) -> list:
    out: list = []
    for name, selector, decode in _BUILTIN_SELECTORS:
        try:
            value = decode_return(decode, rpc.eth_call(address, selector))
        except RpcError:
            continue
        if decode == "address" and value in ("", ZERO_ADDRESS):
            continue
        if value is None:
            continue
        out.append({"name": name, "value": value})
    return out


def _assess_one(rpc: ReadOnlyRpc, entry: dict, deployment_calls_by_addr: dict) -> M.DeploymentResult:
    address = _norm(entry.get("address", ""))
    expected_impl = _norm(entry.get("expected_implementation") or "")
    proxy_expected = entry.get("proxy_expected")
    res = M.DeploymentResult(name=entry.get("name", "contract"), address=address,
                             expected_implementation=expected_impl)
    try:
        facts = rpc.code_facts(address)
    except RpcError:
        res.status = M.RPC_CHECK_FAILED
        res.notes.append("Read-only code check failed.")
        return res
    res.has_code = facts["has_code"]
    res.code_size = facts["code_size"]
    res.code_hash = facts["code_hash"]
    if not res.has_code:
        res.status = M.ADDRESS_NO_CODE
        res.notes.append("No code at the expected address (nothing to attack there).")
        return res

    impl = _read_slot_address(rpc, address, EIP1967_IMPLEMENTATION_SLOT)
    admin = _read_slot_address(rpc, address, EIP1967_ADMIN_SLOT)
    beacon = _read_slot_address(rpc, address, EIP1967_BEACON_SLOT)
    res.admin = admin

    if impl:
        res.proxy_pattern = M.EIP1967_PROXY
        res.implementation = impl
    elif beacon:
        res.proxy_pattern = M.BEACON_PROXY
        res.beacon = beacon
        res.implementation = _beacon_implementation(rpc, beacon)
    elif proxy_expected is True:
        res.proxy_pattern = M.UNKNOWN_PROXY_PATTERN
        res.notes.append("Proxy expected by scope but no EIP-1967 implementation/beacon slot is set.")
    else:
        res.proxy_pattern = M.DIRECT_CONTRACT

    # Compare live implementation / beacon to the expected (audited) implementation.
    if expected_impl and res.implementation:
        if _norm(res.implementation) == expected_impl:
            res.status = M.BEACON_MATCH if res.proxy_pattern == M.BEACON_PROXY else M.IMPLEMENTATION_MATCH
            res.notes.append("Live implementation matches the expected (audited) implementation.")
        else:
            res.status = M.BEACON_CHANGED if res.proxy_pattern == M.BEACON_PROXY else M.DEPLOY_IMPLEMENTATION_CHANGED
            res.notes.append(f"Live implementation {res.implementation} differs from expected {expected_impl}.")
    elif expected_impl and not res.implementation:
        res.status = M.LIVE_SOURCE_UNKNOWN
        res.notes.append("Expected implementation provided but no live implementation slot was readable.")
    else:
        res.status = res.proxy_pattern or M.DIRECT_CONTRACT

    # Optional user-provided read-only eth_call reads for this address.
    for call in deployment_calls_by_addr.get(address, []):
        data = str(call.get("selector", "")) + str(call.get("args_hex", ""))
        if not data or data == "":
            continue
        try:
            value = decode_return(call.get("decode", "raw"), rpc.eth_call(address, data))
            res.calls.append({"name": call.get("name", "call"), "value": value})
        except RpcError:
            res.calls.append({"name": call.get("name", "call"), "value": None, "error": "rpc_check_failed"})
    res.calls.extend(_builtin_calls(rpc, address))
    return res


def assess_deployment(
    ctx: M.HunterContext,
    address_parse: M.AddressParseResult,
    *,
    rpc_endpoint: str = "",
    deployment_calls=None,
    transport=None,
) -> M.DeploymentReality:
    masked = mask_endpoint(rpc_endpoint) or ctx.rpc_endpoint_masked
    entries = list(address_parse.addresses or [])
    addresses_provided = address_parse.status in (M.ADDRESS_OK, M.ADDRESS_PARSE_ERROR) and bool(entries)

    if not entries:
        return M.DeploymentReality(
            status=M.RPC_NOT_PROVIDED, rpc_mode=ctx.rpc_mode, addresses_provided=False,
            recommended_checks=list(_RECOMMENDED_CHECKS), rpc_endpoint_masked=masked,
            reason=f"No usable addresses ({address_parse.status}); deployment reality not run.",
            notes=["Provide a valid --addresses file to enable a deployment-reality plan."],
        )

    if not (rpc_endpoint or "").strip():
        return M.DeploymentReality(
            status=M.RPC_NOT_PROVIDED, rpc_mode=ctx.rpc_mode, addresses_provided=True,
            recommended_checks=list(_RECOMMENDED_CHECKS), safe_commands=list(_SAFE_COMMANDS),
            rpc_endpoint_masked=masked,
            reason="Addresses provided; no endpoint supplied, so read-only live verification was not run.",
            notes=[
                "Live state: NOT_RUN (no endpoint; hunter makes no live-chain calls by default).",
                "Pass a read-only --rpc-url to verify live wiring; the endpoint is masked.",
            ],
        )

    rpc = ReadOnlyRpc(rpc_endpoint, transport=transport)
    chain_id = 0
    try:
        chain_id = rpc.chain_id()
    except RpcError:
        pass

    calls_by_addr: dict = {}
    for call in (deployment_calls or []):
        to = _norm(call.get("to", ""))
        if to:
            calls_by_addr.setdefault(to, []).append(call)

    results: list = []
    mismatches: list = []
    ok = 0
    for entry in entries:
        res = _assess_one(rpc, entry, calls_by_addr)
        res.chain_id = chain_id
        if res.status != M.RPC_CHECK_FAILED:
            ok += 1
        if res.status == M.ADDRESS_NO_CODE:
            mismatches.append({"name": res.name, "address": res.address, "type": M.ADDRESS_NO_CODE})
        elif res.status in M.DEPLOYMENT_MISMATCH_STATUSES:
            mismatches.append({"name": res.name, "address": res.address, "type": res.status,
                               "expected": res.expected_implementation, "live": res.implementation})
        results.append(res.to_dict())

    status = M.READ_ONLY_RPC_ENABLED if ok else M.RPC_CHECK_FAILED
    notes = [
        "Read-only checks only: chain id, code, EIP-1967 implementation/admin/beacon slots, "
        "optional eth_call. No mutation.",
        "Endpoint is masked in all output; no secret is printed.",
    ]
    if mismatches:
        notes.append(f"{len(mismatches)} source-vs-deployed mismatch(es) — a priority signal, not a bug.")
    if not ok:
        notes.append("All read-only checks failed (RPC_CHECK_FAILED); hunter continues without live verification.")

    return M.DeploymentReality(
        status=status, rpc_mode=ctx.rpc_mode, chain_id=chain_id, addresses_provided=True,
        results=results, mismatches=mismatches, recommended_checks=list(_RECOMMENDED_CHECKS),
        safe_commands=list(_SAFE_COMMANDS), rpc_endpoint_masked=masked,
        reason=("Read-only deployment verification ran." if ok else "Read-only deployment verification failed."),
        notes=notes,
    )


def deployment_status_for_contract(deployment: M.DeploymentReality, contract: str) -> str:
    """Best deployment status for a lead's contract (matched by name)."""
    contract = (contract or "").lower()
    if not contract:
        return ""
    for res in deployment.results:
        name = str(res.get("name", "")).lower()
        if not name:
            continue
        if contract == name or contract in name or name in contract:
            return res.get("status", "")
    return ""

"""Step 4 — deployment reality check (local-first, optional, read-only).

Local-first and read-only. Without ``--addresses`` it is NOT_RUN. With addresses but
no endpoint it produces a static verification plan. With an endpoint it performs
allowlisted read-only checks (chain id, code existence + hash, EIP-1967 implementation
slot, optional read-only eth_call) and compares deployed implementation to the
expected implementation from addresses.json. It never sends a transaction, never
signs, never needs a private key, never mutates chain, and masks the endpoint in all
output. A transport can be injected so tests never touch the network.
"""
from __future__ import annotations

import json
from pathlib import Path

from . import models as M
from .deployment_rpc import ReadOnlyRpc, RpcError, decode_return, mask_endpoint

_RECOMMENDED_CHECKS = (
    "EIP-1967 implementation slot for every proxy address.",
    "Proxy admin / owner address for each upgradeable contract.",
    "Registry values and routing entries.",
    "Oracle address, decimals, and staleness window.",
    "Role holders for each privileged role.",
    "Paused / disabled state of value-bearing entry points.",
    "Token balances actually held by the deployment.",
)

_SAFE_COMMANDS = (
    "cast code <address>            # confirm deployed bytecode exists (read-only)",
    "cast storage <proxy> 0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc"
    "  # EIP-1967 implementation slot (read-only)",
    "cast call <oracle> 'decimals()(uint8)'   # read-only oracle metadata",
    "cast call <token> 'balanceOf(address)(uint256)' <deployment>   # read-only balance",
)


def _load_addresses(path: Path) -> tuple:
    """Return (chain, [entries]). Supports the rich schema and simple name->addr."""
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except (OSError, ValueError):
        return "", []
    chain = ""
    entries: list = []

    def _entry(name, address, kind="", source_file="", expected="", tags=None):
        if isinstance(address, str) and address.startswith("0x"):
            entries.append({
                "name": str(name)[:64], "address": address[:80], "kind": kind or "",
                "source_file": source_file or "", "expected_implementation": expected or "",
                "tags": list(tags or []),
            })

    if isinstance(data, dict) and isinstance(data.get("contracts"), list):
        chain = str(data.get("chain", ""))[:32]
        for c in data["contracts"]:
            if isinstance(c, dict) and "address" in c:
                _entry(c.get("name", "contract"), c.get("address"), c.get("kind", ""),
                       c.get("source_file", ""), c.get("expected_implementation", ""), c.get("tags"))
        for group in ("assets", "oracles", "registries"):
            for c in data.get(group, []) or []:
                if isinstance(c, dict) and "address" in c:
                    _entry(c.get("name", c.get("symbol", group)), c.get("address"), group)
    elif isinstance(data, dict):
        for name, value in data.items():
            if isinstance(value, str):
                _entry(name, value)
            elif isinstance(value, dict) and "address" in value:
                _entry(value.get("name", name), value.get("address"), value.get("kind", ""),
                       value.get("source_file", ""), value.get("expected_implementation", ""), value.get("tags"))
    elif isinstance(data, list):
        for c in data:
            if isinstance(c, dict) and "address" in c:
                _entry(c.get("name", "contract"), c.get("address"), c.get("kind", ""),
                       c.get("source_file", ""), c.get("expected_implementation", ""), c.get("tags"))
    return chain, entries[:64]


def _live_checks(entries, endpoint, deployment_calls, transport) -> dict:
    rpc = ReadOnlyRpc(endpoint, transport=transport)
    out = {"chain_id": 0, "results": [], "mismatches": [], "errors": []}
    try:
        out["chain_id"] = rpc.chain_id()
    except RpcError as exc:
        out["errors"].append({"scope": "chain_id", "error": type(exc).__name__})

    calls_by_addr: dict = {}
    for call in (deployment_calls or []):
        to = str(call.get("to", "")).lower()
        if to:
            calls_by_addr.setdefault(to, []).append(call)

    ok = 0
    for entry in entries:
        addr = entry["address"]
        res = {
            "name": entry["name"], "address": addr, "kind": entry.get("kind", ""),
            "has_code": False, "code_size": 0, "code_hash": "", "implementation": "",
            "implementation_code_hash": "", "expected_implementation": entry.get("expected_implementation", ""),
            "status": "", "calls": [],
        }
        try:
            facts = rpc.code_facts(addr)
            res.update(facts)
            ok += 1
            if not facts["has_code"]:
                res["status"] = M.DEPLOY_ADDRESS_NO_CODE
                out["mismatches"].append({"name": entry["name"], "address": addr, "type": M.DEPLOY_ADDRESS_NO_CODE})
            else:
                if entry.get("kind") == "proxy" or entry.get("expected_implementation"):
                    impl = rpc.implementation(addr)
                    res["implementation"] = impl
                    if impl:
                        res["implementation_code_hash"] = rpc.code_facts(impl).get("code_hash", "")
                    expected = (entry.get("expected_implementation") or "").lower()
                    if expected and impl and expected != impl.lower():
                        res["status"] = M.DEPLOY_IMPLEMENTATION_CHANGED
                        out["mismatches"].append({
                            "name": entry["name"], "address": addr,
                            "type": M.DEPLOY_IMPLEMENTATION_CHANGED,
                            "expected": expected, "live": impl,
                        })
                    elif expected and impl and expected == impl.lower():
                        res["status"] = M.DEPLOY_LIVE_SOURCE_MATCH
                for call in calls_by_addr.get(addr.lower(), []):
                    data = str(call.get("selector", "")) + str(call.get("args_hex", ""))
                    if data:
                        decoded = decode_return(call.get("decode", "raw"), rpc.eth_call(addr, data))
                        res["calls"].append({"name": call.get("name", "call"), "value": decoded})
            if not res["status"]:
                res["status"] = "CODE_PRESENT"
        except RpcError as exc:
            res["status"] = M.DEPLOY_RPC_CHECK_FAILED
            out["errors"].append({"name": entry["name"], "address": addr, "error": type(exc).__name__})
        out["results"].append(res)

    out["ok"] = ok
    return out


def assess_deployment(ctx: M.TriageContext, *, rpc_endpoint: str = "", deployment_calls=None, transport=None) -> M.DeploymentRealitySignal:
    rpc_mode = ctx.rpc_mode
    masked = mask_endpoint(rpc_endpoint) or ctx.rpc_endpoint_masked
    addresses_file = (ctx.addresses_file or "").strip()

    if not addresses_file:
        return M.DeploymentRealitySignal(
            status=M.DEPLOY_NOT_RUN, rpc_mode=rpc_mode, addresses_provided=False,
            recommended_checks=list(_RECOMMENDED_CHECKS), rpc_endpoint_masked=masked,
            reason="No addresses file provided (--addresses). Deployment reality not run.",
            notes=["Live state: NOT_RUN.", "Provide --addresses to generate a static deployment-reality plan."],
        )

    chain, entries = _load_addresses(Path(addresses_file).expanduser())
    addresses_view = [{"name": e["name"], "address": e["address"], "kind": e.get("kind", "")} for e in entries]

    if not entries:
        return M.DeploymentRealitySignal(
            status=M.DEPLOY_NOT_RUN, rpc_mode=rpc_mode, addresses_provided=True,
            recommended_checks=list(_RECOMMENDED_CHECKS), safe_commands=list(_SAFE_COMMANDS),
            rpc_endpoint_masked=masked,
            reason="Addresses file present but no usable address entries were parsed.",
            notes=["Provide a JSON object/list mapping names to 0x addresses, or the rich schema."],
        )

    if rpc_endpoint:
        live = _live_checks(entries, rpc_endpoint, deployment_calls, transport)
        any_ok = live.get("ok", 0) > 0
        status = M.DEPLOY_RPC_READ_ONLY_CHECKED if any_ok else M.DEPLOY_RPC_CHECK_FAILED
        notes = [
            "Read-only checks only: code, EIP-1967 implementation slot, optional eth_call. No mutation.",
            "Endpoint is masked in all output; no secret is printed.",
        ]
        if live["mismatches"]:
            notes.append(f"{len(live['mismatches'])} source-vs-deployed mismatch(es) detected — a priority signal, not a bug.")
        if not any_ok:
            notes.append("All read-only checks failed (RPC_CHECK_FAILED); triage continues without live verification.")
        return M.DeploymentRealitySignal(
            status=status, rpc_mode=rpc_mode, chain_id=live["chain_id"], addresses_provided=True,
            addresses=addresses_view, results=live["results"], mismatches=live["mismatches"],
            recommended_checks=list(_RECOMMENDED_CHECKS), safe_commands=list(_SAFE_COMMANDS),
            rpc_endpoint_masked=masked,
            reason=("Read-only deployment verification ran." if any_ok else "Read-only deployment verification failed."),
            notes=notes + ([f"errors: {len(live['errors'])}"] if live["errors"] else []),
        )

    # Addresses provided, no endpoint -> static plan only.
    return M.DeploymentRealitySignal(
        status=M.DEPLOY_ADDRESSES_PROVIDED, rpc_mode=rpc_mode, addresses_provided=True,
        addresses=addresses_view, recommended_checks=list(_RECOMMENDED_CHECKS),
        safe_commands=list(_SAFE_COMMANDS), rpc_endpoint_masked=masked,
        reason="Addresses provided; no endpoint supplied, so read-only live verification was not run.",
        notes=[
            "Live state: NOT_RUN (no endpoint; triage makes no live-chain calls by default).",
            "Use the recommended read-only checks to compare deployed state to source.",
        ],
    )

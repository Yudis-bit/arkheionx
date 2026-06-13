"""Live registry / live-set diff for hunter mode.

A common real-world bounty situation: the scope table lists one set of addresses, but
a live registry points to a newer or different set. Hunter mode can read a registry
through *user-provided* read-only calls (it never guesses selectors) and diff the live
set against the listed set:

    LIVE_AND_LISTED   live set == listed set
    LIVE_NOT_LISTED   a live entry is not in the listed scope (PARK_SCOPE by default)
    LISTED_NOT_LIVE   a listed entry is not live (downrank unless still value-bearing)
    REGISTRY_DIFF_UNKNOWN / REGISTRY_CALL_FAILED / REGISTRY_NOT_RUN

All calls are read-only (eth_call) through the allowlisted client.
"""
from __future__ import annotations

from arkheionx.senior_triage.deployment_rpc import ReadOnlyRpc, RpcError, ZERO_ADDRESS

from . import models as M


def _decode_address_array(raw: str) -> list:
    """Decode an ABI-encoded ``address[]`` return value (offset, length, words)."""
    if not isinstance(raw, str):
        return []
    h = raw[2:] if raw.startswith("0x") else raw
    if len(h) < 128:
        return []
    try:
        offset = int(h[0:64], 16) * 2
        length = int(h[offset:offset + 64], 16)
    except ValueError:
        return []
    out: list = []
    base = offset + 64
    for i in range(length):
        word = h[base + i * 64: base + (i + 1) * 64]
        if len(word) < 64:
            break
        addr = "0x" + word[-40:].lower()
        if addr != ZERO_ADDRESS:
            out.append(addr)
    return out


def _resolve_target(target: str, listed_by_name: dict) -> str:
    if target and target.lower() in listed_by_name:
        return listed_by_name[target.lower()]
    if isinstance(target, str) and target.startswith("0x") and len(target) == 42:
        return target.lower()
    return ""


def assess_registry(
    address_parse: M.AddressParseResult,
    *,
    rpc_endpoint: str = "",
    registry_calls=None,
    transport=None,
) -> M.RegistryDiff:
    listed = [a.get("address", "").lower() for a in (address_parse.addresses or []) if a.get("address")]
    listed_set = set(listed)
    if not registry_calls:
        return M.RegistryDiff(status=M.REGISTRY_NOT_RUN, listed_entries=sorted(listed_set),
                              notes=["No --registry-calls provided; live registry diff not run."])
    if not (rpc_endpoint or "").strip():
        return M.RegistryDiff(status=M.REGISTRY_NOT_RUN, listed_entries=sorted(listed_set),
                              notes=["--registry-calls requires a read-only --rpc-url."])

    listed_by_name = {a.get("name", "").lower(): a.get("address", "").lower()
                      for a in (address_parse.addresses or []) if a.get("name")}
    rpc = ReadOnlyRpc(rpc_endpoint, transport=transport)
    live: set = set()
    failed = False
    notes: list = []
    for call in registry_calls:
        decode = str(call.get("decode", ""))
        target = _resolve_target(str(call.get("target", "")), listed_by_name)
        selector = str(call.get("selector", ""))
        if not target or not selector:
            notes.append(f"Skipped registry call {call.get('name', '?')}: unresolved target or missing selector.")
            continue
        try:
            raw = rpc.eth_call(target, selector + str(call.get("args_hex", "")))
        except RpcError:
            failed = True
            notes.append(f"Registry call {call.get('name', '?')} failed (read-only).")
            continue
        if decode.startswith("address[]"):
            live.update(_decode_address_array(raw))
        elif decode == "address":
            h = (raw or "0x")[2:]
            addr = "0x" + h.rjust(64, "0")[-40:].lower()
            if addr != ZERO_ADDRESS:
                live.add(addr)
        # uint256 (e.g. poolCount) is informational; recorded as a note.
        elif decode == "uint256":
            try:
                notes.append(f"{call.get('name', 'count')} = {int(raw, 16)}")
            except (TypeError, ValueError):
                pass

    if failed and not live:
        return M.RegistryDiff(status=M.REGISTRY_CALL_FAILED, listed_entries=sorted(listed_set),
                              scope_confidence=M.LOW, notes=notes or ["All registry calls failed."])
    if not live:
        return M.RegistryDiff(status=M.REGISTRY_DIFF_UNKNOWN, listed_entries=sorted(listed_set),
                              scope_confidence=M.LOW,
                              notes=notes + ["No live registry entries decoded; diff is unknown."])

    extra = sorted(live - listed_set)     # live but not listed
    missing = sorted(listed_set - live)   # listed but not live
    if extra:
        status = M.LIVE_NOT_LISTED
        notes.append(f"{len(extra)} live registry entry(ies) not in the listed scope set.")
    elif missing:
        status = M.LISTED_NOT_LIVE
        notes.append(f"{len(missing)} listed entry(ies) are not in the live registry set.")
    else:
        status = M.LIVE_AND_LISTED
        notes.append("Live registry set matches the listed scope set.")

    confidence = M.HIGH if status == M.LIVE_AND_LISTED else M.MEDIUM
    return M.RegistryDiff(
        status=status, live_entries=sorted(live), listed_entries=sorted(listed_set),
        missing_entries=missing, extra_entries=extra, scope_confidence=confidence, notes=notes,
    )

"""State transition detector (Layer 3).

Builds a :class:`StateTransition` for each value-affecting entry function. Effects
of directly-called internal helpers are folded in via a bounded closure so an
entry point like ``repay`` reflects what ``_distribute`` actually does.
"""
from __future__ import annotations

import re

from . import transitions as T
from arkheionx.semantic.fallback_parser import match_delim
from arkheionx.semantic import models as SM

# Invariant template ids this layer can hint at (kept as literals to avoid an
# import cycle with the invariants package; they match invariants.templates).
INV_DEBT_RECON = "DEBT_REPAYMENT_RECONCILIATION"
INV_CONSENT = "LENDER_CONSENT_VALUE_AFFECTING_CALLDATA"
INV_BORROW_CONS = "BORROW_CONSERVATION"
INV_DEPOSIT_CONS = "DEPOSIT_CONSUMPTION"
INV_SWAP_RECV = "SWAP_ACTUAL_RECEIVED_VS_CREDITED"
INV_VAULT_SHARE = "VAULT_SHARE_ASSET_RECONCILIATION"
INV_COLLATERAL = "COLLATERAL_STATUS_RELEASE"
INV_ORACLE = "ORACLE_DECIMAL_NORMALIZATION"
INV_XCHAIN = "CROSS_CHAIN_SUPPLY_CONSERVATION"


def _bodies(smap):
    parse = getattr(smap, "_parse", None)
    return getattr(parse, "bodies", {}) if parse else {}


def _closure(smap, fn, max_depth=3):
    """FunctionSemantic objects reachable from ``fn`` via same-contract internal calls."""
    c = smap.contract(fn.contract)
    by_name = {f.name: f for f in c.functions} if c else {}
    seen, order = set(), []
    frontier = [(fn, 0)]
    while frontier:
        cur, d = frontier.pop()
        if cur.name in seen:
            continue
        seen.add(cur.name)
        order.append(cur)
        if d < max_depth:
            for callee in cur.internal_calls:
                nxt = by_name.get(callee)
                if nxt is not None and nxt.name not in seen:
                    frontier.append((nxt, d + 1))
    return order


def _requires(body: str) -> list:
    out = []
    for m in re.finditer(r"\brequire\s*\(", body):
        op = body.find("(", m.start())
        close = match_delim(body, op, "(", ")")
        inner = body[op + 1:close]
        cond = inner.split(",", 1)[0].strip()
        cond = re.sub(r"\s+", " ", cond)
        if cond and cond not in out:
            out.append(cond)
    for m in re.finditer(r"\bif\s*\(([^)]*)\)\s*revert", body):
        cond = re.sub(r"\s+", " ", m.group(1).strip())
        if cond:
            out.append(f"!({cond})")
    return out[:12]


def _status_changes(body: str) -> list:
    out = []
    for m in re.finditer(r"([A-Za-z_]\w*)\s*\.\s*status\s*=\s*(?!=)([^;]+);", body):
        out.append(f"{m.group(1)}.status = {m.group(2).strip()}")
    for m in re.finditer(r"(?<![=!<>])\bstatus\s*=\s*(?!=)([A-Za-z_]\w*\.[A-Za-z_]\w*)", body):
        out.append(f"status = {m.group(1)}")
    for m in re.finditer(r"\b([A-Za-z_]\w*)\s*=\s*(?!=)(true|false)\s*;", body):
        if re.search(r"active|consumed|settled|repaid|closed|held|paused|finalized", m.group(1), re.I):
            out.append(f"{m.group(1)} = {m.group(2)}")
    seen, uniq = set(), []
    for s in out:
        if s not in seen:
            seen.add(s); uniq.append(s)
    return uniq[:8]


def _actor(fn, requires) -> str:
    for mod in fn.role_gates:
        return f"trusted role ({mod})"
    for cond in requires:
        m = re.search(r"msg\.sender\s*==\s*([A-Za-z_][\w.]*)", cond)
        if m:
            return f"caller bound to {m.group(1)}"
    name = fn.name.lower()
    if "borrow" in name or "originat" in name:
        return "borrower"
    if "repay" in name:
        return "borrower/payer"
    if "deposit" in name or "mint" in name:
        return "depositor/user"
    if fn.uses_msg_sender:
        return "user (msg.sender)"
    return "anyone"


def _lifecycle(name: str, vault_ctx: bool) -> str:
    n = name.lower()
    if "liquidat" in n:
        return T.LC_LIQUIDATION
    if "borrow" in n or "originat" in n:
        return T.LC_BORROW
    if "repay" in n or "settle" in n:
        return T.LC_REPAY
    if "redeem" in n or "redemption" in n:
        return T.LC_REDEMPTION
    if "swap" in n or "exchange" in n:
        return T.LC_SWAP
    if "wrap" in n or "adapter" in n:
        return T.LC_ADAPTER
    if "bridge" in n or "lzsend" in n or "lzreceive" in n:
        return T.LC_CROSS_CHAIN
    if "vote" in n or "propos" in n or "delegate" in n:
        return T.LC_GOVERNANCE
    if "consume" in n or "claim" in n:
        return T.LC_DEPOSIT_CONSUME
    if "withdraw" in n:
        return T.LC_VAULT_WITHDRAW if vault_ctx else T.LC_DEPOSIT_CONSUME
    if "deposit" in n or "mint" in n or "supply" in n:
        return T.LC_VAULT_DEPOSIT if vault_ctx else T.LC_DEPOSIT
    return T.LC_GENERIC


def _assets(transfers: set):
    ai, ao = [], []
    for t in transfers:
        tl = t.lower()
        if "transferfrom" in tl:
            ai.append("token via transferFrom (pulled in)")
        elif tl in ("transfer", "safetransfer", "sendvalue") or t == "call{value}":
            ao.append("token/ETH via transfer (paid out)")
        elif tl == "mint":
            ai.append("shares/tokens minted")
        elif tl in ("burn", "burnfrom"):
            ao.append("shares/tokens burned")
    return sorted(set(ai)), sorted(set(ao))


def _shape_flags(fn, bodies, combined, transfers, etypes, vault_ctx):
    """Shape-driven flags that attach an invariant family from *semantics*, not the
    function name. They let an adapter ``deposit``, an oracle-reading ``borrow``, or
    a bridge ``receiveMessage`` reach the right invariant even when the name does not
    match a lifecycle. All heuristic / medium confidence."""
    extra = []
    low = combined.lower()
    entry = bodies.get(fn.qualified_name)
    entry_text = entry.body if entry is not None and entry.body else ""

    # (1) credit-from-nominal: pull tokens in via transferFrom, then credit a ledger
    #     by the nominal amount with no measured balance delta (balanceOf). Guarded
    #     out of vault context, where the share/asset invariant owns this shape.
    tf_pos = entry_text.lower().find("transferfrom")
    credit_after = False
    if tf_pos != -1:
        for m in re.finditer(
                r"\b(credit|credited|shares?|deposited|claimable|claim|owed|minted)\s*\[",
                entry_text, re.I):
            if m.start() > tf_pos:
                credit_after = True
                break
    measures_delta = "balanceof" in low
    if (not vault_ctx) and tf_pos != -1 and credit_after and not measures_delta:
        extra.append("credit_no_balance_delta")

    # (2) oracle price -> value math with hardcoded scaling / ignored decimals.
    oracle_read = bool(re.search(r"latestrounddata|latestanswer|getprice|pricefeed|\.price\s*\(",
                                 low))
    hardcoded_scale = bool(re.search(r"1e18|1e8|1e6|10\s*\*\*", combined))
    price_arith = bool(re.search(r"price\s*\)*\s*[*/]|[*/]\s*1e\d", low))
    if oracle_read and (hardcoded_scale or price_arith):
        extra.append("oracle_value_math")
        if hardcoded_scale and "decimals" not in low:
            extra.append("oracle_hardcoded_scale")

    # (3) cross-chain destination overmint: mint against an incoming message id with
    #     no processed/consumed/replay guard, so the message can be replayed.
    mints = bool(re.search(r"\.\s*mint\s*\(", combined)) or "mint" in {t.lower() for t in transfers}
    msgid_param = any("bytes32" in (p.type or "").lower() for p in fn.parameters) or \
        any(re.search(r"msg.?id|message|nonce", p.name or "", re.I) for p in fn.parameters)
    bridge_ctx = "CrossChainSupply" in etypes
    no_consume_guard = not re.search(r"processed|consumed|usedhash|replay|nonce|seen\b", low)
    if mints and (bridge_ctx or msgid_param) and no_consume_guard:
        extra.append("xchain_overmint")

    return extra


def _invariants(lifecycle, flags, has_collateral, has_division):
    inv = []
    if lifecycle == T.LC_BORROW:
        inv.append(INV_BORROW_CONS)
        if has_collateral:
            inv.append(INV_COLLATERAL)
    elif lifecycle == T.LC_REPAY:
        inv.append(INV_DEBT_RECON)
        if has_collateral:
            inv.append(INV_COLLATERAL)
    elif lifecycle in (T.LC_DEPOSIT, T.LC_DEPOSIT_CONSUME):
        inv.append(INV_DEPOSIT_CONS)
    elif lifecycle in (T.LC_VAULT_DEPOSIT, T.LC_VAULT_WITHDRAW, T.LC_REDEMPTION):
        inv.append(INV_VAULT_SHARE)
    elif lifecycle in (T.LC_SWAP, T.LC_ADAPTER):
        inv.append(INV_SWAP_RECV)
    elif lifecycle == T.LC_CROSS_CHAIN:
        inv.append(INV_XCHAIN)
    if "calldata_route" in flags and INV_CONSENT not in inv:
        inv.append(INV_CONSENT)
    # Shape-driven families (name-independent): an adapter that credits the nominal
    # amount, an oracle read mis-scaled into a value, a bridge that overmints.
    if "credit_no_balance_delta" in flags and INV_SWAP_RECV not in inv:
        inv.append(INV_SWAP_RECV)
    if "oracle_value_math" in flags and INV_ORACLE not in inv:
        inv.append(INV_ORACLE)
    if "xchain_overmint" in flags and INV_XCHAIN not in inv:
        inv.append(INV_XCHAIN)
    return inv


def build_transitions(smap, emap) -> T.TransitionMap:
    bodies = _bodies(smap)
    etypes = emap.types() if emap is not None else set()
    vault_ctx = bool({"Vault", "Share", "ExchangeRate"} & etypes)
    has_collateral = "Collateral" in etypes
    route_funcs = {h.function for h in smap.dataflow_hints
                   if h.tag == SM.TAG_CALLDATA_TO_SWAP_ROUTE}

    tmap = T.TransitionMap(root=smap.root)
    idx = 0
    for c in smap.contracts:
        if c.kind in (SM.KIND_INTERFACE,):
            continue
        for fn in c.functions:
            if fn.mutability in ("view", "pure"):
                continue
            if fn.name == "constructor":
                continue
            if fn.visibility not in ("public", "external"):
                continue
            closure = _closure(smap, fn)
            closure_qns = {f.qualified_name for f in closure}
            combined = "\n".join(bodies[q].body for q in closure_qns
                                 if q in bodies and bodies[q].body)
            transfers = set()
            ext = set()
            writes, reads = set(), set()
            for f in closure:
                transfers |= set(f.transfers)
                ext |= set(f.external_calls)
                writes |= set(f.storage_writes)
                reads |= set(f.storage_reads)
            requires = _requires(combined)
            has_division = bool(re.search(r"[\w\)\]]\s*/\s*[\w\(]", combined))
            flags = []
            if has_division:
                flags.append("has_division")
            if route_funcs & closure_qns:
                flags.append("calldata_route")
            if any(f for f in closure for x in smap.external_calls
                   if x.function == f.qualified_name and x.reentrancy_relevant):
                flags.append("ext_before_write")
            if "balanceof" in combined.lower() and vault_ctx:
                flags.append("balance_based_assets")
            flags += _shape_flags(fn, bodies, combined, transfers, etypes, vault_ctx)

            actor = _actor(fn, requires)
            lifecycle = _lifecycle(fn.name, vault_ctx)
            ai, ao = _assets(transfers)
            status = _status_changes(combined)
            inv = _invariants(lifecycle, flags, has_collateral, has_division)

            idx += 1
            before = f"{actor} initiates {fn.name}; preconditions: " + (
                "; ".join(requires) if requires else "none captured")
            after = "writes [" + ", ".join(sorted(writes)) + "]"
            if ao:
                after += "; assets out: " + ", ".join(ao)
            if ai:
                after += "; assets in: " + ", ".join(ai)
            if status:
                after += "; status: " + ", ".join(status)

            tr = T.StateTransition(
                id=f"ST-{idx:03d}", contract=c.name, function=fn.qualified_name,
                actor=actor, lifecycle=lifecycle, preconditions=requires,
                state_reads=sorted(reads - writes), state_writes=sorted(writes),
                assets_in=ai, assets_out=ao, external_calls=sorted(ext),
                status_changes=status, before_summary=before, after_summary=after,
                possible_invariants=inv, flags=flags, confidence=T.MEDIUM,
            )
            tmap.transitions.append(tr)
    return tmap

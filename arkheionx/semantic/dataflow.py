"""Calldata -> value-affecting-sink data flow (semantic core).

The critical semantic capability: detect when counterparty/attacker-controlled
calldata reaches a sink that affects value — an external call (especially a
swap/route/adapter), a transfer amount, a hash input, or a state write.

This is intraprocedural and heuristic (fallback mode), so hints carry LOW/MEDIUM
confidence. It tracks calldata parameters, their field accesses, and local
variables transitively assigned from them.
"""
from __future__ import annotations

import re

from . import models as M
from .fallback_parser import match_delim

# Field/var names that denote an opaque, route-shaped, counterparty-supplied blob.
_ROUTE_WORDS = re.compile(r"(swapdata|calldata|payload|route|path|data|params|adapterdata|extradata)", re.IGNORECASE)
# Selectors / targets that denote a swap/route/adapter sink.
_SWAP_SELECTOR = re.compile(
    r"(swap|exactinput|exactoutput|multicall|execute|fillorder|exchange|zap|convert|route)",
    re.IGNORECASE)
_SWAP_TARGET = re.compile(r"(router|adapter|swap|dex|pool|zap|aggregator|exchange)", re.IGNORECASE)
_TRANSFER_SEL = {"transfer", "transferfrom", "safetransfer", "safetransferfrom", "sendvalue"}
_HASH_FN = re.compile(r"\b(keccak256|sha256|abi\.encode|abi\.encodePacked)\s*\(")


def _derived_names(fn, body: str) -> set:
    """Calldata param names + transitively assigned local names."""
    derived = {p.name for p in fn.parameters if p.location == "calldata" and p.name}
    # Transitive: <type?> name = <rhs containing a derived name>;
    for _ in range(3):
        added = False
        for m in re.finditer(r"([A-Za-z_]\w*)\s*=\s*([^;]+);", body):
            lhs, rhs = m.group(1), m.group(2)
            if lhs in derived:
                continue
            if any(re.search(r"\b" + re.escape(d) + r"\b", rhs) for d in derived):
                derived.add(lhs)
                added = True
        if not added:
            break
    return derived


def _call_args(body: str, paren_open: int) -> str:
    close = match_delim(body, paren_open, "(", ")")
    return body[paren_open + 1:close]


def _refs_derived(text: str, derived: set) -> str:
    for d in derived:
        if re.search(r"\b" + re.escape(d) + r"\b", text):
            return d
    return ""


def _all_refs(text: str, derived: set) -> list:
    return [d for d in derived if re.search(r"\b" + re.escape(d) + r"\b", text)]


def _origin_expr(body: str, name: str) -> str:
    """Trace ``name`` back to its assignment RHS for a more descriptive source."""
    m = re.search(r"\b" + re.escape(name) + r"\s*=\s*([^;]+);", body)
    if m:
        return m.group(1).strip()
    return name


def build_dataflow(parse) -> list:
    hints = []
    for csem in parse.contracts:
        for fn in csem.functions:
            body_obj = parse.bodies.get(fn.qualified_name)
            if body_obj is None or not body_obj.body:
                continue
            body = body_obj.body
            base = body_obj.body_start_line
            derived = _derived_names(fn, body)
            if not derived:
                continue
            qn = fn.qualified_name
            seen = set()

            def emit(src, sink, skind, sink_off, tag, conf):
                key = (src, sink, skind, tag)
                if key in seen:
                    return
                seen.add(key)
                hints.append(M.DataFlowHint(
                    function=qn, source_expr=src, sink_expr=sink,
                    source_kind=M.SRC_CALLDATA, sink_kind=skind,
                    source_line=fn.line_start,
                    sink_line=base + body.count("\n", 0, sink_off),
                    tag=tag, confidence=conf))

            # External / member calls: target.method( args )
            for m in re.finditer(r"\b([A-Za-z_]\w*)\s*(\([^;{}]*\))?\s*\.\s*([a-z_]\w*)\s*(\{[^}]*\})?\s*\(", body):
                ident, method = m.group(1), m.group(3)
                if ident in ("msg", "block", "tx", "abi", "type", "this", "super"):
                    continue
                paren = body.find("(", m.end() - 1)
                if paren < 0:
                    continue
                args = _call_args(body, paren)
                refs = _all_refs(args, derived)
                if not refs:
                    continue
                target = f"{ident}.{method}"
                sel = method.lower()
                route_ref = next((r for r in refs if _ROUTE_WORDS.search(r)), "")
                is_route = bool(route_ref) or _SWAP_SELECTOR.search(sel) or _SWAP_TARGET.search(ident)
                if sel in _TRANSFER_SEL:
                    src = next((r for r in refs if not _ROUTE_WORDS.search(r)), refs[0])
                    emit(_origin_expr(body, src), target, M.SINK_TRANSFER_AMOUNT, m.start(),
                         M.TAG_CALLDATA_TO_TRANSFER, M.MEDIUM)
                elif is_route:
                    src = route_ref or refs[0]
                    emit(_origin_expr(body, src), target, M.SINK_EXTERNAL_CALL, m.start(),
                         M.TAG_CALLDATA_TO_SWAP_ROUTE, M.MEDIUM)
                else:
                    emit(_origin_expr(body, refs[0]), target, M.SINK_CALL_ARG, m.start(),
                         M.TAG_CALLDATA_TO_EXTERNAL, M.LOW)

            # Hash inputs (consent-relevant: where calldata is bound into a hash).
            for m in _HASH_FN.finditer(body):
                paren = body.find("(", m.start())
                if paren < 0:
                    continue
                args = _call_args(body, paren)
                ref = _refs_derived(args, derived)
                if ref:
                    emit(ref, m.group(1), M.SINK_HASH_INPUT, m.start(), "", M.LOW)

            # State writes fed by calldata.
            for var in fn.storage_writes:
                m = re.search(r"\b" + re.escape(var) + r"\s*(\[[^\]]*\])*\s*=\s*([^;]+);", body)
                if m and _refs_derived(m.group(2), derived):
                    emit(_refs_derived(m.group(2), derived), var, M.SINK_STATE_WRITE,
                         m.start(), "", M.LOW)
    return hints

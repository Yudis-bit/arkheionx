"""External-call extraction with state-write ordering (semantic core).

Records each external/low-level call site and which state writes happen before
and after it. A write *after* an external call flags classic
checks-effects-interactions risk (``reentrancy_relevant``).
"""
from __future__ import annotations

import re

from . import models as M
from .fallback_parser import write_offsets

_CALL_SITE_RE = re.compile(r"\b([A-Za-z_]\w*)\s*(\([^;{}]*\))?\s*\.\s*([a-z_]\w*)\s*(\{[^}]*\})?\s*\(")
_LOWLEVEL_RE = re.compile(r"\.\s*(call|delegatecall|staticcall)\s*(\{[^}]*\})?\s*[({]")
_BUILTINS = {"msg", "block", "tx", "abi", "address", "type", "super", "this", "string", "bytes"}
_NONCALL_METHODS = {"push", "pop", "length"}


def build_external_calls(parse) -> list:
    out = []
    for csem in parse.contracts:
        for fn in csem.functions:
            body_obj = parse.bodies.get(fn.qualified_name)
            if body_obj is None or not body_obj.body:
                continue
            body = body_obj.body
            base = body_obj.body_start_line
            woffs = write_offsets(body, set(fn.storage_writes))

            sites = []  # (offset, target_expr, selector, value_sent)
            for m in _CALL_SITE_RE.finditer(body):
                ident, cast, method, brace = m.group(1), m.group(2), m.group(3), m.group(4)
                if ident in _BUILTINS or method in _NONCALL_METHODS:
                    continue
                target = ident + (cast or "")
                sites.append((m.start(), target, method, bool(brace and "value" in brace)))
            for m in _LOWLEVEL_RE.finditer(body):
                sites.append((m.start(), "<low-level>", m.group(1),
                              bool(m.group(2) and "value" in m.group(2))))

            for off, target, selector, value_sent in sites:
                wbefore = sorted(v for v, o in woffs.items() if o < off)
                wafter = sorted(v for v, o in woffs.items() if o >= off)
                out.append(M.ExternalCall(
                    contract=csem.name, function=fn.qualified_name,
                    target_expr=target, selector=selector, value_sent=value_sent,
                    line=base + body.count("\n", 0, off),
                    writes_before=wbefore, writes_after=wafter,
                    reentrancy_relevant=bool(wafter),
                    confidence=M.MEDIUM,
                ))
    return out

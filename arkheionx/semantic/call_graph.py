"""Call-graph builder for the semantic core.

Resolves the per-function call effects recovered by the parser into typed
``CallEdge`` records: internal (same contract), interface (callee name matches a
known function elsewhere), external (unresolved member call), and low-level.
"""
from __future__ import annotations

import re

from . import models as M


def _line_of_call(body_obj, needle: str) -> int:
    if body_obj is None or not body_obj.body:
        return getattr(body_obj, "body_start_line", 0)
    idx = body_obj.body.find(needle)
    if idx < 0:
        return body_obj.body_start_line
    return body_obj.body_start_line + body_obj.body.count("\n", 0, idx)


def build_call_graph(parse) -> list:
    func_to_contract = {}
    for contract, names in parse.func_names_by_contract.items():
        for nm in names:
            func_to_contract.setdefault(nm, contract)

    edges = {}

    def add(caller, callee, kind, line):
        key = (caller, callee, kind)
        if key not in edges:
            edges[key] = M.CallEdge(caller=caller, callee=callee, kind=kind, line=line,
                                    confidence=M.MEDIUM if kind != M.CALL_EXTERNAL else M.LOW)

    for csem in parse.contracts:
        own = parse.func_names_by_contract.get(csem.name, set())
        for fn in csem.functions:
            caller = fn.qualified_name
            body_obj = parse.bodies.get(caller)
            for callee_name in fn.internal_calls:
                if callee_name in own:
                    add(caller, f"{csem.name}.{callee_name}", M.CALL_INTERNAL,
                        _line_of_call(body_obj, callee_name + "("))
            for ext in fn.external_calls:
                method = ext.split(".")[-1]
                target_contract = func_to_contract.get(method, "")
                if target_contract and target_contract != csem.name:
                    add(caller, f"{target_contract}.{method}", M.CALL_INTERFACE,
                        _line_of_call(body_obj, ext))
                else:
                    add(caller, f"<external>.{method}", M.CALL_EXTERNAL,
                        _line_of_call(body_obj, ext))
            for low in fn.low_level_calls:
                add(caller, f"<external> ({low})", M.CALL_LOWLEVEL,
                    _line_of_call(body_obj, "." + low))
    return list(edges.values())

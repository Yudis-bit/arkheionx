"""Call-graph precision engine for hunter mode.

Builds call edges ONLY from real call evidence in comment-stripped function bodies:
direct internal calls, interface calls, low-level call/delegatecall/staticcall. It
never creates an edge from shared words, comments, import proximity, event names,
variable names, or function-name similarity. Precision over recall: a missed real
edge is acceptable; a fabricated edge is not.

Local/static and read-only.
"""
from __future__ import annotations

import re

from . import models as M
from . import source_scan

# Words that look like a call `name(` but are not a function call.
_NON_CALL = {
    "if", "for", "while", "switch", "catch", "require", "assert", "revert", "return",
    "emit", "new", "function", "modifier", "constructor", "address", "payable", "this",
    "super", "abi", "keccak256", "sha256", "ecrecover", "type", "uint", "uint256",
    "int", "bool", "bytes", "bytes32", "string", "memory", "storage", "calldata",
    "mapping", "struct", "enum", "event", "error", "using", "import", "pragma",
    "unchecked", "do", "else", "try", "selfdestruct", "blockhash", "gasleft",
}
_BUILTIN_NS = {"msg", "block", "tx", "abi", "address", "type", "super", "this", "string", "bytes"}

_DELEGATE_RE = re.compile(r"\.\s*delegatecall\s*[({]")
_STATIC_RE = re.compile(r"\.\s*staticcall\s*[({]")
_LOWLEVEL_RE = re.compile(r"\.\s*call\s*[({]")
# someVar.method(  — simple member call.
_MEMBER_RE = re.compile(r"\b([A-Za-z_]\w*)\s*\.\s*([a-z_]\w*)\s*\(")
# TypeName(...).method(  — cast-then-call (interface call).
_CAST_CALL_RE = re.compile(r"\b([A-Z]\w*)\s*\([^;{}]*?\)\s*\.\s*([a-z_]\w*)\s*\(")
# bare name(  — candidate internal call.
_BARE_RE = re.compile(r"(^|[^.\w])([a-z_]\w*)\s*\(")


def build_call_graph(review_map, sources: dict) -> list:
    # Known internal function names per contract, and a global function->contract map.
    funcs_by_contract: dict[str, set] = {}
    func_to_contract: dict[str, str] = {}
    parsed: dict[str, list] = {}
    for contract, (path, text) in sources.items():
        fns = source_scan.find_functions(text)
        parsed[contract] = fns
        names = {fn.name for fn in fns}
        funcs_by_contract[contract] = names
        for fn in fns:
            func_to_contract.setdefault(fn.name, contract)

    edges: dict[tuple, M.CallEdge] = {}

    def _add(caller: str, callee: str, status: str, line: int) -> None:
        key = (caller, callee, status)
        if key not in edges:
            edges[key] = M.CallEdge(caller=caller, callee=callee, status=status, evidence_line=line)

    for contract, (path, text) in sources.items():
        own_funcs = funcs_by_contract.get(contract, set())
        for fn in parsed.get(contract, []):
            if not fn.body:
                continue
            caller = f"{contract}.{fn.name}"
            base_line = fn.line

            for rx, status in ((_DELEGATE_RE, M.DELEGATECALL),
                               (_STATIC_RE, M.STATICCALL),
                               (_LOWLEVEL_RE, M.LOW_LEVEL_CALL)):
                if rx.search(fn.body):
                    _add(caller, f"<external> ({status.lower()})", status, base_line)

            # Cast-then-call interface calls: TypeName(x).method(
            for m in _CAST_CALL_RE.finditer(fn.body):
                method = m.group(2)
                if method in _NON_CALL:
                    continue
                target_contract = func_to_contract.get(method, "")
                callee = f"{target_contract}.{method}" if target_contract else f"<external>.{method}"
                _add(caller, callee, M.INTERFACE_CALL, base_line)

            # Simple member calls: ident.method(
            for m in _MEMBER_RE.finditer(fn.body):
                ident, method = m.group(1), m.group(2)
                if ident in _BUILTIN_NS or method in _NON_CALL:
                    continue
                target_contract = func_to_contract.get(method, "")
                callee = f"{target_contract}.{method}" if target_contract else f"{ident}.{method}"
                _add(caller, callee, M.INTERFACE_CALL, base_line)

            # Bare internal calls: name(  — only if name is a real function here.
            for m in _BARE_RE.finditer(fn.body):
                name = m.group(2)
                if name in _NON_CALL or name == fn.name:
                    continue
                if name in own_funcs:
                    _add(caller, f"{contract}.{name}", M.DIRECT_CALL, base_line)

    return list(edges.values())


def call_edges_for_contract(edges: list, contract: str) -> list:
    contract = (contract or "").lower()
    return [e for e in edges if e.caller.split(".")[0].lower() == contract]

"""DeFi entity detector (Layer 2).

Walks the semantic map's symbols (contract names, state variables, functions,
struct names and fields) and aggregates them into economic entities using the
name/shape rules in :mod:`entities`.
"""
from __future__ import annotations

from . import entities as E


def _symbols(smap):
    """Yield (kind, name, contract, line, file) tuples to classify."""
    for c in smap.contracts:
        yield ("contract", c.name, c.name, c.line_start, c.file)
        for sv in c.state_variables:
            yield ("state_var", sv.name, c.name, sv.line, c.file)
            # also classify the declared type (e.g., IERC20 -> token-ish)
        for fn in c.functions:
            yield ("function", fn.name, c.name, fn.line_start, c.file)
        for st in c.structs:
            sname = st.get("name") if isinstance(st, dict) else st
            yield ("struct", sname, c.name, c.line_start, c.file)
            if isinstance(st, dict):
                for fld in st.get("fields", []):
                    yield ("struct_field", fld.get("name", ""), c.name, c.line_start, c.file)


def build_defi_entities(smap) -> E.DefiEntityMap:
    agg = {}  # entity_type -> DefiEntity
    for kind, name, contract, line, file in _symbols(smap):
        if not name:
            continue
        low = name.lower()
        for rx, etype in E.DETECTION_RULES:
            if rx.search(low):
                ent = agg.get(etype)
                if ent is None:
                    ent = E.DefiEntity(name=etype, entity_type=etype,
                                       value_direction=E._DIRECTION.get(etype, E.DIR_NONE))
                    agg[etype] = ent
                sym = {"kind": kind, "name": name, "contract": contract, "line": line}
                if sym not in ent.source_symbols:
                    ent.source_symbols.append(sym)
                    ent.evidence_lines.append(f"{file}:{line}")
                if contract not in ent.related_contracts:
                    ent.related_contracts.append(contract)

    # Confidence from independent evidence; warn on single weak signals.
    for ent in agg.values():
        n = len(ent.source_symbols)
        if n >= 2:
            ent.confidence = E.HIGH
        elif n == 1:
            ent.confidence = E.MEDIUM
            if ent.entity_type in (E.TOKEN, E.QUEUE, E.GOVERNANCE_POWER, E.CROSS_CHAIN_SUPPLY):
                ent.confidence = E.LOW
                ent.warnings.append("single weak signal; low confidence")

    # Stable ordering: by descending evidence then name.
    entities = sorted(agg.values(), key=lambda e: (-len(e.source_symbols), e.entity_type))
    emap = E.DefiEntityMap(root=smap.root, entities=entities)
    return emap

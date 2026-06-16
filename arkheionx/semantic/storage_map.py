"""Storage access map for the semantic core.

Turns per-function storage read/write effects into line-precise
``StorageAccess`` records by scanning the recovered function bodies.
"""
from __future__ import annotations

import re

from . import models as M
from .fallback_parser import write_offsets


def _first_write_line(body_obj, var: str) -> int:
    if body_obj is None or not body_obj.body:
        return getattr(body_obj, "body_start_line", 0)
    offs = write_offsets(body_obj.body, {var})
    if var not in offs:
        return body_obj.body_start_line
    return body_obj.body_start_line + body_obj.body.count("\n", 0, offs[var])


def _first_read_line(body_obj, var: str) -> int:
    if body_obj is None or not body_obj.body:
        return getattr(body_obj, "body_start_line", 0)
    m = re.search(r"\b" + re.escape(var) + r"\b", body_obj.body)
    if not m:
        return body_obj.body_start_line
    return body_obj.body_start_line + body_obj.body.count("\n", 0, m.start())


def build_storage_map(parse) -> list:
    out = []
    for csem in parse.contracts:
        for fn in csem.functions:
            body_obj = parse.bodies.get(fn.qualified_name)
            is_deleted = set()
            if body_obj is not None and body_obj.body:
                for m in re.finditer(r"\bdelete\s+([A-Za-z_]\w*)", body_obj.body):
                    is_deleted.add(m.group(1))
            for var in fn.storage_writes:
                kind = "delete" if var in is_deleted else "write"
                out.append(M.StorageAccess(
                    variable=var, kind=kind, function=fn.qualified_name,
                    line=_first_write_line(body_obj, var), expression=f"{var} (write)",
                    confidence=M.MEDIUM))
            for var in fn.storage_reads:
                out.append(M.StorageAccess(
                    variable=var, kind="read", function=fn.qualified_name,
                    line=_first_read_line(body_obj, var), expression=f"{var} (read)",
                    confidence=M.MEDIUM))
    return out

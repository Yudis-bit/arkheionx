"""Semantic core orchestrator.

Builds a :class:`SemanticMap` for a target. Picks AST mode when artifacts are
ingestible (deferred in V10) and otherwise runs the fallback parser, then derives
the call graph, storage map, external calls, and calldata->sink data flow.
"""
from __future__ import annotations

from pathlib import Path

from . import ast_loader, call_graph, dataflow, external_calls, models as M, source_index, storage_map
from .fallback_parser import parse_sources


def build_semantic_map(
    root: Path | str,
    *,
    include_paths: list | None = None,
    include_deps: bool = False,
    include_tests: bool = False,
) -> M.SemanticMap:
    root = Path(root)
    sources = source_index.discover_sources(
        root, include_paths=include_paths, include_deps=include_deps, include_tests=include_tests)

    availability = ast_loader.detect_artifacts(root)
    ast_parse = ast_loader.load_ast_map(root)  # deferred -> None

    smap = M.SemanticMap(root=str(root))
    if ast_parse is not None:  # pragma: no cover - AST ingestion deferred
        parse = ast_parse
        smap.mode = M.MODE_AST
        smap.confidence = M.HIGH
    else:
        parse = parse_sources(sources)
        smap.mode = M.MODE_FALLBACK
        if availability.available:
            smap.warnings.extend(availability.notes)

    smap.contracts = parse.contracts
    smap.call_edges = call_graph.build_call_graph(parse)
    smap.storage_accesses = storage_map.build_storage_map(parse)
    smap.external_calls = external_calls.build_external_calls(parse)
    smap.dataflow_hints = dataflow.build_dataflow(parse)
    smap.files_indexed = len(sources)
    smap.warnings.extend(parse.warnings)

    total_fns = sum(len(c.functions) for c in smap.contracts)
    if not smap.contracts or total_fns == 0:
        smap.confidence = M.LOW
        smap.warnings.append("low semantic confidence: no parseable functions found")
    elif smap.mode == M.MODE_FALLBACK:
        smap.confidence = M.MEDIUM

    # Keep a transient handle to the parse side-table for downstream layers that
    # want raw function bodies (not serialized into the SemanticMap).
    smap._parse = parse  # type: ignore[attr-defined]
    return smap

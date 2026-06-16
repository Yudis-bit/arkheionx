"""Semantic core orchestrator.

Builds a :class:`SemanticMap` for a target. Picks AST mode when artifacts are
ingestible (deferred in V10) and otherwise runs the fallback parser, then derives
the call graph, storage map, external calls, and calldata->sink data flow.
"""
from __future__ import annotations

from pathlib import Path

from arkheionx.ingest.repo_detector import inspect_repository

from . import artifact_loader, call_graph, dataflow, external_calls, models as M, storage_map
from .fallback_parser import parse_sources


def build_semantic_map(
    root: Path | str,
    *,
    include_paths: list | None = None,
    include_deps: bool = False,
    include_tests: bool = False,
    include_scripts: bool = False,
    framework: str = "auto",
    build_artifacts: Path | str | None = None,
    solidity_root: Path | str | None = None,
) -> M.SemanticMap:
    root = Path(root)
    ingest_summary, discovery, artifact_discovery = inspect_repository(
        root,
        framework=framework,
        build_artifacts=build_artifacts,
        solidity_root=solidity_root,
        include_paths=include_paths,
        include_deps=include_deps,
        include_tests=include_tests,
        include_scripts=include_scripts,
    )
    sources = list(discovery.sources)
    source_rels = {source.rel for source in sources}
    artifact_facts = artifact_loader.load_artifacts(
        root,
        build_artifacts=build_artifacts,
        discovery=artifact_discovery,
        source_rels=source_rels,
    )
    existing_rel = {source.rel for source in sources}
    sources.extend(source for source in artifact_facts.virtual_sources if source.rel not in existing_rel)

    smap = M.SemanticMap(root=str(root))
    parse = parse_sources(sources)
    source_contract_names = {contract.name for contract in parse.contracts}
    source_contract_count = len(parse.contracts)
    smap.mode = M.MODE_FALLBACK
    smap.artifact_mode = artifact_facts.mode
    smap.warnings.extend(artifact_facts.warnings)

    smap.contracts = artifact_loader.merge_contracts(parse.contracts, artifact_facts.contracts)
    smap.call_edges = call_graph.build_call_graph(parse)
    smap.storage_accesses = storage_map.build_storage_map(parse)
    smap.external_calls = external_calls.build_external_calls(parse)
    smap.dataflow_hints = dataflow.build_dataflow(parse)
    smap.files_indexed = discovery.files_indexed
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
    smap._source_text = "\n".join(source.text for source in sources)  # type: ignore[attr-defined]
    ingest_summary.contracts_indexed = len(smap.contracts)
    ingest_summary.real_contracts_indexed = source_contract_count
    ingest_summary.artifact_only_contracts_indexed = sum(
        1 for contract in smap.contracts if contract.name not in source_contract_names
    )
    ingest_summary.stale_artifacts_ignored = artifact_facts.stale_artifacts_ignored
    ingest_summary.sample_artifacts_ignored = artifact_facts.sample_artifacts_ignored
    if ingest_summary.contracts_indexed > 0 and ingest_summary.solidity_files_indexed == 0:
        ingest_summary.warnings.append(
            "ARTIFACT_ONLY_WITH_NO_SOURCE_WARNING: contracts were indexed only from compiler artifacts."
        )
    if artifact_facts.stale_artifacts_ignored or artifact_facts.sample_artifacts_ignored:
        ingest_summary.warnings.append(
            "STALE_ARTIFACT_IGNORED: ignored compiler artifacts without live repository source."
        )
    if ingest_summary.real_contracts_indexed == 0:
        ingest_summary.warnings.append(
            "ZERO_REAL_CONTRACTS_INDEXED: no live Solidity source contracts were indexed."
        )
    ingest_summary.warnings = list(dict.fromkeys(ingest_summary.warnings + smap.warnings))
    for warning in ingest_summary.warnings:
        if (
            warning.startswith("ZERO_REAL_CONTRACTS_INDEXED")
            or warning.startswith("ARTIFACT_ONLY_WITH_NO_SOURCE_WARNING")
            or warning.startswith("STALE_ARTIFACT_IGNORED")
        ) and warning not in smap.warnings:
            smap.warnings.append(warning)
    smap._ingest_summary = ingest_summary  # type: ignore[attr-defined]
    smap._artifact_facts = artifact_facts  # type: ignore[attr-defined]
    return smap

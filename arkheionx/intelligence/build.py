"""Build a :class:`ProtocolModel` from existing analysis and review-map outputs.

Internal builder infrastructure only. It reads existing in-memory structures
(protocol ``Analysis`` objects, review-map ``ReviewMap`` objects, or their dict
payloads) and produces one normalized intelligence model. It never mutates its
inputs, adds no CLI command, writes no artifact, and changes no public schema.

Legacy identity (display targets, ``stable_id``/``qualified_id``/``target_id``,
``vp-*``/``asm-*``/``gap-*``/``proof-*``/``ev-*`` IDs, and receipt/package IDs)
is preserved as node aliases, never replaced. Links are only created when the
source data resolves unambiguously; missing links stay empty rather than
invented. The model organizes local/static review context only -- never
confirmed vulnerabilities, final severity, or submission readiness.
"""
from __future__ import annotations

from pathlib import Path

from . import ids
from .model import (
    HEURISTIC,
    AssumptionNode,
    ContractNode,
    EvidenceLinkNode,
    FunctionNode,
    ProofSuggestionNode,
    ProtocolModel,
    TestGapNode,
    ValuePathNode,
)


# --- read-only access helpers (work for dataclasses, objects, and dicts) ----

def _get(obj: object, name: str, default: object = None) -> object:
    if isinstance(obj, dict):
        return obj.get(name, default)
    return getattr(obj, name, default)


def _first(obj: object, *names: str, default: str = "") -> str:
    for name in names:
        value = _get(obj, name, None)
        if value not in (None, ""):
            return value
    return default


def _section(source: object, name: str) -> list:
    value = _get(source, name, []) or []
    return list(value) if isinstance(value, (list, tuple)) else []


def _aliases(**pairs: object) -> dict:
    return {key: value for key, value in pairs.items() if value}


def _display(value: object) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    return text.split(":")[-1].split("#")[0].split("(")[0]


def _source_location(function_like: object, file_path: str) -> str:
    stable = str(_get(function_like, "stable_id", "") or "")
    if stable:
        return stable
    line_range = _get(function_like, "line_range", None)
    if file_path and isinstance(line_range, (list, tuple)) and line_range:
        start, end = (list(line_range) + [0, 0])[:2]
        return f"{file_path}#L{start}-L{end}"
    line = _get(function_like, "line", 0)
    if file_path and line:
        return f"{file_path}#L{line}"
    return file_path


# --- node builders (shared by both entry points) ---------------------------

def _contract_node(contract_like: object, repo_path: str) -> tuple[str, ContractNode]:
    name = _first(contract_like, "contract_name", "name")
    path = _first(contract_like, "file_path", "path")
    cid = ids.contract_id(path, name, repo_path)

    roles = list(_get(contract_like, "roles", None) or [])
    if not roles:
        role = _get(contract_like, "role", None)
        roles = [role] if role else []
    value_state_vars = list(_get(contract_like, "value_state_vars", None) or [])
    value_holding = bool(
        _get(contract_like, "value_holding", False)
        or _get(contract_like, "value_sensitive", False)
        or value_state_vars
    )
    metadata: dict = {}
    if value_state_vars:
        metadata["value_state_vars"] = value_state_vars
    evidence_level = _get(contract_like, "evidence_level", None)
    if evidence_level:
        metadata["evidence_level"] = evidence_level

    node = ContractNode(
        contract_id=cid,
        name=name,
        path=path,
        kind=_first(contract_like, "kind", "source_kind", default="contract"),
        roles=roles,
        value_holding=value_holding,
        confidence=_first(contract_like, "confidence", default="medium"),
        aliases=_aliases(contract_name=name),
        metadata=metadata,
    )
    return name, node


def _function_node(function_like: object, contract_id_value: str, repo_path: str) -> FunctionNode:
    contract = _first(function_like, "contract_name", "contract")
    fname = _first(function_like, "function_name", "name")
    file_path = _first(function_like, "file_path", "path")
    display = _first(function_like, "display_id") or (f"{contract}.{fname}" if contract and fname else fname)

    signature = _first(function_like, "signature")
    metadata: dict = {}
    if signature:
        signature_for_id = signature
    else:
        signature_for_id = display or fname
        metadata["signature_source"] = "display_name"
        metadata["signature_confidence"] = "low"
    visibility = _get(function_like, "visibility", None)
    if visibility:
        metadata["visibility"] = visibility

    stable_id = str(_get(function_like, "stable_id", "") or "")
    roles = list(_get(function_like, "role_surface", None) or _get(function_like, "risk_signals", None) or [])
    if not roles:
        role = _get(function_like, "role", None)
        roles = [role] if role else []

    return FunctionNode(
        function_id=ids.function_id(contract_id_value, signature_for_id),
        contract_id=contract_id_value,
        signature=signature_for_id,
        display_name=display,
        source_location=_source_location(function_like, file_path),
        mutability=_first(function_like, "mutability", default="unknown"),
        value_sensitivity=_first(function_like, "value_sensitivity", "value_direction", default="unknown"),
        role_surface=roles,
        confidence=_first(function_like, "confidence", default="medium"),
        aliases=_aliases(
            display_id=display,
            review_map_target=display,
            stable_id=stable_id,
            qualified_id=str(_get(function_like, "qualified_id", "") or ""),
            target_id=stable_id,
            legacy_function_id=str(_get(function_like, "function_id", "") or ""),
        ),
        metadata=metadata,
    )


def _contracts_and_functions(
    contracts_src: list, functions_src: list, repo_path: str
) -> tuple[list[ContractNode], list[FunctionNode], dict]:
    contract_nodes: list[ContractNode] = []
    cid_by_name: dict[str, str] = {}
    for contract_like in contracts_src:
        name, node = _contract_node(contract_like, repo_path)
        contract_nodes.append(node)
        if name:
            cid_by_name[name] = node.contract_id

    function_nodes: list[FunctionNode] = []
    for function_like in functions_src:
        contract = _first(function_like, "contract_name", "contract")
        file_path = _first(function_like, "file_path", "path")
        cid = cid_by_name.get(contract) or ids.contract_id(file_path, contract, repo_path)
        function_nodes.append(_function_node(function_like, cid, repo_path))
    return contract_nodes, function_nodes, cid_by_name


# --- public (internal) entry points -----------------------------------------

def build_protocol_model_from_analysis(analysis: object, repo_path: str | Path) -> ProtocolModel:
    """Build a ProtocolModel from a protocol ``Analysis`` object or dict."""

    repo = str(repo_path)
    contracts_src = _section(analysis, "contracts")
    functions_src = _section(analysis, "functions")
    contract_nodes, function_nodes, _ = _contracts_and_functions(contracts_src, functions_src, repo)
    return ProtocolModel(
        protocol_id=ids.protocol_id(repo),
        repo_path=repo,
        generated_at=str(_get(analysis, "generated_at", "") or ""),
        contracts=contract_nodes,
        functions=function_nodes,
    )


def build_protocol_model_from_review_map(review_map: object, repo_path: str | Path) -> ProtocolModel:
    """Build a ProtocolModel from a ``ReviewMap`` object or review-map dict payload."""

    repo = str(repo_path) or str(_get(review_map, "repo_path", "") or "")
    contract_nodes, function_nodes, _ = _contracts_and_functions(
        _section(review_map, "contracts"), _section(review_map, "functions"), repo
    )

    fids_by_display: dict[str, set] = {}
    for node in function_nodes:
        if node.display_name:
            fids_by_display.setdefault(node.display_name, set()).add(node.function_id)

    def resolve(display: object) -> str:
        text = str(display or "").strip()
        if not text or "." not in text:
            return ""
        hits = fids_by_display.get(text, set())
        return next(iter(hits)) if len(hits) == 1 else ""

    # Assumptions (built first so value paths can reference new IDs).
    assumption_nodes: list[AssumptionNode] = []
    assumption_by_id: dict[str, AssumptionNode] = {}
    aid_by_legacy: dict[str, str] = {}
    for asm in _section(review_map, "assumptions"):
        legacy = str(_get(asm, "id", "") or "")
        atype = _first(asm, "category", "assumption_type", default="general")
        used_by = list(_get(asm, "used_by", None) or [])
        linked_fids: list[str] = []
        for target in used_by:
            fid = resolve(target)
            if fid and fid not in linked_fids:
                linked_fids.append(fid)
        aid = ids.assumption_id(atype, linked_fids[0] if linked_fids else "", legacy)
        node = AssumptionNode(
            assumption_id=aid,
            assumption_type=atype,
            description=_first(asm, "description", "title"),
            linked_function_ids=linked_fids,
            evidence_level=_first(asm, "evidence_level", default=HEURISTIC),
            aliases=_aliases(id=legacy),
            metadata={"used_by": used_by, "status": _get(asm, "status", "") or ""},
        )
        assumption_nodes.append(node)
        assumption_by_id[aid] = node
        if legacy:
            aid_by_legacy[legacy] = aid

    # Value paths.
    value_path_nodes: list[ValuePathNode] = []
    vpid_by_legacy: dict[str, str] = {}
    for vp in _section(review_map, "value_paths"):
        legacy = str(_get(vp, "id", "") or "")
        entry = resolve(_get(vp, "entry_function", ""))
        exit_fn = resolve(_get(vp, "exit_function", ""))
        label = str(_get(vp, "label", "") or "")
        legacy_asms = list(_get(vp, "assumptions", None) or [])
        new_asms = [aid_by_legacy[a] for a in legacy_asms if a in aid_by_legacy]
        vpid = ids.value_path_id(entry, exit_fn, label or legacy)
        value_path_nodes.append(ValuePathNode(
            value_path_id=vpid,
            entry_function_id=entry,
            exit_function_id=exit_fn,
            label=label,
            assets=list(_get(vp, "assets", None) or []),
            conditions=list(_get(vp, "conditions", None) or []),
            assumptions=new_asms,
            priority=_first(vp, "review_priority", "priority", default="low"),
            aliases=_aliases(
                id=legacy,
                entry_function=str(_get(vp, "entry_function", "") or ""),
                exit_function=str(_get(vp, "exit_function", "") or ""),
            ),
            metadata={
                "test_coverage_hint": _get(vp, "test_coverage_hint", "") or "",
                "evidence_level": _get(vp, "evidence_level", "") or "",
                "legacy_assumptions": legacy_asms,
            },
        ))
        if legacy:
            vpid_by_legacy[legacy] = vpid
        for aid in new_asms:
            asm_node = assumption_by_id.get(aid)
            if asm_node is not None and vpid not in asm_node.linked_value_path_ids:
                asm_node.linked_value_path_ids.append(vpid)

    # Test gaps.
    test_gap_nodes: list[TestGapNode] = []
    gap_by_id: dict[str, TestGapNode] = {}
    gid_by_legacy: dict[str, str] = {}
    for gap in _section(review_map, "test_gaps"):
        legacy = str(_get(gap, "id", "") or "")
        rel_fn = resolve(_get(gap, "related_function", ""))
        scenario = _first(gap, "suggested_test", "title", "description")
        gid = ids.test_gap_id(rel_fn, scenario, legacy)
        node = TestGapNode(
            test_gap_id=gid,
            linked_function_id=rel_fn,
            scenario=scenario,
            priority=_first(gap, "priority", default="low"),
            confidence=_first(gap, "confidence", default="low"),
            aliases=_aliases(id=legacy),
            metadata={
                "related_value_path_id": vpid_by_legacy.get(str(_get(gap, "related_value_path", "") or ""), ""),
                "status": _get(gap, "status", "") or "",
                "evidence_level": _get(gap, "evidence_level", "") or "",
            },
        )
        test_gap_nodes.append(node)
        gap_by_id[gid] = node
        if legacy:
            gid_by_legacy[legacy] = gid

    # Proof suggestions.
    proof_suggestion_nodes: list[ProofSuggestionNode] = []
    for proof in _section(review_map, "proof_suggestions"):
        legacy = str(_get(proof, "id", "") or "")
        target_fid = resolve(_get(proof, "target", ""))
        rel_gap_legacy = str(_get(proof, "related_test_gap", "") or "")
        linked_gap = gid_by_legacy.get(rel_gap_legacy, "")
        psid = ids.proof_suggestion_id(linked_gap or rel_gap_legacy, target_fid, legacy)
        proof_suggestion_nodes.append(ProofSuggestionNode(
            proof_suggestion_id=psid,
            linked_test_gap_id=linked_gap,
            target_function_id=target_fid,
            objective=str(_get(proof, "objective", "") or ""),
            setup=list(_get(proof, "setup", None) or []),
            action=str(_get(proof, "action", "") or ""),
            assertions=list(_get(proof, "assertions", None) or []),
            aliases=_aliases(id=legacy, related_assumption=str(_get(proof, "related_assumption", "") or "")),
        ))
        if linked_gap in gap_by_id:
            gap_by_id[linked_gap].proof_suggestion_id = psid

    # Evidence links (receipt/package IDs preserved; receipt node lists stay empty).
    evidence_link_nodes: list[EvidenceLinkNode] = []
    for link in _section(review_map, "evidence_links"):
        legacy = str(_get(link, "id", "") or "")
        kind = _first(link, "artifact_kind", "source")
        target_disp = _first(link, "target", "related_target") or _display(_get(link, "target_id"))
        target_fid = resolve(target_disp)
        evidence_link_nodes.append(EvidenceLinkNode(
            evidence_link_id=ids.evidence_link_id(kind, target_fid, legacy),
            linked_target_function_id=target_fid,
            linked_artifact_kind=kind,
            linked_artifact_path=str(_get(link, "artifact_path", "") or ""),
            evidence_package_id=str(_get(link, "evidence_package_id", "") or ""),
            proof_receipt_id=str(_get(link, "proof_receipt_id", "") or ""),
            trace_receipt_id=str(_get(link, "trace_receipt_id", "") or ""),
            report_id=str(_get(link, "report_id", "") or ""),
            evidence_level=_first(link, "evidence_level", default=HEURISTIC),
            aliases=_aliases(id=legacy, target=target_disp, target_id=str(_get(link, "target_id", "") or "")),
            metadata={"readiness": _get(link, "readiness", "") or ""},
        ))

    return ProtocolModel(
        protocol_id=ids.protocol_id(repo),
        repo_path=repo,
        generated_at=str(_get(review_map, "generated_at", "") or ""),
        contracts=contract_nodes,
        functions=function_nodes,
        value_paths=value_path_nodes,
        assumptions=assumption_nodes,
        test_gaps=test_gap_nodes,
        proof_suggestions=proof_suggestion_nodes,
        evidence_links=evidence_link_nodes,
    )


# --- resolution helpers ------------------------------------------------------

def resolve_function_id_by_alias(model: ProtocolModel, alias: str) -> str:
    """Resolve a function_id by exact match only (no fuzzy/substring matching).

    Order: function_id, then alias values, then display_name, then signature.
    Returns an empty string for an empty alias or any ambiguous match.
    """

    alias = str(alias or "")
    if not alias:
        return ""
    selectors = (
        lambda f: f.function_id == alias,
        lambda f: alias in set((f.aliases or {}).values()),
        lambda f: f.display_name == alias,
        lambda f: f.signature == alias,
    )
    for selector in selectors:
        matches = [f.function_id for f in model.functions if selector(f)]
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            return ""
    return ""


def index_functions_by_alias(model: ProtocolModel) -> dict:
    """Map every function_id, alias value, display_name, and signature to function_ids."""

    index: dict[str, list[str]] = {}
    for function in model.functions:
        keys = set((function.aliases or {}).values())
        keys.update({function.function_id, function.display_name, function.signature})
        for key in keys:
            if not key:
                continue
            bucket = index.setdefault(key, [])
            if function.function_id not in bucket:
                bucket.append(function.function_id)
    return index


def protocol_model_to_dict(model: ProtocolModel) -> dict:
    """Return a plain, JSON-ready dict for the model."""

    return model.to_dict()

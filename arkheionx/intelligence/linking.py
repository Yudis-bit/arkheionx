"""Reasoning-link helpers for the protocol intelligence model (v3.5, Agent 5).

Connect assumptions, test gaps, proof suggestions, and value paths through the
stable IDs already present on a :class:`ProtocolModel`. Linking is exact-ID only
(no fuzzy or substring matching); an ambiguous or missing relationship stays
empty rather than invented. These helpers mutate the passed model in place and
return it, so they are idempotent (re-running adds nothing new) and
deterministic (same input model -> same links). They preserve every existing
field, alias, and link, and add review-context structure only -- never confirmed
vulnerabilities, severity, or submission readiness.
"""
from __future__ import annotations

import copy

from . import ids
from .build import resolve_function_id_by_alias
from .model import (
    HEURISTIC,
    EvidenceLinkNode,
    EvidencePackageNode,
    ProofReceiptNode,
    ProtocolModel,
    ReportDraftNode,
    TraceReceiptNode,
)


def _unique(values: list[str]) -> str:
    """Return the single distinct non-empty value, or '' for 0 or >1 (no overlink)."""

    distinct = {v for v in values if v}
    return next(iter(distinct)) if len(distinct) == 1 else ""


def link_assumptions_to_value_paths(model: ProtocolModel) -> ProtocolModel:
    """Back-link each assumption to value paths that reference it (exact id)."""

    by_id = {a.assumption_id: a for a in model.assumptions}
    for vp in model.value_paths:
        for aid in vp.assumptions:
            asm = by_id.get(aid)
            if asm is not None and vp.value_path_id and vp.value_path_id not in asm.linked_value_path_ids:
                asm.linked_value_path_ids.append(vp.value_path_id)
    return model


def link_test_gaps_to_assumptions(model: ProtocolModel) -> ProtocolModel:
    """Set test_gap.linked_assumption_id when exactly one assumption shares its function."""

    by_function: dict[str, list[str]] = {}
    for asm in model.assumptions:
        for fid in asm.linked_function_ids:
            if fid:
                by_function.setdefault(fid, []).append(asm.assumption_id)
    for gap in model.test_gaps:
        if gap.linked_assumption_id or not gap.linked_function_id:
            continue
        gap.linked_assumption_id = _unique(by_function.get(gap.linked_function_id, []))
    return model


def link_proof_suggestions_to_test_gaps(model: ProtocolModel) -> ProtocolModel:
    """Back-link each test gap to its proof suggestion by exact test_gap_id."""

    by_gap: dict[str, list[str]] = {}
    for ps in model.proof_suggestions:
        if ps.linked_test_gap_id:
            by_gap.setdefault(ps.linked_test_gap_id, []).append(ps.proof_suggestion_id)
    for gap in model.test_gaps:
        if gap.proof_suggestion_id:
            continue
        gap.proof_suggestion_id = _unique(by_gap.get(gap.test_gap_id, []))
    return model


def link_reasoning(model: ProtocolModel) -> ProtocolModel:
    """Apply every reasoning link in place and return the same model.

    Order is irrelevant to the result (each pass is independent and idempotent):
    value-path -> assumption back-links, test-gap -> assumption, and
    test-gap <-> proof-suggestion.
    """

    link_assumptions_to_value_paths(model)
    link_test_gaps_to_assumptions(model)
    link_proof_suggestions_to_test_gaps(model)
    return model


# --- artifact linkage (v3.5, Agent 6) ---------------------------------------
#
# Connect v3.4 proof, trace, evidence-package, report-draft, and evidence-link
# artifacts to the model by populating the receipt/package/report/link node
# lists. Linkage is additive and exact-only: old receipt/package/report/link IDs
# are preserved verbatim, target functions resolve only by exact alias, and
# evidence levels, statuses, readiness, and report review state are copied
# unchanged (never promoted, never invented). Re-linking an artifact already in
# the model is a no-op (dedupe by primary ID), so these helpers are idempotent
# and deterministic, and they never mutate the input payloads.


def _alias_map(**pairs: object) -> dict:
    return {key: str(value) for key, value in pairs.items() if value}


def _display(value: object) -> str:
    text = str(value or "").strip()
    return text.split(":")[-1].split("#")[0].split("(")[0] if text else ""


def _resolve_target(model: ProtocolModel, *candidates: object) -> str:
    """Resolve a function_id from the first candidate (raw or display-extracted) that
    exact-matches exactly one function. Ambiguous or missing candidates are skipped."""

    for candidate in candidates:
        for text in (str(candidate or "").strip(), _display(candidate)):
            if text:
                fid = resolve_function_id_by_alias(model, text)
                if fid:
                    return fid
    return ""


def _resolve_proof_suggestion_id(model: ProtocolModel, legacy_id: object) -> str:
    """Map a legacy/new proof_suggestion id to a ProofSuggestionNode id (exact, unique)."""

    legacy = str(legacy_id or "")
    if not legacy:
        return ""
    matches = [
        ps.proof_suggestion_id
        for ps in model.proof_suggestions
        if ps.proof_suggestion_id == legacy or (ps.aliases or {}).get("id") == legacy
    ]
    return matches[0] if len(matches) == 1 else ""


def _manifest_source(payload: dict, kind: str) -> dict:
    sources = ((payload.get("manifest", {}) or {}).get("sources", []) or [])
    return next((s for s in sources if isinstance(s, dict) and s.get("kind") == kind), {})


def link_proof_receipts_to_model(model: ProtocolModel, proof_payloads: list[dict]) -> ProtocolModel:
    """Add a ProofReceiptNode per proof payload (old proof_receipt_id preserved)."""

    existing = {n.proof_receipt_id for n in model.proof_receipts}
    for payload in proof_payloads or []:
        rid = str(payload.get("proof_receipt_id", "") or "")
        if not rid or rid in existing:
            continue
        existing.add(rid)
        trace_ref = payload.get("trace", {}) or {}
        source_artifacts = {
            key: value
            for key, value in {
                "proof_json": str(payload.get("proof_json", "") or ""),
                "raw_output": str((payload.get("test_result", {}) or {}).get("raw_output_path", "") or ""),
                "trace_json_path": str(trace_ref.get("trace_json_path", "") or ""),
            }.items()
            if value
        }
        model.proof_receipts.append(ProofReceiptNode(
            proof_receipt_id=rid,
            linked_proof_suggestion_id=_resolve_proof_suggestion_id(model, payload.get("proof_suggestion_id")),
            target_function_id=_resolve_target(
                model, payload.get("review_map_target"), payload.get("target_id"), payload.get("target")),
            status=str(payload.get("status", "") or ""),
            evidence_level=str(payload.get("evidence_level", "") or HEURISTIC),
            source_artifacts=source_artifacts,
            aliases=_alias_map(
                proof_receipt_id=rid,
                target=payload.get("target"),
                target_id=payload.get("target_id"),
                review_map_target=payload.get("review_map_target"),
                related_test_gap=payload.get("related_test_gap"),
                proof_suggestion_id=payload.get("proof_suggestion_id"),
            ),
        ))
    return model


def link_evidence_packages_to_model(model: ProtocolModel, evidence_payloads: list[dict]) -> ProtocolModel:
    """Add an EvidencePackageNode per evidence payload (level/readiness copied as-is)."""

    existing = {n.evidence_package_id for n in model.evidence_packages}
    for payload in evidence_payloads or []:
        pid = str(payload.get("evidence_package_id", "") or "")
        if not pid or pid in existing:
            continue
        existing.add(pid)
        manifest = copy.deepcopy(payload.get("manifest", {}) or {})
        proof_src = _manifest_source(payload, "proof")
        trace_src = _manifest_source(payload, "trace")
        review_target = proof_src.get("review_map_target") or trace_src.get("review_map_target")
        model.evidence_packages.append(EvidencePackageNode(
            evidence_package_id=pid,
            linked_proof_receipt_id=str(proof_src.get("receipt_id", "") or ""),
            linked_trace_receipt_id=str(trace_src.get("receipt_id", "") or ""),
            target_function_id=_resolve_target(
                model, review_target, payload.get("target_id"), payload.get("target")),
            evidence_level=str(payload.get("evidence_level", "") or HEURISTIC),
            manifest=manifest,
            readiness=str(manifest.get("readiness", "") or payload.get("readiness", "") or ""),
            aliases=_alias_map(
                evidence_package_id=pid,
                target=payload.get("target"),
                target_id=payload.get("target_id"),
                review_map_target=review_target,
            ),
        ))
    return model


def link_trace_receipts_to_model(model: ProtocolModel, trace_payloads: list[dict]) -> ProtocolModel:
    """Add a TraceReceiptNode per trace payload; link to its proof receipt only when exact."""

    proof_ids = {n.proof_receipt_id for n in model.proof_receipts}
    proof_by_path: dict[str, set] = {}
    for node in model.proof_receipts:
        path = node.source_artifacts.get("proof_json")
        if path:
            proof_by_path.setdefault(str(path), set()).add(node.proof_receipt_id)
    for pkg in model.evidence_packages:
        src = next((s for s in (pkg.manifest.get("sources", []) or [])
                    if isinstance(s, dict) and s.get("kind") == "proof"), {})
        path, rid = str(src.get("path", "") or ""), str(src.get("receipt_id", "") or "")
        if path and rid:
            proof_by_path.setdefault(path, set()).add(rid)

    existing = {n.trace_receipt_id for n in model.trace_receipts}
    for payload in trace_payloads or []:
        rid = str(payload.get("trace_receipt_id", "") or "")
        if not rid or rid in existing:
            continue
        existing.add(rid)
        explicit = str(payload.get("proof_receipt_id", "") or "")
        source_proof = str(payload.get("source_proof_json", "") or "")
        linked_proof = ""
        if explicit and explicit in proof_ids:
            linked_proof = explicit
        elif source_proof:
            hits = proof_by_path.get(source_proof, set())
            if len(hits) == 1:
                linked_proof = next(iter(hits))
        model.trace_receipts.append(TraceReceiptNode(
            trace_receipt_id=rid,
            linked_proof_receipt_id=linked_proof,
            target_function_id=_resolve_target(
                model, payload.get("review_map_target"), payload.get("target_id"), payload.get("target")),
            status=str(payload.get("status", "") or ""),
            evidence_level=str(payload.get("evidence_level", "") or HEURISTIC),
            source_artifacts={
                key: value
                for key, value in {
                    "source_proof_json": source_proof,
                    "source_raw_output": str(payload.get("source_raw_output", "") or ""),
                }.items()
                if value
            },
            aliases=_alias_map(
                trace_receipt_id=rid,
                target=payload.get("target"),
                target_id=payload.get("target_id"),
                review_map_target=payload.get("review_map_target"),
                source_proof_json=source_proof,
            ),
        ))
    return model


def link_report_drafts_to_model(model: ProtocolModel, report_payloads: list[dict]) -> ProtocolModel:
    """Add a ReportDraftNode per report payload (review_status/readiness preserved)."""

    pkg_by_id = {n.evidence_package_id: n for n in model.evidence_packages}
    existing = {n.report_id for n in model.report_drafts}
    for payload in report_payloads or []:
        ctx = payload.get("evidence_context", {}) or {}
        receipts = payload.get("receipt_references", {}) or {}
        paths = payload.get("artifact_paths", {}) or {}
        pkg_id = str(ctx.get("evidence_package_id", "") or receipts.get("evidence_package_id", "") or "")
        report_json = str(paths.get("report_json", "") or (ctx.get("source_artifacts", {}) or {}).get("report_json", "") or "")
        target = payload.get("target", "")
        rid = str(payload.get("report_id", "") or "") or ids.report_id(pkg_id, report_json or str(target))
        if rid in existing:
            continue
        existing.add(rid)
        target_fid = _resolve_target(model, target, payload.get("target_id"))
        if not target_fid and pkg_id in pkg_by_id:
            target_fid = pkg_by_id[pkg_id].target_function_id
        model.report_drafts.append(ReportDraftNode(
            report_id=rid,
            linked_evidence_package_id=pkg_id,
            linked_target_function_id=target_fid,
            review_status=str(payload.get("review_status", "") or ctx.get("review_status", "") or "NEEDS_HUMAN_REVIEW"),
            report_readiness=copy.deepcopy(payload.get("report_readiness", {}) or {}),
            safety_boundary=list(payload.get("what_is_not_proven", []) or []),
            aliases=_alias_map(report_json=report_json, target=target, title=payload.get("title")),
            metadata={
                "evidence_level": str(payload.get("evidence_level", "") or ""),
                "status": str(payload.get("status", "") or ""),
            },
        ))
    return model


def _evidence_link_entries(payload: object) -> list[dict]:
    if isinstance(payload, dict):
        payload = payload.get("evidence_links", [])
    if isinstance(payload, (list, tuple)):
        return [item for item in payload if isinstance(item, dict)]
    return []


def link_evidence_links_to_model(model: ProtocolModel, evidence_links_payload: object) -> ProtocolModel:
    """Add an EvidenceLinkNode per evidence-link entry (read-only; old IDs preserved)."""

    existing = {n.evidence_link_id for n in model.evidence_links}
    for entry in _evidence_link_entries(evidence_links_payload):
        legacy = str(entry.get("id", "") or "")
        kind = str(entry.get("artifact_kind", "") or entry.get("source", "") or "")
        target_disp = str(entry.get("target", "") or entry.get("related_target", "") or "") or _display(entry.get("target_id"))
        target_fid = _resolve_target(model, target_disp, entry.get("target_id"))
        link_id = ids.evidence_link_id(kind, target_fid, legacy)
        if link_id in existing:
            continue
        existing.add(link_id)
        model.evidence_links.append(EvidenceLinkNode(
            evidence_link_id=link_id,
            linked_target_function_id=target_fid,
            linked_artifact_kind=kind,
            linked_artifact_path=str(entry.get("artifact_path", "") or ""),
            evidence_package_id=str(entry.get("evidence_package_id", "") or ""),
            proof_receipt_id=str(entry.get("proof_receipt_id", "") or ""),
            trace_receipt_id=str(entry.get("trace_receipt_id", "") or ""),
            report_id=str(entry.get("report_id", "") or ""),
            evidence_level=str(entry.get("evidence_level", "") or HEURISTIC),
            aliases=_alias_map(id=legacy, target=target_disp, target_id=entry.get("target_id")),
            metadata={"readiness": str(entry.get("readiness", "") or "")},
        ))
    return model


def _crosslink_traces_via_evidence(model: ProtocolModel) -> ProtocolModel:
    """Fill an empty trace->proof link when an evidence package uniquely pairs them."""

    proof_ids = {n.proof_receipt_id for n in model.proof_receipts}
    proof_for_trace: dict[str, set] = {}
    for pkg in model.evidence_packages:
        if pkg.linked_trace_receipt_id and pkg.linked_proof_receipt_id:
            proof_for_trace.setdefault(pkg.linked_trace_receipt_id, set()).add(pkg.linked_proof_receipt_id)
    for trace in model.trace_receipts:
        if trace.linked_proof_receipt_id:
            continue
        hits = proof_for_trace.get(trace.trace_receipt_id, set()) & proof_ids
        if len(hits) == 1:
            trace.linked_proof_receipt_id = next(iter(hits))
    return model


def link_artifacts_to_protocol_model(
    model: ProtocolModel,
    *,
    proofs: list[dict] | None = None,
    traces: list[dict] | None = None,
    evidence_packages: list[dict] | None = None,
    reports: list[dict] | None = None,
    evidence_links: object | None = None,
) -> ProtocolModel:
    """Link all v3.4 artifact payloads into the model in place and return it.

    Proofs and evidence packages are linked before traces (so trace->proof can
    resolve via recorded proof paths and the evidence manifest), then reports and
    evidence-links, then a final pass fills trace->proof from evidence pairings.
    """

    link_proof_receipts_to_model(model, proofs or [])
    link_evidence_packages_to_model(model, evidence_packages or [])
    link_trace_receipts_to_model(model, traces or [])
    link_report_drafts_to_model(model, reports or [])
    if evidence_links is not None:
        link_evidence_links_to_model(model, evidence_links)
    _crosslink_traces_via_evidence(model)
    return model

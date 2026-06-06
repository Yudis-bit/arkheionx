"""Build a structured evidence package from proof + trace artifacts."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
from pathlib import Path

from arkheionx.artifacts import ArtifactWriter
from arkheionx.proof.payloads import target_slug
from arkheionx.protocol.model import COMPILER_CONFIRMED, EXECUTION_CONFIRMED, HEURISTIC
from arkheionx.version import __version__

from . import model as M
from .model import EvidencePackage

MANIFEST_SCHEMA_VERSION = "1.0.0"


def _read_json(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _bug_classes_for(target_id: str, analysis) -> tuple[str, str, list[str], int]:
    """Return (role, money_flow_role, bug_classes, score) from analysis context."""
    role = ""
    score = 0
    bug_classes: list[str] = []
    for t in analysis.hunter_targets:
        if t.target_id == target_id:
            bug_classes = list(t.bug_classes)
            score = t.score
            break
    fr = next((f for f in analysis.all_functions if f.function_id == target_id), None)
    if fr is not None:
        role = fr.role
    flow = analysis.money_flow
    money_role = "internal"
    if target_id in flow.entrypoints:
        money_role = "entry"
    elif target_id in flow.exits:
        money_role = "exit"
    elif target_id in flow.privileged_movers:
        money_role = "privileged"
    elif target_id in flow.pricing_dependencies:
        money_role = "pricing"
    return role, money_role, bug_classes, score


def _readiness(level: str) -> str:
    return {
        M.EVIDENCE_READY: "evidence_ready",
        EXECUTION_CONFIRMED: "execution_confirmed",
        COMPILER_CONFIRMED: "compiler_confirmed",
    }.get(level, "heuristic")


def _path_exists(path: str) -> bool:
    return bool(path) and Path(path).exists()


def _source_record(kind: str, path: str, payload: dict | None) -> dict:
    payload = payload or {}
    receipt_key = f"{kind}_receipt_id"
    source = {
        "kind": kind,
        "path": path,
        "exists": _path_exists(path),
        "receipt_id": str(payload.get(receipt_key, "")),
        "target_id": str(payload.get("target_id", "")),
        "review_map_target": str(payload.get("review_map_target", "")),
        "evidence_level": str(payload.get("evidence_level", "")),
        "status": str(payload.get("status", "")),
    }
    if kind == "trace":
        source["source_proof_json"] = str(payload.get("source_proof_json", ""))
    return source


def _evidence_package_id(
    slug: str,
    target_id: str,
    evidence_level: str,
    proof: dict,
    trace: dict | None,
    proof_source_path: str,
    trace_source_path: str,
) -> str:
    seed = {
        "target_id": target_id,
        "evidence_level": evidence_level,
        "proof_receipt_id": proof.get("proof_receipt_id", ""),
        "trace_receipt_id": (trace or {}).get("trace_receipt_id", ""),
        "proof_source_path": proof_source_path,
        "trace_source_path": trace_source_path if trace else "",
    }
    digest = hashlib.sha256(json.dumps(seed, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()[:12]
    return f"evidence:{slug}:{digest}"


def _build_manifest(
    package_id: str,
    target: str,
    target_id: str,
    evidence_level: str,
    proof: dict,
    trace: dict | None,
    proof_source_path: str,
    trace_source_path: str,
) -> dict:
    trace_linked = isinstance(trace, dict) and bool(trace) and bool(trace_source_path)
    sources = [_source_record("proof", proof_source_path, proof)]
    if trace_linked:
        sources.append(_source_record("trace", trace_source_path, trace))
    checks = {
        "proof_linked": bool(proof_source_path),
        "trace_linked": trace_linked,
        "trace_required_for_evidence_ready": True,
        "source_paths_recorded": bool(proof_source_path) and (evidence_level != M.EVIDENCE_READY or bool(trace_source_path)),
        "human_review_required": True,
    }
    return {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "package_id": package_id,
        "target": target,
        "target_id": target_id,
        "evidence_level": evidence_level,
        "readiness": _readiness(evidence_level),
        "source_count": len(sources),
        "sources": sources,
        "checks": checks,
    }


_LV_SUPPORT_LIMITATIONS = [
    "Local validation is supporting context only; it does not confirm a finding or finalize severity.",
    "A passing local test was recorded as supporting context; it does not prove absence of bugs.",
    "A failing, skipped, or errored local test requires manual review.",
    "Manual review is required; ready_for_submission is false.",
]


def build_local_validation_support(writer: ArtifactWriter, *, contract_name: str = "", function_name: str = "") -> dict | None:
    """Return an optional local-validation support block from existing artifacts.

    Reads ``<out>/local-validation/`` (written by ``arkheionx local-validate``).
    A passing test is recorded as ``SUPPORT_TESTED`` supporting context, or
    ``SUPPORT_TRACE_BOUND`` only when an explicit local trace receipt links it;
    failing/skipped/errored tests are recorded as ``SUPPORT_NONE`` with a
    manual-review warning. It invents nothing, confirms nothing, finalizes no
    severity, never emits HUMAN_REVIEWED, and keeps ready_for_submission false.
    Returns ``None`` when no local-validation summary or matching result exists.
    """

    from arkheionx.local_validation import ids as lv_ids
    from arkheionx.local_validation.model import SUPPORT_NONE, SUPPORT_TESTED, SUPPORT_TRACE_BOUND

    lv_root = writer.root / "local-validation"
    summary = _read_json(lv_root / "summary.json")
    if not isinstance(summary, dict):
        return None
    summary_id = str(summary.get("summary_id", ""))
    run_ids = [str(r) for r in (summary.get("run_ids", []) or [])]

    trace_by_result: dict[str, str] = {}
    traces_dir = lv_root / "traces"
    if traces_dir.is_dir():
        for tp in sorted(traces_dir.glob("*.json")):
            trace = _read_json(tp)
            if isinstance(trace, dict) and trace.get("test_result_id"):
                trace_by_result[str(trace["test_result_id"])] = str(trace.get("trace_receipt_id", ""))

    entries: list[dict] = []
    results_dir = lv_root / "results"
    for rp in (sorted(results_dir.glob("*.json")) if results_dir.is_dir() else []):
        result = _read_json(rp)
        if not isinstance(result, dict):
            continue
        if (contract_name or function_name) and (
            str(result.get("contract_name", "")) != contract_name
            or str(result.get("function_name", "")) != function_name
        ):
            continue
        status = str(result.get("status", ""))
        test_result_id = str(result.get("test_result_id", ""))
        trace_receipt_id = trace_by_result.get(test_result_id, "")
        warnings: list[str] = []
        if status == "TEST_PASSED":
            support_level = SUPPORT_TRACE_BOUND if trace_receipt_id else SUPPORT_TESTED
        else:
            support_level = SUPPORT_NONE
            warnings.append(f"local test {result.get('test_name', '')} status {status or 'unknown'} requires manual review")
        entries.append({
            "support_id": f"local-validation-support:{lv_ids.short_hash([test_result_id, support_level, trace_receipt_id])}",
            "source_kind": "local_validation",
            "source_path": f"local-validation/results/{rp.name}",
            "test_result_id": test_result_id,
            "trace_receipt_id": trace_receipt_id,
            "run_id": str(result.get("run_id", "")) or (run_ids[0] if run_ids else ""),
            "summary_id": summary_id,
            "support_level": support_level,
            "test_name": str(result.get("test_name", "")),
            "test_status": status,
            "linked_function_ids": list(result.get("linked_function_ids", []) or []),
            "linked_value_path_ids": list(result.get("linked_value_path_ids", []) or []),
            "linked_assumption_ids": list(result.get("linked_assumption_ids", []) or []),
            "linked_test_gap_ids": list(result.get("linked_test_gap_ids", []) or []),
            "warnings": warnings,
            "manual_review_required": True,
            "ready_for_submission": False,
        })
    if not entries:
        return None
    return {
        "summary_id": summary_id,
        "run_id": run_ids[0] if run_ids else "",
        "source": "local-validation/summary.json",
        "tested_count": sum(1 for e in entries if e["support_level"] == SUPPORT_TESTED),
        "trace_bound_count": sum(1 for e in entries if e["support_level"] == SUPPORT_TRACE_BOUND),
        "needs_review_count": sum(1 for e in entries if e["support_level"] == SUPPORT_NONE),
        "entries": sorted(entries, key=lambda e: e["test_result_id"]),
        "limitations": list(_LV_SUPPORT_LIMITATIONS),
        "manual_review_required": True,
        "ready_for_submission": False,
    }


def build_protocol_graph_context(graph: object | None = None, coverage_summary: object | None = None) -> dict | None:
    """Summarize an optional protocol intelligence graph and/or local-validation
    coverage summary into a supporting-context block for an evidence payload.

    Pure and read-only: it builds no graph, reads no files, parses no artifacts,
    runs no local validation or CLI, and does not mutate its inputs -- it only
    summarizes already-supplied objects (dataclasses or dict-like). Returns
    ``None`` when both inputs are absent. Protocol graph context is supporting
    review context only: it never confirms a vulnerability, finalizes severity,
    marks an audit passed, emits HUMAN_REVIEWED, or sets ready_for_submission.
    A graph warning is not a vulnerability and a graph error is not a final
    severity.
    """

    if graph is None and coverage_summary is None:
        return None

    def _g(obj, key, default):
        if obj is None:
            return default
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    # Graph node-kind strings (mirror arkheionx/intelligence/graph.py; kept local
    # to avoid an import-time dependency on the intelligence package).
    _FUNCTION_ROLE, _VALUE_PATH = "GRAPH_NODE_FUNCTION_ROLE", "GRAPH_NODE_VALUE_PATH"
    _ASSUMPTION, _TEST_GAP = "GRAPH_NODE_ASSUMPTION", "GRAPH_NODE_TEST_GAP"
    _LINK_KEYS = ("linked_function_ids", "linked_value_path_ids", "linked_assumption_ids",
                  "linked_test_gap_ids", "linked_local_validation_ids")

    ctx: dict = {
        "observed": True, "graph_id": "",
        "node_count": 0, "edge_count": 0, "warning_count": 0, "error_count": 0,
        "function_role_count": 0, "value_path_count": 0, "assumption_count": 0, "test_gap_count": 0,
        "coverage_count": 0, "tested_count": 0, "trace_bound_count": 0,
        "support_note": "Protocol graph context is supporting review context only; manual review is required.",
        "manual_review_required": True, "ready_for_submission": False, "warnings": [],
    }
    linked: dict = {key: set() for key in _LINK_KEYS}
    warnings: set = set()

    if graph is not None:
        ctx["graph_id"] = str(_g(graph, "graph_id", "") or "")
        ctx["node_count"] = int(_g(graph, "node_count", 0) or 0)
        ctx["edge_count"] = int(_g(graph, "edge_count", 0) or 0)
        ctx["warning_count"] = int(_g(graph, "warning_count", 0) or 0)
        ctx["error_count"] = int(_g(graph, "error_count", 0) or 0)
        for node in (_g(graph, "nodes", []) or []):
            kind = str(_g(node, "node_kind", ""))
            if kind == _FUNCTION_ROLE:
                ctx["function_role_count"] += 1
            elif kind == _VALUE_PATH:
                ctx["value_path_count"] += 1
            elif kind == _ASSUMPTION:
                ctx["assumption_count"] += 1
            elif kind == _TEST_GAP:
                ctx["test_gap_count"] += 1
        for key in _LINK_KEYS:
            linked[key].update(str(x) for x in (_g(graph, key, []) or []) if x)
        warnings.update(str(w) for w in (_g(graph, "warnings", []) or []) if w)

    if coverage_summary is not None:
        ctx["coverage_count"] = int(_g(coverage_summary, "coverage_count", 0) or 0)
        ctx["tested_count"] = int(_g(coverage_summary, "tested_count", 0) or 0)
        ctx["trace_bound_count"] = int(_g(coverage_summary, "trace_bound_count", 0) or 0)
        for key in _LINK_KEYS:
            linked[key].update(str(x) for x in (_g(coverage_summary, key, []) or []) if x)
        warnings.update(str(w) for w in (_g(coverage_summary, "warnings", []) or []) if w)

    for key in _LINK_KEYS:
        ctx[key] = sorted(linked[key])
    ctx["warnings"] = sorted(warnings)
    return ctx


def build_evidence(match, root: Path, writer: ArtifactWriter, analysis, write: bool = True,
                   proof_override: dict | None = None, trace_override: dict | None = None,
                   proof_source_path: str = "", trace_source_path: str = "",
                   protocol_graph: object | None = None,
                   coverage_summary: object | None = None) -> EvidencePackage:
    slug = target_slug(match.display_id)
    default_proof_path = writer.path_for(f"proof/{slug}/proof.json")
    default_trace_path = writer.path_for(f"proof/{slug}/trace.json")
    if proof_override is not None:
        proof = proof_override
        trace = trace_override
    else:
        proof = _read_json(default_proof_path)
        trace = _read_json(default_trace_path)
        proof_source_path = proof_source_path or str(default_proof_path)
        if trace is not None:
            trace_source_path = trace_source_path or str(default_trace_path)

    if proof is None:
        pkg = EvidencePackage(
            target=match.qualified_id,
            target_id=match.stable_id or match.display_id,
            evidence_level=HEURISTIC,
            status=M.NO_PROOF,
            next_command=f"arkheionx prove . --target {match.display_id} --run",
        )
        return pkg

    proof_level = proof.get("evidence_level", HEURISTIC)
    trace_found = isinstance(trace, dict) and bool(trace)
    if trace_found and not trace_source_path:
        trace_source_path = str(default_trace_path)
    proof_source_path = proof_source_path or str(default_proof_path)
    if proof_level == EXECUTION_CONFIRMED and trace_found:
        evidence_level = M.EVIDENCE_READY
        status = M.EVIDENCE_READY_STATUS
    elif proof_level == EXECUTION_CONFIRMED:
        evidence_level = EXECUTION_CONFIRMED
        status = M.EXECUTION_CONFIRMED
    elif proof_level == COMPILER_CONFIRMED:
        evidence_level = COMPILER_CONFIRMED
        status = M.COMPILER_CONFIRMED_ONLY
    else:
        evidence_level = HEURISTIC
        status = M.SCAFFOLD_ONLY

    test_result = proof.get("test_result", {})
    role, money_role, bug_classes, score = _bug_classes_for(match.stable_id or match.display_id, analysis)
    line_range = getattr(match, "line_range", []) or []
    affected = f"{match.contract_name}.{match.function_name}"
    if match.file_path:
        loc = f"#L{line_range[0]}-L{line_range[1]}" if len(line_range) == 2 and line_range[0] else ""
        affected = f"{match.file_path}:{affected}{loc}"

    candidate_impact = "; ".join(bug_classes) if bug_classes else "value-flow review surface"
    if proof_level == EXECUTION_CONFIRMED and not trace_found:
        recommended_next_steps = [
            f"arkheionx trace . --target {match.display_id}",
            f"arkheionx evidence . --target {match.display_id}",
            "Review the proof artifact; evidence-ready status requires a linked trace artifact.",
        ]
        next_command = f"arkheionx trace . --target {match.display_id}"
    else:
        recommended_next_steps = [
            f"arkheionx report . --target {match.display_id}",
            "Review the proof/trace artifacts and confirm the property under test.",
        ]
        next_command = f"arkheionx report . --target {match.display_id}"
    target_id = match.stable_id or match.display_id
    target = match.qualified_id
    package_id = _evidence_package_id(
        slug, target_id, evidence_level, proof, trace if trace_found else None,
        proof_source_path, trace_source_path if trace_found else "",
    )
    manifest = _build_manifest(
        package_id, target, target_id, evidence_level, proof, trace if trace_found else None,
        proof_source_path, trace_source_path if trace_found else "",
    )
    payload = {
        "schema_version": "1.0.0",
        "arkheionx_version": __version__,
        "evidence_package_id": package_id,
        "generated_at": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "project_root": str(root),
        "target": target,
        "target_id": target_id,
        "evidence_level": evidence_level,
        "status": status,
        "source_artifacts": {
            "proof_json": proof_source_path,
            "trace_json": trace_source_path if trace_found else "",
            "trace_status": "linked" if trace_found else "missing",
            "raw_foundry_output": (proof.get("test_result", {}) or {}).get("raw_output_path", ""),
            "generated_test": next((f for f in proof.get("generated_files", []) if f.endswith(".sol")), ""),
        },
        "manifest": manifest,
        "proof_summary": {
            "status": proof.get("status", ""),
            "tests_run": test_result.get("tests_run", 0),
            "passed": test_result.get("passed", 0),
            "failed": test_result.get("failed", 0),
            "skipped": test_result.get("skipped", 0),
            "failed_tests": test_result.get("failed_tests", []),
            "skipped_tests": test_result.get("skipped_tests", []),
            "foundry_command": (proof.get("foundry", {}) or {}).get("test_command", ""),
        },
        "trace_summary": {
            "summary_available": trace_found,
            "status": "linked" if trace_found else "missing",
            "source": trace_source_path if trace_found else "",
            "reverts": (trace or {}).get("reverts", []),
            "assertion_failures": (trace or {}).get("assertion_failures", []),
            "call_sequence": (trace or {}).get("call_sequence", []),
            "logs": (trace or {}).get("logs", []),
        },
        "protocol_context": {
            "role": role,
            "score": score,
            "why_it_matters": match.reasons,
            "likely_bug_classes": bug_classes,
            "money_flow_role": money_role,
        },
        "impact_notes": {
            "candidate_impact": candidate_impact,
            "affected_components": [affected],
            "assumptions": [
                "Local Foundry results reflect the committed test code and mocks only.",
                "Behavior on a live deployment may differ from the local harness.",
            ],
            "limitations": [
                "Not a formal audit. Not a severity guarantee.",
                "A passing test does not prove absence of bugs; a failing test does not by itself prove a vulnerability.",
                "Human review is required to determine whether this represents a valid vulnerability.",
            ],
        },
        "recommended_next_steps": recommended_next_steps,
    }

    lv_support = build_local_validation_support(writer)
    if lv_support is not None:
        payload["local_validation_support"] = lv_support

    graph_context = build_protocol_graph_context(protocol_graph, coverage_summary)
    if graph_context is not None:
        payload["protocol_graph_context"] = graph_context

    pkg = EvidencePackage(
        target=match.qualified_id,
        target_id=match.stable_id or match.display_id,
        evidence_level=evidence_level,
        status=status,
        proof_found=True,
        trace_found=trace_found,
        tests_run=test_result.get("tests_run", 0),
        passed=test_result.get("passed", 0),
        failed=test_result.get("failed", 0),
        skipped=test_result.get("skipped", 0),
        next_command=next_command,
        payload=payload,
    )
    if write:
        pkg.json_path = str(writer.write_text(f"evidence/{slug}/evidence.json", json.dumps(payload, indent=2)))
        from .render import evidence_text

        pkg.text_path = str(writer.write_text(f"evidence/{slug}/evidence.txt", evidence_text(payload)))
    return pkg

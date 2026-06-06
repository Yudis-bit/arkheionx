"""validate-artifacts: local validation of generated evidence-workflow artifacts."""
from __future__ import annotations

import json
from pathlib import Path

from arkheionx.artifacts import ArtifactWriter

from . import index as idx

_REQUIRED = {
    "proof.json": ["schema_version", "target", "status", "evidence_level", "foundry", "test_result"],
    "trace.json": ["schema_version", "target", "status", "evidence_level", "tests_run"],
    "evidence.json": ["schema_version", "target", "evidence_level", "status", "source_artifacts", "impact_notes"],
    "report.json": ["schema_version", "target", "title", "evidence_level", "summary", "safety_notice", "limitations", "reproduction_steps"],
}
_LEVELS = {"HEURISTIC", "COMPILER_CONFIRMED", "EXECUTION_CONFIRMED", "EVIDENCE_READY"}
_UNSAFE_REPORT = ["ready to submit", "guaranteed bounty", "guaranteed exploit", "final severity:"]
_UNSAFE_REPRO = ["--fork-url", "rpc_url", "deploy to mainnet", "broadcast the transaction"]


def validate_protocol_graph_context(context: object, label: str = "evidence.json", slug: str = "") -> list[str]:
    """Validate an optional protocol_graph_context block (supporting context only).

    Returns a list of issue strings. Review context only: a graph warning is not
    a vulnerability and a graph error is not a final severity. The block must keep
    manual_review_required true and ready_for_submission false, emit no
    HUMAN_REVIEWED status, and contain no finality wording. A non-dict block is
    ignored (no issue), so existing payloads without the block still validate.
    """

    issues: list[str] = []
    if not isinstance(context, dict):
        return issues
    where = f"{slug}/{label} protocol_graph_context" if slug else f"{label} protocol_graph_context"
    if context.get("ready_for_submission") is True:
        issues.append(f"{where} must not be ready_for_submission")
    if context.get("manual_review_required") is False:
        issues.append(f"{where} must require manual review")
    blob = json.dumps(context).lower()
    if "human_reviewed" in blob:
        issues.append(f"{where} must not emit HUMAN_REVIEWED")
    for phrase in ("confirmed vulnerability", "final severity", "audit passed",
                   "bounty eligible", "verified safe", "proven safe"):
        if phrase in blob:
            issues.append(f"{where} contains disallowed phrase `{phrase}`")
    return issues


def _load(path: Path) -> tuple[dict | None, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except (OSError, ValueError) as exc:
        return None, str(exc)


def _check_required(name: str, data: dict, slug: str, issues: list[str]) -> None:
    for field in _REQUIRED.get(name, []):
        if field not in data:
            issues.append(f"{slug}/{name} missing required field `{field}`")


def _manifest_source(manifest: dict, kind: str) -> dict:
    sources = manifest.get("sources", [])
    if not isinstance(sources, list):
        return {}
    return next(
        (source for source in sources if isinstance(source, dict) and source.get("kind") == kind),
        {},
    )


def _path_exists(path: str) -> bool:
    return bool(path) and Path(path).exists()


def validate_artifacts(writer: ArtifactWriter) -> tuple[dict, list[str]]:
    """Return (checked_counts, issues)."""

    root = writer.root
    counts = {"proof.json": 0, "trace.json": 0, "evidence.json": 0, "report.json": 0}
    issues: list[str] = []
    records = idx.scan_targets(writer)

    for r in records:
        for label, attr in (("proof.json", r.proof_json), ("trace.json", r.trace_json),
                            ("evidence.json", r.evidence_json), ("report.json", r.report_json)):
            if not attr:
                continue
            data, err = _load(Path(attr))
            if err is not None:
                issues.append(f"{r.slug}/{label} is malformed JSON")
                continue
            counts[label] += 1
            _check_required(label, data, r.slug, issues)
            _validate_specific(label, data, r, root, issues)

    return counts, issues


def _validate_specific(label: str, data: dict, r: idx.TargetRecord, root: Path, issues: list[str]) -> None:
    level = data.get("evidence_level")
    if label in {"proof.json", "evidence.json", "report.json", "trace.json"} and level not in _LEVELS:
        issues.append(f"{r.slug}/{label} has unknown evidence_level `{level}`")

    if label == "proof.json":
        tr = data.get("test_result", {}) or {}
        executed = (tr.get("passed", 0) or 0) + (tr.get("failed", 0) or 0)
        if level == "EXECUTION_CONFIRMED" and executed == 0:
            issues.append(f"{r.slug}/proof.json has EXECUTION_CONFIRMED but no executed tests")

    if label == "evidence.json":
        src = data.get("source_artifacts", {}) or {}
        trace_ref = src.get("trace_json", "")
        trace_status = str(src.get("trace_status", ""))
        if trace_ref and not Path(trace_ref).exists():
            issues.append(f"{r.slug}/evidence.json references missing trace.json")
        if level == "EVIDENCE_READY" and not (trace_ref and Path(trace_ref).exists()):
            issues.append(f"{r.slug}/evidence.json is EVIDENCE_READY without a trace artifact")
        if level == "EVIDENCE_READY" and not trace_status:
            issues.append(f"{r.slug}/evidence.json is EVIDENCE_READY without trace_status")
        elif level == "EVIDENCE_READY" and trace_status != "linked":
            issues.append(f"{r.slug}/evidence.json is EVIDENCE_READY but trace_status is `{trace_status}`")
        _validate_evidence_manifest(data, r, issues)
        lvs = data.get("local_validation_support")
        if isinstance(lvs, dict):
            if lvs.get("ready_for_submission") is True:
                issues.append(f"{r.slug}/evidence.json local_validation_support must not be ready_for_submission")
            if lvs.get("manual_review_required") is False:
                issues.append(f"{r.slug}/evidence.json local_validation_support must require manual review")
            if "HUMAN_REVIEWED" in json.dumps(lvs):
                issues.append(f"{r.slug}/evidence.json local_validation_support must not emit HUMAN_REVIEWED")
        issues.extend(validate_protocol_graph_context(data.get("protocol_graph_context"), "evidence.json", r.slug))

    if label == "report.json":
        if not str(data.get("safety_notice", "")).strip():
            issues.append(f"{r.slug}/report.json missing safety_notice")
        blob = json.dumps(data).lower()
        for phrase in _UNSAFE_REPORT:
            if phrase in blob:
                issues.append(f"{r.slug}/report.json contains disallowed phrase `{phrase}`")
        if "HUMAN_REVIEWED" in json.dumps(data):
            issues.append(f"{r.slug}/report.json must not emit HUMAN_REVIEWED")
        repro = " ".join(data.get("reproduction_steps", [])).lower()
        for phrase in _UNSAFE_REPRO:
            if phrase in repro:
                issues.append(f"{r.slug}/report.json reproduction includes live-chain step `{phrase}`")
        readiness = data.get("report_readiness")
        if isinstance(readiness, dict):
            if readiness.get("ready_for_submission") is True:
                issues.append(f"{r.slug}/report.json must remain not ready for submission")
            if readiness.get("requires_manual_review") is False:
                issues.append(f"{r.slug}/report.json must require manual review")
        context = data.get("evidence_context")
        if isinstance(context, dict) and context.get("human_review_required") is False:
            issues.append(f"{r.slug}/report.json evidence_context must require human review")
        claims = data.get("claim_references")
        if isinstance(claims, list):
            for claim in claims:
                if isinstance(claim, dict) and claim.get("status") != "needs_human_review":
                    issues.append(f"{r.slug}/report.json claim_references must stay needs_human_review")


def _validate_evidence_manifest(data: dict, r: idx.TargetRecord, issues: list[str]) -> None:
    manifest = data.get("manifest")
    if manifest is None:
        return
    if not isinstance(manifest, dict):
        issues.append(f"{r.slug}/evidence.json manifest is not an object")
        return

    package_id = str(data.get("evidence_package_id", ""))
    if package_id and manifest.get("package_id") != package_id:
        issues.append(f"{r.slug}/evidence.json manifest package_id does not match evidence_package_id")
    if manifest.get("target_id") and data.get("target_id") and manifest.get("target_id") != data.get("target_id"):
        issues.append(f"{r.slug}/evidence.json manifest target_id does not match evidence target_id")
    if manifest.get("evidence_level") != data.get("evidence_level"):
        issues.append(f"{r.slug}/evidence.json manifest evidence_level does not match package evidence_level")

    sources = manifest.get("sources", [])
    if not isinstance(sources, list):
        issues.append(f"{r.slug}/evidence.json manifest sources is not a list")
        sources = []
    elif manifest.get("source_count") != len(sources):
        issues.append(f"{r.slug}/evidence.json manifest source_count does not match sources")

    src = data.get("source_artifacts", {}) or {}
    proof_source = _manifest_source(manifest, "proof")
    trace_source = _manifest_source(manifest, "trace")
    if proof_source and src.get("proof_json", "") and proof_source.get("path") != src.get("proof_json"):
        issues.append(f"{r.slug}/evidence.json manifest proof path does not match source_artifacts.proof_json")
    if trace_source and src.get("trace_json", "") and trace_source.get("path") != src.get("trace_json"):
        issues.append(f"{r.slug}/evidence.json manifest trace path does not match source_artifacts.trace_json")

    for source in sources:
        if not isinstance(source, dict):
            continue
        path = str(source.get("path", ""))
        if path and bool(source.get("exists", False)) != _path_exists(path):
            issues.append(f"{r.slug}/evidence.json manifest {source.get('kind', 'source')} exists flag is stale")

    checks = manifest.get("checks", {}) or {}
    if not isinstance(checks, dict):
        issues.append(f"{r.slug}/evidence.json manifest checks is not an object")
        checks = {}
    level = data.get("evidence_level")
    if level == "EVIDENCE_READY":
        if checks.get("trace_linked") is not True:
            issues.append(f"{r.slug}/evidence.json is EVIDENCE_READY but manifest trace_linked is false")
        trace_path = str(trace_source.get("path", ""))
        if not trace_path:
            issues.append(f"{r.slug}/evidence.json is EVIDENCE_READY but manifest has no trace source")
        elif not _path_exists(trace_path):
            issues.append(f"{r.slug}/evidence.json is EVIDENCE_READY but manifest trace source is missing")
    if checks.get("human_review_required") is False:
        issues.append(f"{r.slug}/evidence.json manifest does not require human review")

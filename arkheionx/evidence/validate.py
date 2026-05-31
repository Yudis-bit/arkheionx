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


def _load(path: Path) -> tuple[dict | None, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except (OSError, ValueError) as exc:
        return None, str(exc)


def _check_required(name: str, data: dict, slug: str, issues: list[str]) -> None:
    for field in _REQUIRED.get(name, []):
        if field not in data:
            issues.append(f"{slug}/{name} missing required field `{field}`")


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
        if trace_ref and not Path(trace_ref).exists():
            issues.append(f"{r.slug}/evidence.json references missing trace.json")
        if level == "EVIDENCE_READY" and not (trace_ref and Path(trace_ref).exists()):
            issues.append(f"{r.slug}/evidence.json is EVIDENCE_READY without a trace artifact")

    if label == "report.json":
        if not str(data.get("safety_notice", "")).strip():
            issues.append(f"{r.slug}/report.json missing safety_notice")
        blob = json.dumps(data).lower()
        for phrase in _UNSAFE_REPORT:
            if phrase in blob:
                issues.append(f"{r.slug}/report.json contains disallowed phrase `{phrase}`")
        repro = " ".join(data.get("reproduction_steps", [])).lower()
        for phrase in _UNSAFE_REPRO:
            if phrase in repro:
                issues.append(f"{r.slug}/report.json reproduction includes live-chain step `{phrase}`")

"""Artifact index for the evidence workflow.

Scans ``.arkheionx/out/`` for proof/trace/evidence/report artifacts and builds
a deterministic index. The index is a cache: it can always be rebuilt by
scanning, so a missing or stale index never blocks the workflow.
"""
from __future__ import annotations

import datetime as dt
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from arkheionx.artifacts import ArtifactWriter

INDEX_SCHEMA_VERSION = "1.0.0"
INDEX_REL = "artifacts-index.json"

# Review statuses (furthest stage reached for a target).
NO_PROOF = "NO_PROOF"
PROOF_ONLY = "PROOF_ONLY"
TRACE_READY = "TRACE_READY"
EVIDENCE_READY = "EVIDENCE_READY"
REPORT_DRAFTED = "REPORT_DRAFTED"


@dataclass
class TargetRecord:
    target: str
    slug: str
    proof_json: str = ""
    trace_json: str = ""
    evidence_json: str = ""
    report_json: str = ""
    status: str = ""
    evidence_level: str = "HEURISTIC"
    review_status: str = NO_PROOF
    malformed: list[str] = field(default_factory=list)
    updated_at: str = ""


def compute_review_status(has_proof: bool, has_trace: bool, has_evidence: bool, has_report: bool) -> str:
    if has_report:
        return REPORT_DRAFTED
    if has_evidence:
        return EVIDENCE_READY
    if has_proof and has_trace:
        return TRACE_READY
    if has_proof:
        return PROOF_ONLY
    return NO_PROOF


def _load(path: Path, malformed: list[str], label: str) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        malformed.append(label)
        return {}


def _mtime(path: Path) -> str:
    try:
        return dt.datetime.fromtimestamp(path.stat().st_mtime, dt.timezone.utc).replace(microsecond=0).isoformat()
    except OSError:
        return ""


def scan_targets(writer: ArtifactWriter) -> list[TargetRecord]:
    root = writer.root  # .arkheionx/out
    slugs: set[str] = set()
    for sub in ("proof", "evidence", "reports"):
        base = root / sub
        if base.is_dir():
            slugs.update(p.name for p in base.iterdir() if p.is_dir())

    records: list[TargetRecord] = []
    for slug in sorted(slugs):
        proof_p = root / "proof" / slug / "proof.json"
        trace_p = root / "proof" / slug / "trace.json"
        ev_p = root / "evidence" / slug / "evidence.json"
        rep_p = root / "reports" / slug / "report.json"
        malformed: list[str] = []
        proof = _load(proof_p, malformed, "proof.json")
        trace = _load(trace_p, malformed, "trace.json")
        evidence = _load(ev_p, malformed, "evidence.json")
        report = _load(rep_p, malformed, "report.json")

        display = ""
        for doc in (evidence, proof, report, trace):
            if doc and not display:
                display = str(doc.get("target", ""))
        level = "HEURISTIC"
        for doc in (trace, proof, report, evidence):  # evidence package is authoritative (last wins)
            if doc:
                level = doc.get("evidence_level", level) or level
        record = TargetRecord(
            target=display or slug,
            slug=slug,
            proof_json=str(proof_p) if proof_p.exists() else "",
            trace_json=str(trace_p) if trace_p.exists() else "",
            evidence_json=str(ev_p) if ev_p.exists() else "",
            report_json=str(rep_p) if rep_p.exists() else "",
            status=str((report or evidence or proof or {}).get("status", "")),
            evidence_level=level,
            review_status=compute_review_status(proof_p.exists(), trace_p.exists(), ev_p.exists(), rep_p.exists()),
            malformed=malformed,
            updated_at=max((_mtime(p) for p in (proof_p, trace_p, ev_p, rep_p) if p.exists()), default=""),
        )
        records.append(record)
    return records


def build_index(project_root: str, records: list[TargetRecord]) -> dict:
    return {
        "schema_version": INDEX_SCHEMA_VERSION,
        "generated_at": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "project_root": project_root,
        "targets": [asdict(r) for r in records],
    }


def refresh_index(project_root: str, writer: ArtifactWriter) -> dict:
    """Rebuild the index from a scan and write it. Returns the index payload."""

    index = build_index(project_root, scan_targets(writer))
    writer.write_text(INDEX_REL, json.dumps(index, indent=2))
    return index


def load_or_rebuild(project_root: str, writer: ArtifactWriter) -> dict:
    path = writer.path_for(INDEX_REL)
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            pass
    return build_index(project_root, scan_targets(writer))

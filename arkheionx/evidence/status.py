"""evidence-status: inspect proof/evidence/report artifact state for a repo."""
from __future__ import annotations

from arkheionx.artifacts import ArtifactWriter

from . import index as idx


def _next_for(record: dict, project: str) -> str:
    rs = record.get("review_status", idx.NO_PROOF)
    name = record.get("target", record.get("slug", "")).split(":")[-1].split("#")[0].split("(")[0]
    if rs == idx.NO_PROOF:
        return f"arkheionx prove {project} --target {name} --run"
    if rs == idx.PROOF_ONLY:
        return f"arkheionx trace {project} --target {name}"
    if rs == idx.TRACE_READY:
        return f"arkheionx evidence {project} --target {name}"
    if rs == idx.EVIDENCE_READY:
        return f"arkheionx report {project} --target {name}"
    return "manual review"


def build_status(project: str, writer: ArtifactWriter, target: str | None = None) -> dict:
    """Return a status payload. Rebuilds the index from a scan when artifacts exist."""

    records = idx.scan_targets(writer)
    if target:
        t = target.lower()
        records = [r for r in records if t in r.target.lower() or t in r.slug.lower()]
    if records and not target:
        idx.refresh_index(project, writer)  # keep the cache fresh

    ready = [r for r in records if r.review_status in {idx.EVIDENCE_READY, idx.REPORT_DRAFTED}]
    needs = [r for r in records if r.review_status not in {idx.EVIDENCE_READY, idx.REPORT_DRAFTED}]
    counts = {
        "proof": sum(1 for r in records if r.proof_json),
        "trace": sum(1 for r in records if r.trace_json),
        "evidence": sum(1 for r in records if r.evidence_json),
        "report": sum(1 for r in records if r.report_json),
    }
    malformed = sum(1 for r in records if r.malformed)
    status = "no-artifacts" if not records else ("warning" if (needs or malformed) else "ok")
    return {
        "project_root": project,
        "status": status,
        "counts": counts,
        "ready": [_record_view(r, project) for r in ready],
        "needs_work": [_record_view(r, project) for r in needs],
        "artifacts_root": str(writer.root),
        "next_command": _top_next(records, project),
    }


def _record_view(r: idx.TargetRecord, project: str) -> dict:
    return {
        "target": r.target,
        "review_status": r.review_status,
        "evidence_level": r.evidence_level,
        "proof": bool(r.proof_json),
        "trace": bool(r.trace_json),
        "evidence": bool(r.evidence_json),
        "report": bool(r.report_json),
        "malformed": r.malformed,
        "next": _next_for(r.__dict__, project),
    }


def _top_next(records: list[idx.TargetRecord], project: str) -> str:
    if not records:
        return f"arkheionx hunt {project} --top 5"
    # Surface the least-complete target's next step first.
    order = {idx.NO_PROOF: 0, idx.PROOF_ONLY: 1, idx.TRACE_READY: 2, idx.EVIDENCE_READY: 3, idx.REPORT_DRAFTED: 4}
    least = min(records, key=lambda r: order.get(r.review_status, 0))
    return _next_for(least.__dict__, project)

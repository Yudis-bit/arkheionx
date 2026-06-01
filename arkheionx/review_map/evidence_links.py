"""Evidence linking for the Review Map.

Scans the repo's existing ``.arkheionx/out`` proof/trace/evidence/report
artifacts (read-only) and links them to review-map targets by name. When no
artifacts exist, no links are produced and the reviewer is told so.
"""
from __future__ import annotations

from pathlib import Path

from arkheionx.artifacts import ArtifactWriter
from arkheionx.evidence import index as _index

from .model import EvidenceLink


def _rel(path_str: str, repo_root: Path) -> str:
    if not path_str:
        return ""
    try:
        return Path(path_str).resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path_str


def generate_evidence_links(repo_root: Path) -> list[EvidenceLink]:
    """Return evidence links for existing local artifacts (read-only scan)."""

    writer = ArtifactWriter(repo_root)
    if not writer.root.is_dir():
        return []
    try:
        records = _index.scan_targets(writer)
    except Exception:  # scanning is best-effort; never fail the review map
        return []

    links: list[EvidenceLink] = []
    for record in records:
        sources = (
            ("proof", record.proof_json),
            ("trace", record.trace_json),
            ("evidence", record.evidence_json),
            ("report", record.report_json),
        )
        for source, path_str in sources:
            if not path_str:
                continue
            links.append(
                EvidenceLink(
                    id=f"ev-{source}-{record.slug}",
                    source=source,
                    artifact_path=_rel(path_str, repo_root),
                    related_target=record.target,
                    evidence_level=record.evidence_level,
                    status="linked",
                )
            )
    return links

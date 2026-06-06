"""Evidence linking for the Review Map.

Scans bounded local Arkheionx artifact roots for existing proof/trace/evidence/
report artifacts (read-only) and links them to review-map targets. When no
artifacts exist, no links are produced and the reviewer is told so.
"""
from __future__ import annotations

import json
from pathlib import Path

from arkheionx.artifacts import ArtifactWriter

from .model import EvidenceLink, ReviewMap, to_dict

_LIMITATIONS = [
    "Review guidance only.",
    "Manual review required.",
    "Not a confirmed bug.",
    "Evidence level is not final severity.",
]


def build_evidence_links_payload(rm: ReviewMap) -> dict:
    """Return the exact payload shape written to ``evidence-links.json``."""

    return {
        "schema_version": rm.schema_version,
        "generated_at": rm.generated_at,
        "repo_path": rm.repo_path,
        "evidence_links": to_dict(rm.evidence_links),
    }


def _rel(path_str: str, repo_root: Path) -> str:
    if not path_str:
        return ""
    try:
        return Path(path_str).resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path_str


def _read_json(path: Path) -> dict | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return payload if isinstance(payload, dict) else None


def _artifact_roots(repo_root: Path, artifact_roots: list[Path] | None = None) -> list[Path]:
    candidates = [ArtifactWriter(repo_root).root]
    for root in artifact_roots or []:
        path = Path(root).expanduser()
        candidates.append(path)
        candidates.append(path / ".arkheionx" / "out")
        if path.name == "review-map":
            candidates.append(path.parent)

    roots: list[Path] = []
    seen: set[str] = set()
    for candidate in candidates:
        try:
            key = str(candidate.resolve())
        except OSError:
            key = str(candidate)
        if key in seen or not candidate.is_dir():
            continue
        seen.add(key)
        roots.append(candidate)
    return roots


def _slugs(root: Path) -> list[str]:
    found: set[str] = set()
    for subdir in ("proof", "evidence", "reports"):
        base = root / subdir
        if base.is_dir():
            found.update(path.name for path in base.iterdir() if path.is_dir())
    return sorted(found)


def _manifest_source(evidence: dict | None, kind: str) -> dict:
    if not isinstance(evidence, dict):
        return {}
    sources = ((evidence.get("manifest", {}) or {}).get("sources", []) or [])
    if not isinstance(sources, list):
        return {}
    return next(
        (source for source in sources if isinstance(source, dict) and source.get("kind") == kind),
        {},
    )


def _display_target(value: object) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    text = text.split(":")[-1].split("#")[0]
    return text.split("(")[0]


def _first_text(*values: object) -> str:
    for value in values:
        text = str(value or "").strip()
        if text:
            return text
    return ""


def _readiness(level: str) -> str:
    return {
        "EVIDENCE_READY": "evidence_ready",
        "EXECUTION_CONFIRMED": "execution_confirmed",
        "COMPILER_CONFIRMED": "compiler_confirmed",
    }.get(level, "heuristic")


def _context_for_slug(root: Path, slug: str) -> dict:
    proof_path = root / "proof" / slug / "proof.json"
    trace_path = root / "proof" / slug / "trace.json"
    evidence_path = root / "evidence" / slug / "evidence.json"
    report_path = root / "reports" / slug / "report.json"
    report_md_path = root / "reports" / slug / "report.md"

    proof = _read_json(proof_path) if proof_path.exists() else None
    trace = _read_json(trace_path) if trace_path.exists() else None
    evidence = _read_json(evidence_path) if evidence_path.exists() else None
    report = _read_json(report_path) if report_path.exists() else None

    proof_source = _manifest_source(evidence, "proof")
    trace_source = _manifest_source(evidence, "trace")
    source_artifacts = (evidence or {}).get("source_artifacts", {}) or {}
    report_artifacts = (report or {}).get("artifact_paths", {}) or {}
    report_context = (report or {}).get("evidence_context", {}) or {}
    report_sources = report_context.get("source_artifacts", {}) or {}
    receipts = (report or {}).get("receipt_references", {}) or {}
    report_readiness = (report or {}).get("report_readiness", {}) or {}

    artifacts = {
        "proof_json": str(proof_path) if proof_path.exists() else "",
        "trace_json": str(trace_path) if trace_path.exists() else "",
        "evidence_json": str(evidence_path) if evidence_path.exists() else "",
        "report_json": str(report_path) if report_path.exists() else "",
        "report_md": str(report_md_path) if report_md_path.exists() else "",
    }
    artifacts["proof_json"] = _first_text(
        artifacts["proof_json"],
        source_artifacts.get("proof_json"),
        proof_source.get("path"),
        report_artifacts.get("proof_json"),
        report_sources.get("proof_json"),
        receipts.get("proof_source"),
    )
    artifacts["trace_json"] = _first_text(
        artifacts["trace_json"],
        source_artifacts.get("trace_json"),
        trace_source.get("path"),
        report_artifacts.get("trace_json"),
        report_sources.get("trace_json"),
        receipts.get("trace_source"),
    )
    artifacts["evidence_json"] = _first_text(
        artifacts["evidence_json"],
        report_artifacts.get("evidence_json"),
        report_sources.get("evidence_json"),
        receipts.get("evidence_source"),
    )

    level = _first_text(
        (evidence or {}).get("evidence_level"),
        (report or {}).get("evidence_level"),
        (trace or {}).get("evidence_level"),
        (proof or {}).get("evidence_level"),
        "HEURISTIC",
    )
    evidence_manifest = (evidence or {}).get("manifest", {}) or {}
    readiness = _first_text(evidence_manifest.get("readiness"), report_context.get("readiness"), _readiness(level))
    target_id = _first_text(
        (evidence or {}).get("target_id"),
        evidence_manifest.get("target_id"),
        (proof or {}).get("target_id"),
        (trace or {}).get("target_id"),
        (report or {}).get("target"),
    )
    target = _first_text(
        (proof or {}).get("review_map_target"),
        (trace or {}).get("review_map_target"),
        proof_source.get("review_map_target"),
        trace_source.get("review_map_target"),
        _display_target((proof or {}).get("target")),
        _display_target((trace or {}).get("target")),
        _display_target(target_id),
        _display_target((evidence or {}).get("target")),
        _display_target((report or {}).get("target")),
        slug,
    )
    evidence_package_id = _first_text(
        (evidence or {}).get("evidence_package_id"),
        evidence_manifest.get("package_id"),
        report_context.get("evidence_package_id"),
        receipts.get("evidence_package_id"),
    )
    proof_receipt_id = _first_text(
        (proof or {}).get("proof_receipt_id"),
        proof_source.get("receipt_id"),
        receipts.get("proof_receipt_id"),
    )
    trace_receipt_id = _first_text(
        (trace or {}).get("trace_receipt_id"),
        trace_source.get("receipt_id"),
        receipts.get("trace_receipt_id"),
    )
    review_status = _first_text(
        (report or {}).get("review_status"),
        report_context.get("review_status"),
        "NEEDS_HUMAN_REVIEW",
    )
    manual_review = report_readiness.get("requires_manual_review")
    if manual_review is None:
        manual_review = report_context.get("human_review_required")
    if manual_review is None:
        manual_review = True

    limitations = list(_LIMITATIONS)
    if report_path.exists():
        limitations.append("Report links are draft/manual-review only.")

    return {
        "slug": slug,
        "target": target,
        "target_id": target_id,
        "evidence_level": level,
        "readiness": readiness,
        "evidence_package_id": evidence_package_id,
        "proof_receipt_id": proof_receipt_id,
        "trace_receipt_id": trace_receipt_id,
        "artifacts": artifacts,
        "review_status": review_status,
        "manual_review_required": bool(manual_review),
        "report_status": _first_text(report_readiness.get("status"), (report or {}).get("status")),
        "report_readiness": report_readiness if isinstance(report_readiness, dict) else {},
        "limitations": limitations,
    }


def _link_for_source(context: dict, source: str, repo_root: Path) -> EvidenceLink | None:
    artifact_key = "report_json" if source == "report" else f"{source}_json"
    artifact_path = str(context["artifacts"].get(artifact_key, ""))
    if not artifact_path:
        return None
    artifacts = {
        key: _rel(value, repo_root)
        for key, value in context["artifacts"].items()
        if value
    }
    related_target = context["target"]
    return EvidenceLink(
        id=f"ev-{source}-{context['slug']}",
        source=source,
        artifact_path=_rel(artifact_path, repo_root),
        related_target=related_target,
        evidence_level=context["evidence_level"],
        status="linked",
        target=related_target,
        target_id=context["target_id"],
        readiness=context["readiness"],
        evidence_package_id=context["evidence_package_id"],
        proof_receipt_id=context["proof_receipt_id"],
        trace_receipt_id=context["trace_receipt_id"],
        artifacts=artifacts,
        artifact_kind=source,
        review_status=context["review_status"],
        manual_review_required=context["manual_review_required"],
        report_status=context["report_status"],
        report_readiness=context["report_readiness"],
        limitations=list(context["limitations"]),
    )


def generate_evidence_links(repo_root: Path, artifact_roots: list[Path] | None = None) -> list[EvidenceLink]:
    """Return evidence links for existing local artifacts (read-only scan)."""

    links: list[EvidenceLink] = []
    try:
        for root in _artifact_roots(repo_root, artifact_roots):
            for slug in _slugs(root):
                context = _context_for_slug(root, slug)
                for source in ("proof", "trace", "evidence", "report"):
                    link = _link_for_source(context, source, repo_root)
                    if link is not None:
                        links.append(link)
    except Exception:  # scanning is best-effort; never fail the review map
        return []
    return links


def _evidence_links(data: object) -> list[dict]:
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    if isinstance(data, dict):
        links = data.get("evidence_links", [])
        if isinstance(links, list):
            return [item for item in links if isinstance(item, dict)]
    return []


def _evidence_target(link: dict) -> str:
    target = str(link.get("target") or link.get("related_target") or "").strip()
    return target or "unknown"


def _evidence_level(link: dict) -> str:
    return str(link.get("evidence_level") or "HEURISTIC").strip() or "HEURISTIC"


def _evidence_path(link: dict) -> str:
    return str(link.get("artifact_path") or "").strip()


def _source_counts(links: list[dict]) -> str:
    counts: dict[str, int] = {}
    for link in links:
        source = str(link.get("source") or "unknown").strip() or "unknown"
        counts[source] = counts.get(source, 0) + 1
    return ", ".join(f"{name} {count}" for name, count in sorted(counts.items())) or "none"


def _level_counts(links: list[dict]) -> str:
    counts: dict[str, int] = {}
    for link in links:
        level = _evidence_level(link)
        counts[level] = counts.get(level, 0) + 1
    return ", ".join(f"{name} {count}" for name, count in sorted(counts.items())) or "none"


def _readiness_counts(links: list[dict]) -> str:
    counts: dict[str, int] = {}
    for link in links:
        readiness = str(link.get("readiness") or _readiness(_evidence_level(link))).strip() or "heuristic"
        counts[readiness] = counts.get(readiness, 0) + 1
    return ", ".join(f"{name} {count}" for name, count in sorted(counts.items())) or "none"


def _unique_values(links: list[dict], key: str, limit: int = 3) -> list[str]:
    values: list[str] = []
    for link in links:
        value = str(link.get(key) or "").strip()
        if value and value not in values:
            values.append(value)
        if len(values) >= limit:
            break
    return values


def _report_links(links: list[dict], limit: int = 3) -> list[str]:
    values: list[str] = []
    for link in links:
        artifacts = link.get("artifacts") if isinstance(link.get("artifacts"), dict) else {}
        value = str(artifacts.get("report_json") or "").strip()
        if value and value not in values:
            values.append(value)
        if len(values) >= limit:
            break
    return values


def render_evidence_links_cli(data: object, repo: str, *, top: int = 5, source: str = "", mode: str = "") -> str:
    """Render a concise human report for the focused evidence-links command."""

    links = _evidence_links(data)
    ranked = sorted(
        links,
        key=lambda item: (_evidence_target(item), str(item.get("source", "")), str(item.get("id", ""))),
    )
    top_links = ranked[:max(0, top)]
    display_mode = mode or (str(data.get("mode", "")) if isinstance(data, dict) else "") or "review-map evidence-links artifact"

    lines = [
        "ARKHEIONX EVIDENCE LINKS",
        "View: Evidence Links",
        "Local/static review guidance only.",
        "Evidence links are references to existing local proof, trace, evidence, or report artifacts.",
        "This command does not create evidence, execute proofs, or modify evidence records.",
        "Evidence links are not confirmed bugs; evidence level is not final severity. Human review required.",
        "",
        "Scope",
        f"  Repo: {repo}",
        f"  Mode: {display_mode}",
    ]
    if source:
        lines.append(f"  Source: {source}")
    lines += [
        "",
        "Summary",
        f"  Total evidence links: {len(links)}",
        f"  Evidence level buckets: {_level_counts(links)}",
        f"  Readiness buckets: {_readiness_counts(links)}",
        f"  Artifact source buckets: {_source_counts(links)}",
    ]
    package_ids = _unique_values(links, "evidence_package_id")
    proof_receipts = _unique_values(links, "proof_receipt_id")
    trace_receipts = _unique_values(links, "trace_receipt_id")
    report_links = _report_links(links)
    if package_ids:
        lines.append(f"  Evidence packages: {', '.join(package_ids)}")
    if proof_receipts:
        lines.append(f"  Proof receipts: {', '.join(proof_receipts)}")
    if trace_receipts:
        lines.append(f"  Trace receipts: {', '.join(trace_receipts)}")
    if report_links:
        lines.append(f"  Report drafts: {', '.join(report_links)}")
    lines += [
        "",
        "Top Evidence Links",
    ]

    if top_links:
        for index, link in enumerate(top_links, 1):
            target = _evidence_target(link)
            src = str(link.get("source") or "unknown")
            level = _evidence_level(link)
            readiness = str(link.get("readiness") or _readiness(level))
            status = str(link.get("status") or "linked")
            path = _evidence_path(link) or "path unavailable"
            lines.append(f"  {index}. {target} [{src}; {level}; {readiness}; {status}]")
            lines.append(f"     Artifact: {path}")
            refs = [
                f"package {link.get('evidence_package_id')}" if link.get("evidence_package_id") else "",
                f"proof {link.get('proof_receipt_id')}" if link.get("proof_receipt_id") else "",
                f"trace {link.get('trace_receipt_id')}" if link.get("trace_receipt_id") else "",
            ]
            refs = [ref for ref in refs if ref]
            if refs:
                lines.append(f"     Receipts: {', '.join(refs)}")
            artifacts = link.get("artifacts") if isinstance(link.get("artifacts"), dict) else {}
            report_path = str(artifacts.get("report_json") or "").strip()
            report_status = str(link.get("report_status") or "").strip()
            if report_path:
                suffix = f"; {report_status}" if report_status else ""
                lines.append(f"     Report: {report_path} (draft/manual review{suffix})")
    else:
        lines.append("  No evidence links found.")
        lines.append("  Review-map did not find existing local proof, trace, evidence, or report artifacts to link.")

    lines += [
        "",
        "Next",
        f"  Full review map: arkheionx review-map {repo}",
        f"  Test gaps: arkheionx test-gap-map {repo}",
        f"  Value paths: arkheionx value-paths {repo}",
        f"  Assumptions: arkheionx assumptions {repo}",
        f"  Proof plan: arkheionx proof-plan {repo}",
        f"  Create local evidence from a target: arkheionx evidence {repo} --target <Contract.function>",
        f"  Draft report after evidence: arkheionx report {repo} --target <Contract.function>",
        "",
        "Boundary",
        "  Local/static only. No RPC, no private keys, no live-chain calls.",
        "  No exploit automation, no transaction broadcasting, no auto-submit.",
        "  Read-only evidence-link view. No evidence was created or promoted.",
        "  Review guidance only. Human review required.",
    ]
    return "\n".join(lines) + "\n"

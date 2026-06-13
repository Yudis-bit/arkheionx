"""Extract a lens's protocol model from a local repository.

Given a :class:`~arkheionx.protocol_lens.base.ProtocolLens` and an authorized local
repo, this scans Solidity source for the lens's extraction groups (terms, function
hints, state-variable names) and produces a structured :class:`ProtocolModel`.

Symbols the lens looked for but did not find are marked
:data:`~arkheionx.protocol_lens.models.UNKNOWN_IN_LOCAL_REPO`. Nothing is invented.

It reuses the v4 review map and the v7 repo context (surface records) and the
existing Solidity file finder, so the lens layer stays consistent with the layers
it builds on. Local/static only: it reads files; it never executes anything.
"""
from __future__ import annotations

import re
from pathlib import Path

from arkheionx.protocol.semantic_adapter import find_solidity_files
from arkheionx.review_map.model import ReviewMap
from arkheionx.scope_orchestration import scope_parser
from arkheionx.scope_orchestration.repo_context import build_repo_context

from . import models as m
from .base import ProtocolLens

_MAX_FILE_BYTES = 2_000_000


def _read_text(path: Path) -> str:
    try:
        if path.stat().st_size > _MAX_FILE_BYTES:
            return ""
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def _rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _term_pattern(term: str) -> re.Pattern:
    # Match the term as a whole identifier-ish token (case-insensitive), so
    # "credit" does not match inside "accredited".
    return re.compile(rf"(?<![A-Za-z0-9_]){re.escape(term)}(?![A-Za-z0-9_])", re.IGNORECASE)


def scan_terms(lens: ProtocolLens, source_texts: dict[str, str]) -> tuple[list[dict], dict[str, list[str]]]:
    """Scan source files for each extraction group's terms.

    Returns ``(groups, term_files)`` where ``groups`` is a per-group record with
    found terms (and the files they appear in) and unknown terms, and ``term_files``
    maps a lowercased term to the sorted files that contain it.
    """
    term_files: dict[str, list[str]] = {}
    compiled: dict[str, re.Pattern] = {}

    groups_out: list[dict] = []
    for grp in lens.extraction_groups():
        found: list[dict] = []
        unknown: list[str] = []
        for term in grp.terms:
            key = term.lower()
            pat = compiled.get(key)
            if pat is None:
                pat = _term_pattern(term)
                compiled[key] = pat
            files = sorted(rel for rel, text in source_texts.items() if pat.search(text))
            if files:
                term_files[key] = files
                found.append({"term": term, "files": files[:12], "file_count": len(files)})
            else:
                unknown.append(term)
        groups_out.append({
            "group_id": grp.group_id,
            "title": grp.title,
            "found": found,
            "found_count": len(found),
            "unknown": unknown,
            "unknown_status": m.UNKNOWN_IN_LOCAL_REPO if unknown else "",
        })
    return groups_out, term_files


def _periphery_models(lens: ProtocolLens, records, source_texts: dict[str, str]) -> list[dict]:
    """Bind periphery function-name hints to discovered functions and cap usage."""
    hints = [h.lower() for h in lens.periphery_function_names()]
    if not hints:
        return []
    cap_terms = ("targetassets", "targetunits", "maxassets", "maxunits")
    out: list[dict] = []
    seen: set[str] = set()
    for rec in records:
        fn = (rec.function or "").lower()
        if not fn or rec.target in seen:
            continue
        if not any(h in fn for h in hints):
            continue
        seen.add(rec.target)
        src_file = (rec.source or "").split(":", 1)[0]
        text = source_texts.get(src_file, "")
        caps = sorted({c for c in cap_terms if c in text.lower()})
        model = m.PeripheryFunctionModel(
            name=rec.target,
            target_kind=m.UNKNOWN_IN_LOCAL_REPO,
            side=m.UNKNOWN_IN_LOCAL_REPO,
            gross_net=m.UNKNOWN_IN_LOCAL_REPO,
            caps=caps or [m.UNKNOWN_IN_LOCAL_REPO],
            source=rec.source or "",
            notes="Cap dimension and net/gross must be confirmed by reading the function; not inferred.",
        )
        out.append(model.to_dict())
    return out


def bind_functions(records, hints: list[str]) -> list[dict]:
    """Return discovered surfaces whose function name matches any hint substring."""
    low = [h.lower() for h in hints if h]
    out: list[dict] = []
    seen: set[str] = set()
    for rec in records:
        fn = (rec.function or "").lower()
        if not fn or rec.target in seen:
            continue
        if any(h in fn for h in low):
            seen.add(rec.target)
            out.append({"target": rec.target, "function": rec.function,
                        "contract": rec.contract, "source": rec.source or ""})
    return out


def extract_protocol_model(lens: ProtocolLens, root: Path | str, records=None) -> dict:
    """Build the structured :class:`ProtocolModel` for ``lens`` against ``root``."""
    root = Path(root)
    sources, _tests = find_solidity_files(root)
    source_texts: dict[str, str] = {}
    for p in sources:
        rel = _rel(Path(p), root)
        source_texts[rel] = _read_text(Path(p))

    groups, term_files = scan_terms(lens, source_texts)
    discovered = sorted(term_files)
    unknown = sorted({t for g in groups for t in g["unknown"]})

    periphery = _periphery_models(lens, records or [], source_texts)

    value_flows: list[dict] = []
    for vf in lens.value_flow_templates():
        present = [s for s in vf.signals if s.lower() in term_files]
        d = vf.to_dict()
        d["discovered_signals"] = present
        d["status"] = "observed" if present else m.UNKNOWN_IN_LOCAL_REPO
        value_flows.append(d)

    notes = []
    if not sources:
        notes.append("No Solidity source files found locally; the protocol model is empty.")
    if unknown:
        notes.append(f"{len(unknown)} lens term(s) were not found locally and are marked {m.UNKNOWN_IN_LOCAL_REPO}.")

    model = m.ProtocolModel(
        lens_id=lens.lens_id,
        families=list(lens.meta().families),
        groups=groups,
        discovered_terms=discovered,
        unknown_terms=unknown,
        periphery_functions=periphery,
        value_flow_paths=value_flows,
        source_files=sorted(source_texts),
        notes=notes,
    )
    return {"model": model.to_dict(), "term_files": term_files, "source_texts_count": len(source_texts)}


def build_lens_context(lens: ProtocolLens, rm: ReviewMap, root: Path | str,
                       scope_file: str | None = None, *,
                       source_files: int = 0, test_files: int = 0) -> dict:
    """Build the shared lens context reused by every builder.

    Returns scope data, surface records, repo summary, the extracted protocol
    model, and term/function binding indexes. No source file is re-scanned by the
    downstream builders.
    """
    root = Path(root)
    scope = scope_parser.parse_scope_file(scope_file)
    ctx = build_repo_context(rm, root, source_files=source_files, test_files=test_files)
    records = ctx["records"]
    extraction = extract_protocol_model(lens, root, records=records)
    return {
        "lens": lens,
        "scope": scope,
        "records": records,
        "repo_summary": ctx["repo_summary"],
        "generated_at": ctx["generated_at"],
        "protocol_model": extraction["model"],
        "term_files": extraction["term_files"],
    }

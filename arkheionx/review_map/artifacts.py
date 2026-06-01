"""Write Review Map artifacts deterministically (plain text, no ANSI).

Default output directory is ``<repo>/.arkheionx/out/review-map/``. ``--out``
overrides it and writes directly into the given directory. Nothing is written
in ``--no-write`` mode (the caller simply does not call :func:`write_artifacts`).
"""
from __future__ import annotations

import json
from pathlib import Path

from . import render
from .model import ReviewMap, to_dict


def default_out_dir(repo_root: Path) -> Path:
    return repo_root / ".arkheionx" / "out" / "review-map"


def _write(path: Path, content: str) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not content.endswith("\n"):
        content += "\n"
    path.write_text(content, encoding="utf-8")
    return str(path)


def _json(payload: object) -> str:
    return json.dumps(payload, indent=2)


def write_artifacts(rm: ReviewMap, out_dir: Path, include_mermaid: bool = True) -> dict[str, str]:
    out_dir = Path(out_dir)
    meta = {"schema_version": rm.schema_version, "generated_at": rm.generated_at, "repo_path": rm.repo_path}
    written: dict[str, str] = {}
    written["review-map.json"] = _write(out_dir / "review-map.json", _json(rm.to_payload()))
    written["review-map.md"] = _write(out_dir / "review-map.md", render.render_markdown(rm))
    written["value-paths.json"] = _write(out_dir / "value-paths.json", _json({**meta, "value_paths": to_dict(rm.value_paths)}))
    written["test-gaps.json"] = _write(out_dir / "test-gaps.json", _json({**meta, "test_gaps": to_dict(rm.test_gaps)}))
    written["assumptions.json"] = _write(out_dir / "assumptions.json", _json({**meta, "assumptions": to_dict(rm.assumptions)}))
    written["proof-plan.json"] = _write(out_dir / "proof-plan.json", _json({**meta, "proof_suggestions": to_dict(rm.proof_suggestions)}))
    written["evidence-links.json"] = _write(out_dir / "evidence-links.json", _json({**meta, "evidence_links": to_dict(rm.evidence_links)}))
    written["review-summary.md"] = _write(out_dir / "review-summary.md", render.render_summary_md(rm))
    if include_mermaid:
        written["review-map.mmd"] = _write(out_dir / "review-map.mmd", render.render_mermaid(rm))
    return written

"""Write Review Map artifacts deterministically (plain text, no ANSI).

Default output directory is ``<repo>/.arkheionx/out/review-map/``. ``--out``
overrides it and writes directly into the given directory. Nothing is written
in ``--no-write`` mode (the caller simply does not call :func:`write_artifacts`).
"""
from __future__ import annotations

import json
from pathlib import Path

from . import render
from .assumptions import build_assumptions_payload
from .evidence_links import build_evidence_links_payload
from .model import ReviewMap, to_dict
from .proof_plan import build_proof_plan_payload
from .test_gap_map import build_test_gap_map, render_test_gap_map_md
from .value_paths import build_value_paths_payload


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
    written["value-paths.json"] = _write(out_dir / "value-paths.json", _json(build_value_paths_payload(rm)))
    written["test-gaps.json"] = _write(out_dir / "test-gaps.json", _json({**meta, "test_gaps": to_dict(rm.test_gaps)}))
    written["assumptions.json"] = _write(out_dir / "assumptions.json", _json(build_assumptions_payload(rm)))
    written["proof-plan.json"] = _write(out_dir / "proof-plan.json", _json(build_proof_plan_payload(rm)))
    written["evidence-links.json"] = _write(out_dir / "evidence-links.json", _json(build_evidence_links_payload(rm)))
    written["review-summary.md"] = _write(out_dir / "review-summary.md", render.render_summary_md(rm))
    test_gap_map = build_test_gap_map(rm)
    written["test-gap-map.json"] = _write(out_dir / "test-gap-map.json", _json(test_gap_map))
    written["test-gap-map.md"] = _write(out_dir / "test-gap-map.md", render_test_gap_map_md(test_gap_map))
    if include_mermaid:
        written["review-map.mmd"] = _write(out_dir / "review-map.mmd", render.render_mermaid(rm))
    return written

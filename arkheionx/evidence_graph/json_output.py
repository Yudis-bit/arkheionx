"""Write v6 Evidence Graph artifacts deterministically (plain text).

JSON is ``json.dumps(payload, indent=2)``; Markdown comes from the renderers.
Default output directories live under ``<repo>/.arkheionx/`` (gitignored).
"""
from __future__ import annotations

import json
from pathlib import Path

from . import render


def default_evidence_graph_dir(repo_root: Path) -> Path:
    return Path(repo_root) / ".arkheionx" / "evidence-graph"


def default_interaction_matrix_dir(repo_root: Path) -> Path:
    return Path(repo_root) / ".arkheionx" / "interaction-matrix"


def default_unresolved_map_dir(repo_root: Path) -> Path:
    return Path(repo_root) / ".arkheionx" / "unresolved-map"


def default_complete_review_dir(repo_root: Path) -> Path:
    return Path(repo_root) / ".arkheionx" / "complete-review"


def _write(path: Path, content: str) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not content.endswith("\n"):
        content += "\n"
    path.write_text(content, encoding="utf-8")
    return str(path)


def _json(payload: object) -> str:
    return json.dumps(payload, indent=2)


def write_evidence_graph(data: dict, out_dir: Path) -> dict[str, str]:
    out_dir = Path(out_dir)
    return {
        "evidence-graph.json": _write(out_dir / "evidence-graph.json", _json(data)),
        "evidence-graph.md": _write(out_dir / "evidence-graph.md", render.render_evidence_graph_md(data)),
    }


def write_interaction_matrix(data: dict, out_dir: Path) -> dict[str, str]:
    out_dir = Path(out_dir)
    return {
        "interaction-matrix.json": _write(out_dir / "interaction-matrix.json", _json(data)),
        "interaction-matrix.md": _write(out_dir / "interaction-matrix.md", render.render_interaction_matrix_md(data)),
    }


def write_unresolved_map(data: dict, out_dir: Path) -> dict[str, str]:
    out_dir = Path(out_dir)
    return {
        "unresolved-map.json": _write(out_dir / "unresolved-map.json", _json(data)),
        "unresolved-map.md": _write(out_dir / "unresolved-map.md", render.render_unresolved_map_md(data)),
    }

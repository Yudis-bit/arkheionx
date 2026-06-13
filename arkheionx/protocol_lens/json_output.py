"""Write v7.5 lens artifacts deterministically (plain text + JSON).

JSON is ``json.dumps(payload, indent=2)``; Markdown comes from the renderers.
Default output directories live under ``<repo>/.arkheionx/`` (gitignored).
"""
from __future__ import annotations

import json
from pathlib import Path

from . import render


def default_lens_map_dir(repo_root: Path) -> Path:
    return Path(repo_root) / ".arkheionx" / "lens-map"


def default_lens_lanes_dir(repo_root: Path) -> Path:
    return Path(repo_root) / ".arkheionx" / "lens-lanes"


def default_lens_tasks_dir(repo_root: Path) -> Path:
    return Path(repo_root) / ".arkheionx" / "lens-tasks"


def default_lens_evidence_dir(repo_root: Path) -> Path:
    return Path(repo_root) / ".arkheionx" / "lens-evidence"


def default_lens_report_filter_dir(repo_root: Path) -> Path:
    return Path(repo_root) / ".arkheionx" / "lens-report-filter"


def default_lens_pack_dir(repo_root: Path) -> Path:
    return Path(repo_root) / ".arkheionx" / "lens-pack"


def _write(path: Path, content: str) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not content.endswith("\n"):
        content += "\n"
    path.write_text(content, encoding="utf-8")
    return str(path)


def _json(payload: object) -> str:
    return json.dumps(payload, indent=2)


def write_lens_map(data: dict, out_dir: Path) -> dict[str, str]:
    out_dir = Path(out_dir)
    return {
        "lens-map.json": _write(out_dir / "lens-map.json", _json(data)),
        "lens-map.md": _write(out_dir / "lens-map.md", render.render_lens_map_md(data)),
    }


def write_lens_lanes(data: dict, out_dir: Path) -> dict[str, str]:
    out_dir = Path(out_dir)
    return {
        "lens-lanes.json": _write(out_dir / "lens-lanes.json", _json(data)),
        "lens-lanes.md": _write(out_dir / "lens-lanes.md", render.render_review_lanes_md(data)),
    }


def write_lens_tasks(data: dict, out_dir: Path) -> dict[str, str]:
    out_dir = Path(out_dir)
    return {
        "lens-tasks.json": _write(out_dir / "lens-tasks.json", _json(data)),
        "lens-tasks.md": _write(out_dir / "lens-tasks.md", render.render_scope_tasks_md(data)),
    }


def write_lens_evidence(data: dict, out_dir: Path) -> dict[str, str]:
    out_dir = Path(out_dir)
    return {
        "lens-evidence.json": _write(out_dir / "lens-evidence.json", _json(data)),
        "lens-evidence.md": _write(out_dir / "lens-evidence.md", render.render_evidence_map_md(data)),
    }


def write_lens_report_filter(data: dict, out_dir: Path) -> dict[str, str]:
    out_dir = Path(out_dir)
    return {
        "lens-report-filter.json": _write(out_dir / "lens-report-filter.json", _json(data)),
        "lens-report-filter.md": _write(out_dir / "lens-report-filter.md", render.render_report_filter_md(data)),
    }

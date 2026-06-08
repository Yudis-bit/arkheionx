"""Write v7 scope-orchestration artifacts deterministically (plain text + JSON).

JSON is ``json.dumps(payload, indent=2)``; Markdown comes from the renderers.
Default output directories live under ``<repo>/.arkheionx/`` (gitignored).
"""
from __future__ import annotations

import json
from pathlib import Path

from . import render


def default_scope_map_dir(repo_root: Path) -> Path:
    return Path(repo_root) / ".arkheionx" / "scope-map"


def default_scope_lanes_dir(repo_root: Path) -> Path:
    return Path(repo_root) / ".arkheionx" / "scope-lanes"


def default_scope_tasks_dir(repo_root: Path) -> Path:
    return Path(repo_root) / ".arkheionx" / "scope-tasks"


def default_scope_pack_dir(repo_root: Path) -> Path:
    return Path(repo_root) / ".arkheionx" / "scope-pack"


def default_evidence_judge_dir(repo_root: Path) -> Path:
    return Path(repo_root) / ".arkheionx" / "evidence-judge"


def default_report_filter_dir(repo_root: Path) -> Path:
    return Path(repo_root) / ".arkheionx" / "report-filter"


def _write(path: Path, content: str) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not content.endswith("\n"):
        content += "\n"
    path.write_text(content, encoding="utf-8")
    return str(path)


def _json(payload: object) -> str:
    return json.dumps(payload, indent=2)


def write_scope_map(data: dict, out_dir: Path) -> dict[str, str]:
    out_dir = Path(out_dir)
    return {
        "scope-map.json": _write(out_dir / "scope-map.json", _json(data)),
        "scope-map.md": _write(out_dir / "scope-map.md", render.render_scope_map_md(data)),
    }


def write_scope_lanes(data: dict, out_dir: Path) -> dict[str, str]:
    out_dir = Path(out_dir)
    return {
        "scope-lanes.json": _write(out_dir / "scope-lanes.json", _json(data)),
        "scope-lanes.md": _write(out_dir / "scope-lanes.md", render.render_scope_lanes_md(data)),
    }


def write_scope_tasks(data: dict, out_dir: Path) -> dict[str, str]:
    out_dir = Path(out_dir)
    return {
        "scope-tasks.json": _write(out_dir / "scope-tasks.json", _json(data)),
        "scope-tasks.md": _write(out_dir / "scope-tasks.md", render.render_scope_tasks_md(data)),
    }


def write_evidence_judge(data: dict, out_dir: Path) -> dict[str, str]:
    out_dir = Path(out_dir)
    return {
        "evidence-judge.json": _write(out_dir / "evidence-judge.json", _json(data)),
        "evidence-judge.md": _write(out_dir / "evidence-judge.md", render.render_evidence_judge_md(data)),
    }


def write_report_filter(data: dict, out_dir: Path) -> dict[str, str]:
    out_dir = Path(out_dir)
    return {
        "report-filter.json": _write(out_dir / "report-filter.json", _json(data)),
        "report-filter.md": _write(out_dir / "report-filter.md", render.render_report_filter_md(data)),
    }

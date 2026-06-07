"""Write v5 Blind Spot Intelligence artifacts deterministically (plain text).

JSON is ``json.dumps(payload, indent=2)``; Markdown comes from the renderers.
Default output directories live under ``<repo>/.arkheionx/`` (gitignored).
"""
from __future__ import annotations

import json
from pathlib import Path

from . import render


def default_blind_spots_dir(repo_root: Path) -> Path:
    return Path(repo_root) / ".arkheionx" / "blind-spots"


def default_criticality_dir(repo_root: Path) -> Path:
    return Path(repo_root) / ".arkheionx" / "criticality-map"


def default_counterfactuals_dir(repo_root: Path) -> Path:
    return Path(repo_root) / ".arkheionx" / "counterfactuals"


def default_research_pack_dir(repo_root: Path) -> Path:
    return Path(repo_root) / ".arkheionx" / "research-pack"


def _write(path: Path, content: str) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not content.endswith("\n"):
        content += "\n"
    path.write_text(content, encoding="utf-8")
    return str(path)


def _json(payload: object) -> str:
    return json.dumps(payload, indent=2)


def write_blind_spots(data: dict, out_dir: Path) -> dict[str, str]:
    out_dir = Path(out_dir)
    return {
        "blind-spots.json": _write(out_dir / "blind-spots.json", _json(data)),
        "blind-spots.md": _write(out_dir / "blind-spots.md", render.render_blind_spots_md(data)),
    }


def write_criticality_map(data: dict, out_dir: Path) -> dict[str, str]:
    out_dir = Path(out_dir)
    return {
        "criticality-map.json": _write(out_dir / "criticality-map.json", _json(data)),
        "criticality-map.md": _write(out_dir / "criticality-map.md", render.render_criticality_map_md(data)),
    }


def write_counterfactuals(data: dict, out_dir: Path) -> dict[str, str]:
    out_dir = Path(out_dir)
    return {
        "counterfactuals.json": _write(out_dir / "counterfactuals.json", _json(data)),
        "counterfactuals.md": _write(out_dir / "counterfactuals.md", render.render_counterfactuals_md(data)),
    }

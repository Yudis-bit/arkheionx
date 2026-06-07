"""Write research-memory artifacts deterministically (plain text, no ANSI).

Default output directory is ``<repo>/.arkheionx/research/``. ``--out`` overrides
it. JSON is ``json.dumps(payload, indent=2)``; Markdown comes from the renderers.
"""
from __future__ import annotations

import json
from pathlib import Path

from . import agent_brief, case_study, hypothesis_log


def default_research_dir(repo_root: Path) -> Path:
    return repo_root / ".arkheionx" / "research"


def _write(path: Path, content: str) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not content.endswith("\n"):
        content += "\n"
    path.write_text(content, encoding="utf-8")
    return str(path)


def _json(payload: object) -> str:
    return json.dumps(payload, indent=2)


def write_agent_brief(data: dict, out_dir: Path) -> dict[str, str]:
    out_dir = Path(out_dir)
    return {
        "agent-brief.json": _write(out_dir / "agent-brief.json", _json(data)),
        "agent-brief.md": _write(out_dir / "agent-brief.md", agent_brief.render_agent_brief_md(data)),
    }


def write_hypothesis_log(data: dict, out_dir: Path) -> dict[str, str]:
    out_dir = Path(out_dir)
    return {
        "hypotheses.json": _write(out_dir / "hypotheses.json", _json(data)),
        "hypotheses.md": _write(out_dir / "hypotheses.md", hypothesis_log.render_hypothesis_log_md(data)),
    }


def write_case_study(data: dict, out_dir: Path) -> dict[str, str]:
    out_dir = Path(out_dir)
    return {
        "case-study.json": _write(out_dir / "case-study.json", _json(data)),
        "case-study.md": _write(out_dir / "case-study.md", case_study.render_case_study_md(data)),
    }

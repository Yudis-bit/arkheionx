from pathlib import Path

from arkheionx.warrun import run_war_run

ROOT = Path(__file__).resolve().parents[1] / "fixtures" / "repos"


def run_fixture(name: str, **kwargs):
    return run_war_run(ROOT / name, write=False, **kwargs)

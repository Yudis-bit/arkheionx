from pathlib import Path

from arkheionx.auth import analyze_authorization
from arkheionx.semantic import build_semantic_map

ROOT = Path(__file__).resolve().parents[1] / "fixtures" / "auth"


def analyze(name: str):
    return analyze_authorization(build_semantic_map(ROOT / name))

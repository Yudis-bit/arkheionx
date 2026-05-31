"""Registry of safe, local-only Arkheionx demo fixtures."""
from __future__ import annotations

from pathlib import Path

from arkheionx.demo.model import Demo

# Repository root that ships the bundled example fixtures (works from a source
# checkout or an editable install). arkheionx/demo/registry.py -> repo root.
REPO_ROOT = Path(__file__).resolve().parents[2]

DEMOS: list[Demo] = [
    Demo(
        id="oracle-staking",
        name="Oracle Staking Fixture",
        description="Local fixture for the open/hunt/prove/trace/evidence/report workflow.",
        path="examples/oracle-staking-fixture",
        recommended_target="OracleRewardFixture.stake",
        requires_foundry=False,
        expected_mode="heuristic (compiler/execution-confirmed with Foundry)",
        docs="docs/DEMO_WORKFLOW.md",
        notes="Toy fixture only. Not a real protocol and not a real vulnerability report.",
    ),
]


def list_demos() -> list[Demo]:
    return list(DEMOS)


def get_demo(demo_id: str) -> Demo | None:
    for demo in DEMOS:
        if demo.id == demo_id:
            return demo
    return None


def demo_ids() -> list[str]:
    return [demo.id for demo in DEMOS]


def source_dir(demo: Demo) -> Path:
    return (REPO_ROOT / demo.path).resolve()


def workflow_commands(demo: Demo, dest: str) -> tuple[list[str], list[str]]:
    """Return (heuristic_commands, foundry_commands) for a copied demo at dest."""
    heuristic = [
        "arkheionx doctor",
        f"arkheionx open {dest}",
        f"arkheionx map {dest}",
        f"arkheionx flow {dest}",
        f"arkheionx hunt {dest} --top 5",
        f"arkheionx evidence-status {dest}",
        f"arkheionx validate-artifacts {dest}",
    ]
    foundry = [
        f"arkheionx prove {dest} --target {demo.recommended_target} --run",
        f"arkheionx trace {dest} --target {demo.recommended_target}",
        f"arkheionx evidence {dest} --target {demo.recommended_target}",
        f"arkheionx report {dest} --target {demo.recommended_target}",
    ]
    return heuristic, foundry

"""Registry of safe, local-only Arkheionx demo fixtures.

Demo fixtures are resolved as bundled package resources first
(`arkheionx.demo.fixtures.<id>`), falling back to the source-checkout copy
under `examples/` for development. This lets `arkheionx demo --copy` work from
an installed package, not only from a repository checkout.
"""
from __future__ import annotations

import importlib.resources as resources
from contextlib import contextmanager
from pathlib import Path

from arkheionx.demo.model import Demo

# Repository root for the source-checkout fallback. registry.py -> repo root.
REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES_PACKAGE = "arkheionx.demo.fixtures"

PACKAGE_SOURCE = "bundled package fixture"
CHECKOUT_SOURCE = "source checkout fixture"

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


def _package_fixture(demo: Demo):
    """Return the bundled package resource for a demo, or None."""
    try:
        root = resources.files(FIXTURES_PACKAGE).joinpath(demo.id)
    except (ModuleNotFoundError, FileNotFoundError):
        return None
    try:
        return root if root.is_dir() else None
    except OSError:
        return None


def _checkout_fixture(demo: Demo) -> Path | None:
    candidate = (REPO_ROOT / demo.path)
    return candidate if candidate.is_dir() else None


def resolve_source_kind(demo: Demo) -> str:
    """Describe where the fixture would resolve from, without copying."""
    if _package_fixture(demo) is not None:
        return PACKAGE_SOURCE
    if _checkout_fixture(demo) is not None:
        return CHECKOUT_SOURCE
    return "unavailable"


@contextmanager
def fixture_source(demo: Demo):
    """Yield (concrete_dir, source_kind) for a demo fixture.

    Prefers the bundled package resource and falls back to the source checkout.
    Uses importlib.resources.as_file so package data works even when zipped.
    """
    package = _package_fixture(demo)
    if package is not None:
        with resources.as_file(package) as real_dir:
            yield Path(real_dir), PACKAGE_SOURCE
        return
    checkout = _checkout_fixture(demo)
    if checkout is not None:
        yield checkout, CHECKOUT_SOURCE
        return
    raise FileNotFoundError(
        "demo fixture resource not found; reinstall Arkheionx or use a source checkout."
    )


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

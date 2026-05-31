#!/usr/bin/env python3
"""Aggregate release-readiness gate for Arkheionx.

Complements the focused checkers (version consistency, docs links, safety
wording) with readiness-specific checks: public command surface coverage,
stability/readiness docs, README stable line and visuals, bundled fixtures,
release notes / changelog presence, and forbidden distribution claims.

Reads only current/live surface (README + the readiness docs); historical files
under release-notes/ and CHANGELOG history are intentionally not scanned for
claim wording.
"""
from __future__ import annotations

import argparse
import importlib
import importlib.util
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from arkheionx.version import CURRENT_MILESTONE, STABLE_RELEASE, __version__  # noqa: E402

REQUIRED_VISUALS = [
    "docs/assets/arkheionx-workflow-v27.svg",
    "docs/assets/arkheionx-output-pipeline.svg",
    "docs/assets/arkheionx-evidence-ladder.svg",
    "docs/assets/arkheionx-v3-architecture.svg",
    "docs/assets/arkheionx-v3-public-surface.svg",
    "docs/assets/arkheionx-v3-demo-fixtures.svg",
    "docs/assets/arkheionx-v3-stability.svg",
]
READINESS_DOCS = [
    "docs/PUBLIC_SURFACE.md",
    "docs/STABILITY_CONTRACT.md",
    "docs/V3_READINESS.md",
]
REQUIRED_README_DISCLAIMERS = [
    "No RPC by default",
    "No private keys or secrets",
    "No automated exploitation",
    "No auto-submit",
    "No guaranteed vulnerability discovery",
    "No severity guarantee",
]
# Promotional claims that must not appear on the live README surface. Phrased to
# avoid colliding with the negative disclaimers above (e.g. "No Homebrew").
FORBIDDEN_README = [
    r"\bpip install arkheionx\b",
    r"\bbrew install\b",
    r"\bhomebrew tap\b",
    r"download the (?:standalone )?binary",
    r"guaranteed to (?:find|discover)",
    r"\bbounty eligible\b",
    r"automatically submits?",
]


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8", errors="ignore")


def public_commands() -> list[str]:
    main = importlib.import_module("arkheionx.cli.main")
    parser = main.build_parser()
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            return list(action.choices.keys())
    return []


def bundled_demos() -> list[str]:
    from importlib.resources import files

    root = files("arkheionx.demo.fixtures")
    demos = []
    for entry in root.iterdir():
        if entry.is_dir() and entry.joinpath("foundry.toml").is_file():
            demos.append(entry.name)
    return sorted(demos)


def check() -> list[str]:
    failures: list[str] = []

    # Reuse the focused checkers.
    failures += _load("check_version_consistency").check()
    failures += [f"docs link: {item}" for item in _load("check_docs_links").missing_links()]
    failures += [f"safety wording: {item}" for item in _load("check_safety_wording").scan()]

    readme = read("README.md")

    # Readiness docs.
    for doc in READINESS_DOCS:
        if not (ROOT / doc).is_file():
            failures.append(f"missing readiness doc: {doc}")

    # Public command surface coverage.
    surface = read("docs/PUBLIC_SURFACE.md") if (ROOT / "docs/PUBLIC_SURFACE.md").is_file() else ""
    for command in public_commands():
        if f"`arkheionx {command}`" not in surface:
            failures.append(f"docs/PUBLIC_SURFACE.md does not list command: {command}")
    for script in ("install.sh", "uninstall.sh", "arkup"):
        if f"`{script}`" not in surface:
            failures.append(f"docs/PUBLIC_SURFACE.md does not list script: {script}")

    # README stable line and visuals.
    if f"Latest stable release: **{STABLE_RELEASE}" not in readme:
        failures.append(f"README.md missing latest stable line for {STABLE_RELEASE}")
    for visual in REQUIRED_VISUALS:
        if not (ROOT / visual).is_file():
            failures.append(f"missing README visual: {visual}")
        if visual not in readme:
            failures.append(f"README.md does not reference visual: {visual}")
    for disclaimer in REQUIRED_README_DISCLAIMERS:
        if disclaimer not in readme:
            failures.append(f"README.md missing safety disclaimer: {disclaimer}")
    for pattern in FORBIDDEN_README:
        if re.search(pattern, readme, re.IGNORECASE):
            failures.append(f"README.md contains forbidden claim pattern: {pattern}")

    # Bundled fixtures and demo-id documentation.
    demos = bundled_demos()
    if not demos:
        failures.append("no bundled demo fixtures found")
    for doc in ("docs/DEMO_WORKFLOW.md", "docs/PACKAGE_DATA.md"):
        text = read(doc)
        for demo in demos:
            if demo not in text:
                failures.append(f"{doc} does not mention demo: {demo}")

    # Release notes and changelog for the current milestone.
    notes = ROOT / "release-notes" / f"{CURRENT_MILESTONE}.md"
    if not notes.is_file():
        failures.append(f"missing release notes: release-notes/{CURRENT_MILESTONE}.md")
    if f"## {CURRENT_MILESTONE}" not in read("CHANGELOG.md"):
        failures.append(f"CHANGELOG.md missing section: ## {CURRENT_MILESTONE}")

    # GitHub Action examples and install/arkup stable tag track STABLE_RELEASE.
    action_tag = f"pre-audit@{STABLE_RELEASE}"
    for doc in ("README.md", "docs/GITHUB_ACTION_USAGE.md"):
        if action_tag not in read(doc):
            failures.append(f"{doc} GitHub Action example does not use {action_tag}")
    stable_tag_line = f'ARKHEIONX_STABLE_TAG:-{STABLE_RELEASE}'
    for script in ("install.sh", "arkup"):
        if stable_tag_line not in read(script):
            failures.append(f"{script} stable tag does not track STABLE_RELEASE ({STABLE_RELEASE})")

    # No stale dev wording on the live README surface (dev version must not leak).
    if __version__.endswith("-dev") and __version__ in readme:
        failures.append(f"README.md leaks dev version string {__version__}")
    for claim in (f"{CURRENT_MILESTONE} is released", f"{CURRENT_MILESTONE} released", "now on PyPI", "available on PyPI"):
        if claim.lower() in readme.lower():
            failures.append(f"README.md contains premature/forbidden claim: {claim}")

    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check Arkheionx release readiness.")
    parser.add_argument("--check", action="store_true", help="Exit nonzero if not ready.")
    args = parser.parse_args(argv)
    failures = check()
    if failures:
        print("Release readiness issues:")
        for failure in failures:
            print(f"- {failure}")
        return 1 if args.check else 0
    print(f"ok: release readiness valid ({CURRENT_MILESTONE}, stable {STABLE_RELEASE})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

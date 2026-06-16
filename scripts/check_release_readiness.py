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

# The clean v8.0.1 product README no longer embeds the architecture image wall.
# Visual assets still live under docs/assets/ for the docs site, but the README is
# intentionally text-first, so no visuals are required on the README surface.
REQUIRED_VISUALS: list[str] = []
READINESS_DOCS = [
    "docs/PUBLIC_SURFACE.md",
    "docs/STABILITY_CONTRACT.md",
    "docs/V3_READINESS.md",
]
REQUIRED_README_BOUNDARIES = [
    ("No RPC by default", ["No RPC by default"]),
    ("No private keys or secrets", ["No private keys or secrets", "private keys"]),
    ("No automated exploitation", ["No automated exploitation", "exploit automation"]),
    ("No auto-submit", ["No auto-submit", "auto-submit"]),
    (
        "No automatic vulnerability discovery claim",
        ["does not automatically find vulnerabilities", "No automatic vulnerability discovery"],
    ),
    ("No bounty guarantee claim", ["guarantee bounty outcomes", "No bounty guarantee"]),
    ("No severity guarantee", ["No severity guarantee"]),
    ("Human review required", ["Human review required"]),
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
    private_dev = ".dev" in __version__ or CURRENT_MILESTONE.endswith("-dev")

    # Reuse the focused checkers.
    failures += _load("check_version_consistency").check()
    failures += [f"docs link: {item}" for item in _load("check_docs_links").missing_links()]
    failures += [f"safety wording: {item}" for item in _load("check_safety_wording").scan()]

    readme = read("README.md")

    # License must be resolved for public alpha: a real LICENSE file must exist
    # and the README must point to it (not advertise a pending license).
    if not (ROOT / "LICENSE").is_file():
        failures.append("missing LICENSE file (public-alpha blocker)")
    if "](LICENSE)" not in readme:
        failures.append("README.md does not link the canonical LICENSE file")
    if "License selection is pending" in readme:
        failures.append("README.md still advertises a pending license")

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
    readme_lower = readme.lower()
    for label, options in REQUIRED_README_BOUNDARIES:
        if not any(option.lower() in readme_lower for option in options):
            failures.append(f"README.md missing safety boundary: {label}")
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

    # Private development milestones keep the public release surface pinned to the
    # latest stable release until an explicit release-prep change is made.
    release_milestone = STABLE_RELEASE if private_dev else CURRENT_MILESTONE
    notes = ROOT / "release-notes" / f"{release_milestone}.md"
    if not notes.is_file():
        failures.append(f"missing release notes: release-notes/{release_milestone}.md")
    if f"## {release_milestone}" not in read("CHANGELOG.md"):
        failures.append(f"CHANGELOG.md missing section: ## {release_milestone}")

    # Review Map feature surface (v3.1.0+). Only enforced when the command is
    # present, so the gate stays correct across milestones.
    if "review-map" in public_commands():
        if not (ROOT / "docs/REVIEW_MAP.md").is_file():
            failures.append("missing docs/REVIEW_MAP.md")
        if not (ROOT / "schemas/review-map.schema.json").is_file():
            failures.append("missing schemas/review-map.schema.json")
        if "review-map" not in read("docs/CLI_REFERENCE.md"):
            failures.append("docs/CLI_REFERENCE.md does not document review-map")
        if "review-map" not in readme:
            failures.append("README.md does not mention review-map")
        if notes.is_file() and "review-map" not in notes.read_text(encoding="utf-8", errors="ignore"):
            failures.append(f"release notes {notes.name} do not describe review-map")

    # GitHub Action examples and install/arkup stable tag track STABLE_RELEASE.
    action_tag = f"pre-audit@{STABLE_RELEASE}"
    for doc in ("docs/GITHUB_ACTION_USAGE.md",):
        if action_tag not in read(doc):
            failures.append(f"{doc} GitHub Action example does not use {action_tag}")
    stable_tag_line = f'ARKHEIONX_STABLE_TAG:-{STABLE_RELEASE}'
    for script in ("install.sh", "arkup"):
        if stable_tag_line not in read(script):
            failures.append(f"{script} stable tag does not track STABLE_RELEASE ({STABLE_RELEASE})")

    # No stale dev wording on the live README surface (dev version must not leak).
    if private_dev and __version__ in readme:
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

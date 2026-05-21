#!/usr/bin/env python3
"""Generate downstream artifacts from metadata/registry.json.

Outputs:
  - README.md vulnerability registry section (between markers)
  - web/public/metadata.json (legacy shape, fed by canonical registry)

Usage:
  python scripts/generate_registry.py            # write
  python scripts/generate_registry.py --check    # exit 1 if outputs would change
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REGISTRY = REPO_ROOT / "metadata" / "registry.json"
README = REPO_ROOT / "README.md"
WEB_METADATA = REPO_ROOT / "web" / "public" / "metadata.json"

REGISTRY_BEGIN = "<!-- BEGIN: registry -->"
REGISTRY_END = "<!-- END: registry -->"

SEVERITY_RANK = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
    "informational": 4,
}


def load_registry() -> dict:
    return json.loads(REGISTRY.read_text())


def render_readme_table(entries: list[dict]) -> str:
    rows = []
    rows.append("| Date | Protocol | Chain | Severity | Category | Status | PoC |")
    rows.append("|------|----------|-------|----------|----------|--------|-----|")
    for e in sorted(entries, key=lambda x: x["date"]):
        rows.append(
            "| {date} | {title} | {chain} | {severity} | {category} | {status} | [`{path}`]({path}) |".format(
                date=e["date"],
                title=e["title"],
                chain=e["chain"],
                severity=e["severity"],
                category=e["category"],
                status=e["status"],
                path=e["poc_path"],
            )
        )
    return "\n".join(rows)


def render_readme_section(entries: list[dict]) -> str:
    body = render_readme_table(entries)
    note = (
        "_Generated from `metadata/registry.json`. Run "
        "`python scripts/generate_registry.py` to regenerate. "
        f"Total entries: {len(entries)}._"
    )
    return f"{REGISTRY_BEGIN}\n\n{note}\n\n{body}\n\n{REGISTRY_END}"


def render_web_metadata(reg: dict) -> dict:
    entries = reg["entries"]
    out_entries = []
    for e in sorted(entries, key=lambda x: (SEVERITY_RANK.get(x["severity"], 99), x["date"])):
        out_entries.append({
            "id": e["id"],
            "title": e["title"],
            "protocol": e["protocol"],
            "date": e["date"],
            "vm": e["vm"],
            "chain": e["chain"],
            "severity": e["severity"],
            "category": e["category"],
            "status": e["status"],
            "reproducibility": e["reproducibility"],
            "summary": e["summary"],
            "root_cause": e["root_cause"],
            "impact": e["impact"],
            "poc_path": e.get("poc_path"),
            "block_number": e.get("block_number"),
            "loss_usd": e.get("loss_usd"),
            "attack_tx": e.get("attack_tx"),
            "references": e.get("references", []),
        })
    return {
        "schema_version": "1",
        "maintainer": reg.get("maintainer", ""),
        "total": len(out_entries),
        "entries": out_entries,
    }


def replace_section(text: str, begin: str, end: str, replacement: str) -> str:
    if begin in text and end in text:
        before, _, rest = text.partition(begin)
        _, _, after = rest.partition(end)
        return f"{before}{replacement}{after}"
    return text + ("\n\n" if not text.endswith("\n") else "\n") + replacement + "\n"


def write_file(path: Path, content: str, check: bool) -> bool:
    current = path.read_text() if path.exists() else ""
    if current == content:
        return False
    if check:
        print(f"would update: {path.relative_to(REPO_ROOT)}", file=sys.stderr)
        return True
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    print(f"updated: {path.relative_to(REPO_ROOT)}")
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="Exit 1 if any output would change. Make no writes.")
    args = ap.parse_args()

    reg = load_registry()
    entries = reg["entries"]

    readme_text = README.read_text() if README.exists() else ""
    new_section = render_readme_section(entries)
    new_readme = replace_section(readme_text, REGISTRY_BEGIN, REGISTRY_END, new_section)

    web_payload = render_web_metadata(reg)
    new_web = json.dumps(web_payload, indent=2) + "\n"

    changed = False
    changed |= write_file(README, new_readme, args.check)
    changed |= write_file(WEB_METADATA, new_web, args.check)

    if args.check and changed:
        return 1
    print(f"ok: {len(entries)} entries")
    return 0


if __name__ == "__main__":
    sys.exit(main())

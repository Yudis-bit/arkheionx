#!/usr/bin/env python3
"""Generate the Arkheionx paid offer index from local catalog metadata."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
CATALOG_PATH = ROOT / "metadata" / "paid_offer_catalog.json"
OUTPUT_PATH = ROOT / "reports" / "paid_offer_index.md"


def load_catalog() -> dict[str, Any]:
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def bullet_list(items: list[str]) -> list[str]:
    if not items:
        return ["- None scoped."]
    return [f"- {item}" for item in items]


def render_offer(offer: dict[str, Any]) -> list[str]:
    lines = [
        f"## {offer['name']}",
        "",
        f"- Offer ID: `{offer['offer_id']}`",
        f"- Audience: {offer['audience']}",
        f"- Starting price: USD {offer['starting_price_usd']:,}",
        f"- Typical range: {offer['typical_price_range_usd']}",
        f"- Duration: {offer['duration']}",
        "",
        offer["description"],
        "",
        "### Deliverables",
        "",
    ]
    lines.extend(bullet_list(offer.get("deliverables", [])))
    lines.extend(["", "### Required Inputs", ""])
    lines.extend(bullet_list(offer.get("required_inputs", [])))
    lines.extend(["", "### Not Included", ""])
    lines.extend(bullet_list(offer.get("not_included", [])))
    lines.extend(["", "### Safety Boundaries", ""])
    lines.extend(bullet_list(offer.get("safety_boundaries", [])))
    lines.extend(["", "### Recommended For", ""])
    lines.extend(bullet_list(offer.get("recommended_for", [])))
    lines.extend(["", "### Not Recommended For", ""])
    lines.extend(bullet_list(offer.get("not_recommended_for", [])))
    lines.append("")
    return lines


def render(catalog: dict[str, Any]) -> str:
    offers = catalog.get("offers", [])
    lines = [
        "# Arkheionx Paid Offer Index",
        "",
        "Generated from `metadata/paid_offer_catalog.json`.",
        "",
        "Paid Arkheionx work is a readiness engagement, not a formal audit.",
        "It helps teams prepare authorized repositories for audits, contests,",
        "and bug bounty launches by turning readiness gaps into reports, issue",
        "plans, and remediation workflows.",
        "",
        "No paid offer includes live-chain scanning, transaction execution,",
        "private key handling, exploit automation, security guarantees, bounty",
        "guarantees, or formal audit sign-off.",
        "",
        "## Offer Summary",
        "",
        "| Offer | Starting price | Typical range | Duration |",
        "|---|---:|---|---|",
    ]
    for offer in offers:
        lines.append(
            "| {name} | USD {price:,} | {range} | {duration} |".format(
                name=offer["name"],
                price=offer["starting_price_usd"],
                range=offer["typical_price_range_usd"],
                duration=offer["duration"],
            )
        )
    lines.append("")
    for offer in offers:
        lines.extend(render_offer(offer))
    lines.extend(
        [
            "## Inquiry Path",
            "",
            "Start with `templates/client_intake.md` and the relevant scope",
            "template under `templates/`. Share only repositories you own or are",
            "authorized to evaluate. Do not paste secrets, private keys, mnemonics,",
            "RPC credentials, API tokens, or unpatched vulnerability details into",
            "public channels.",
            "",
        ]
    )
    return "\n".join(lines)


def write() -> None:
    OUTPUT_PATH.write_text(render(load_catalog()), encoding="utf-8")


def check() -> list[str]:
    expected = render(load_catalog())
    if not OUTPUT_PATH.exists():
        return [f"missing: {OUTPUT_PATH.relative_to(ROOT)}"]
    actual = OUTPUT_PATH.read_text(encoding="utf-8")
    if actual != expected:
        return [f"stale: {OUTPUT_PATH.relative_to(ROOT)}"]
    return []


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate Arkheionx paid offer index.")
    parser.add_argument("--check", action="store_true", help="Exit nonzero if generated output is stale.")
    args = parser.parse_args(argv)
    if args.check:
        failures = check()
        if failures:
            for failure in failures:
                print(failure)
            return 1
        print("ok: paid offer index up to date")
        return 0
    write()
    print(f"updated: {OUTPUT_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

#!/usr/bin/env python3
"""Compute and render the PoC maturity index.

Reads metadata/registry.json and produces reports/poc_maturity_index.md.

The maturity ladder (L0..L5) is defined in docs/POC_MATURITY_MODEL.md.
This script encodes the computation rules in one place. It is purely
derivative — it never edits the registry, never claims a level the
registry does not back up, and never promotes an entry past what its
verification artifacts justify.

Usage:
    python scripts/poc_maturity_index.py             # write report
    python scripts/poc_maturity_index.py --check     # exit 1 if changed
    python scripts/poc_maturity_index.py --stdout    # print, no write
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
REGISTRY = REPO / "metadata" / "registry.json"
OUT = REPO / "reports" / "poc_maturity_index.md"
VERIFY_DIR = REPO / "reports" / "verification"
CASE_DIR = REPO / "reports" / "case-studies"

LEVELS = ("L0", "L1", "L2", "L3", "L4", "L5")

LEVEL_LABEL = {
    "L0": "Raw Replay",
    "L1": "Structured Metadata",
    "L2": "Assertion-Hardened",
    "L3": "Public RPC Smoke-Tested",
    "L4": "Archival Verified",
    "L5": "Research-Grade Case Study",
}

REQUIRED_METADATA_FIELDS = (
    "id", "title", "protocol", "date", "vm", "chain",
    "block_number", "rpc_alias", "category", "severity", "status",
    "reproducibility", "poc_path", "summary", "root_cause", "impact",
    "exploit_primitive", "attacker_path", "invariant_broken",
    "protocol_assumption_failure", "attacker_profit_check",
    "victim_loss_check", "assertion_quality", "verification_status",
)

STUB_MARKERS = (
    "no real run output recorded",
    "verification not yet performed",
    "pending archival rpc",
)


@dataclass
class Maturity:
    entry_id: str
    level: str
    reasons: list[str] = field(default_factory=list)
    next_action: str = ""


def _has_required_metadata(e: dict) -> bool:
    for f in REQUIRED_METADATA_FIELDS:
        v = e.get(f)
        if v in (None, "", [], "unknown"):
            return False
    return True


def _verification_report_has_real_output(e: dict) -> bool:
    """Heuristic: a real run report has more than just generated stub
    text. We treat known stub markers as a negative signal and require
    either a `verification_status == verified` claim or explicit run
    output sections in the file.
    """
    eid = e.get("id", "")
    p = VERIFY_DIR / f"{eid}.md"
    if not p.exists():
        return False
    try:
        text = p.read_text().lower()
    except Exception:
        return False
    if any(m in text for m in STUB_MARKERS):
        return False
    return any(
        marker in text
        for marker in (
            "## run output",
            "## actual run",
            "real fork run",
            "verified on archival",
        )
    )


def _case_study_exists(e: dict) -> bool:
    eid = e.get("id", "")
    return (CASE_DIR / f"{eid}.md").exists()


def _public_rpc_pass(e: dict) -> bool:
    return e.get("latest_public_rpc_status") == "public-rpc-pass"


def _public_rpc_recorded(e: dict) -> bool:
    return e.get("latest_public_rpc_status") in (
        "public-rpc-pass",
        "public-rpc-not-archival",
        "public-rpc-rate-limited",
        "public-rpc-unstable",
    )


def _assertion_hardened(e: dict) -> bool:
    return e.get("assertion_quality") in ("medium", "strong")


def compute(e: dict) -> Maturity:
    eid = e.get("id", "")
    reasons: list[str] = []
    have_metadata = _has_required_metadata(e)
    have_assertions = _assertion_hardened(e)
    have_pub_rpc = _public_rpc_recorded(e)
    have_real_report = _verification_report_has_real_output(e)
    verified = (
        e.get("verification_status") == "verified"
        and e.get("reproducibility") == "deterministic-confirmed"
        and have_real_report
    )
    case_study = _case_study_exists(e)

    if verified and case_study:
        level = "L5"
        reasons.append("verified + case study present")
        nxt = "maintain reference quality and archive sources"
    elif verified:
        level = "L4"
        reasons.append("archival fork verified with real run output")
        nxt = "draft research-grade case study under reports/case-studies/"
    elif have_real_report or _public_rpc_pass(e):
        level = "L3"
        if have_real_report:
            reasons.append("verification report contains run output")
        if _public_rpc_pass(e):
            reasons.append("public RPC smoke test passed")
        nxt = "configure archival RPC and re-run for L4"
    elif have_assertions:
        level = "L2"
        reasons.append(
            f"assertion_quality={e.get('assertion_quality')!r} on post-state"
        )
        if have_pub_rpc:
            reasons.append(
                f"public RPC observed: {e.get('latest_public_rpc_status')!r}"
            )
        nxt = "record archival fork run output for L3 / L4"
    elif have_metadata:
        level = "L1"
        reasons.append("metadata required fields populated")
        nxt = "add hard assertions covering category families"
    else:
        level = "L0"
        reasons.append("metadata or proof gaps")
        nxt = "fill required metadata; add hard assertions"

    return Maturity(entry_id=eid, level=level, reasons=reasons, next_action=nxt)


def render(maturities: list[tuple[Maturity, dict]]) -> str:
    lines: list[str] = []
    lines.append("# PoC Maturity Index")
    lines.append("")
    lines.append(
        "Per-PoC maturity level computed from `metadata/registry.json` and "
        "verification artifacts under `reports/verification/`. Ladder is "
        "defined in `docs/POC_MATURITY_MODEL.md`."
    )
    lines.append("")
    lines.append("Generated by `scripts/poc_maturity_index.py`. Do not hand-edit.")
    lines.append("")

    counts: dict[str, int] = {l: 0 for l in LEVELS}
    for m, _ in maturities:
        counts[m.level] = counts.get(m.level, 0) + 1

    lines.append("## Distribution")
    lines.append("")
    lines.append("| Level | Label | Count |")
    lines.append("|---|---|---|")
    for l in LEVELS:
        lines.append(f"| {l} | {LEVEL_LABEL[l]} | {counts.get(l, 0)} |")
    lines.append("")
    lines.append(f"Total: {len(maturities)}")
    lines.append("")

    lines.append("## Per-PoC")
    lines.append("")
    lines.append("| ID | Level | Label | Why | Next action |")
    lines.append("|---|---|---|---|---|")
    for m, e in sorted(maturities, key=lambda x: (x[0].level, x[0].entry_id)):
        why = "; ".join(m.reasons) if m.reasons else "—"
        lines.append(
            f"| `{m.entry_id}` | {m.level} | {LEVEL_LABEL[m.level]} | "
            f"{why} | {m.next_action} |"
        )
    lines.append("")

    lines.append("## Notes")
    lines.append("")
    lines.append(
        "- L4 requires `verification_status=verified`, "
        "`reproducibility=deterministic-confirmed`, AND a verification report "
        "with real run output. None of the three conditions is sufficient on "
        "its own."
    )
    lines.append(
        "- `public-rpc-not-archival`, `public-rpc-rate-limited`, and "
        "`public-rpc-unstable` are RPC limitations, not progress. They do not "
        "promote an entry past L2."
    )
    lines.append(
        "- L5 is reserved for entries with a long-form case study under "
        "`reports/case-studies/<id>.md`. The directory is reserved; entries "
        "are added when they reach the level."
    )
    lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="Exit 1 if reports/poc_maturity_index.md would change.")
    ap.add_argument("--stdout", action="store_true",
                    help="Print to stdout, do not write.")
    args = ap.parse_args()

    reg = json.loads(REGISTRY.read_text())
    entries = reg.get("entries", [])
    maturities = [(compute(e), e) for e in entries]

    text = render(maturities)

    if args.stdout:
        sys.stdout.write(text)
        return 0

    OUT.parent.mkdir(parents=True, exist_ok=True)
    current = OUT.read_text() if OUT.exists() else ""
    if current == text:
        print(f"ok: maturity index unchanged ({len(entries)} entries)")
        return 0

    if args.check:
        print(f"would update: {OUT.relative_to(REPO)}", file=sys.stderr)
        return 1

    OUT.write_text(text)
    print(f"updated: {OUT.relative_to(REPO)} ({len(entries)} entries)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

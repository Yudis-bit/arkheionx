#!/usr/bin/env python3
"""Compute the maturity level of every PoC and write a per-PoC index.

Reads metadata/registry.json (and reports/poc_quality_matrix.md when
available for cross-checking) and writes reports/poc_maturity_index.md.

This script is honest: it never marks an entry L4 unless metadata says
the entry is `deterministic-confirmed` AND `verified` AND a verification
report exists with a real run transcript. It never marks L5 unless the
case-study artifacts are present.

Usage:
    python3 scripts/poc_maturity_index.py             # write index
    python3 scripts/poc_maturity_index.py --check     # exit 1 if stale
    python3 scripts/poc_maturity_index.py --stdout    # print, no write
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
REGISTRY = REPO / "metadata" / "registry.json"
VERIFICATION_DIR = REPO / "reports" / "verification"
OUT = REPO / "reports" / "poc_maturity_index.md"

VERIFIED_TRANSCRIPT_MARKERS = (
    "Test result: ok",
    "tests passed",
    "passing tests",
)

PLACEHOLDER_TOKENS = (
    "_to be filled by verifier_",
    "TODO",
    "<placeholder>",
)


def load_registry() -> list[dict]:
    return json.loads(REGISTRY.read_text())["entries"]


def has_real_verification_report(entry_id: str) -> bool:
    """A verification report counts only if it has been filled in.

    The generator writes a skeleton with placeholder verifier handle,
    date, and commit. Those skeletons must NOT count as L4 evidence.
    """
    path = VERIFICATION_DIR / f"{entry_id}.md"
    if not path.exists():
        return False
    text = path.read_text()
    if any(token in text for token in PLACEHOLDER_TOKENS):
        return False
    if not any(marker in text for marker in VERIFIED_TRANSCRIPT_MARKERS):
        return False
    return True


def has_case_study(entry: dict) -> bool:
    """L5 requires a case-study artifact alongside L4 verification."""
    poc_path = entry.get("poc_path") or ""
    if poc_path:
        candidate = REPO / Path(poc_path).parent / "WRITEUP.md"
        if candidate.exists() and candidate.stat().st_size > 0:
            return True
    case_study = REPO / "docs" / "case-studies" / f"{entry['id']}.md"
    if case_study.exists() and case_study.stat().st_size > 0:
        return True
    return False


def metadata_complete(entry: dict) -> bool:
    """L1 gate: structured metadata is filled in honestly."""
    required = (
        "id", "title", "protocol", "date", "vm", "chain",
        "category", "poc_path", "summary", "root_cause",
        "exploit_primitive", "attacker_path", "invariant_broken",
        "protocol_assumption_failure",
    )
    for field in required:
        value = entry.get(field)
        if value in (None, "", "unknown"):
            return False
    refs = entry.get("references") or []
    if not isinstance(refs, list) or len(refs) < 1:
        return False
    return True


def maturity_level(entry: dict) -> tuple[int, str]:
    """Return (level, justification)."""
    aq = (entry.get("assertion_quality") or "").lower()
    repro = (entry.get("reproducibility") or "").lower()
    vstatus = (entry.get("verification_status") or "").lower()
    rpc_status = (entry.get("latest_public_rpc_status") or "").lower()

    has_report = has_real_verification_report(entry["id"])
    has_study = has_case_study(entry)

    if (
        repro == "deterministic-confirmed"
        and vstatus == "verified"
        and has_report
        and aq in ("medium", "strong")
    ):
        if has_study:
            return 5, "archival-verified + case study"
        return 4, "archival-verified"

    if rpc_status in ("public-rpc-pass", "public-rpc-fail", "public-rpc-not-archival"):
        if aq in ("medium", "strong"):
            return 3, f"smoke-tested ({rpc_status})"

    if aq in ("medium", "strong"):
        return 2, f"assertion-hardened ({aq})"

    if metadata_complete(entry):
        return 1, "structured metadata"

    return 0, "raw replay"


def next_action(entry: dict, level: int) -> str:
    aq = (entry.get("assertion_quality") or "").lower()
    rpc_status = (entry.get("latest_public_rpc_status") or "").lower()

    if level == 0:
        return "fill structured metadata (root cause, invariant, references)"
    if level == 1:
        return "add hard assertions per docs/ASSERTION_STANDARD.md"
    if level == 2:
        if aq == "weak":
            return "promote assertion_quality from weak to medium/strong"
        if not rpc_status:
            return "attempt public-RPC smoke test and record outcome"
        return "configure archival RPC and run fork test"
    if level == 3:
        return "configure archival RPC, run pinned fork, write verification report"
    if level == 4:
        return "add long-form case study + auditor checklist walkthrough"
    return "maintain — re-verify on RPC drift"


def render(entries: list[dict]) -> str:
    rows = []
    counts = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for e in sorted(entries, key=lambda x: x["id"]):
        level, why = maturity_level(e)
        counts[level] += 1
        rows.append({
            "id": e["id"],
            "protocol": e.get("protocol") or "?",
            "aq": e.get("assertion_quality") or "—",
            "repro": e.get("reproducibility") or "—",
            "vstatus": e.get("verification_status") or "—",
            "rpc": e.get("latest_public_rpc_status") or "—",
            "level": level,
            "why": why,
            "next": next_action(e, level),
        })

    lines = []
    lines.append("# PoC Maturity Index")
    lines.append("")
    lines.append(
        "Per-PoC maturity level computed from `metadata/registry.json` "
        "and `reports/verification/`. The level model is documented in "
        "[`docs/POC_MATURITY_MODEL.md`](../docs/POC_MATURITY_MODEL.md)."
    )
    lines.append("")
    lines.append("Generated by `scripts/poc_maturity_index.py`. Do not hand-edit.")
    lines.append("")
    lines.append("## Distribution")
    lines.append("")
    lines.append("| Level | Count | Meaning |")
    lines.append("|---|---|---|")
    lines.append(f"| L5 | {counts[5]} | Research-grade case study |")
    lines.append(f"| L4 | {counts[4]} | Archival verified |")
    lines.append(f"| L3 | {counts[3]} | Public RPC smoke-tested |")
    lines.append(f"| L2 | {counts[2]} | Assertion-hardened |")
    lines.append(f"| L1 | {counts[1]} | Structured metadata |")
    lines.append(f"| L0 | {counts[0]} | Raw replay |")
    lines.append("")
    lines.append(f"Total: {len(rows)}")
    lines.append("")
    lines.append("**L4+ requires** archival fork verification AND a verification report with a real run transcript and committed verifier identity. Skeleton reports do not count.")
    lines.append("")
    lines.append("## Per-PoC")
    lines.append("")
    lines.append(
        "| ID | Protocol | Assertion | Reproducibility | Verification | Public RPC | Level | Next action |"
    )
    lines.append("|---|---|---|---|---|---|---|---|")
    for r in rows:
        lines.append(
            f"| `{r['id']}` | {r['protocol']} | {r['aq']} | {r['repro']} | "
            f"{r['vstatus']} | {r['rpc']} | **L{r['level']}** | {r['next']} |"
        )
    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("- A PoC with `assertion_quality: weak` cannot exceed L1 in this index, even if a public-RPC smoke test passed. Without hard assertions, a green run does not prove the compromise.")
    lines.append("- A `public-rpc-not-archival` outcome is treated as a recorded smoke attempt. It does not reduce assertion quality and is not penalized — public RPCs simply lack the historical state needed to fork at the declared block. See [`docs/FORK_VERIFICATION.md`](../docs/FORK_VERIFICATION.md).")
    lines.append("- L4 promotion requires `metadata.reproducibility = deterministic-confirmed`, `metadata.verification_status = verified`, and a verification report whose verifier handle, date, and commit are filled in (not placeholder values).")
    lines.append("")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true",
                        help="exit 1 if the index would change")
    parser.add_argument("--stdout", action="store_true",
                        help="print to stdout, do not write")
    args = parser.parse_args()

    entries = load_registry()
    rendered = render(entries)

    if args.stdout:
        sys.stdout.write(rendered)
        return 0

    if args.check:
        if not OUT.exists() or OUT.read_text() != rendered:
            print("reports/poc_maturity_index.md is stale.", file=sys.stderr)
            print("re-run: python3 scripts/poc_maturity_index.py", file=sys.stderr)
            return 1
        return 0

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(rendered)
    print(f"wrote {OUT.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

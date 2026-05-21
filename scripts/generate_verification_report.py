#!/usr/bin/env python3
"""Generate per-PoC verification report skeletons.

Reads metadata/registry.json. For each entry, writes a markdown report at
reports/verification/<id>.md describing what verification *would* require.
The report is honest about whether verification has actually happened — it
does not claim success unless metadata says so AND a real run output has
been recorded.

Usage:
    python scripts/generate_verification_report.py
    python scripts/generate_verification_report.py --id 2017-07-parity-multisig
    python scripts/generate_verification_report.py --check
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
REGISTRY = REPO / "metadata" / "registry.json"
OUT_DIR = REPO / "reports" / "verification"

REQUIRED_FAMILIES: dict[str, list[str]] = {
    "oracle-manipulation":                 ["F1", "F2", "F5"],
    "flash-loan-price-manipulation":       ["F1", "F2", "F5"],
    "reentrancy":                          ["F1", "F2"],
    "read-only-reentrancy":                ["F1", "F5"],
    "access-control-failure":              ["F4|F7"],
    "arithmetic-precision-rounding":       ["F1|F3"],
    "accounting-mismatch":                 ["F6"],
    "share-price-manipulation":            ["F1", "F9"],
    "donation-inflation":                  ["F1", "F9", "F6"],
    "governance-attack":                   ["F7"],
    "signature-permit-misuse":             ["F4|F1"],
    "bridge-validation-failure":           ["F1", "F2"],
    "liquidation-logic-flaw":              ["F8", "F1"],
    "vault-strategy-accounting-flaw":      ["F3", "F6"],
    "amm-invariant-manipulation":          ["F3", "F1"],
    "fee-on-transfer-rebasing-assumption": ["F6", "F1"],
    "callback-misuse":                     ["F4|F1"],
    "initialization-bug":                  ["F4", "F7"],
    "proxy-upgradeability-issue":          ["F4", "F7"],
    "unsafe-external-call":                ["F4|F1"],
    "bad-debt-creation":                   ["F3"],
    "invariant-bypass":                    ["F3", "F4"],
    "economic-design-flaw":                ["F1"],
    "other":                               [],
}

FAMILY_DESC = {
    "F1": "Attacker profit assertion",
    "F2": "Victim loss assertion",
    "F3": "Invariant break assertion",
    "F4": "Unauthorized state transition assertion",
    "F5": "Oracle deviation assertion",
    "F6": "Accounting mismatch assertion",
    "F7": "Ownership / control assertion",
    "F8": "Liquidation result assertion",
    "F9": "Share price manipulation assertion",
}


def required_lines(category: str) -> str:
    fams = REQUIRED_FAMILIES.get(category, [])
    if not fams:
        return "_No category-specific assertion families required._"
    out = []
    for f in fams:
        if "|" in f:
            options = f.split("|")
            descs = " or ".join(f"**{o}** ({FAMILY_DESC.get(o, '?')})" for o in options)
            out.append(f"- {descs}")
        else:
            out.append(f"- **{f}** — {FAMILY_DESC.get(f, '?')}")
    return "\n".join(out)


def render_report(e: dict) -> str:
    eid = e["id"]
    cat = e.get("category", "other")
    repro = e.get("reproducibility", "unknown")
    vstatus = e.get("verification_status", "unknown")
    poc_path = e.get("poc_path", "")

    if poc_path.startswith("EVM/"):
        match = poc_path[len("EVM/"):]
        run_cmd = f'cd EVM && forge test --match-path "{match}" -vvv'
    else:
        run_cmd = f"# no canonical run command for poc_path={poc_path!r}"

    not_locally_verified = vstatus != "verified"

    lines: list[str] = []
    lines.append(f"# Verification Report — {eid}")
    lines.append("")
    lines.append(f"- **Entry id:** `{eid}`")
    lines.append(f"- **Title:** {e.get('title', '')}")
    lines.append(f"- **Protocol:** {e.get('protocol', '')}")
    lines.append(f"- **Date of incident:** {e.get('date', '')}")
    lines.append(f"- **VM:** {e.get('vm', '')}")
    lines.append(f"- **Chain:** {e.get('chain', '')}")
    lines.append(f"- **Fork block:** `{e.get('block_number', 'unknown')}`")
    lines.append(f"- **RPC alias:** `{e.get('rpc_alias', '')}`")
    lines.append(f"- **Category:** `{cat}`")
    lines.append(f"- **Reproducibility:** `{repro}`")
    lines.append(f"- **Verification status:** `{vstatus}`")
    lines.append("")

    lines.append("## Command to run")
    lines.append("")
    lines.append("```sh")
    lines.append(run_cmd)
    lines.append("```")
    lines.append("")

    lines.append("## Required assertion families")
    lines.append("")
    lines.append(required_lines(cat))
    lines.append("")
    lines.append(
        "Family definitions are in "
        "[`docs/ASSERTION_STANDARD.md`](../../docs/ASSERTION_STANDARD.md)."
    )
    lines.append("")

    lines.append("## Current verification status")
    lines.append("")
    if not_locally_verified:
        lines.append(
            "**Not verified locally because required archival RPC was not "
            "configured at report-generation time.**"
        )
        lines.append("")
        lines.append(
            "The metadata records "
            f"`reproducibility: {repro}` and "
            f"`verification_status: {vstatus}`. To produce a verified run, "
            "configure the appropriate `*_RPC_URL` env var (see "
            "[`docs/FORK_VERIFICATION.md`](../../docs/FORK_VERIFICATION.md)), "
            "execute the command above, and replace this section with the run "
            "transcript."
        )
    else:
        lines.append(
            "Metadata claims `verification_status: verified`. The run transcript, "
            "exit status, and assertion outcomes should appear below; if they do "
            "not, the metadata is wrong."
        )
    lines.append("")

    lines.append("## Attacker path")
    lines.append("")
    lines.append(e.get("attacker_path", "unknown"))
    lines.append("")

    lines.append("## Invariant broken")
    lines.append("")
    lines.append(e.get("invariant_broken", "unknown"))
    lines.append("")

    lines.append("## Victim impact")
    lines.append("")
    lines.append(e.get("impact", "unknown"))
    lines.append("")
    if e.get("victim_loss_check"):
        lines.append("**Loss check:** " + e["victim_loss_check"])
        lines.append("")

    lines.append("## Root cause")
    lines.append("")
    lines.append(e.get("root_cause", "unknown"))
    lines.append("")
    paf = e.get("protocol_assumption_failure")
    if paf:
        lines.append("**Protocol assumption that failed:** " + paf)
        lines.append("")

    lines.append("## References")
    lines.append("")
    refs = e.get("references", []) or []
    if not refs:
        lines.append("_No references recorded in metadata._")
    else:
        for r in refs:
            lines.append(f"- [{r.get('title', r.get('url', ''))}]({r.get('url', '')})")
    if e.get("attack_tx"):
        lines.append(f"- attack tx: `{e['attack_tx']}`")
    lines.append("")

    lines.append("## Missing verification steps")
    lines.append("")
    if not_locally_verified:
        lines.append("- [ ] Configure archival RPC for chain "
                     f"`{e.get('chain', '?')}` (alias `{e.get('rpc_alias', '?')}`).")
        lines.append("- [ ] Run the command above against the declared fork block.")
        lines.append("- [ ] Confirm all required assertion families pass.")
        lines.append("- [ ] Replace the current-status section with run output.")
        lines.append("- [ ] Update metadata `reproducibility` to "
                     "`deterministic-confirmed` and `verification_status` to "
                     "`verified` in the same change.")
    else:
        lines.append("- [ ] (none — entry already at `verified`).")
    lines.append("")

    lines.append("## Verifier")
    lines.append("")
    lines.append("- **Handle:** _to be filled by verifier_")
    lines.append("- **Date:** _to be filled by verifier_")
    lines.append("- **Repository commit:** _to be filled by verifier_")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("Generated by `scripts/generate_verification_report.py` from "
                 "`metadata/registry.json`. Replace generated sections with "
                 "real run transcripts when verification is performed.")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", help="Generate only this entry id")
    ap.add_argument("--check", action="store_true",
                    help="Exit 1 if any output would change.")
    args = ap.parse_args()

    reg = json.loads(REGISTRY.read_text())
    entries = reg.get("entries", [])
    if args.id:
        entries = [e for e in entries if e["id"] == args.id]
        if not entries:
            print(f"error: id {args.id!r} not found", file=sys.stderr)
            return 1

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    changed = 0
    for e in entries:
        report = render_report(e)
        target = OUT_DIR / f"{e['id']}.md"
        current = target.read_text() if target.exists() else ""
        if current == report:
            continue
        if args.check:
            print(f"would update: {target.relative_to(REPO)}", file=sys.stderr)
            changed += 1
            continue
        target.write_text(report)
        print(f"updated: {target.relative_to(REPO)}")
        changed += 1

    if args.check and changed:
        return 1
    print(f"ok: {len(entries)} entr{'y' if len(entries) == 1 else 'ies'} processed, {changed} changed")
    return 0


if __name__ == "__main__":
    sys.exit(main())

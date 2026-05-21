#!/usr/bin/env python3
"""Score every PoC entry in metadata/registry.json on static readiness.

Static readiness only — this script does NOT execute fork tests. It
inspects metadata, optionally peeks at the PoC source file for cheap
signals, and reports a per-PoC score with a grade and a list of
weaknesses.

Usage:
    python scripts/score_pocs.py             # write reports/poc_quality_matrix.md
    python scripts/score_pocs.py --check     # exit 1 if matrix would change
    python scripts/score_pocs.py --stdout    # print matrix to stdout, no write
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

REPO = Path(__file__).resolve().parent.parent
REGISTRY = REPO / "metadata" / "registry.json"
OUT = REPO / "reports" / "poc_quality_matrix.md"

# Required assertion families per category. Mirrors docs/ASSERTION_STANDARD.md.
# Values are sets of family codes; a category may require any one of two
# alternatives, encoded as a frozenset within a tuple.
REQUIRED_FAMILIES: dict[str, list] = {
    "oracle-manipulation":                 ["F1", "F2", "F5"],
    "flash-loan-price-manipulation":       ["F1", "F2", "F5"],
    "reentrancy":                          ["F1", "F2"],
    "read-only-reentrancy":                ["F1", "F5"],
    "access-control-failure":              [("F4", "F7")],
    "arithmetic-precision-rounding":       [("F1", "F3")],
    "accounting-mismatch":                 ["F6"],
    "share-price-manipulation":            ["F1", "F9"],
    "donation-inflation":                  ["F1", "F9", "F6"],
    "governance-attack":                   ["F7"],
    "signature-permit-misuse":             [("F4", "F1")],
    "bridge-validation-failure":           ["F1", "F2"],
    "liquidation-logic-flaw":              ["F8", "F1"],
    "vault-strategy-accounting-flaw":      ["F3", "F6"],
    "amm-invariant-manipulation":          ["F3", "F1"],
    "fee-on-transfer-rebasing-assumption": ["F6", "F1"],
    "callback-misuse":                     [("F4", "F1")],
    "initialization-bug":                  ["F4", "F7"],
    "proxy-upgradeability-issue":          ["F4", "F7"],
    "unsafe-external-call":                [("F4", "F1")],
    "bad-debt-creation":                   ["F3"],
    "invariant-bypass":                    ["F3", "F4"],
    "economic-design-flaw":                ["F1"],
    "other":                               [],
}


@dataclass
class Score:
    entry_id: str
    metadata: int = 0
    reproducibility: int = 0
    assertion: int = 0
    root_cause: int = 0
    anatomy: int = 0
    references: int = 0
    safety: int = 0
    notes: list[str] = field(default_factory=list)

    @property
    def total(self) -> int:
        return (self.metadata + self.reproducibility + self.assertion
                + self.root_cause + self.anatomy + self.references
                + self.safety)

    @property
    def grade(self) -> str:
        t = self.total
        if t >= 90:
            return "A"
        if t >= 80:
            return "B"
        if t >= 70:
            return "C"
        if t >= 60:
            return "D"
        return "F"


def _nonempty(value) -> bool:
    return isinstance(value, str) and len(value.strip()) > 0


def score_metadata(e: dict) -> tuple[int, list[str]]:
    """0-20. Required-field completeness."""
    notes: list[str] = []
    required = [
        "id", "title", "protocol", "date", "vm", "chain", "rpc_alias",
        "block_number", "category", "exploit_primitive", "severity",
        "status", "reproducibility", "poc_path", "summary", "root_cause",
        "impact", "attacker_path", "invariant_broken",
        "protocol_assumption_failure", "attacker_profit_check",
        "victim_loss_check", "assertion_quality", "verification_status",
    ]
    missing = [k for k in required if k not in e or e[k] in (None, "", [])]
    if missing:
        notes.append(f"missing fields: {', '.join(missing)}")
    placeholder_fields = [
        k for k in
        ("attacker_path", "invariant_broken", "protocol_assumption_failure",
         "attacker_profit_check", "victim_loss_check", "exploit_primitive")
        if e.get(k) == "unknown"
    ]
    if placeholder_fields:
        notes.append("placeholder 'unknown' values: "
                     + ", ".join(placeholder_fields))
    score = 20
    score -= 2 * len(missing)
    score -= 2 * len(placeholder_fields)
    return max(0, score), notes


def score_reproducibility(e: dict) -> tuple[int, list[str]]:
    """0-15. Honest status + presence of verification report.

    Public-RPC failure is recorded separately on the entry as
    `latest_public_rpc_status` and is NOT a reason to penalize a PoC's
    reproducibility — that is an endpoint capability issue, not a PoC defect.
    """
    notes: list[str] = []
    repro = e.get("reproducibility", "unknown")
    vstatus = e.get("verification_status", "unknown")
    pub = e.get("latest_public_rpc_status", "not-tested")
    eid = e.get("id", "")
    report = REPO / "reports" / "verification" / f"{eid}.md"

    base = {
        "deterministic-confirmed": 15,
        "deterministic-likely-but-unverified": 9,
        "requires-archival-rpc": 8,
        "partially-reproducible": 6,
        "compile-only": 4,
        "incomplete": 2,
        "unknown": 0,
    }.get(repro, 0)

    if repro == "deterministic-confirmed" and not report.exists():
        notes.append("status claims confirmed but no verification report")
        base = min(base, 8)

    if vstatus == "verified" and not report.exists():
        notes.append("verification_status=verified but no report file")
        base = min(base, 8)

    if pub == "public-rpc-not-archival":
        notes.append(
            "public RPC lacks archive state (recorded, not penalized); "
            "archival RPC required for final verification"
        )
    elif pub == "public-rpc-rate-limited":
        notes.append("public RPC rate-limited the last smoke test (not penalized)")
    elif pub == "public-rpc-unstable":
        notes.append("public RPC unstable on last smoke test (not penalized)")
    elif pub == "public-rpc-pass" and vstatus != "verified":
        notes.append(
            "public RPC smoke test passed; assertion quality and fork-block "
            "review still required before promoting to verified"
        )

    return base, notes


def _read_poc_text(e: dict) -> str:
    p = e.get("poc_path")
    if not p:
        return ""
    full = REPO / p
    if not full.exists():
        return ""
    try:
        return full.read_text()
    except Exception:
        return ""


def score_assertion(e: dict) -> tuple[int, list[str]]:
    """0-20. Required assertion families present in PoC source.

    Static heuristic: count assert*-family calls in the PoC file. This is
    a readiness indicator, not a proof.
    """
    notes: list[str] = []
    src = _read_poc_text(e)
    if not src:
        notes.append("PoC source not found; cannot score assertions statically")
        return 0, notes

    n_asserts = 0
    for needle in ("assertEq", "assertGt", "assertLt", "assertGe", "assertLe",
                   "assertTrue", "assertFalse", "assertApproxEqAbs",
                   "assertApproxEqRel", "assertNotEq", "vm.expectRevert"):
        n_asserts += src.count(needle)

    cat = e.get("category", "other")
    requirements = REQUIRED_FAMILIES.get(cat, [])
    n_required = len([r for r in requirements if not isinstance(r, tuple)])
    n_required += sum(1 for r in requirements if isinstance(r, tuple))

    if n_asserts == 0:
        notes.append("no assert* calls detected; PoC proves nothing")
        return 0, notes

    if n_required == 0:
        target = 2
    else:
        target = max(2, n_required)

    score = min(20, int(20 * n_asserts / target))
    if n_asserts < target:
        notes.append(f"detected {n_asserts} assertions; category {cat!r} expects ~{target}")

    if e.get("assertion_quality") == "unknown":
        notes.append("assertion_quality=unknown; needs manual review")

    return score, notes


def score_root_cause(e: dict) -> tuple[int, list[str]]:
    """0-15. Root-cause-related fields populated and non-trivial."""
    notes: list[str] = []
    fields = ("root_cause", "invariant_broken", "protocol_assumption_failure")
    points_per = 5
    total = 0
    for f in fields:
        val = e.get(f, "")
        if _nonempty(val) and val != "unknown" and len(val) >= 40:
            total += points_per
        elif _nonempty(val) and val != "unknown":
            total += 2
            notes.append(f"{f} present but short (<40 chars)")
        else:
            notes.append(f"{f} missing or placeholder")
    return total, notes


def score_anatomy(e: dict) -> tuple[int, list[str]]:
    """0-10. Attacker path + profit/loss checks populated."""
    notes: list[str] = []
    fields = ("attacker_path", "attacker_profit_check", "victim_loss_check",
              "exploit_primitive")
    total = 0
    for f in fields:
        val = e.get(f, "")
        if _nonempty(val) and val != "unknown" and len(val) >= 30:
            total += 2.5
        elif _nonempty(val) and val != "unknown":
            total += 1
            notes.append(f"{f} present but short")
        else:
            notes.append(f"{f} missing or placeholder")
    return int(total), notes


def score_references(e: dict) -> tuple[int, list[str]]:
    """0-10. References quality."""
    notes: list[str] = []
    refs = e.get("references", []) or []
    if not refs:
        return 0, ["no references"]
    n = len(refs)
    score = min(10, 4 + 3 * n)
    has_attack_tx = bool(e.get("attack_tx"))
    if not has_attack_tx and e.get("status") not in ("educational", "template"):
        notes.append("no attack_tx for a historical incident")
        score = max(0, score - 2)
    return score, notes


def score_safety(e: dict) -> tuple[int, list[str]]:
    """0-10. Safety-compliance heuristics on PoC source."""
    notes: list[str] = []
    src = _read_poc_text(e)
    score = 10
    if src:
        red_flags = [
            ("vm.envString", "reads env vars from inside test (RPC URL?)"),
            ("vm.envOr", "reads env vars from inside test"),
            ("PRIVATE_KEY", "private-key string referenced"),
            ("privateKey", "private-key string referenced"),
            ("--broadcast", "broadcast flag referenced"),
            ("scan.target", "target scanner pattern"),
        ]
        for needle, msg in red_flags:
            if needle in src:
                notes.append(f"red flag: {msg}")
                score -= 3
    return max(0, score), notes


def score_entry(e: dict) -> Score:
    s = Score(entry_id=e["id"])

    val, notes = score_metadata(e);       s.metadata = val;        s.notes += notes
    val, notes = score_reproducibility(e);s.reproducibility = val; s.notes += notes
    val, notes = score_assertion(e);      s.assertion = val;       s.notes += notes
    val, notes = score_root_cause(e);     s.root_cause = val;      s.notes += notes
    val, notes = score_anatomy(e);        s.anatomy = val;         s.notes += notes
    val, notes = score_references(e);     s.references = val;      s.notes += notes
    val, notes = score_safety(e);         s.safety = val;          s.notes += notes
    return s


def recommended_action(s: Score, e: dict) -> str:
    if s.reproducibility < 10 and e.get("verification_status") != "verified":
        return "configure archival RPC and run fork test"
    if s.assertion < 12:
        return "strengthen assertions for category"
    if s.root_cause < 12:
        return "expand root-cause and invariant fields"
    if s.references < 7:
        return "add post-mortem / writeup references"
    if s.metadata < 18:
        return "fill missing metadata fields"
    return "promote to deterministic-confirmed after verification report"


def render_matrix(scores: list[tuple[Score, dict]]) -> str:
    lines: list[str] = []
    lines.append("# PoC Quality Matrix")
    lines.append("")
    lines.append("Static readiness scoring for every entry in "
                 "`metadata/registry.json`. This is a metadata + source-pattern "
                 "heuristic; it does not prove a PoC works. See "
                 "`docs/REPRODUCIBILITY_STANDARD.md` for the actual verification bar.")
    lines.append("")
    lines.append("Generated by `scripts/score_pocs.py`. Do not hand-edit.")
    lines.append("")

    lines.append("## Summary")
    lines.append("")
    grades: dict[str, int] = {}
    for s, _ in scores:
        grades[s.grade] = grades.get(s.grade, 0) + 1
    grade_line = ", ".join(
        f"{g}: {grades.get(g, 0)}" for g in ("A", "B", "C", "D", "F"))
    lines.append(f"- Total entries: {len(scores)}")
    lines.append(f"- Grade distribution: {grade_line}")
    avg = sum(s.total for s, _ in scores) / max(1, len(scores))
    lines.append(f"- Average score: {avg:.1f} / 100")
    lines.append("")

    lines.append("## Scoring categories")
    lines.append("")
    lines.append("| Category | Max | Description |")
    lines.append("|---|---|---|")
    lines.append("| Metadata completeness | 20 | Required fields present, no `unknown` placeholders |")
    lines.append("| Reproducibility readiness | 15 | Honest status; verification report when claimed |")
    lines.append("| Assertion quality | 20 | `assert*` calls present, count vs. category requirement |")
    lines.append("| Root cause clarity | 15 | `root_cause`, `invariant_broken`, `protocol_assumption_failure` substantive |")
    lines.append("| Exploit anatomy | 10 | `attacker_path`, profit / loss checks, primitive populated |")
    lines.append("| Reference quality | 10 | Number of references; presence of `attack_tx` |")
    lines.append("| Safety compliance | 10 | No live-target or scanner red flags in PoC source |")
    lines.append("")

    lines.append("## Per-PoC scores")
    lines.append("")
    lines.append("| ID | Total | Grade | Meta | Repro | Assert | Cause | Anatomy | Ref | Safety | Recommended next action |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for s, e in sorted(scores, key=lambda x: (-x[0].total, x[0].entry_id)):
        action = recommended_action(s, e)
        lines.append(
            f"| `{s.entry_id}` | {s.total} | {s.grade} | "
            f"{s.metadata} | {s.reproducibility} | {s.assertion} | "
            f"{s.root_cause} | {s.anatomy} | {s.references} | {s.safety} | "
            f"{action} |"
        )
    lines.append("")

    lines.append("## Notes per entry")
    lines.append("")
    for s, e in sorted(scores, key=lambda x: x[0].entry_id):
        lines.append(f"### `{s.entry_id}` — grade {s.grade} ({s.total}/100)")
        if not s.notes:
            lines.append("- no findings")
        else:
            for n in s.notes:
                lines.append(f"- {n}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="Exit 1 if reports/poc_quality_matrix.md would change.")
    ap.add_argument("--stdout", action="store_true",
                    help="Print matrix to stdout, do not write.")
    args = ap.parse_args()

    reg = json.loads(REGISTRY.read_text())
    entries = reg.get("entries", [])
    scores: list[tuple[Score, dict]] = [(score_entry(e), e) for e in entries]

    matrix = render_matrix(scores)

    if args.stdout:
        sys.stdout.write(matrix)
        return 0

    OUT.parent.mkdir(parents=True, exist_ok=True)
    current = OUT.read_text() if OUT.exists() else ""
    if current == matrix:
        print(f"ok: matrix unchanged ({len(entries)} entries)")
        return 0

    if args.check:
        print(f"would update: {OUT.relative_to(REPO)}", file=sys.stderr)
        return 1

    OUT.write_text(matrix)
    print(f"updated: {OUT.relative_to(REPO)} ({len(entries)} entries)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Aggregate Arkheionx Vault registry into a single dashboard report.

Reads `metadata/registry.json` and the maturity gates from
`scripts/poc_maturity_index.py`, then writes
`reports/research_dashboard.md` — a single-page snapshot of corpus
truth.

The dashboard does not invent metrics. Every value is derived from
metadata or from generated artifacts. It does not run tests, not call
RPC, not score safety beyond what the registry already records.

Usage:
    python3 scripts/research_dashboard.py             # write
    python3 scripts/research_dashboard.py --check     # exit 1 if stale
    python3 scripts/research_dashboard.py --stdout    # print, no write
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
REGISTRY = REPO / "metadata" / "registry.json"
OUT = REPO / "reports" / "research_dashboard.md"

sys.path.insert(0, str(REPO / "scripts"))
from poc_maturity_index import maturity_level, next_action  # noqa: E402

# Milestones from docs/EXPANSION_PLAN.md, evaluated against current truth.
# Progress is reported honestly: an L4 entry counts as "verified", an L2
# assertion-hardened entry counts toward the assertion-hardening lane.
MILESTONES = [
    {
        "id": "M0",
        "label": "Current corpus (18 structured PoCs)",
        "target": 18,
        "metric": "total",
    },
    {
        "id": "M1a",
        "label": "25 assertion-hardened PoCs",
        "target": 25,
        "metric": "assertion_hardened",
    },
    {
        "id": "M1b",
        "label": "25 archival-verified PoCs",
        "target": 25,
        "metric": "archival_verified",
    },
    {
        "id": "M2",
        "label": "100 structured PoCs",
        "target": 100,
        "metric": "total",
    },
    {
        "id": "M3",
        "label": "300+ taxonomy-covered entries",
        "target": 300,
        "metric": "total",
    },
]


def load_entries() -> list[dict]:
    return json.loads(REGISTRY.read_text())["entries"]


def normalize(value, default="—") -> str:
    if value is None or value == "":
        return default
    return str(value)


def count_by(entries, key, default="—") -> Counter:
    return Counter(normalize(e.get(key), default) for e in entries)


def is_legacy_slug_retained(entry: dict) -> bool:
    """Heuristic: phase-6A reclassification kept the original id slug
    while metadata `protocol` / `category` was corrected. Tag entries
    whose `notes` document such a retention so the public surface can
    surface the count honestly without scraping commit messages."""
    notes = (entry.get("notes") or "").lower()
    tags = [t.lower() for t in (entry.get("tags") or [])]
    if "legacy-slug-retained" in tags:
        return True
    markers = ("legacy slug", "id slug retained", "phase 6a", "phase-6a",
               "reclassification", "slug retained")
    return any(m in notes for m in markers)


def is_archival_blocked(entry: dict) -> bool:
    return (entry.get("latest_public_rpc_status") or "").lower() in (
        "public-rpc-not-archival",
        "public-rpc-rate-limited",
        "public-rpc-unstable",
    )


def needs_verification(entry: dict) -> bool:
    return (entry.get("verification_status") or "").lower() in (
        "needs-verification",
        "not-run-no-rpc",
        "unknown",
    )


def is_assertion_hardened(entry: dict) -> bool:
    return (entry.get("assertion_quality") or "").lower() in ("medium", "strong")


def is_archival_verified(entry: dict) -> bool:
    level, _ = maturity_level(entry)
    return level >= 4


def render_distribution(title: str, counter: Counter, total: int) -> list[str]:
    lines = [f"### {title}", ""]
    if not counter:
        lines += ["_no data_", ""]
        return lines
    lines += ["| Value | Count | Share |", "|---|---|---|"]
    for value, count in sorted(counter.items(), key=lambda x: (-x[1], x[0])):
        pct = (count / total * 100) if total else 0.0
        lines.append(f"| `{value}` | {count} | {pct:.0f}% |")
    lines.append("")
    return lines


def render_milestone(label: str, current: int, target: int) -> str:
    if target <= 0:
        return f"- **{label}** — n/a"
    pct = min(100, int(round(current / target * 100)))
    blocks = pct // 10
    bar = "█" * blocks + "░" * (10 - blocks)
    return f"- **{label}** — {current} / {target} ({pct}%) `{bar}`"


def render(entries: list[dict]) -> str:
    total = len(entries)

    aq_counts = count_by(entries, "assertion_quality")
    repro_counts = count_by(entries, "reproducibility")
    vstatus_counts = count_by(entries, "verification_status")
    rpc_counts = count_by(entries, "latest_public_rpc_status",
                          default="not-run")
    cat_counts = count_by(entries, "category")
    severity_counts = count_by(entries, "severity")

    levels: Counter = Counter()
    next_actions: Counter = Counter()
    weak_entries: list[dict] = []
    pending_smoke: list[dict] = []
    archival_blocked: list[dict] = []
    legacy_slugs: list[dict] = []
    needs_verify: list[dict] = []
    assertion_hardened: int = 0
    archival_verified: int = 0
    for e in entries:
        level, _ = maturity_level(e)
        levels[level] += 1
        action = next_action(e, level)
        next_actions[action] += 1
        if (e.get("assertion_quality") or "").lower() == "weak":
            weak_entries.append(e)
        if not (e.get("latest_public_rpc_status") or ""):
            pending_smoke.append(e)
        if is_archival_blocked(e):
            archival_blocked.append(e)
        if is_legacy_slug_retained(e):
            legacy_slugs.append(e)
        if needs_verification(e):
            needs_verify.append(e)
        if is_assertion_hardened(e):
            assertion_hardened += 1
        if is_archival_verified(e):
            archival_verified += 1

    metric_values = {
        "total": total,
        "assertion_hardened": assertion_hardened,
        "archival_verified": archival_verified,
    }

    lines: list[str] = []
    lines.append("# Arkheionx Vault — Research Dashboard")
    lines.append("")
    lines.append(
        "Single-page snapshot of the registry. Values are derived from "
        "`metadata/registry.json` and the maturity gate in "
        "`scripts/poc_maturity_index.py`. Generated by "
        "`scripts/research_dashboard.py` — do not hand-edit."
    )
    lines.append("")
    lines.append("Linked artifacts:")
    lines.append("")
    lines.append("- [`reports/poc_quality_matrix.md`](poc_quality_matrix.md) — static readiness scoring")
    lines.append("- [`reports/poc_maturity_index.md`](poc_maturity_index.md) — per-PoC maturity level")
    lines.append("- [`reports/verification/`](verification/) — per-PoC verification reports (skeleton until archival run)")
    lines.append("")

    lines.append("## Headline numbers")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|---|---|")
    lines.append(f"| Total PoCs | {total} |")
    lines.append(f"| Assertion-hardened (medium / strong) | {assertion_hardened} |")
    lines.append(f"| Archival-verified (L4+) | {archival_verified} |")
    lines.append(f"| Public-RPC smoke attempted | {sum(rpc_counts.values()) - rpc_counts.get('not-run', 0)} |")
    lines.append(f"| Needs verification | {len(needs_verify)} |")
    lines.append(f"| Legacy slug retained | {len(legacy_slugs)} |")
    lines.append(f"| Archival-RPC blocked on public endpoint | {len(archival_blocked)} |")
    lines.append("")
    lines.append(
        "`Archival-verified` requires deterministic-confirmed metadata, "
        "verified status, a verification report with a real run "
        "transcript, and at least medium assertions. Skeleton reports "
        "do not count."
    )
    lines.append("")

    lines.append("## Maturity distribution")
    lines.append("")
    lines.append("| Level | Count | Meaning |")
    lines.append("|---|---|---|")
    lines.append(f"| L5 | {levels[5]} | Research-grade case study |")
    lines.append(f"| L4 | {levels[4]} | Archival verified |")
    lines.append(f"| L3 | {levels[3]} | Public RPC smoke-tested |")
    lines.append(f"| L2 | {levels[2]} | Assertion-hardened |")
    lines.append(f"| L1 | {levels[1]} | Structured metadata |")
    lines.append(f"| L0 | {levels[0]} | Raw replay |")
    lines.append("")

    lines.append("## Milestone progress")
    lines.append("")
    for m in MILESTONES:
        current = metric_values.get(m["metric"], 0)
        lines.append(render_milestone(m["label"], current, m["target"]))
    lines.append("")
    lines.append(
        "Milestones are quality gates, not dates. See "
        "[`docs/EXPANSION_PLAN.md`](../docs/EXPANSION_PLAN.md) for the "
        "definition of each lane."
    )
    lines.append("")

    lines.append("## Distributions")
    lines.append("")
    lines += render_distribution("Assertion quality", aq_counts, total)
    lines += render_distribution("Reproducibility", repro_counts, total)
    lines += render_distribution("Verification status", vstatus_counts, total)
    lines += render_distribution("Public RPC smoke result", rpc_counts, total)
    lines += render_distribution("Category", cat_counts, total)
    lines += render_distribution("Severity", severity_counts, total)

    lines.append("## Top next actions")
    lines.append("")
    lines.append("| Count | Next action |")
    lines.append("|---|---|")
    for action, count in next_actions.most_common():
        lines.append(f"| {count} | {action} |")
    lines.append("")

    lines.append("## Working set")
    lines.append("")
    lines.append("PoCs grouped by the work they need next.")
    lines.append("")

    def _ids(items: list[dict]) -> str:
        if not items:
            return "_none_"
        return ", ".join(f"`{e['id']}`" for e in sorted(items, key=lambda x: x["id"]))

    lines.append("### Weak assertions remaining")
    lines.append("")
    lines.append(f"Count: {len(weak_entries)}")
    lines.append("")
    lines.append(_ids(weak_entries))
    lines.append("")
    lines.append("### Needs verification")
    lines.append("")
    lines.append(f"Count: {len(needs_verify)}")
    lines.append("")
    lines.append(_ids(needs_verify))
    lines.append("")
    lines.append("### Public-RPC smoke not yet attempted")
    lines.append("")
    lines.append(f"Count: {len(pending_smoke)}")
    lines.append("")
    lines.append(_ids(pending_smoke))
    lines.append("")
    lines.append("### Archival-RPC blocked (smoke recorded, archival required)")
    lines.append("")
    lines.append(f"Count: {len(archival_blocked)}")
    lines.append("")
    lines.append(_ids(archival_blocked))
    lines.append("")
    lines.append("### Legacy slug retained (id slug from earlier metadata)")
    lines.append("")
    lines.append(f"Count: {len(legacy_slugs)}")
    lines.append("")
    lines.append(_ids(legacy_slugs))
    lines.append("")

    lines.append("## Notes")
    lines.append("")
    lines.append(
        "- `Archival-RPC blocked` is **not** a PoC defect. It records "
        "that the public RPC lacks the historical state needed to fork "
        "at the declared block. See "
        "[`docs/FORK_VERIFICATION.md`](../docs/FORK_VERIFICATION.md)."
    )
    lines.append(
        "- `Legacy slug retained` flags entries whose registry `id` "
        "stayed the same after a Phase 6A protocol/category "
        "reclassification, to keep file paths stable. The current "
        "metadata is the source of truth."
    )
    lines.append(
        "- This dashboard is a static snapshot of the registry at the "
        "current commit. Re-run the generator after every metadata or "
        "verification change."
    )
    lines.append("")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if dashboard would change")
    ap.add_argument("--stdout", action="store_true",
                    help="print to stdout, do not write")
    args = ap.parse_args()

    entries = load_entries()
    rendered = render(entries)

    if args.stdout:
        sys.stdout.write(rendered)
        return 0

    if args.check:
        if not OUT.exists() or OUT.read_text() != rendered:
            print("reports/research_dashboard.md is stale.", file=sys.stderr)
            print("re-run: python3 scripts/research_dashboard.py", file=sys.stderr)
            return 1
        return 0

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(rendered)
    print(f"wrote {OUT.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

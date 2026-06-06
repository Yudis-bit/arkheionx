"""Assumption mapping for the Review Map.

Assumptions are protective properties a value path appears to rely on. They are
review prompts, not findings. Each is emitted only when a matching signal is
detected locally, and starts at HEURISTIC.
"""
from __future__ import annotations

from collections.abc import Callable

from .model import Assumption, FunctionSurface, ReviewMap, to_dict

# (id, title, description, category, predicate(FunctionSurface) -> bool)
_SPECS: list[tuple[str, str, str, str, Callable[[FunctionSurface], bool]]] = [
    (
        "asm-oracle-fresh", "Oracle price is fresh and trusted",
        "Value paths assume the oracle/price source is current, non-stale, and not manipulable within a block.",
        "oracle", lambda fs: "oracle-dependent" in fs.risk_signals,
    ),
    (
        "asm-standard-erc20", "Tokens behave like standard ERC20",
        "Token transfers are assumed to return true, not take fees, and not re-enter on transfer.",
        "token", lambda fs: fs.value_direction in ("in", "out", "both"),
    ),
    (
        "asm-admin-bounded", "Admin/owner role is trusted and bounded",
        "Privileged configuration is assumed to be controlled by a trusted, bounded role.",
        "access-control", lambda fs: "privileged" in fs.risk_signals,
    ),
    (
        "asm-reward-monotonic", "Reward index is monotonic",
        "Reward accounting assumes the reward index never decreases and is updated before balance changes.",
        "accounting", lambda fs: any(k in fs.name.lower() for k in ("claim", "reward", "accrue", "distribute", "harvest")),
    ),
    (
        "asm-share-proportional", "Share accounting remains proportional",
        "Minted shares / liquidity are assumed to stay proportional to deposited value.",
        "accounting", lambda fs: any(k in fs.name.lower() for k in ("mint", "addliquidity", "share", "deposit", "stake")),
    ),
    (
        "asm-no-reentrancy", "External calls cannot re-enter unsafe state",
        "State is assumed to be settled before external calls, or guarded against re-entry.",
        "reentrancy", lambda fs: "external-call" in fs.risk_signals,
    ),
    (
        "asm-decimals-normalized", "Token and price decimals are normalized",
        "Math assumes consistent decimal scaling between tokens and price feeds.",
        "math", lambda fs: "oracle-dependent" in fs.risk_signals or "decimals" in fs.value_keywords,
    ),
    (
        "asm-fee-bounded", "Fee bounds are enforced",
        "Configurable fees are assumed to be bounded and validated.",
        "config", lambda fs: "fee" in fs.name.lower(),
    ),
    (
        "asm-liquidation-bounded", "Liquidation and health math is bounded",
        "Collateral/debt and liquidation math is assumed to be bounded and free of rounding abuse.",
        "lending", lambda fs: any(k in fs.name.lower() for k in ("borrow", "liquidate", "health", "collateral", "debt")),
    ),
]


def generate_assumptions(surfaces: list[FunctionSurface]) -> list[Assumption]:
    out: list[Assumption] = []
    for aid, title, desc, category, predicate in _SPECS:
        used_by = sorted({fs.display_id for fs in surfaces if predicate(fs)})
        if not used_by:
            continue
        signals = sorted({s for fs in surfaces if predicate(fs) for s in fs.risk_signals})
        out.append(
            Assumption(
                id=aid,
                title=title,
                description=desc,
                category=category,
                used_by=used_by,
                signals=signals,
            )
        )
    return out


def build_assumptions_payload(rm: ReviewMap) -> dict:
    """Return the exact payload shape written to ``assumptions.json``."""

    return {
        "schema_version": rm.schema_version,
        "generated_at": rm.generated_at,
        "repo_path": rm.repo_path,
        "assumptions": to_dict(rm.assumptions),
    }


def _assumptions(data: object) -> list[dict]:
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    if isinstance(data, dict):
        assumptions = data.get("assumptions", [])
        if isinstance(assumptions, list):
            return [item for item in assumptions if isinstance(item, dict)]
    return []


def _assumption_target(assumption: dict) -> str:
    used_by = assumption.get("used_by")
    if isinstance(used_by, list):
        for target in used_by:
            text = str(target).strip()
            if "." in text:
                return text
    return ""


def _one_line(values: object, fallback: str = "none") -> str:
    if isinstance(values, list):
        return ", ".join(str(value) for value in values if str(value).strip()) or fallback
    text = str(values or "").strip()
    return text or fallback


def _category_counts(assumptions: list[dict]) -> list[tuple[str, int]]:
    counts: dict[str, int] = {}
    for assumption in assumptions:
        category = str(assumption.get("category") or "general")
        counts[category] = counts.get(category, 0) + 1
    return sorted(counts.items(), key=lambda item: (item[0] == "general", item[0]))


def _review_priority_counts(assumptions: list[dict]) -> tuple[int, int]:
    with_missing_tests = sum(1 for assumption in assumptions if assumption.get("missing_tests"))
    with_targets = sum(1 for assumption in assumptions if assumption.get("used_by"))
    return with_missing_tests, with_targets


def render_assumptions_cli(data: object, repo: str, *, top: int = 5, source: str = "", mode: str = "") -> str:
    """Render a concise human report for the focused assumptions command."""

    assumptions = _assumptions(data)
    ranked = sorted(
        assumptions,
        key=lambda item: (
            0 if item.get("missing_tests") else 1,
            str(item.get("category", "")),
            str(item.get("id", "")),
        ),
    )
    top_items = ranked[:max(0, top)]
    with_missing_tests, with_targets = _review_priority_counts(assumptions)
    categories = ", ".join(f"{name} {count}" for name, count in _category_counts(assumptions)) or "none"
    display_mode = mode or (str(data.get("mode", "")) if isinstance(data, dict) else "") or "review-map assumptions artifact"

    lines = [
        "ARKHEIONX ASSUMPTIONS",
        "View: Assumptions",
        "Local/static review guidance only.",
        "Assumptions are review prompts, not confirmed bugs. Human review required.",
        "Priority is review order, not severity.",
        "",
        "Scope",
        f"  Repo: {repo}",
        f"  Mode: {display_mode}",
    ]
    if source:
        lines.append(f"  Source: {source}")
    lines += [
        "",
        "Summary",
        f"  Total assumptions: {len(assumptions)}",
        f"  Categories: {categories}",
        f"  Related targets: {with_targets}",
        f"  With related test gaps: {with_missing_tests}",
        "",
        "Top Assumptions",
    ]

    if top_items:
        for index, assumption in enumerate(top_items, 1):
            title = str(assumption.get("title") or assumption.get("id") or "assumption")
            category = str(assumption.get("category") or "general")
            status = str(assumption.get("status") or "unverified")
            evidence = str(assumption.get("evidence_level") or "unknown")
            lines.append(f"  {index}. {title} [{category}; {status}; {evidence}]")
            lines.append(f"     Targets: {_one_line(assumption.get('used_by'))}")
            lines.append(f"     Signals: {_one_line(assumption.get('signals'))}")
            lines.append(f"     Related test gaps: {_one_line(assumption.get('missing_tests'))}")
    else:
        lines.append("  No assumptions surfaced. Inspect the full review map for contract/function context.")

    lines += [
        "",
        "Next",
        f"  Full review map: arkheionx review-map {repo}",
        f"  Value paths: arkheionx value-paths {repo}",
        f"  Test gaps: arkheionx test-gap-map {repo}",
    ]
    if top_items:
        target = _assumption_target(top_items[0])
        if target:
            lines.append(f"  First local proof: arkheionx prove {repo} --target {target} --run")
    lines += [
        "",
        "Boundary",
        "  Local/static only. No RPC, no private keys, no live-chain calls.",
        "  No exploit automation, no transaction broadcasting, no auto-submit.",
        "  Review guidance only. Human review required.",
    ]
    return "\n".join(lines) + "\n"

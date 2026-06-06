"""Test-file detection and test-gap suggestions for the Review Map.

Matching is a heuristic "test reference hint", not proof of coverage. A name
appearing in a test file is treated as a weak reference only.
"""
from __future__ import annotations

import re
from pathlib import Path

from arkheionx.protocol.semantic_adapter import find_solidity_files

from .detect import is_value_sensitive
from .model import HIGH, LOW, MEDIUM, FunctionSurface, TestGap

# Suggested local Foundry test scenarios per surface kind. Review guidance only.
# Each function maps to exactly one primary kind so suggestions stay targeted
# (a swap never receives withdrawal-only scenarios, etc.).
_SCENARIOS = {
    "exit": ["withdrawal boundary", "zero amount", "full balance", "partial balance", "reentrancy receiver"],
    "liquidity_exit": ["withdrawal boundary", "zero amount", "full balance", "partial balance",
                       "reentrancy receiver", "reserve/accounting sync"],
    "swap": ["slippage bound", "reserve sync", "fee rounding", "low liquidity",
             "invariant preservation", "non-standard ERC20 behavior", "failed transfer behavior"],
    "borrow": ["stale oracle rejection", "decimals normalization", "borrow cap boundary",
               "health factor boundary", "price shock regression"],
    "liquidate": ["liquidation threshold", "price shock", "partial liquidation",
                  "bad debt edge case", "decimals normalization"],
    "reward": ["double claim", "reward index monotonicity", "zero reward",
               "stake/unstake ordering", "distribution after balance change"],
    "admin": ["access control", "zero address", "parameter bounds", "pause behavior", "role revocation"],
    "entry": ["zero amount", "accounting after deposit", "balance update", "double counting"],
}

_EXIT_KEYWORDS = ("withdraw", "redeem", "unstake", "burn", "collect", "payout", "sweep", "rescue")
_ENTRY_KEYWORDS = ("deposit", "stake", "mint", "addliquidity", "supply", "lock", "fund", "contribute")


def find_test_files(root: Path) -> list[Path]:
    _sources, tests = find_solidity_files(root)
    return tests


def load_test_blobs(root: Path) -> list[tuple[str, str]]:
    """Return (relative_path, lowercased_text) for each test file."""

    blobs: list[tuple[str, str]] = []
    for path in find_test_files(root):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore").lower()
        except OSError:
            continue
        blobs.append((path.relative_to(root).as_posix(), text))
    return blobs


def function_test_references(name: str, blobs: list[tuple[str, str]]) -> list[str]:
    needle = name.lower()
    if len(needle) < 4:  # too short to match reliably; skip to avoid noise
        return []
    return sorted({rel for rel, text in blobs if needle in text})


def _scenario_kind(fs: FunctionSurface) -> str | None:
    """Pick one primary scenario kind for a function. Most specific wins."""

    name = fs.name.lower()
    if "liquidate" in name:
        return "liquidate"
    if "borrow" in name:
        return "borrow"
    if "swap" in name:
        return "swap"
    if any(k in name for k in ("claim", "reward", "distribute", "accrue", "harvest")):
        return "reward"
    if "removeliquidity" in name:
        return "liquidity_exit"
    if fs.value_direction in ("out", "both") or any(k in name for k in _EXIT_KEYWORDS):
        return "exit"
    if "privileged" in fs.risk_signals or (fs.mutability == "state-changing" and name.startswith("set")):
        return "admin"
    if fs.value_direction == "in" or any(k in name for k in _ENTRY_KEYWORDS):
        return "entry"
    return None


def suggested_tests_for(fs: FunctionSurface) -> list[str]:
    kind = _scenario_kind(fs)
    return list(_SCENARIOS[kind]) if kind else []


def _gap_confidence(fs: FunctionSurface, has_reference: bool) -> str:
    if has_reference:
        return LOW
    return MEDIUM if fs.review_priority == HIGH else LOW


def generate_test_gaps(surfaces: list[FunctionSurface], blobs: list[tuple[str, str]]) -> list[TestGap]:
    """Generate test-gap suggestions for value-sensitive functions.

    A gap is review guidance to add or strengthen a local test, not a claim that
    a bug exists.
    """

    gaps: list[TestGap] = []
    for fs in surfaces:
        if not is_value_sensitive(fs) or fs.review_priority == LOW:
            continue
        refs = function_test_references(fs.name, blobs)
        fs.test_references = refs
        suggested = suggested_tests_for(fs)
        if not suggested:
            continue
        fs.suggested_tests = suggested
        has_ref = bool(refs)
        title = (
            f"Strengthen tests for {fs.display_id}" if has_ref else f"Add targeted tests for {fs.display_id}"
        )
        rationale = (
            "A value-sensitive function with only an incidental test reference; targeted scenarios appear missing."
            if has_ref
            else "A value-sensitive function with no matching local test reference was found."
        )
        gaps.append(
            TestGap(
                id=_gap_id(fs),
                title=title,
                description=f"{fs.display_id} ({fs.value_direction} value, {', '.join(fs.risk_signals) or 'review'}).",
                related_function=fs.display_id,
                suggested_test="; ".join(suggested),
                rationale=rationale,
                confidence=_gap_confidence(fs, has_ref),
            )
        )
    return gaps


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def _gap_id(fs: FunctionSurface) -> str:
    return f"gap-{_slug(fs.contract)}-{_slug(fs.name)}"

#!/usr/bin/env python3
"""Arkheionx pre-audit readiness scanner.

This scanner is intentionally defensive:
- local repository inspection only;
- no RPC, network, transaction submission, or deployed-contract testing;
- risk-signal and readiness-gap language only;
- deterministic Markdown and JSON reports for audit preparation.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


VERSION = "0.1.0"
MAX_READ_BYTES = 750_000
PACKAGE_ROOT = Path(__file__).resolve().parent.parent
DISCLAIMER = (
    "This is an automated pre-audit readiness report. It is not a formal "
    "audit, does not prove the absence or presence of vulnerabilities, does "
    "not authorize live-target testing, and should only be used on repositories "
    "you own or are authorized to review. A formal audit is recommended before "
    "handling real user funds."
)

RELEVANT_EXTENSIONS = {".sol", ".md"}
CONFIG_FILENAMES = {
    "foundry.toml",
    "hardhat.config.js",
    "hardhat.config.ts",
    "package.json",
    "remappings.txt",
    "slither.config.json",
    "echidna.yaml",
    "echidna.yml",
}
IGNORED_DIRS = {
    ".git",
    "node_modules",
    "out",
    "cache",
    "broadcast",
    "artifacts",
    "target",
    "dist",
    "build",
}


SIGNAL_TERMS: dict[str, list[str]] = {
    "vault_accounting": [
        "totalAssets",
        "convertToShares",
        "convertToAssets",
        "pricePerShare",
        "sharePrice",
        "totalSupply",
        "balanceOf",
        "shares",
        "assets",
        "strategy",
        "withdraw",
        "deposit",
        "redeem",
        "mint",
    ],
    "oracle": [
        "oracle",
        "priceFeed",
        "latestRoundData",
        "latestAnswer",
        "getReserves",
        "reserve0",
        "reserve1",
        "twap",
        "spot",
        "consult",
        "decimals",
        "stale",
        "heartbeat",
        "setOracle",
    ],
    "access_control": [
        "onlyOwner",
        "Ownable",
        "AccessControl",
        "DEFAULT_ADMIN_ROLE",
        "owner",
        "admin",
        "role",
        "setFee",
        "setOracle",
        "setStrategy",
        "setTreasury",
        "pause",
        "unpause",
        "emergencyWithdraw",
        "upgradeTo",
    ],
    "upgradeability": [
        "initializer",
        "reinitializer",
        "UUPS",
        "TransparentUpgradeableProxy",
        "implementation",
        "proxy",
        "storage gap",
        "__gap",
        "upgradeTo",
    ],
    "reentrancy_value_flow": [
        ".call(",
        "call{",
        "delegatecall",
        "staticcall",
        "safeTransfer",
        "transferFrom",
        "transfer(",
        "onERC721Received",
        "onERC1155Received",
        "ERC777",
        "callback",
        "flashLoan",
        "executeOperation",
        "nonReentrant",
        "ReentrancyGuard",
    ],
    "accounting_complexity": [
        "fee",
        "performanceFee",
        "managementFee",
        "reward",
        "accumulator",
        "index",
        "exchangeRate",
        "debt",
        "collateral",
        "rounding",
        "decimals",
        "precision",
        "mulDiv",
    ],
    "governance": [
        "governor",
        "proposal",
        "vote",
        "quorum",
        "timelock",
        "delegate",
        "executeProposal",
    ],
    "bridge_cross_chain": [
        "bridge",
        "endpoint",
        "layerzero",
        "ccip",
        "hyperlane",
        "message",
        "relayer",
        "wormhole",
    ],
    "amm": [
        "swap",
        "pool",
        "pair",
        "reserve",
        "getReserves",
        "kLast",
        "invariant",
        "liquidity",
        "addLiquidity",
        "removeLiquidity",
        "sqrtPriceX96",
    ],
    "lending": [
        "borrow",
        "repay",
        "collateral",
        "liquidation",
        "liquidate",
        "healthFactor",
        "debt",
        "utilization",
        "interestRate",
        "loanToValue",
    ],
    "staking_rewards": [
        "stake",
        "unstake",
        "reward",
        "claim",
        "rewardPerToken",
        "accumulator",
        "index",
        "emission",
    ],
}

PROTOCOL_WEIGHTS: dict[str, dict[str, int]] = {
    "vault": {
        "vault": 4,
        "deposit": 3,
        "withdraw": 3,
        "mint": 2,
        "redeem": 3,
        "totalAssets": 5,
        "convertToShares": 5,
        "convertToAssets": 5,
        "pricePerShare": 4,
        "share": 2,
        "strategy": 3,
        "asset": 2,
        "ERC4626": 5,
    },
    "amm": {
        "swap": 4,
        "pool": 3,
        "pair": 3,
        "reserve": 3,
        "getReserves": 5,
        "kLast": 4,
        "invariant": 2,
        "liquidity": 3,
        "addLiquidity": 4,
        "removeLiquidity": 4,
        "sqrtPriceX96": 5,
    },
    "lending": {
        "borrow": 4,
        "repay": 4,
        "collateral": 4,
        "liquidation": 5,
        "liquidate": 5,
        "healthFactor": 5,
        "debt": 3,
        "utilization": 3,
        "interestRate": 3,
        "loanToValue": 4,
    },
    "staking": {
        "stake": 4,
        "unstake": 4,
        "reward": 3,
        "claim": 2,
        "rewardPerToken": 5,
        "accumulator": 4,
        "index": 2,
        "emission": 3,
    },
    "oracle": {
        "oracle": 4,
        "priceFeed": 5,
        "latestRoundData": 5,
        "latestAnswer": 5,
        "aggregator": 4,
        "getPrice": 4,
        "twap": 5,
        "spot": 3,
        "consult": 3,
    },
}

SCORE_BANDS = [
    (0, 39, "Not audit-ready"),
    (40, 59, "Early readiness"),
    (60, 74, "Improving"),
    (75, 89, "Near audit-ready"),
    (90, 100, "Strong pre-audit hygiene"),
]


@dataclass
class ClassifiedFiles:
    solidity_sources: list[Path] = field(default_factory=list)
    solidity_tests: list[Path] = field(default_factory=list)
    docs: list[Path] = field(default_factory=list)
    configs: list[Path] = field(default_factory=list)
    workflows: list[Path] = field(default_factory=list)
    unknown: list[Path] = field(default_factory=list)


@dataclass
class HistoricalPattern:
    name: str
    confidence: str
    detected_signals: list[str]
    why_it_matters: str
    failed_assumption_class: str
    broken_invariant_class: str
    defensive_checks: list[str]
    suggested_test: str
    search_tags: list[str]


@dataclass
class ReadinessGap:
    severity: str
    title: str
    detail: str
    recommendation: str
    tags: list[str]


def rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def is_workflow(path: Path) -> bool:
    parts = path.parts
    return (
        len(parts) >= 3
        and ".github" in parts
        and "workflows" in parts
        and path.suffix.lower() in {".yml", ".yaml"}
    )


def is_relevant_file(path: Path) -> bool:
    if path.name in CONFIG_FILENAMES:
        return True
    if is_workflow(path):
        return True
    if path.suffix in RELEVANT_EXTENSIONS:
        return True
    return False


def collect_files(root: Path) -> list[Path]:
    root = root.resolve()
    included: list[Path] = []
    lib_candidates: list[Path] = []

    for current, dirs, files in os.walk(root):
        current_path = Path(current)
        dirs[:] = [
            d
            for d in dirs
            if d not in IGNORED_DIRS and not (d == "lib" and current_path == root)
        ]
        for file_name in files:
            path = current_path / file_name
            if is_relevant_file(path):
                included.append(path)

    lib_dir = root / "lib"
    if lib_dir.exists() and not any(p.suffix == ".sol" for p in included):
        for current, dirs, files in os.walk(lib_dir):
            dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
            for file_name in files:
                path = Path(current) / file_name
                if is_relevant_file(path):
                    lib_candidates.append(path)

    return sorted(set(included + lib_candidates))


def classify_files(files: Iterable[Path]) -> ClassifiedFiles:
    classified = ClassifiedFiles()
    for path in files:
        parts = {p.lower() for p in path.parts}
        lower_name = path.name.lower()
        if is_workflow(path):
            classified.workflows.append(path)
        elif lower_name in CONFIG_FILENAMES:
            classified.configs.append(path)
        elif path.suffix == ".sol" and (path.name.endswith(".t.sol") or "test" in parts):
            classified.solidity_tests.append(path)
        elif path.suffix == ".sol":
            classified.solidity_sources.append(path)
        elif path.suffix == ".md":
            classified.docs.append(path)
        else:
            classified.unknown.append(path)
    return classified


def read_text_safe(path: Path) -> str:
    try:
        if path.stat().st_size > MAX_READ_BYTES:
            with path.open("rb") as fh:
                data = fh.read(MAX_READ_BYTES)
            return data.decode("utf-8", errors="ignore")
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def is_placeholder_skeleton(text: str) -> bool:
    markers = [
        "Arkheionx defensive readiness skeleton",
        "TODO: replace placeholders with protocol-specific assertions",
    ]
    return all(marker in text for marker in markers)


def corpus(files: Iterable[Path]) -> dict[Path, str]:
    return {path: read_text_safe(path) for path in files}


def combined_text(contents: dict[Path, str], paths: Iterable[Path] | None = None) -> str:
    selected = paths if paths is not None else contents.keys()
    return "\n".join(contents.get(path, "") for path in selected)


def count_term(text: str, term: str) -> int:
    if not term:
        return 0
    escaped = re.escape(term)
    if re.search(r"^[A-Za-z_][A-Za-z0-9_]*$", term):
        pattern = rf"\b{escaped}\b"
        return len(re.findall(pattern, text, flags=re.IGNORECASE))
    return text.lower().count(term.lower())


def detect_protocol_type(
    contents: dict[Path, str],
    classified: ClassifiedFiles,
    requested: str,
) -> tuple[str, str, dict[str, int]]:
    source_text = combined_text(
        contents,
        classified.solidity_sources or classified.solidity_tests or contents.keys(),
    )
    scores: dict[str, int] = {}
    for protocol, weights in PROTOCOL_WEIGHTS.items():
        scores[protocol] = sum(count_term(source_text, term) * weight for term, weight in weights.items())

    if requested != "auto":
        return requested, "manual", scores

    best_protocol = max(scores, key=scores.get) if scores else "generic"
    best_score = scores.get(best_protocol, 0)
    ordered = sorted(scores.values(), reverse=True)
    runner_up = ordered[1] if len(ordered) > 1 else 0
    if best_score <= 2:
        return "generic", "low", scores
    if best_score >= 18 and best_score >= runner_up * 1.35:
        confidence = "high"
    elif best_score >= 8:
        confidence = "medium"
    else:
        confidence = "low"
    return best_protocol, confidence, scores


def detect_signals(
    contents: dict[Path, str],
    root: Path,
    paths: Iterable[Path] | None = None,
) -> dict[str, dict[str, object]]:
    result: dict[str, dict[str, object]] = {}
    selected = list(paths) if paths is not None else list(contents)
    for category, terms in SIGNAL_TERMS.items():
        found_terms: dict[str, int] = {}
        files: set[str] = set()
        for path in selected:
            text = contents.get(path, "")
            for term in terms:
                count = count_term(text, term)
                if count:
                    found_terms[term] = found_terms.get(term, 0) + count
                    files.add(rel(path, root))
        result[category] = {
            "terms": sorted(found_terms),
            "counts": dict(sorted(found_terms.items())),
            "files": sorted(files)[:25],
            "file_count": len(files),
        }
    return result


def has_any(signals: dict[str, dict[str, object]], category: str, terms: Iterable[str] | None = None) -> bool:
    found = set(signals.get(category, {}).get("terms", []))
    if terms is None:
        return bool(found)
    return any(term in found for term in terms)


def has_meaningful_oracle_signal(signals: dict[str, dict[str, object]]) -> bool:
    """Treat decimals alone as accounting complexity, not an oracle dependency."""
    found = set(signals.get("oracle", {}).get("terms", []))
    return bool(found - {"decimals"})


def detect_test_readiness(
    contents: dict[Path, str],
    classified: ClassifiedFiles,
    root: Path,
) -> dict[str, object]:
    usable_tests = [
        path
        for path in classified.solidity_tests
        if not is_placeholder_skeleton(contents.get(path, ""))
    ]
    code_paths = classified.solidity_sources + usable_tests + classified.configs + classified.workflows
    all_text = combined_text(contents, code_paths or contents.keys())
    test_paths = usable_tests
    lower_paths = [rel(p, root).lower() for p in contents]
    has_test_dir = any("/test/" in f"/{p}" or p.startswith("test/") for p in lower_paths)
    foundry = any(p.name == "foundry.toml" for p in classified.configs) or "forge-std" in all_text
    hardhat = any(p.name.startswith("hardhat.config") for p in classified.configs)
    assert_count = len(re.findall(r"\bassert[A-Za-z_]*\s*\(", all_text))
    invariant_count = count_term(all_text, "invariant") + len(
        [p for p in test_paths if "invariant" in rel(p, root).lower()]
    )
    fuzz_count = count_term(all_text, "fuzz") + len(re.findall(r"\btestFuzz", all_text))
    handler_count = count_term(all_text, "handler") + count_term(all_text, "StdInvariant")
    edge_case_terms = [
        "zero",
        "rounding",
        "decimals",
        "paused",
        "revert",
        "unauthorized",
        "boundary",
        "max",
        "min",
    ]
    edge_case_count = sum(count_term(all_text, term) for term in edge_case_terms)
    slither = any(p.name == "slither.config.json" for p in classified.configs) or count_term(all_text, "slither") > 0
    echidna = any(p.name in {"echidna.yaml", "echidna.yml"} for p in classified.configs) or count_term(all_text, "echidna") > 0
    ci = bool(classified.workflows)

    return {
        "test_directory": has_test_dir,
        "foundry_tests": bool(test_paths and foundry),
        "hardhat_tests": hardhat and any("test" in p for p in lower_paths),
        "test_files": [rel(p, root) for p in test_paths],
        "test_file_count": len(test_paths),
        "invariant_tests": invariant_count > 0,
        "fuzz_tests": fuzz_count > 0,
        "handler_contracts": handler_count > 0,
        "assert_usage": assert_count > 0,
        "assert_count": assert_count,
        "forge_std": "forge-std" in all_text or foundry,
        "echidna": echidna,
        "slither": slither,
        "ci_workflow": ci,
        "edge_case_tests": edge_case_count >= 3,
    }


def load_existing_registry_metadata(scan_root: Path) -> dict[str, object]:
    candidates = [
        scan_root / "metadata" / "registry.json",
        PACKAGE_ROOT / "metadata" / "registry.json",
    ]
    for path in candidates:
        try:
            if path.exists():
                data = json.loads(path.read_text(encoding="utf-8"))
                entries = data.get("entries", []) if isinstance(data, dict) else data
                categories = sorted({e.get("category", "") for e in entries if isinstance(e, dict) and e.get("category")})
                tags = sorted({tag for e in entries if isinstance(e, dict) for tag in e.get("tags", [])})
                primitives = sorted(
                    {
                        e.get("exploit_primitive", "")
                        for e in entries
                        if isinstance(e, dict) and e.get("exploit_primitive")
                    }
                )
                return {
                    "path": str(path),
                    "entry_count": len(entries),
                    "categories": categories,
                    "tags": tags,
                    "exploit_primitives": primitives,
                }
        except (OSError, json.JSONDecodeError):
            continue
    return {"path": None, "entry_count": 0, "categories": [], "tags": [], "exploit_primitives": []}


def confidence_from_signal_count(count: int) -> str:
    if count >= 8:
        return "high"
    if count >= 3:
        return "medium"
    return "low"


def pattern(
    name: str,
    signals: list[str],
    why: str,
    failed: str,
    broken: str,
    checks: list[str],
    suggested: str,
    tags: list[str],
) -> HistoricalPattern:
    return HistoricalPattern(
        name=name,
        confidence=confidence_from_signal_count(len(signals)),
        detected_signals=signals,
        why_it_matters=why,
        failed_assumption_class=failed,
        broken_invariant_class=broken,
        defensive_checks=checks,
        suggested_test=suggested,
        search_tags=tags,
    )


def signal_terms(signals: dict[str, dict[str, object]], *categories: str) -> list[str]:
    terms: list[str] = []
    for category in categories:
        terms.extend(signals.get(category, {}).get("terms", []))
    return sorted(set(terms))


def map_historical_patterns(
    signals: dict[str, dict[str, object]],
    test_readiness: dict[str, object],
) -> list[HistoricalPattern]:
    patterns: list[HistoricalPattern] = []
    weak_invariants = not bool(test_readiness.get("invariant_tests"))

    if has_any(signals, "vault_accounting") and has_meaningful_oracle_signal(signals) and weak_invariants:
        patterns.append(
            pattern(
                "Vault/oracle price-manipulation readiness gap",
                signal_terms(signals, "vault_accounting", "oracle"),
                "Vault accounting that depends on price or reserve assumptions has historically failed when spot values were trusted without enough defensive checks.",
                "Price source remains representative during deposits, withdrawals, and share conversions.",
                "Share/accounting value cannot be moved by transient price state.",
                [
                    "Document oracle freshness, bounds, and fallback behavior.",
                    "Test deposit and withdraw paths under manipulated local mock prices.",
                    "Prefer TWAP, sanity bounds, or explicit staleness checks where appropriate.",
                ],
                "Invariant: share price and totalAssets cannot be inflated by a single mocked price movement.",
                ["vault-accounting", "oracle-risk", "price-manipulation", "invariant-testing"],
            )
        )

    if has_any(signals, "vault_accounting") and weak_invariants:
        patterns.append(
            pattern(
                "Vault accounting invariant readiness gap",
                signal_terms(signals, "vault_accounting", "accounting_complexity"),
                "Vaults need explicit conservation and roundtrip properties because share math, fees, donations, and rounding can break user-value assumptions.",
                "Shares and assets remain exchangeable according to documented accounting rules.",
                "Deposits, withdrawals, redemptions, and fee paths conserve value within expected rounding bounds.",
                [
                    "Add totalAssets consistency tests.",
                    "Add deposit-withdraw roundtrip tests across small and large amounts.",
                    "Test donation, zero-supply, rounding, and fee paths.",
                ],
                "Invariant: deposit followed by withdraw does not create value and does not strand assets beyond expected rounding.",
                ["vault-security", "share-accounting", "totalAssets", "audit-readiness"],
            )
        )

    external_terms = signal_terms(signals, "reentrancy_value_flow")
    value_terms = signal_terms(signals, "vault_accounting", "staking_rewards")
    has_guard = has_any(signals, "reentrancy_value_flow", ["nonReentrant", "ReentrancyGuard"])
    if external_terms and value_terms and not has_guard:
        patterns.append(
            pattern(
                "Reentrancy-sensitive value flow review recommended",
                sorted(set(external_terms + value_terms)),
                "External calls around withdrawals, claims, callbacks, or token transfers have repeatedly exposed state-ordering assumptions.",
                "External receivers cannot re-enter before internal accounting reaches a safe state.",
                "Value flow remains single-entry and accounting is updated before control leaves the contract.",
                [
                    "Review checks-effects-interactions order.",
                    "Add reentrancy tests using local receiver mocks.",
                    "Use guards where the protocol design requires them.",
                ],
                "Test: malicious local receiver cannot withdraw, claim, or redeem twice through a callback.",
                ["reentrancy-review", "value-flow", "checks-effects-interactions"],
            )
        )

    if has_any(signals, "access_control") or has_any(signals, "governance"):
        patterns.append(
            pattern(
                "Privileged control and operational risk review recommended",
                signal_terms(signals, "access_control", "governance"),
                "Admin setters, emergency controls, fee updates, and governance execution paths can become launch blockers if role boundaries are unclear or untested.",
                "Privileged actors can only perform documented, intended operations.",
                "Admin actions cannot silently bypass accounting, oracle, or user-safety invariants.",
                [
                    "Document every privileged role and setter.",
                    "Add unauthorized-call tests for each privileged function.",
                    "Add tests showing pause/emergency controls behave as documented.",
                ],
                "Invariant: unprivileged callers cannot change fees, oracles, strategies, treasury, pause state, or upgrade target.",
                ["access-control-review", "admin-risk", "operational-security"],
            )
        )

    if has_any(signals, "upgradeability"):
        patterns.append(
            pattern(
                "Initialization and upgrade boundary review recommended",
                signal_terms(signals, "upgradeability"),
                "Upgradeable contracts can fail when initialization, authorization, storage layout, or implementation boundaries are not tested explicitly.",
                "Initialization and upgrade authority cannot be taken by the wrong actor.",
                "Storage and implementation changes preserve core accounting and access-control invariants.",
                [
                    "Test initializer can only run once.",
                    "Test upgrade authorization boundaries.",
                    "Document storage layout and upgrade process.",
                ],
                "Test: unauthorized caller cannot initialize, reinitialize, or upgrade the implementation.",
                ["upgradeability", "initialization-bug", "proxy-review"],
            )
        )

    if has_any(signals, "staking_rewards") or has_any(signals, "accounting_complexity", ["reward", "accumulator", "index", "rewardPerToken"]):
        patterns.append(
            pattern(
                "Reward accounting mismatch review recommended",
                signal_terms(signals, "staking_rewards", "accounting_complexity"),
                "Reward indexes and accumulators are common sources of overclaim, underclaim, and precision drift when supply changes across epochs.",
                "Reward index math always reflects actual funded rewards and stake weights.",
                "Claimable rewards cannot exceed funded rewards beyond documented rounding.",
                [
                    "Test claim conservation across multiple users.",
                    "Test stake/unstake around reward updates.",
                    "Check precision and rounding around small balances.",
                ],
                "Invariant: total claimed plus remaining claimable never exceeds funded rewards beyond expected rounding.",
                ["reward-accounting", "staking", "index-math", "precision"],
            )
        )

    if has_any(signals, "amm"):
        patterns.append(
            pattern(
                "AMM invariant manipulation review recommended",
                signal_terms(signals, "amm", "oracle"),
                "AMM integrations need invariant and reserve assumptions tested under swaps, liquidity changes, fees, and price movements.",
                "Pool reserves and quote functions remain representative for protocol decisions.",
                "Swaps and liquidity changes cannot create value outside documented fee mechanics.",
                [
                    "Add invariant conservation tests.",
                    "Test add/remove liquidity proportionality.",
                    "Avoid relying on same-block spot reserves without documented controls.",
                ],
                "Invariant: swaps and liquidity operations preserve the AMM invariant within fee and rounding bounds.",
                ["amm-invariant", "liquidity", "spot-price", "reserve-manipulation"],
            )
        )

    if has_any(signals, "lending"):
        patterns.append(
            pattern(
                "Liquidation and collateral accounting review recommended",
                signal_terms(signals, "lending", "oracle"),
                "Lending systems depend on collateral, debt, oracle, and liquidation assumptions staying consistent through edge cases.",
                "Collateral value and debt state stay aligned with liquidation and solvency rules.",
                "Borrowers cannot become undercollateralized without expected liquidation or protocol accounting response.",
                [
                    "Test collateralization and liquidation boundaries.",
                    "Test oracle movement around borrow and liquidation flows.",
                    "Check interest index monotonicity and debt accounting.",
                ],
                "Invariant: positions below required collateralization are liquidatable and solvent positions are not incorrectly liquidated.",
                ["lending", "liquidation", "collateral", "oracle-risk"],
            )
        )

    if has_any(signals, "bridge_cross_chain"):
        patterns.append(
            pattern(
                "Cross-chain message validation review recommended",
                signal_terms(signals, "bridge_cross_chain", "access_control"),
                "Cross-chain flows need explicit source, sender, replay, and message-authentication checks before they should be considered launch-ready.",
                "Inbound messages are authentic, authorized, and replay-protected.",
                "Cross-chain state transitions cannot be triggered by an untrusted endpoint or malformed message.",
                [
                    "Document trusted endpoints and relayer assumptions.",
                    "Test source-chain and sender validation.",
                    "Test replay and malformed message rejection.",
                ],
                "Test: untrusted local message sender cannot execute privileged cross-chain state transitions.",
                ["cross-chain", "bridge-validation", "message-authentication"],
            )
        )

    return patterns


def add_gap(
    gaps: list[ReadinessGap],
    severity: str,
    title: str,
    detail: str,
    recommendation: str,
    tags: list[str],
) -> None:
    gaps.append(ReadinessGap(severity, title, detail, recommendation, tags))


def compute_readiness_score(
    root: Path,
    classified: ClassifiedFiles,
    contents: dict[Path, str],
    signals: dict[str, dict[str, object]],
    test_readiness: dict[str, object],
    protocol_type: str,
) -> tuple[int, dict[str, dict[str, object]], list[ReadinessGap], list[str]]:
    all_text = combined_text(contents)
    lower_paths = [rel(p, root).lower() for p in contents]
    gaps: list[ReadinessGap] = []

    score: dict[str, dict[str, object]] = {
        "repository_structure": {"score": 0, "max": 15, "notes": []},
        "test_presence": {"score": 0, "max": 20, "notes": []},
        "invariant_fuzz_readiness": {"score": 0, "max": 20, "notes": []},
        "defi_risk_coverage": {"score": 0, "max": 20, "notes": []},
        "documentation_readiness": {"score": 0, "max": 10, "notes": []},
        "operational_admin_readiness": {"score": 0, "max": 15, "notes": []},
    }

    def award(category: str, points: int, note: str) -> None:
        score[category]["score"] = int(score[category]["score"]) + points
        score[category]["notes"].append(note)

    has_sources = bool(classified.solidity_sources)
    has_config = bool(classified.configs)
    has_src = any(p.startswith("src/") or "/src/" in f"/{p}" for p in lower_paths)
    has_tests = bool(classified.solidity_tests)
    has_docs_dir = any(p.startswith("docs/") for p in lower_paths)
    has_workflow = bool(classified.workflows)

    if has_sources:
        award("repository_structure", 5, "Solidity sources detected.")
    if has_config:
        award("repository_structure", 4, "Recognized build or analysis config detected.")
    if has_src and (has_tests or has_docs_dir):
        award("repository_structure", 3, "Clear src/test/docs structure detected.")
    if has_workflow:
        award("repository_structure", 3, "CI workflow detected.")

    if has_tests:
        award("test_presence", 7, "Solidity test files detected.")
    if test_readiness["assert_usage"]:
        award("test_presence", 4, "Assert usage detected.")
    if test_readiness["foundry_tests"] or test_readiness["hardhat_tests"]:
        award("test_presence", 4, "Foundry or Hardhat test environment detected.")
    protocol_terms = signal_terms(signals, "vault_accounting", "oracle", "amm", "lending", "staking_rewards")
    if has_tests and len(protocol_terms) >= 3:
        award("test_presence", 5, "Protocol-specific terms appear in the testable codebase.")

    if test_readiness["invariant_tests"]:
        award("invariant_fuzz_readiness", 8, "Invariant tests or invariant terms detected.")
    if test_readiness["fuzz_tests"]:
        award("invariant_fuzz_readiness", 5, "Fuzz tests detected.")
    if test_readiness["handler_contracts"]:
        award("invariant_fuzz_readiness", 4, "Handler or property-style testing terms detected.")
    if test_readiness["edge_case_tests"]:
        award("invariant_fuzz_readiness", 3, "Edge-case testing terms detected.")

    oracle_documented = has_meaningful_oracle_signal(signals) and any(term in all_text.lower() for term in ["stale", "heartbeat", "twap", "bounds", "sanity"])
    accounting_documented = has_any(signals, "vault_accounting") and any(
        term in all_text.lower() for term in ["roundtrip", "conservation", "totalassets", "shares", "rounding"]
    )
    role_covered = has_any(signals, "access_control") and any(
        term in all_text.lower() for term in ["unauthorized", "onlyowner", "accesscontrol", "role", "admin"]
    )
    value_flow_covered = has_any(signals, "reentrancy_value_flow") and (
        has_any(signals, "reentrancy_value_flow", ["nonReentrant", "ReentrancyGuard"]) or "reentr" in all_text.lower()
    )
    protocol_checklist = protocol_type != "generic" and (
        test_readiness["edge_case_tests"] or test_readiness["invariant_tests"] or "checklist" in all_text.lower()
    )
    if oracle_documented:
        award("defi_risk_coverage", 5, "Oracle assumptions have at least some documented or tested controls.")
    if accounting_documented:
        award("defi_risk_coverage", 5, "Accounting assumptions have at least some documented or tested controls.")
    if role_covered:
        award("defi_risk_coverage", 4, "Role or admin boundaries have some visible coverage.")
    if value_flow_covered:
        award("defi_risk_coverage", 3, "Value-flow or reentrancy guard/review signals detected.")
    if protocol_checklist:
        award("defi_risk_coverage", 3, "Protocol-specific checklist or property coverage detected.")

    has_readme = any(p.name.lower() == "readme.md" for p in classified.docs)
    has_security = any(p.name.lower() == "security.md" or "docs/security" in rel(p, root).lower() for p in classified.docs)
    assumptions_documented = any(term in all_text.lower() for term in ["assumption", "invariant", "limitations", "oracle", "roles"])
    roles_documented = any(term in all_text.lower() for term in ["deployment", "owner", "admin", "role", "treasury"])
    if has_readme:
        award("documentation_readiness", 3, "README detected.")
    if has_security:
        award("documentation_readiness", 2, "SECURITY or docs/security material detected.")
    if assumptions_documented:
        award("documentation_readiness", 3, "Assumptions, invariants, or limitations are documented.")
    if roles_documented:
        award("documentation_readiness", 2, "Deployment or role information appears in docs/code comments.")

    if has_any(signals, "access_control"):
        award("operational_admin_readiness", 3, "Access-control surface is visible.")
    if any(term in all_text.lower() for term in ["pause", "emergency", "incident", "runbook"]):
        award("operational_admin_readiness", 3, "Emergency control or incident terms detected.")
    if not has_any(signals, "upgradeability") or any(term in all_text.lower() for term in ["initializer", "upgrade", "storage gap", "__gap"]):
        award("operational_admin_readiness", 3, "Upgradeability is absent or has visible documentation/test terms.")
    if any(term in all_text for term in ["setFee", "setOracle", "setStrategy", "setTreasury", "onlyOwner"]):
        award("operational_admin_readiness", 3, "Privileged setters or owner boundaries are visible for review.")
    if any(term in all_text.lower() for term in ["monitor", "incident", "limitations", "pause", "emergency"]):
        award("operational_admin_readiness", 3, "Monitoring, incident, limitation, or emergency notes detected.")

    if not has_tests:
        add_gap(
            gaps,
            "Critical readiness gap",
            "No Solidity tests detected",
            "The scanner did not find Solidity test files. A DeFi repository without tests is not ready for formal audit intake.",
            "Add Foundry or Hardhat tests for core user flows before requesting a formal audit.",
            ["testing", "audit-blocker"],
        )
    if protocol_type != "generic" and not test_readiness["invariant_tests"]:
        add_gap(
            gaps,
            "High readiness gap",
            "No invariant tests detected for DeFi protocol shape",
            "Protocol-like value flows were detected, but no invariant/property testing signal was found.",
            "Add Foundry invariant tests for accounting, oracle, role, and value-flow assumptions.",
            ["invariant-testing", protocol_type],
        )
    if has_meaningful_oracle_signal(signals) and not oracle_documented:
        add_gap(
            gaps,
            "High readiness gap",
            "Oracle usage lacks visible staleness, TWAP, bounds, or sanity coverage",
            "Oracle and price-feed signals were detected without enough freshness or sanity-check language.",
            "Document and test oracle freshness, decimals normalization, price bounds, and fallback behavior.",
            ["oracle-risk", "price-assumptions"],
        )
    if has_any(signals, "vault_accounting") and not accounting_documented:
        add_gap(
            gaps,
            "High readiness gap",
            "Vault accounting lacks visible roundtrip or conservation coverage",
            "Vault/share/accounting terms were detected without enough explicit conservation or roundtrip testing language.",
            "Add deposit/withdraw roundtrip tests and totalAssets/share accounting invariants.",
            ["vault-accounting", "share-accounting"],
        )
    if has_any(signals, "reentrancy_value_flow") and not value_flow_covered:
        add_gap(
            gaps,
            "Medium readiness gap",
            "External-call value flow needs reentrancy review",
            "External call or token transfer terms were detected without guard or reentrancy-review signals.",
            "Review state update order and add local malicious-receiver tests where callbacks are possible.",
            ["reentrancy-review", "value-flow"],
        )
    if has_any(signals, "upgradeability") and "initializer" not in all_text:
        add_gap(
            gaps,
            "Medium readiness gap",
            "Upgradeability surface needs initializer review",
            "Proxy or implementation terms were detected without a strong initializer signal.",
            "Add initializer, reinitializer, authorization, and storage layout tests/docs.",
            ["upgradeability", "initialization"],
        )
    if has_any(signals, "access_control") and not role_covered:
        add_gap(
            gaps,
            "Medium readiness gap",
            "Admin setters need explicit authorization coverage",
            "Privileged role/setter terms were detected without enough unauthorized-call coverage.",
            "Add tests that unauthorized users cannot call privileged setters or emergency controls.",
            ["access-control-review", "admin-risk"],
        )
    if has_any(signals, "staking_rewards") and not test_readiness["invariant_tests"]:
        add_gap(
            gaps,
            "Medium readiness gap",
            "Reward accounting needs conservation coverage",
            "Reward/index/claim signals were detected without invariant testing.",
            "Add reward conservation and no-overclaim tests across multiple users and timing boundaries.",
            ["reward-accounting", "precision"],
        )
    if has_any(signals, "amm") and not test_readiness["invariant_tests"]:
        add_gap(
            gaps,
            "Medium readiness gap",
            "AMM math needs invariant coverage",
            "AMM reserve/liquidity/swap terms were detected without invariant testing.",
            "Add AMM invariant, liquidity proportionality, and fee-growth tests.",
            ["amm-invariant", "liquidity"],
        )

    total = sum(int(category["score"]) for category in score.values())
    total = max(0, min(100, total))
    next_steps = recommended_next_steps(gaps, protocol_type)
    return total, score, gaps, next_steps


def score_band(score: int) -> str:
    for low, high, label in SCORE_BANDS:
        if low <= score <= high:
            return label
    return "Unknown"


def recommended_next_steps(gaps: list[ReadinessGap], protocol_type: str) -> list[str]:
    steps: list[str] = []
    gap_titles = " ".join(g.title.lower() for g in gaps)
    if "no solidity tests" in gap_titles:
        steps.append("Add Foundry or Hardhat tests for every core user flow.")
    if "invariant" in gap_titles or protocol_type != "generic":
        steps.append("Add Foundry invariant tests for accounting, roles, and value-flow boundaries.")
    if "oracle" in gap_titles:
        steps.append("Document and test oracle freshness, decimals normalization, bounds, and fallback behavior.")
    if "vault" in gap_titles or protocol_type == "vault":
        steps.append("Add deposit/withdraw roundtrip, totalAssets consistency, and donation/inflation-resistance tests.")
    if "admin" in gap_titles or "authorization" in gap_titles:
        steps.append("Document privileged roles and add unauthorized-call tests for every setter and emergency control.")
    if "reentrancy" in gap_titles:
        steps.append("Review state update order and add malicious local receiver tests for callback-capable flows.")
    steps.extend(
        [
            "Write a formal audit scope with contracts, roles, assumptions, known limitations, and test commands.",
            "Run a formal smart contract audit before mainnet launch or before handling real user funds.",
        ]
    )
    unique: list[str] = []
    for step in steps:
        if step not in unique:
            unique.append(step)
    return unique[:5]


def suggest_invariants(
    protocol_type: str,
    signals: dict[str, dict[str, object]],
) -> list[dict[str, str]]:
    suggestions: list[dict[str, str]] = []

    def add(name: str, category: str, description: str) -> None:
        suggestions.append({"name": name, "category": category, "description": description})

    if protocol_type == "vault" or has_any(signals, "vault_accounting"):
        add("totalAssets consistency", "vault", "totalAssets should match local asset accounting and strategy balances within documented rounding.")
        add("deposit/withdraw roundtrip", "vault", "A user should not create value by depositing and withdrawing through normal paths.")
        add("share price manipulation resistance", "vault", "Donations, supply edges, or local price changes should not let one actor distort share value unexpectedly.")
        add("fee accounting conservation", "vault", "Fees should be bounded, documented, and unable to overcharge beyond configured limits.")
        add("strategy balance drift handling", "vault", "Strategy gains, losses, and withdrawals should remain reflected in accounting assumptions.")
        add("pause behavior", "vault", "Pause should block risky flows while preserving documented emergency exits.")
    if protocol_type == "oracle" or has_meaningful_oracle_signal(signals):
        add("stale price rejection", "oracle", "Stale oracle rounds should be rejected or handled according to documented policy.")
        add("decimals normalization", "oracle", "Price decimals should be normalized consistently before accounting decisions.")
        add("price bounds", "oracle", "Outlier prices should hit documented bounds or review paths.")
        add("TWAP or sanity check", "oracle", "Spot price dependence should be bounded by TWAP, sanity checks, or explicit assumptions.")
        add("oracle update access control", "oracle", "Only authorized roles should change oracle configuration.")
    if protocol_type == "amm" or has_any(signals, "amm"):
        add("invariant conservation", "amm", "Swaps should preserve the AMM invariant within fee and rounding expectations.")
        add("swap does not create value", "amm", "No swap sequence should create value outside documented fee mechanics.")
        add("liquidity add/remove proportionality", "amm", "Liquidity mint/burn should be proportional to reserves within expected rounding.")
        add("fee growth consistency", "amm", "Fee growth should be monotonic and attributable to swaps or configured fee paths.")
    if protocol_type == "lending" or has_any(signals, "lending"):
        add("collateralization invariant", "lending", "Borrower positions should respect collateralization requirements after every user action.")
        add("liquidation solvency", "lending", "Liquidations should improve solvency and preserve accounting assumptions.")
        add("interest index monotonicity", "lending", "Interest indexes should move monotonically according to configured rate logic.")
        add("oracle manipulation resistance", "lending", "Borrow and liquidation paths should resist transient price manipulation.")
        add("borrow/repay accounting consistency", "lending", "Debt and collateral balances should reconcile after borrow and repay sequences.")
    if protocol_type == "staking" or has_any(signals, "staking_rewards"):
        add("reward conservation", "staking", "Total claimed plus remaining claimable should not exceed funded rewards beyond rounding.")
        add("no overclaim", "staking", "Users should not claim more than their funded and accrued share.")
        add("index monotonicity", "staking", "Reward indexes should be monotonic and supply-aware.")
        add("stake/unstake roundtrip", "staking", "Stake and unstake flows should preserve balances and reward accounting.")
        add("reward accounting precision", "staking", "Small balances and precision edges should not create systematic reward drift.")
    if has_any(signals, "access_control"):
        add("unauthorized role rejection", "access control", "Unauthorized users cannot call privileged setters or emergency functions.")
        add("admin cannot bypass accounting", "access control", "Owner/admin operations cannot silently break accounting invariants unless explicitly trusted and documented.")
        add("pause blocks risky flows", "access control", "Pause blocks documented risky flows and preserves expected recovery paths.")
        add("upgrade authorization", "access control", "Upgrade authorization works as intended and cannot be triggered by untrusted callers.")

    seen: set[str] = set()
    deduped: list[dict[str, str]] = []
    for item in suggestions:
        if item["name"] not in seen:
            seen.add(item["name"])
            deduped.append(item)
    return deduped[:18]


def markdown_table(rows: list[list[str]]) -> str:
    if not rows:
        return ""
    header = rows[0]
    widths = [len(cell) for cell in header]
    for row in rows[1:]:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))
    lines = [
        "| " + " | ".join(cell.ljust(widths[i]) for i, cell in enumerate(header)) + " |",
        "| " + " | ".join("-" * widths[i] for i in range(len(header))) + " |",
    ]
    for row in rows[1:]:
        lines.append("| " + " | ".join(cell.ljust(widths[i]) for i, cell in enumerate(row)) + " |")
    return "\n".join(lines)


def generate_report(
    root: Path,
    output: Path,
    classified: ClassifiedFiles,
    protocol_type: str,
    protocol_confidence: str,
    protocol_scores: dict[str, int],
    signals: dict[str, dict[str, object]],
    test_readiness: dict[str, object],
    registry_metadata: dict[str, object],
    historical_patterns: list[HistoricalPattern],
    score: int,
    score_breakdown: dict[str, dict[str, object]],
    gaps: list[ReadinessGap],
    invariants: list[dict[str, str]],
    next_steps: list[str],
    skeleton_path: Path | None,
) -> None:
    generated_at = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    output.parent.mkdir(parents=True, exist_ok=True)

    file_summary = [
        ["File class", "Count"],
        ["Solidity sources", str(len(classified.solidity_sources))],
        ["Solidity tests", str(len(classified.solidity_tests))],
        ["Docs", str(len(classified.docs))],
        ["Configs", str(len(classified.configs))],
        ["Workflows", str(len(classified.workflows))],
    ]
    score_rows = [["Category", "Score", "Max", "Notes"]]
    for key, data in score_breakdown.items():
        label = key.replace("_", " ").title()
        score_rows.append(
            [
                label,
                str(data["score"]),
                str(data["max"]),
                "; ".join(data["notes"]) if data["notes"] else "No positive signal detected.",
            ]
        )

    lines: list[str] = []
    lines.append("# Arkheionx Pre-Audit Readiness Report")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append(f"- Repository root: `{display_path(root)}`")
    lines.append(f"- Generated at: `{generated_at}`")
    lines.append(f"- Protocol type: `{protocol_type}`")
    lines.append(f"- Protocol confidence: `{protocol_confidence}`")
    lines.append(f"- Files scanned: `{sum(len(v) for v in [classified.solidity_sources, classified.solidity_tests, classified.docs, classified.configs, classified.workflows, classified.unknown])}`")
    lines.append(f"- Scanner version: `{VERSION}`")
    lines.append("")
    lines.append(markdown_table(file_summary))
    lines.append("")
    lines.append("## Disclaimer")
    lines.append("")
    lines.append(DISCLAIMER)
    lines.append("")
    lines.append("## Executive Summary")
    lines.append("")
    lines.append(f"- Readiness score: **{score}/100**")
    lines.append(f"- Score band: **{score_band(score)}**")
    lines.append("- Top readiness gaps:")
    for gap in gaps[:5] or [ReadinessGap("Informational", "No major automated readiness gaps detected", "Manual review is still required.", "Proceed to manual review and formal audit planning.", ["manual-review"])]:
        lines.append(f"  - **{gap.severity}:** {gap.title} — {gap.recommendation}")
    lines.append("- Top recommended actions:")
    for step in next_steps[:5]:
        lines.append(f"  - {step}")
    lines.append("")
    lines.append("## Detected Protocol Shape")
    lines.append("")
    lines.append(f"- Detected protocol type: `{protocol_type}`")
    lines.append(f"- Confidence: `{protocol_confidence}`")
    lines.append(f"- Protocol score signals: `{json.dumps(protocol_scores, sort_keys=True)}`")
    lines.append(f"- Arkheionx memory metadata loaded: `{registry_metadata.get('entry_count', 0)}` entries")
    lines.append("")
    lines.append("## Readiness Score Breakdown")
    lines.append("")
    lines.append(markdown_table(score_rows))
    lines.append("")
    lines.append("## Risk Signal Summary")
    lines.append("")
    for category in [
        "vault_accounting",
        "oracle",
        "access_control",
        "reentrancy_value_flow",
        "upgradeability",
        "accounting_complexity",
        "staking_rewards",
        "amm",
        "lending",
        "bridge_cross_chain",
        "governance",
    ]:
        data = signals.get(category, {})
        terms = data.get("terms", [])
        if terms:
            lines.append(f"### {category.replace('_', ' ').title()}")
            lines.append("")
            lines.append(f"- Detected signals: `{', '.join(terms)}`")
            lines.append(f"- Files with signals: `{data.get('file_count', 0)}`")
            example_files = data.get("files", [])[:5]
            if example_files:
                lines.append(f"- Example files: `{', '.join(example_files)}`")
            lines.append("")
    lines.append("### Testing And Documentation")
    lines.append("")
    for key, value in test_readiness.items():
        if key != "test_files":
            lines.append(f"- {key.replace('_', ' ').title()}: `{value}`")
    if test_readiness.get("test_files"):
        lines.append(f"- Test files: `{', '.join(test_readiness['test_files'][:10])}`")
    lines.append("")
    lines.append("## Historical Exploit-Pattern Similarity")
    lines.append("")
    if historical_patterns:
        for item in historical_patterns:
            lines.append(f"### {item.name}")
            lines.append("")
            lines.append(f"- Confidence: `{item.confidence}`")
            lines.append(f"- Detected signals: `{', '.join(item.detected_signals[:20])}`")
            lines.append(f"- Why it matters: {item.why_it_matters}")
            lines.append(f"- Failed assumption class: {item.failed_assumption_class}")
            lines.append(f"- Broken invariant class: {item.broken_invariant_class}")
            lines.append("- Recommended defensive checks:")
            for check in item.defensive_checks:
                lines.append(f"  - {check}")
            lines.append(f"- Suggested test/invariant: {item.suggested_test}")
            lines.append(f"- Search tags: `{', '.join(item.search_tags)}`")
            lines.append("")
    else:
        lines.append("No strong historical pattern similarity was detected by the automated scanner. Manual review is still recommended.")
        lines.append("")
    lines.append("## Missing Invariant And Test Coverage")
    lines.append("")
    if gaps:
        for gap in gaps:
            lines.append(f"- **{gap.severity}: {gap.title}.** {gap.detail} Recommendation: {gap.recommendation} Tags: `{', '.join(gap.tags)}`")
    else:
        lines.append("- No major automated gaps detected. This does not prove safety and should be followed by manual review.")
    lines.append("")
    lines.append("## Suggested Foundry Invariant Skeletons")
    lines.append("")
    if skeleton_path:
        lines.append(f"- Generated skeleton: `{rel(skeleton_path, root)}`")
    else:
        lines.append("- Skeleton not generated in this run.")
        lines.append("- To generate: `python3 scripts/pre_audit_scan.py --root . --generate-invariant-skeletons`")
    lines.append("")
    if invariants:
        for item in invariants:
            lines.append(f"- **{item['name']}** (`{item['category']}`): {item['description']}")
    lines.append("")
    lines.append("## Audit Readiness Checklist")
    lines.append("")
    checklist = [
        "Core user flows have deterministic unit tests.",
        "Accounting, oracle, reward, and role assumptions are documented.",
        "Foundry invariant tests cover value conservation and access boundaries.",
        "Fuzz tests cover edge cases, rounding, and unexpected user sequences.",
        "Privileged roles, upgrade controls, and emergency controls are documented and tested.",
        "Known limitations are written down for auditors.",
        "A formal audit scope names contracts, commit hash, deployment assumptions, and out-of-scope areas.",
    ]
    for item in checklist:
        lines.append(f"- [ ] {item}")
    lines.append("")
    lines.append("## Search Tags")
    lines.append("")
    search_tags = [
        "arkheionx",
        "pre-audit-readiness",
        "indie-defi",
        "defi-security",
        "smart-contract-security",
        "solidity-security",
        "foundry",
        "invariant-testing",
        "oracle-risk",
        "vault-accounting",
        "reentrancy-review",
        "access-control-review",
        "historical-exploit-pattern",
        "root-cause-analysis",
        "audit-preparation",
    ]
    lines.append("`" + "`, `".join(search_tags) + "`")
    lines.append("")
    lines.append("## Recommended Next Steps")
    lines.append("")
    for i, step in enumerate(next_steps, 1):
        lines.append(f"{i}. {step}")
    lines.append("")
    lines.append("## What This Report Does Not Prove")
    lines.append("")
    lines.append("- It does not prove protocol safety.")
    lines.append("- It does not confirm exploitability.")
    lines.append("- It does not replace manual review.")
    lines.append("- It does not replace a formal audit.")
    lines.append("")
    lines.append("## Formal Audit Recommendation")
    lines.append("")
    lines.append("Run a formal smart contract audit before mainnet deployment, before material TVL, or before handling real user funds.")
    lines.append("")
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def json_report(
    root: Path,
    protocol_type: str,
    protocol_confidence: str,
    score: int,
    score_breakdown: dict[str, dict[str, object]],
    classified: ClassifiedFiles,
    signals: dict[str, dict[str, object]],
    historical_patterns: list[HistoricalPattern],
    gaps: list[ReadinessGap],
    invariants: list[dict[str, str]],
    next_steps: list[str],
) -> dict[str, object]:
    return {
        "tool": "Arkheionx Pre-Audit Scanner",
        "version": VERSION,
        "generated_at": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "repo_root": display_path(root),
        "protocol_type": protocol_type,
        "protocol_confidence": protocol_confidence,
        "score": score,
        "score_band": score_band(score),
        "score_breakdown": score_breakdown,
        "files_scanned": {
            "solidity_sources": [rel(p, root) for p in classified.solidity_sources],
            "solidity_tests": [rel(p, root) for p in classified.solidity_tests],
            "docs": [rel(p, root) for p in classified.docs],
            "configs": [rel(p, root) for p in classified.configs],
            "workflows": [rel(p, root) for p in classified.workflows],
        },
        "signals": signals,
        "historical_patterns": [item.__dict__ for item in historical_patterns],
        "readiness_gaps": [item.__dict__ for item in gaps],
        "suggested_invariants": invariants,
        "next_steps": next_steps,
        "disclaimer": DISCLAIMER,
    }


def generate_json_report(path: Path, report: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


SKELETON = """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// Arkheionx defensive readiness skeleton.
// This file is generated for local pre-audit preparation only.
// It contains no live addresses, no RPC calls, and no exploit payloads.

contract ArkheionxReadinessInvariants {
    // TODO: import your protocol contracts.
    // TODO: deploy a local test instance.
    // TODO: wire mock assets and mock oracles.
    // TODO: replace placeholders with protocol-specific assertions.

    function invariant_totalAssetsConsistency() public {
        // TODO: assert local accounting equals assets held or documented strategy value.
    }

    function invariant_depositWithdrawRoundtripDoesNotCreateValue() public {
        // TODO: assert deposit/withdraw sequences do not create value beyond rounding.
    }

    function invariant_sharePriceManipulationResistance() public {
        // TODO: assert donation, supply, and mock-price edges cannot distort share value unexpectedly.
    }

    function invariant_adminRoleCannotBypassAccounting() public {
        // TODO: assert privileged actions cannot silently bypass documented accounting invariants.
    }

    function invariant_pauseBlocksRiskyFlows() public {
        // TODO: assert pause blocks risky flows and preserves documented emergency behavior.
    }

    function invariant_oracleAssumptionsAreDocumented() public {
        // TODO: assert stale, bounded, or mocked oracle behavior follows documented assumptions.
    }
}
"""


def generate_invariant_skeleton(root: Path) -> Path:
    path = root / "test" / "invariant" / "ArkheionxReadinessInvariants.t.sol"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(SKELETON, encoding="utf-8")
    return path


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a GitHub-native Arkheionx pre-audit readiness report.")
    parser.add_argument("--root", default=".", help="Repository root to scan.")
    parser.add_argument(
        "--protocol-type",
        default="auto",
        choices=["auto", "vault", "amm", "lending", "staking", "oracle", "generic"],
        help="Protocol type hint.",
    )
    parser.add_argument("--output", default="ARKHEIONX_PRE_AUDIT_REPORT.md", help="Markdown report output path.")
    parser.add_argument("--json-output", default="", help="Optional JSON report output path.")
    parser.add_argument("--generate-invariant-skeletons", action="store_true", help="Generate safe Foundry invariant skeletons.")
    parser.add_argument("--fail-on-critical-readiness-gap", action="store_true", help="Exit 2 if critical readiness gaps are detected.")
    parser.add_argument("--create-issues", action="store_true", help="Reserved for future local issue suggestions; no remote issues are created.")
    parser.add_argument("--verbose", action="store_true", help="Print scanner details.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    root = Path(args.root).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        print(f"error: --root does not exist or is not a directory: {root}", file=sys.stderr)
        return 1
    if args.create_issues and args.verbose:
        print("notice: --create-issues is reserved for future local issue suggestions; no remote issues are created.")

    files = collect_files(root)
    classified = classify_files(files)
    contents = corpus(files)
    protocol_type, protocol_confidence, protocol_scores = detect_protocol_type(contents, classified, args.protocol_type)
    signal_paths = [
        path
        for path in classified.solidity_sources + classified.solidity_tests + classified.configs
        if not is_placeholder_skeleton(contents.get(path, ""))
    ]
    signals = detect_signals(contents, root, signal_paths or contents.keys())
    test_readiness = detect_test_readiness(contents, classified, root)
    registry_metadata = load_existing_registry_metadata(root)
    historical_patterns = map_historical_patterns(signals, test_readiness)
    score, score_breakdown, gaps, next_steps = compute_readiness_score(
        root,
        classified,
        contents,
        signals,
        test_readiness,
        protocol_type,
    )
    invariants = suggest_invariants(protocol_type, signals)
    skeleton_path = generate_invariant_skeleton(root) if args.generate_invariant_skeletons else None

    output = Path(args.output)
    if not output.is_absolute():
        output = Path.cwd() / output
    generate_report(
        root=root,
        output=output,
        classified=classified,
        protocol_type=protocol_type,
        protocol_confidence=protocol_confidence,
        protocol_scores=protocol_scores,
        signals=signals,
        test_readiness=test_readiness,
        registry_metadata=registry_metadata,
        historical_patterns=historical_patterns,
        score=score,
        score_breakdown=score_breakdown,
        gaps=gaps,
        invariants=invariants,
        next_steps=next_steps,
        skeleton_path=skeleton_path,
    )

    if args.json_output:
        json_output = Path(args.json_output)
        if not json_output.is_absolute():
            json_output = Path.cwd() / json_output
        generate_json_report(
            json_output,
            json_report(
                root,
                protocol_type,
                protocol_confidence,
                score,
                score_breakdown,
                classified,
                signals,
                historical_patterns,
                gaps,
                invariants,
                next_steps,
            ),
        )

    critical_gaps = [gap for gap in gaps if gap.severity == "Critical readiness gap"]
    print(f"Arkheionx pre-audit report generated: {output}")
    if args.json_output:
        print(f"Arkheionx JSON report generated: {Path(args.json_output)}")
    if skeleton_path:
        print(f"Arkheionx invariant skeleton generated: {skeleton_path}")
    print(f"Readiness score: {score}/100 ({score_band(score)})")

    if args.fail_on_critical_readiness_gap and critical_gaps:
        print("critical readiness gaps detected; failing because --fail-on-critical-readiness-gap was set", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

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
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


VERSION = "0.4.0"
FINGERPRINT_VERSION = "0.4.0"
MAX_READ_BYTES = 750_000
PACKAGE_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = ".arkheionx.json"
COMMENT_MARKER = "<!-- arkheionx-pre-audit-comment -->"
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


VAULT_ERC4626_TERMS = [
    "ERC4626",
    "asset()",
    "totalAssets",
    "convertToShares",
    "convertToAssets",
    "previewDeposit",
    "previewMint",
    "previewWithdraw",
    "previewRedeem",
    "maxDeposit",
    "maxMint",
    "maxWithdraw",
    "maxRedeem",
    "deposit",
    "mint",
    "withdraw",
    "redeem",
    "shares",
    "assets",
    "totalSupply",
    "balanceOf",
    "pricePerShare",
    "exchangeRate",
    "sharePrice",
]

VAULT_ACCOUNTING_RISK_TERMS = [
    "totalAssets",
    "convertToShares",
    "convertToAssets",
    "previewDeposit",
    "previewMint",
    "previewWithdraw",
    "previewRedeem",
    "rounding",
    "mulDiv",
    "precision",
    "decimals",
    "donation",
    "inflation",
    "feeOnTransfer",
    "fee-on-transfer",
    "rebasing",
    "performanceFee",
    "managementFee",
    "withdrawalFee",
    "depositFee",
    "treasury",
    "feeRecipient",
    "externalBalance",
]

VAULT_STRATEGY_TERMS = [
    "strategy",
    "strategies",
    "allocate",
    "withdrawFromStrategy",
    "harvest",
    "rebalance",
    "report",
    "debt",
    "totalDebt",
    "credit",
    "loss",
    "gain",
    "profit",
    "migrateStrategy",
    "strategyMigration",
    "emergencyExit",
]

VAULT_PRICING_TERMS = [
    "oracle",
    "priceFeed",
    "getPrice",
    "latestRoundData",
    "latestAnswer",
    "getReserves",
    "spot",
    "twap",
    "stale",
    "heartbeat",
    "decimals",
    "Chainlink",
    "UniswapV2",
    "UniswapV3",
    "Curve",
    "pool price",
    "lpPrice",
    "LP token",
]

VAULT_WITHDRAWAL_TERMS = [
    "queue",
    "withdrawalQueue",
    "requestWithdraw",
    "claimWithdraw",
    "cooldown",
    "lock",
    "epoch",
    "pendingWithdraw",
    "availableLiquidity",
    "liquidityBuffer",
    "instantWithdraw",
    "delayedWithdraw",
    "cancelWithdraw",
]

VAULT_ADMIN_TERMS = [
    "setStrategy",
    "setOracle",
    "setFee",
    "setTreasury",
    "pause",
    "unpause",
    "emergencyWithdraw",
    "sweep",
    "rescue",
    "setDepositLimit",
    "setWithdrawLimit",
    "setMaxLoss",
    "setSlippage",
    "upgradeTo",
    "initialize",
    "initializer",
]

VAULT_TEST_COVERAGE_TERMS: dict[str, list[str]] = {
    "deposit": ["deposit", "previewDeposit"],
    "withdraw": ["withdraw", "previewWithdraw", "redeem", "previewRedeem"],
    "mint": ["mint", "previewMint"],
    "preview_functions": ["previewDeposit", "previewMint", "previewWithdraw", "previewRedeem"],
    "total_assets": ["totalAssets"],
    "share_conversion": ["convertToShares", "convertToAssets", "shares", "assets"],
    "roundtrip": ["roundtrip", "depositWithdraw", "withdrawDeposit"],
    "invariant": ["invariant", "StdInvariant"],
    "fuzz": ["fuzz", "testFuzz"],
    "donation_inflation": ["donation", "inflation"],
    "decimals_rounding": ["decimals", "rounding", "precision", "mulDiv"],
    "fee": ["fee", "performanceFee", "managementFee", "withdrawalFee", "depositFee"],
    "strategy_loss": ["strategy", "loss", "gain", "debt", "harvest", "rebalance"],
    "withdrawal_lifecycle": ["withdrawalQueue", "requestWithdraw", "claimWithdraw", "cooldown", "pendingWithdraw"],
    "emergency_pause": ["emergency", "pause", "unpause"],
    "oracle_pricing": ["oracle", "priceFeed", "stale", "twap", "heartbeat", "bounds", "slippage"],
}

SIGNAL_TERMS: dict[str, list[str]] = {
    "vault_accounting": [
        "ERC4626",
        "totalAssets",
        "convertToShares",
        "convertToAssets",
        "previewDeposit",
        "previewMint",
        "previewWithdraw",
        "previewRedeem",
        "maxDeposit",
        "maxMint",
        "maxWithdraw",
        "maxRedeem",
        "pricePerShare",
        "sharePrice",
        "exchangeRate",
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
    "vault_erc4626": VAULT_ERC4626_TERMS,
    "vault_accounting_risk": VAULT_ACCOUNTING_RISK_TERMS,
    "vault_strategy": VAULT_STRATEGY_TERMS,
    "vault_pricing": VAULT_PRICING_TERMS,
    "vault_withdrawal_liquidity": VAULT_WITHDRAWAL_TERMS,
    "vault_admin_ops": VAULT_ADMIN_TERMS,
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
        "donation",
        "inflation",
        "feeOnTransfer",
        "rebasing",
        "withdrawalFee",
        "depositFee",
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
        "ERC4626": 8,
        "deposit": 3,
        "withdraw": 3,
        "mint": 2,
        "redeem": 3,
        "totalAssets": 5,
        "convertToShares": 5,
        "convertToAssets": 5,
        "previewDeposit": 4,
        "previewWithdraw": 4,
        "previewRedeem": 4,
        "maxWithdraw": 3,
        "pricePerShare": 4,
        "sharePrice": 4,
        "exchangeRate": 4,
        "share": 2,
        "strategy": 3,
        "withdrawalQueue": 4,
        "asset": 2,
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
    priority: str = "Medium readiness gap"
    id: str = ""
    category: str = "generic"
    confidence: str = "medium"
    fingerprint: str = ""
    detected: list[str] = field(default_factory=list)
    affected_files: list[str] = field(default_factory=list)
    why_it_matters: str = ""
    historical_pattern_similarity: str = ""
    defensive_checks: list[str] = field(default_factory=list)
    suggested_test: str = ""
    suppressible: bool = True
    suppression: dict[str, str] = field(default_factory=dict)


FINDING_RULES: list[tuple[str, str, str]] = [
    ("No Solidity tests detected", "ARK-TST-001", "testing-readiness"),
    ("No invariant tests detected for DeFi protocol shape", "ARK-TST-002", "testing-readiness"),
    ("Vault accounting without invariant tests", "ARK-VLT-001", "vault-accounting"),
    ("ERC4626-like interface without preview function tests", "ARK-VLT-002", "vault-accounting"),
    ("Shares/assets conversion without rounding tests", "ARK-VLT-003", "vault-accounting"),
    ("totalAssets external dependency without manipulation-resistance tests", "ARK-VLT-004", "vault-accounting"),
    ("Strategy accounting without gain/loss tests", "ARK-VLT-005", "vault-strategy"),
    ("Withdrawal queue/cooldown without lifecycle tests", "ARK-VLT-006", "vault-withdrawal"),
    ("Fee logic without fee accounting tests", "ARK-VLT-007", "vault-accounting"),
    ("Pause/emergency controls without operational tests", "ARK-VLT-008", "vault-operations"),
    ("Oracle-dependent vault without stale-price or bounds tests", "ARK-ORC-001", "oracle-pricing"),
    ("Oracle usage lacks visible staleness, TWAP, bounds, or sanity coverage", "ARK-ORC-002", "oracle-pricing"),
    ("Admin setters without role-boundary tests", "ARK-ACC-001", "access-control"),
    ("Admin setters need explicit authorization coverage", "ARK-ACC-002", "access-control"),
    ("External-call value flow needs reentrancy review", "ARK-REENT-001", "reentrancy-value-flow"),
    ("Upgradeable vault without initializer/upgrade tests", "ARK-UPG-001", "upgradeability-initialization"),
    ("Upgradeability surface needs initializer review", "ARK-UPG-002", "upgradeability-initialization"),
    ("Reward accounting needs conservation coverage", "ARK-RWD-001", "reward-accounting"),
    ("AMM math needs invariant coverage", "ARK-AMM-001", "amm-invariant"),
    ("Vault accounting lacks visible roundtrip or conservation coverage", "ARK-VLT-009", "vault-accounting"),
]

CATEGORY_PREFIXES: list[tuple[set[str], str, str]] = [
    ({"vault-accounting", "erc4626", "share-accounting", "totalAssets", "fee-accounting"}, "ARK-VLT-900", "vault-accounting"),
    ({"oracle-risk", "vault-pricing", "price-assumptions", "pool-price"}, "ARK-ORC-900", "oracle-pricing"),
    ({"access-control-review", "admin-risk", "vault-admin"}, "ARK-ACC-900", "access-control"),
    ({"reentrancy-review", "value-flow"}, "ARK-REENT-900", "reentrancy-value-flow"),
    ({"upgradeability", "initializer", "proxy-review"}, "ARK-UPG-900", "upgradeability-initialization"),
    ({"reward-accounting", "staking"}, "ARK-RWD-900", "reward-accounting"),
    ({"amm-invariant", "liquidity"}, "ARK-AMM-900", "amm-invariant"),
    ({"lending", "liquidation", "collateral"}, "ARK-LEND-900", "lending-liquidation"),
    ({"cross-chain", "bridge-validation"}, "ARK-XCH-900", "cross-chain-validation"),
    ({"testing", "audit-blocker", "invariant-testing"}, "ARK-TST-900", "testing-readiness"),
]


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


def finding_identity(title: str, tags: list[str]) -> tuple[str, str]:
    for known_title, finding_id, category in FINDING_RULES:
        if title == known_title:
            return finding_id, category

    tag_set = set(tags)
    for trigger_tags, finding_id, category in CATEGORY_PREFIXES:
        if tag_set & trigger_tags:
            return finding_id, category
    return "ARK-GEN-001", "generic"


def priority_label(severity: str, priority: str | None = None) -> str:
    label = priority or severity
    if "readiness gap" in label.lower():
        return label
    return f"{label} readiness gap"


def confidence_from_terms(terms: list[str]) -> str:
    if len(terms) >= 8:
        return "high"
    if len(terms) >= 3:
        return "medium"
    return "low"


def normalize_for_fingerprint(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def compute_finding_fingerprint(gap: ReadinessGap, protocol_type: str) -> str:
    payload = {
        "fingerprint_version": FINGERPRINT_VERSION,
        "protocol_type": protocol_type,
        "id": gap.id,
        "category": gap.category,
        "title": normalize_for_fingerprint(gap.title),
        "detected_signals": sorted(gap.detected),
        "affected_files": sorted(gap.affected_files),
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:24]


def is_high_or_critical(gap: ReadinessGap | dict[str, object]) -> bool:
    if isinstance(gap, ReadinessGap):
        text = f"{gap.priority} {gap.severity}".lower()
    else:
        text = f"{gap.get('priority', '')} {gap.get('severity', '')}".lower()
    return "critical" in text or "high" in text


def normalize_ignore_path(value: str) -> str:
    return value.strip().replace("\\", "/").lstrip("./")


def should_ignore_config_path(path: Path, root: Path, ignore_paths: Iterable[str]) -> bool:
    relative = rel(path, root)
    for raw in ignore_paths:
        item = normalize_ignore_path(raw)
        if not item:
            continue
        if item.endswith("/"):
            if relative.startswith(item):
                return True
        elif relative == item or relative.startswith(item.rstrip("/") + "/"):
            return True
    return False


def load_local_config(path: Path | None, root: Path) -> tuple[dict[str, object], list[str]]:
    if path is None:
        return {}, []
    if path.is_absolute():
        config_path = path
    else:
        cwd_candidate = Path.cwd() / path
        root_candidate = root / path
        config_path = cwd_candidate if cwd_candidate.exists() else root_candidate
    if not config_path.exists():
        return {}, []
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {}, [f"Could not parse Arkheionx config `{display_path(config_path)}`: {exc}"]
    if not isinstance(data, dict):
        return {}, [f"Arkheionx config `{display_path(config_path)}` must be a JSON object."]
    return data, []


def config_ignore_paths(config: dict[str, object]) -> list[str]:
    raw = config.get("ignore_paths", [])
    if not isinstance(raw, list):
        return []
    return [str(item) for item in raw if isinstance(item, str)]


def config_suppressions(config: dict[str, object]) -> dict[str, dict[str, str]]:
    raw = config.get("suppress_findings", [])
    suppressions: dict[str, dict[str, str]] = {}
    if not isinstance(raw, list):
        return suppressions
    for item in raw:
        if not isinstance(item, dict) or not item.get("id"):
            continue
        finding_id = str(item.get("id", "")).strip()
        suppressions[finding_id] = {
            "reason": str(item.get("reason", "No reason provided.")),
            "expires": str(item.get("expires", "")),
        }
    return suppressions


def config_additional_tags(config: dict[str, object]) -> list[str]:
    raw = config.get("additional_search_tags", [])
    if not isinstance(raw, list):
        return []
    return sorted({str(item) for item in raw if isinstance(item, str) and item.strip()})


def config_max_top_gaps(config: dict[str, object]) -> int:
    report = config.get("report", {})
    if not isinstance(report, dict):
        return 5
    try:
        value = int(report.get("max_top_gaps", 5))
    except (TypeError, ValueError):
        return 5
    return max(1, min(20, value))


def resolve_output_path(raw_path: str) -> Path | None:
    if not raw_path:
        return None
    path = Path(raw_path).expanduser()
    if not path.is_absolute():
        path = Path.cwd() / path
    return path


def gap_priority_rank(gap: ReadinessGap) -> int:
    text = f"{gap.priority} {gap.severity}".lower()
    if "critical" in text:
        return 0
    if "high" in text:
        return 1
    if "medium" in text:
        return 2
    if "low" in text:
        return 3
    return 4


def top_findings(gaps: list[ReadinessGap], limit: int = 5) -> list[ReadinessGap]:
    return sorted(gaps, key=lambda gap: (gap_priority_rank(gap), gap.id, gap.title))[:limit]


def finding_counts(gaps: list[ReadinessGap], suppressed: list[ReadinessGap]) -> dict[str, int]:
    counts = {
        "total_readiness_gaps": len(gaps),
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
        "informational": 0,
        "suppressed": len(suppressed),
    }
    for gap in gaps:
        text = f"{gap.priority} {gap.severity}".lower()
        if "critical" in text:
            counts["critical"] += 1
        elif "high" in text:
            counts["high"] += 1
        elif "medium" in text:
            counts["medium"] += 1
        elif "low" in text:
            counts["low"] += 1
        else:
            counts["informational"] += 1
    return counts


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


def has_meaningful_vault_pricing_signal(signals: dict[str, dict[str, object]]) -> bool:
    """Treat decimals alone as accounting complexity, not a vault pricing dependency."""
    found = set(signals.get("vault_pricing", {}).get("terms", []))
    return bool(found - {"decimals"})


def detected_terms(signals: dict[str, dict[str, object]], *categories: str) -> list[str]:
    return signal_terms(signals, *categories)


def signal_count(signals: dict[str, dict[str, object]], category: str) -> int:
    return len(signals.get(category, {}).get("terms", []))


def collect_text_for_paths(contents: dict[Path, str], paths: Iterable[Path]) -> str:
    return combined_text(contents, paths)


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


def detect_vault_test_coverage(
    contents: dict[Path, str],
    classified: ClassifiedFiles,
) -> dict[str, object]:
    usable_tests = [
        path
        for path in classified.solidity_tests
        if not is_placeholder_skeleton(contents.get(path, ""))
    ]
    test_text = collect_text_for_paths(contents, usable_tests)
    coverage: dict[str, bool] = {}
    matched_terms: dict[str, list[str]] = {}
    for key, terms in VAULT_TEST_COVERAGE_TERMS.items():
        matched = sorted({term for term in terms if count_term(test_text, term) > 0})
        coverage[key] = bool(matched)
        matched_terms[key] = matched

    return {
        "coverage": coverage,
        "matched_terms": matched_terms,
        "covered_count": sum(1 for value in coverage.values() if value),
        "total_checks": len(coverage),
        "test_files_considered": len(usable_tests),
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
    vault_like = has_any(signals, "vault_accounting") or has_any(signals, "vault_erc4626")

    if vault_like and (has_meaningful_oracle_signal(signals) or has_meaningful_vault_pricing_signal(signals)) and weak_invariants:
        patterns.append(
            pattern(
                "Harvest/Yearn-style oracle or pool price readiness gap",
                signal_terms(signals, "vault_accounting", "vault_pricing", "oracle"),
                "Vault accounting that depends on oracle, pool, LP, or reserve pricing needs explicit tests for stale, spot, and manipulated local price assumptions.",
                "Price source remains representative during deposits, withdrawals, and share conversions.",
                "Share/accounting value cannot be moved by transient price state.",
                [
                    "Document oracle freshness, bounds, and fallback behavior.",
                    "Test deposit, withdraw, and totalAssets under mocked stale and bounded prices.",
                    "Prefer TWAP, sanity bounds, or explicit staleness checks where the design depends on external prices.",
                ],
                "Invariant: share price and totalAssets cannot be inflated by a single mocked price or pool-state movement.",
                ["vault-accounting", "oracle-risk", "pool-pricing", "historical-vault-pattern", "invariant-testing"],
            )
        )

    if vault_like and weak_invariants:
        patterns.append(
            pattern(
                "Vault accounting invariant readiness gap",
                signal_terms(signals, "vault_accounting", "vault_erc4626", "vault_accounting_risk", "accounting_complexity"),
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

    if vault_like and has_any(signals, "vault_accounting_risk", ["donation", "inflation"]) and weak_invariants:
        patterns.append(
            pattern(
                "ERC4626/share inflation or donation sensitivity readiness gap",
                signal_terms(signals, "vault_erc4626", "vault_accounting_risk"),
                "ERC4626-like share systems need tests for zero-supply, donation, inflation, and rounding edges before audit intake.",
                "Initial or low-liquidity share accounting cannot be distorted by donated assets or rounding direction.",
                "Share issuance and redemption preserve user value across supply edges.",
                [
                    "Test first deposit and low-supply states.",
                    "Test donated assets before and after deposits.",
                    "Test convertToShares and convertToAssets around rounding boundaries.",
                ],
                "Invariant: donations and low-supply states do not let share accounting create value beyond documented rounding.",
                ["erc4626", "share-inflation-risk", "donation-sensitivity", "vault-invariant"],
            )
        )

    if vault_like and has_any(signals, "vault_strategy"):
        patterns.append(
            pattern(
                "Strategy debt/gain/loss accounting readiness gap",
                signal_terms(signals, "vault_strategy", "vault_accounting"),
                "Strategy vaults need explicit tests for gain, loss, debt, harvest, report, and migration lifecycle assumptions.",
                "Strategy-reported balances, gains, losses, and debt remain aligned with vault accounting.",
                "Strategy lifecycle events cannot silently break totalAssets, share price, or withdrawal accounting.",
                [
                    "Test harvest/report gain and loss paths with local mocks.",
                    "Test strategy withdrawal and migration accounting.",
                    "Document trusted strategy roles and loss-handling assumptions.",
                ],
                "Invariant: strategy gain/loss reports update totalAssets and share accounting according to documented policy.",
                ["strategy-accounting", "vault-lifecycle", "gain-loss", "audit-readiness"],
            )
        )

    if vault_like and has_any(signals, "vault_withdrawal_liquidity"):
        patterns.append(
            pattern(
                "Withdrawal liquidity and queue lifecycle readiness gap",
                signal_terms(signals, "vault_withdrawal_liquidity", "vault_accounting"),
                "Withdrawal queues, cooldowns, epochs, and liquidity buffers need lifecycle tests because user exits depend on state transitions over time.",
                "Requested, pending, claimable, and cancelled withdrawals move through documented states only.",
                "Withdrawal lifecycle preserves shares/assets accounting and available liquidity assumptions.",
                [
                    "Test request, cancel, claim, cooldown, and epoch transitions.",
                    "Test available liquidity and buffer boundaries.",
                    "Document delayed withdrawal assumptions for auditors.",
                ],
                "Test: withdrawal lifecycle conserves shares and assets across request, cooldown, claim, and cancellation.",
                ["withdrawal-queue", "liquidity-buffer", "vault-lifecycle", "audit-readiness"],
            )
        )

    if vault_like and has_any(signals, "vault_admin_ops"):
        patterns.append(
            pattern(
                "Privileged vault controls and emergency operation readiness gap",
                signal_terms(signals, "vault_admin_ops", "access_control", "upgradeability"),
                "Vault admin operations can change strategy, oracle, fee, limits, slippage, pause state, or upgrade targets and should be tested as launch-critical boundaries.",
                "Privileged operations are limited to documented roles and cannot bypass accounting assumptions silently.",
                "Emergency and configuration changes preserve the user-facing safety properties the protocol claims.",
                [
                    "Test unauthorized calls for each setter and emergency function.",
                    "Test pause and emergency controls against deposit, withdraw, redeem, and strategy paths.",
                    "Document trusted-role powers and operational limits.",
                ],
                "Invariant: admin operations cannot bypass vault accounting without explicit, documented trust assumptions.",
                ["vault-admin", "emergency-controls", "access-control-review", "operational-readiness"],
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
    priority: str | None = None,
    finding_id: str | None = None,
    category: str | None = None,
    confidence: str | None = None,
    detected: list[str] | None = None,
    affected_files: list[str] | None = None,
    why_it_matters: str = "",
    historical_pattern_similarity: str = "",
    defensive_checks: list[str] | None = None,
    suggested_test: str = "",
    suppressible: bool = True,
) -> None:
    detected_signals = sorted(set(detected or []))
    default_id, default_category = finding_identity(title, tags)
    gaps.append(
        ReadinessGap(
            severity=severity,
            title=title,
            detail=detail,
            recommendation=recommendation,
            tags=tags,
            priority=priority_label(severity, priority),
            id=finding_id or default_id,
            category=category or default_category,
            confidence=confidence or confidence_from_terms(detected_signals),
            detected=detected_signals,
            affected_files=sorted(set(affected_files or []))[:10],
            why_it_matters=why_it_matters,
            historical_pattern_similarity=historical_pattern_similarity,
            defensive_checks=defensive_checks or [],
            suggested_test=suggested_test,
            suppressible=suppressible,
        )
    )


def compute_vault_readiness_score(
    root: Path,
    classified: ClassifiedFiles,
    contents: dict[Path, str],
    signals: dict[str, dict[str, object]],
    test_readiness: dict[str, object],
) -> tuple[int, dict[str, dict[str, object]], list[ReadinessGap], list[str]]:
    all_text = combined_text(contents)
    lower_text = all_text.lower()
    lower_paths = [rel(p, root).lower() for p in contents]
    vault_tests = detect_vault_test_coverage(contents, classified)
    coverage = vault_tests["coverage"]
    gaps: list[ReadinessGap] = []

    score: dict[str, dict[str, object]] = {
        "repository_structure": {"score": 0, "max": 10, "notes": []},
        "test_presence": {"score": 0, "max": 15, "notes": []},
        "vault_accounting_coverage": {"score": 0, "max": 20, "notes": []},
        "invariant_fuzz_readiness": {"score": 0, "max": 20, "notes": []},
        "oracle_pricing_readiness": {"score": 0, "max": 10, "notes": []},
        "strategy_withdrawal_lifecycle_readiness": {"score": 0, "max": 10, "notes": []},
        "admin_operational_readiness": {"score": 0, "max": 10, "notes": []},
        "documentation_readiness": {"score": 0, "max": 5, "notes": []},
    }

    def award(category: str, points: int, note: str) -> None:
        score[category]["score"] = min(
            int(score[category]["max"]),
            int(score[category]["score"]) + points,
        )
        score[category]["notes"].append(note)

    has_sources = bool(classified.solidity_sources)
    has_config = bool(classified.configs)
    has_src = any(p.startswith("src/") or "/src/" in f"/{p}" for p in lower_paths)
    has_tests = bool(classified.solidity_tests)
    has_docs_dir = any(p.startswith("docs/") for p in lower_paths)
    has_workflow = bool(classified.workflows)
    vault_like_terms = detected_terms(signals, "vault_erc4626", "vault_accounting")
    pricing_terms = detected_terms(signals, "vault_pricing", "oracle")
    meaningful_pricing_terms = sorted(set(pricing_terms) - {"decimals"})
    strategy_terms = detected_terms(signals, "vault_strategy")
    withdrawal_terms = detected_terms(signals, "vault_withdrawal_liquidity")
    admin_terms = detected_terms(signals, "vault_admin_ops", "access_control")
    upgrade_terms = detected_terms(signals, "upgradeability")
    fee_terms = [term for term in detected_terms(signals, "vault_accounting_risk", "accounting_complexity") if "fee" in term.lower()]
    share_conversion_signal = has_any(signals, "vault_erc4626", ["convertToShares", "convertToAssets", "previewDeposit", "previewWithdraw"]) or has_any(signals, "vault_accounting", ["convertToShares", "convertToAssets", "shares", "assets"])
    role_covered = any(term in lower_text for term in ["unauthorized", "onlyowner", "accesscontrol", "role", "admin"])
    oracle_controls = any(term in lower_text for term in ["stale", "heartbeat", "twap", "bounds", "sanity", "slippage"])
    upgrade_covered = not upgrade_terms or any(term in lower_text for term in ["initializer", "reinitializer", "upgrade", "storage gap", "__gap"])

    if has_sources:
        award("repository_structure", 4, "Solidity vault-like sources detected.")
    if has_config:
        award("repository_structure", 2, "Recognized build or analysis config detected.")
    if has_src and (has_tests or has_docs_dir):
        award("repository_structure", 2, "Clear src/test/docs structure detected.")
    if has_workflow:
        award("repository_structure", 2, "CI workflow detected.")

    if has_tests:
        award("test_presence", 5, "Solidity tests detected.")
    if test_readiness["assert_usage"]:
        award("test_presence", 3, "Assert usage detected.")
    if test_readiness["foundry_tests"] or test_readiness["hardhat_tests"]:
        award("test_presence", 3, "Foundry or Hardhat environment detected.")
    if coverage["deposit"] and coverage["withdraw"]:
        award("test_presence", 2, "Deposit and withdraw/redeem test signals detected.")
    if coverage["mint"] or coverage["preview_functions"]:
        award("test_presence", 2, "Mint or preview function test signals detected.")

    if vault_like_terms:
        award("vault_accounting_coverage", 4, "Vault/ERC4626 share-accounting surface detected.")
    if coverage["total_assets"]:
        award("vault_accounting_coverage", 4, "totalAssets test signal detected.")
    if coverage["share_conversion"]:
        award("vault_accounting_coverage", 4, "Shares/assets conversion test signal detected.")
    if coverage["roundtrip"]:
        award("vault_accounting_coverage", 4, "Deposit/withdraw roundtrip test signal detected.")
    if coverage["donation_inflation"] or coverage["decimals_rounding"]:
        award("vault_accounting_coverage", 4, "Donation, inflation, decimals, or rounding test signal detected.")

    if test_readiness["invariant_tests"]:
        award("invariant_fuzz_readiness", 8, "Invariant tests detected.")
    if test_readiness["fuzz_tests"]:
        award("invariant_fuzz_readiness", 4, "Fuzz tests detected.")
    if test_readiness["handler_contracts"]:
        award("invariant_fuzz_readiness", 3, "Handler/property-style test signal detected.")
    if test_readiness["edge_case_tests"]:
        award("invariant_fuzz_readiness", 2, "Edge-case test signal detected.")
    if vault_tests["covered_count"] >= 8:
        award("invariant_fuzz_readiness", 3, "Broad vault test vocabulary detected.")

    if has_meaningful_oracle_signal(signals) or has_meaningful_vault_pricing_signal(signals):
        if oracle_controls:
            award("oracle_pricing_readiness", 4, "Oracle/pool pricing controls are documented or tested.")
        if coverage["oracle_pricing"]:
            award("oracle_pricing_readiness", 3, "Oracle/pricing test signal detected.")
        if coverage["decimals_rounding"]:
            award("oracle_pricing_readiness", 2, "Decimals or normalization test signal detected.")
        if role_covered:
            award("oracle_pricing_readiness", 1, "Oracle update role boundary signal detected.")
    else:
        award("oracle_pricing_readiness", 10, "No explicit oracle or pool-pricing dependency detected.")

    if strategy_terms or withdrawal_terms:
        if strategy_terms and coverage["strategy_loss"]:
            award("strategy_withdrawal_lifecycle_readiness", 4, "Strategy gain/loss lifecycle test signal detected.")
        if withdrawal_terms and coverage["withdrawal_lifecycle"]:
            award("strategy_withdrawal_lifecycle_readiness", 4, "Withdrawal lifecycle test signal detected.")
        if (strategy_terms or withdrawal_terms) and (coverage["emergency_pause"] or role_covered):
            award("strategy_withdrawal_lifecycle_readiness", 2, "Lifecycle operational boundary signal detected.")
    else:
        award("strategy_withdrawal_lifecycle_readiness", 10, "No strategy or queued-withdrawal lifecycle surface detected.")

    if admin_terms:
        award("admin_operational_readiness", 2, "Vault admin/operational surface is visible.")
    if role_covered:
        award("admin_operational_readiness", 3, "Role or unauthorized-call coverage signal detected.")
    if coverage["emergency_pause"] or any(term in lower_text for term in ["pause", "emergency"]):
        award("admin_operational_readiness", 2, "Pause or emergency control signal detected.")
    if upgrade_covered:
        award("admin_operational_readiness", 2, "Upgradeability is absent or initializer/upgrade terms are visible.")
    if fee_terms and coverage["fee"]:
        award("admin_operational_readiness", 1, "Fee accounting test signal detected.")
    elif not fee_terms:
        award("admin_operational_readiness", 1, "No explicit fee logic detected.")

    has_readme = any(p.name.lower() == "readme.md" for p in classified.docs)
    if has_readme:
        award("documentation_readiness", 2, "README detected.")
    if any(term in lower_text for term in ["assumption", "invariant", "limitations", "rounding", "oracle"]):
        award("documentation_readiness", 2, "Vault assumptions or limitations are documented.")
    if any(term in lower_text for term in ["owner", "admin", "role", "treasury", "deployment"]):
        award("documentation_readiness", 1, "Role, treasury, owner, or deployment terms are documented.")

    if not has_tests:
        add_gap(
            gaps,
            "Critical readiness gap",
            "No Solidity tests detected",
            "The scanner did not find Solidity test files. A value-bearing vault repository without tests is not ready for audit intake.",
            "Add Foundry or Hardhat tests for deposit, mint, withdraw, redeem, totalAssets, conversion, admin, and emergency flows.",
            ["testing", "vault", "audit-blocker"],
            priority="Critical",
            detected=vault_like_terms,
            why_it_matters="Vault accounting depends on user balances, shares, assets, and role-gated operations staying consistent across state transitions.",
            historical_pattern_similarity="Maps to historical vault/accounting failure classes where untested assumptions created audit blockers or loss conditions.",
            defensive_checks=["Core flow tests", "Role-boundary tests", "Accounting conservation tests"],
            suggested_test="Add local unit tests for deposit, withdraw/redeem, totalAssets, convertToShares, convertToAssets, pause, and admin setters.",
        )
    if vault_like_terms and not test_readiness["invariant_tests"]:
        add_gap(
            gaps,
            "High readiness gap",
            "Vault accounting without invariant tests",
            "Vault/ERC4626-like accounting signals were detected, but no non-placeholder invariant/property testing signal was found.",
            "Add Foundry invariants for share/accounting conservation across deposit, withdraw, donation, fee, and emergency scenarios.",
            ["vault-accounting", "invariant-testing", "erc4626"],
            priority="High",
            detected=vault_like_terms,
            why_it_matters="Vault bugs often appear when shares, assets, totalSupply, totalAssets, and external balances drift from assumptions used during deposits and withdrawals.",
            historical_pattern_similarity="Maps to historical vault/accounting failure classes where broken share valuation or manipulated accounting state caused loss.",
            defensive_checks=[
                "deposit/withdraw roundtrip",
                "convertToShares/convertToAssets consistency",
                "donation/inflation resistance",
                "rounding direction tests",
                "totalAssets external dependency tests",
            ],
            suggested_test="Add a Foundry invariant that checks totalAssets and share accounting conservation across deposit, withdraw, donation, and fee scenarios.",
        )
    if has_any(signals, "vault_erc4626", ["previewDeposit", "previewMint", "previewWithdraw", "previewRedeem"]) and not coverage["preview_functions"]:
        add_gap(
            gaps,
            "High readiness gap",
            "ERC4626-like interface without preview function tests",
            "Preview function signals were detected, but test files do not visibly cover previewDeposit, previewMint, previewWithdraw, or previewRedeem.",
            "Add tests that preview functions match actual state-changing outcomes within documented rounding bounds.",
            ["erc4626", "preview-functions", "vault-accounting"],
            priority="High",
            detected=detected_terms(signals, "vault_erc4626"),
            why_it_matters="ERC4626 integrations often rely on preview functions for quotes and UX; inconsistent previews can create user and integration risk.",
            historical_pattern_similarity="Maps to share/accounting mismatch classes where quoted and realized vault state diverge.",
            defensive_checks=["preview/action equivalence", "rounding direction tests", "max function boundary tests"],
            suggested_test="For each preview function, compare the previewed shares/assets with the actual deposit, mint, withdraw, or redeem result.",
        )
    if share_conversion_signal and not coverage["decimals_rounding"]:
        add_gap(
            gaps,
            "High readiness gap",
            "Shares/assets conversion without rounding tests",
            "Shares/assets conversion signals were detected without visible decimals, precision, mulDiv, or rounding test coverage.",
            "Add tests for rounding direction, small values, decimals mismatch, and conversion reversibility.",
            ["share-accounting", "rounding", "precision"],
            priority="High",
            detected=detected_terms(signals, "vault_erc4626", "vault_accounting_risk"),
            why_it_matters="Small rounding mistakes in conversion functions can compound into unfair share issuance, redemption drift, or stranded assets.",
            historical_pattern_similarity="Maps to historical arithmetic and accounting mismatch classes where precision assumptions failed.",
            defensive_checks=["small amount tests", "decimals normalization", "mulDiv/precision review", "conversion reversibility"],
            suggested_test="Fuzz assets and shares across small, large, and decimal-edge values and assert conversion error stays within documented bounds.",
        )
    if (strategy_terms or meaningful_pricing_terms or has_any(signals, "vault_accounting_risk", ["externalBalance"])) and not (coverage["donation_inflation"] or coverage["oracle_pricing"] or coverage["strategy_loss"]):
        add_gap(
            gaps,
            "High readiness gap",
            "totalAssets external dependency without manipulation-resistance tests",
            "totalAssets appears connected to external strategy, pricing, or balance assumptions without visible manipulation-resistance test coverage.",
            "Test totalAssets under donated assets, mocked strategy gain/loss, and mocked stale or bounded pricing where relevant.",
            ["totalAssets", "strategy-accounting", "oracle-risk"],
            priority="High",
            detected=sorted(set(strategy_terms + meaningful_pricing_terms + detected_terms(signals, "vault_accounting"))),
            why_it_matters="Vault share value often depends on totalAssets; external balances, strategies, or prices can make the accounting view drift from user expectations.",
            historical_pattern_similarity="Maps to Harvest/Yearn-style vault readiness classes where pricing or strategy state influenced share accounting.",
            defensive_checks=["donation tests", "mock strategy gain/loss", "stale/bounded oracle tests", "share price drift checks"],
            suggested_test="Mock external strategy or price state and assert totalAssets, share price, and withdrawal accounting remain within documented policy.",
        )
    if strategy_terms and not coverage["strategy_loss"]:
        add_gap(
            gaps,
            "High readiness gap",
            "Strategy accounting without gain/loss tests",
            "Strategy, harvest, debt, gain, loss, or migration signals were detected without visible strategy lifecycle tests.",
            "Add tests for strategy report, harvest, gain, loss, debt changes, withdrawals, and migration or emergency exit if present.",
            ["strategy-accounting", "gain-loss", "vault-lifecycle"],
            priority="High",
            detected=strategy_terms,
            why_it_matters="Strategy vaults can look solvent until gain/loss, debt, or migration paths update accounting in unexpected ways.",
            historical_pattern_similarity="Maps to strategy debt/gain/loss accounting readiness classes.",
            defensive_checks=["gain report", "loss report", "debt update", "withdrawFromStrategy", "strategy migration"],
            suggested_test="Use a local mock strategy that reports gain and loss, then assert totalAssets and share accounting follow documented policy.",
        )
    if withdrawal_terms and not coverage["withdrawal_lifecycle"]:
        add_gap(
            gaps,
            "High readiness gap",
            "Withdrawal queue/cooldown without lifecycle tests",
            "Withdrawal queue, cooldown, epoch, pending withdrawal, or liquidity-buffer signals were detected without visible lifecycle tests.",
            "Add tests for request, cooldown/epoch movement, claim, cancellation, and insufficient-liquidity behavior.",
            ["withdrawal-queue", "liquidity", "vault-lifecycle"],
            priority="High",
            detected=withdrawal_terms,
            why_it_matters="Delayed withdrawals create state machines; audit preparation should prove shares and assets are conserved through each state.",
            historical_pattern_similarity="Maps to vault lifecycle readiness classes where exit accounting or liquidity assumptions can break.",
            defensive_checks=["requestWithdraw", "claimWithdraw", "cancelWithdraw", "cooldown", "available liquidity"],
            suggested_test="Test the full withdrawal lifecycle and assert shares/assets are conserved across request, cooldown, claim, and cancellation.",
        )
    if (has_meaningful_oracle_signal(signals) or has_meaningful_vault_pricing_signal(signals)) and not (coverage["oracle_pricing"] and oracle_controls):
        add_gap(
            gaps,
            "High readiness gap",
            "Oracle-dependent vault without stale-price or bounds tests",
            "Oracle, price-feed, pool-price, reserve, TWAP, or LP pricing signals were detected without enough stale-price, bounds, or sanity-check coverage.",
            "Add local mock price tests for stale rounds, decimals normalization, price bounds, and fallback behavior.",
            ["oracle-risk", "vault-pricing", "pool-price"],
            priority="High",
            detected=meaningful_pricing_terms,
            why_it_matters="Vaults that price assets, LP tokens, or strategies through external sources need explicit assumptions around stale, spot, and bounded prices.",
            historical_pattern_similarity="Maps to historical vault/oracle and pool-price manipulation readiness classes.",
            defensive_checks=["stale price rejection", "decimals normalization", "TWAP/sanity check", "bounds", "oracle setter roles"],
            suggested_test="Use local mock oracles/pools to test stale, out-of-bounds, decimals, and spot-price scenarios without live-chain calls.",
        )
    if fee_terms and not coverage["fee"]:
        add_gap(
            gaps,
            "Medium readiness gap",
            "Fee logic without fee accounting tests",
            "Fee terms were detected without visible tests for fee accounting, recipient balances, or conservation around fee paths.",
            "Add deposit, withdrawal, management, and performance fee tests where relevant.",
            ["fee-accounting", "vault-accounting"],
            priority="Medium",
            detected=fee_terms,
            why_it_matters="Fee logic changes share issuance, redemption value, and treasury balances; missing tests make audit review slower and riskier.",
            historical_pattern_similarity="Maps to accounting mismatch classes where protocol fees changed conservation assumptions.",
            defensive_checks=["fee bounds", "recipient accounting", "share conservation", "rounding with fees"],
            suggested_test="Assert user shares, treasury shares/assets, and totalAssets remain consistent before and after fee-bearing operations.",
        )
    if admin_terms and not role_covered:
        add_gap(
            gaps,
            "Medium readiness gap",
            "Admin setters without role-boundary tests",
            "Vault admin setter or emergency-control signals were detected without visible unauthorized-call or role-boundary coverage.",
            "Add unauthorized-call tests for every setter, strategy/oracle update, fee update, limit change, rescue, sweep, pause, and upgrade path.",
            ["access-control-review", "vault-admin", "operational-security"],
            priority="Medium",
            detected=admin_terms,
            why_it_matters="Vault owners or roles can often change pricing, strategies, fees, limits, and emergency behavior; boundaries should be explicit before audit.",
            historical_pattern_similarity="Maps to privileged control and operational risk readiness classes.",
            defensive_checks=["unauthorized-call tests", "role documentation", "timelock/multisig assumptions", "setter bounds"],
            suggested_test="For each admin function, assert an unprivileged caller reverts and the authorized role changes only the documented state.",
        )
    if has_any(signals, "vault_admin_ops", ["pause", "unpause", "emergencyWithdraw", "emergencyExit"]) and not coverage["emergency_pause"]:
        add_gap(
            gaps,
            "Medium readiness gap",
            "Pause/emergency controls without operational tests",
            "Pause or emergency signals were detected without visible tests for blocked flows and documented recovery behavior.",
            "Add tests showing pause/emergency controls block risky flows and preserve documented exit or recovery paths.",
            ["pause", "emergency-controls", "vault-operations"],
            priority="Medium",
            detected=detected_terms(signals, "vault_admin_ops"),
            why_it_matters="Emergency controls are launch-critical; they should behave predictably under stress without bypassing accounting assumptions.",
            historical_pattern_similarity="Maps to operational readiness classes where emergency behavior changes core state transitions.",
            defensive_checks=["pause blocks deposit", "pause blocks withdraw/redeem if intended", "emergency exit behavior", "role boundary"],
            suggested_test="Assert pause and emergency states block or allow each vault flow exactly as documented.",
        )
    if upgrade_terms and not upgrade_covered:
        add_gap(
            gaps,
            "Medium readiness gap",
            "Upgradeable vault without initializer/upgrade tests",
            "Upgradeable/proxy signals were detected without visible initializer, reinitializer, storage, or upgrade authorization coverage.",
            "Add initializer-once, unauthorized-upgrade, storage layout, and post-upgrade accounting tests.",
            ["upgradeability", "initializer", "proxy-review"],
            priority="Medium",
            detected=upgrade_terms,
            why_it_matters="Upgradeable vaults combine accounting risk with implementation risk; initialization and authorization gaps are common audit blockers.",
            historical_pattern_similarity="Maps to initialization and upgrade boundary readiness classes.",
            defensive_checks=["initializer can run once", "upgrade authorization", "storage layout notes", "post-upgrade invariant"],
            suggested_test="Assert unauthorized callers cannot initialize or upgrade and that accounting invariants hold after a local upgrade simulation.",
        )

    total = sum(int(category["score"]) for category in score.values())
    total = max(0, min(100, total))
    next_steps = recommended_next_steps(gaps, "vault")
    return total, score, gaps, next_steps


def compute_readiness_score(
    root: Path,
    classified: ClassifiedFiles,
    contents: dict[Path, str],
    signals: dict[str, dict[str, object]],
    test_readiness: dict[str, object],
    protocol_type: str,
) -> tuple[int, dict[str, dict[str, object]], list[ReadinessGap], list[str]]:
    if protocol_type == "vault":
        return compute_vault_readiness_score(root, classified, contents, signals, test_readiness)

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
        steps.append("Add convertToShares/convertToAssets rounding tests and preview/action equivalence checks for ERC4626-like flows.")
    if "strategy" in gap_titles:
        steps.append("Add local mock strategy tests for gain, loss, debt, harvest, and migration accounting.")
    if "withdrawal queue" in gap_titles or "cooldown" in gap_titles:
        steps.append("Add withdrawal lifecycle tests for request, cooldown, claim, cancellation, and liquidity-buffer boundaries.")
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


def infer_affected_files(gap: ReadinessGap, signals: dict[str, dict[str, object]]) -> list[str]:
    files: set[str] = set(gap.affected_files)
    detected = set(gap.detected)
    for data in signals.values():
        terms = set(data.get("terms", []))
        if detected and not (detected & terms):
            continue
        for path in data.get("files", [])[:10]:
            files.add(str(path))
    return sorted(files)[:10]


def apply_finding_metadata(
    gaps: list[ReadinessGap],
    signals: dict[str, dict[str, object]],
    protocol_type: str,
) -> list[ReadinessGap]:
    seen: dict[str, int] = {}
    for gap in gaps:
        if not gap.id:
            gap.id, gap.category = finding_identity(gap.title, gap.tags)
        seen[gap.id] = seen.get(gap.id, 0) + 1
        if seen[gap.id] > 1 and gap.id.endswith("-900"):
            prefix = gap.id.rsplit("-", 1)[0]
            gap.id = f"{prefix}-{900 + seen[gap.id]:03d}"
        gap.affected_files = infer_affected_files(gap, signals)
        gap.fingerprint = compute_finding_fingerprint(gap, protocol_type)
    return gaps


def apply_suppressions(
    gaps: list[ReadinessGap],
    config: dict[str, object],
) -> tuple[list[ReadinessGap], list[ReadinessGap]]:
    suppressions = config_suppressions(config)
    active: list[ReadinessGap] = []
    suppressed: list[ReadinessGap] = []
    for gap in gaps:
        suppression = suppressions.get(gap.id)
        if suppression and gap.suppressible:
            gap.suppression = suppression
            suppressed.append(gap)
        else:
            active.append(gap)
    return active, suppressed


def finding_to_dict(gap: ReadinessGap) -> dict[str, object]:
    data: dict[str, object] = {
        "id": gap.id,
        "fingerprint": gap.fingerprint,
        "title": gap.title,
        "category": gap.category,
        "priority": gap.priority,
        "severity": gap.severity,
        "confidence": gap.confidence,
        "detected_signals": gap.detected,
        "affected_files": gap.affected_files,
        "why_it_matters": gap.why_it_matters,
        "historical_pattern_similarity": gap.historical_pattern_similarity,
        "recommended_defensive_checks": gap.defensive_checks,
        "suggested_tests": [gap.suggested_test] if gap.suggested_test else [gap.recommendation],
        "recommendation": gap.recommendation,
        "detail": gap.detail,
        "tags": gap.tags,
        "suppressible": gap.suppressible,
    }
    if gap.suppression:
        data["suppression"] = gap.suppression
    return data


def gap_table_rows(gaps: list[ReadinessGap]) -> list[list[str]]:
    rows = [["ID", "Priority", "Category", "Title"]]
    for gap in gaps:
        rows.append([gap.id, gap.priority, gap.category, gap.title])
    return rows


def baseline_finding_dict(gap: ReadinessGap) -> dict[str, object]:
    return {
        "id": gap.id,
        "title": gap.title,
        "category": gap.category,
        "priority": gap.priority,
        "severity": gap.severity,
        "confidence": gap.confidence,
        "fingerprint": gap.fingerprint,
        "affected_files": gap.affected_files,
        "tags": gap.tags,
    }


def build_baseline(
    root: Path,
    protocol_type: str,
    score: int,
    gaps: list[ReadinessGap],
    suppressed_gaps: list[ReadinessGap],
) -> dict[str, object]:
    return {
        "tool": "Arkheionx Pre-Audit Scanner",
        "version": VERSION,
        "fingerprint_version": FINGERPRINT_VERSION,
        "generated_at": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "repo_root": display_path(root),
        "protocol_type": protocol_type,
        "score": score,
        "score_band": score_band(score),
        "findings": [baseline_finding_dict(gap) for gap in gaps],
        "suppressed_findings": [baseline_finding_dict(gap) for gap in suppressed_gaps],
    }


def write_baseline(path: Path, baseline: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(baseline, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_baseline(path: Path) -> tuple[dict[str, object] | None, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except (OSError, json.JSONDecodeError) as exc:
        return None, f"Could not load Arkheionx baseline `{display_path(path)}`: {exc}"


def previous_finding_to_current_shape(item: dict[str, object]) -> dict[str, object]:
    return {
        "id": item.get("id", ""),
        "fingerprint": item.get("fingerprint", ""),
        "title": item.get("title", ""),
        "category": item.get("category", ""),
        "priority": item.get("priority", ""),
        "severity": item.get("severity", ""),
        "confidence": item.get("confidence", ""),
        "affected_files": item.get("affected_files", []),
        "tags": item.get("tags", []),
    }


def diff_counts(diff_data: dict[str, object]) -> dict[str, int]:
    return {
        "new": len(diff_data.get("new", [])),
        "resolved": len(diff_data.get("resolved", [])),
        "unchanged": len(diff_data.get("unchanged", [])),
        "changed": len(diff_data.get("changed", [])),
        "suppressed": len(diff_data.get("suppressed_findings", [])),
    }


def empty_diff_data() -> dict[str, object]:
    return {
        "baseline_path": "",
        "new": [],
        "resolved": [],
        "unchanged": [],
        "changed": [],
        "suppressed_findings": [],
        "counts": {"new": 0, "resolved": 0, "unchanged": 0, "changed": 0, "suppressed": 0},
        "warnings": [],
    }


def compare_findings(
    baseline_path: Path,
    previous_baseline: dict[str, object],
    current_gaps: list[ReadinessGap],
    suppressed_gaps: list[ReadinessGap],
) -> dict[str, object]:
    previous_items = [
        previous_finding_to_current_shape(item)
        for item in previous_baseline.get("findings", [])
        if isinstance(item, dict)
    ]
    current_items = [finding_to_dict(gap) for gap in current_gaps]

    previous_by_fp = {str(item.get("fingerprint", "")): item for item in previous_items if item.get("fingerprint")}
    current_by_fp = {str(item.get("fingerprint", "")): item for item in current_items if item.get("fingerprint")}
    matched_prev: set[str] = set()
    matched_curr: set[str] = set()
    unchanged: list[dict[str, object]] = []
    changed: list[dict[str, object]] = []

    for fingerprint, current in current_by_fp.items():
        previous = previous_by_fp.get(fingerprint)
        if not previous:
            continue
        matched_prev.add(fingerprint)
        matched_curr.add(fingerprint)
        if previous.get("title") != current.get("title") or previous.get("priority") != current.get("priority"):
            changed.append({"previous": previous, "current": current})
        else:
            unchanged.append(current)

    unmatched_previous = [item for item in previous_items if item.get("fingerprint") not in matched_prev]
    unmatched_current = [item for item in current_items if item.get("fingerprint") not in matched_curr]
    changed_prev_ids: set[int] = set()
    changed_curr_ids: set[int] = set()
    for current_index, current in enumerate(unmatched_current):
        for previous_index, previous in enumerate(unmatched_previous):
            if previous_index in changed_prev_ids:
                continue
            if previous.get("id") == current.get("id"):
                changed.append({"previous": previous, "current": current})
                changed_prev_ids.add(previous_index)
                changed_curr_ids.add(current_index)
                break

    new = [item for index, item in enumerate(unmatched_current) if index not in changed_curr_ids]
    resolved = [item for index, item in enumerate(unmatched_previous) if index not in changed_prev_ids]
    diff_data: dict[str, object] = {
        "baseline_path": display_path(baseline_path),
        "new": new,
        "resolved": resolved,
        "unchanged": unchanged,
        "changed": changed,
        "suppressed_findings": [finding_to_dict(gap) for gap in suppressed_gaps],
        "warnings": [],
    }
    diff_data["counts"] = diff_counts(diff_data)
    return diff_data


def render_diff_markdown(diff_data: dict[str, object]) -> list[str]:
    lines = [
        "## Baseline Diff",
        "",
    ]
    baseline_path = diff_data.get("baseline_path", "")
    if baseline_path:
        lines.append(f"Compared against: `{baseline_path}`")
    else:
        lines.append("No baseline was provided for this run.")
    lines.append("")
    counts = diff_data.get("counts", {})
    lines.append(markdown_table([
        ["Status", "Count"],
        ["New readiness gaps", str(counts.get("new", 0))],
        ["Resolved readiness gaps", str(counts.get("resolved", 0))],
        ["Unchanged readiness gaps", str(counts.get("unchanged", 0))],
        ["Changed readiness gaps", str(counts.get("changed", 0))],
        ["Suppressed readiness gaps", str(counts.get("suppressed", 0))],
    ]))
    lines.append("")

    sections = [
        ("New readiness gaps", diff_data.get("new", [])),
        ("Resolved readiness gaps", diff_data.get("resolved", [])),
        ("Unchanged readiness gaps", diff_data.get("unchanged", [])),
    ]
    for heading, items in sections:
        lines.append(f"### {heading}")
        lines.append("")
        if items:
            for item in items:
                lines.append(f"- `{item.get('id', '')}` - {item.get('title', '')}")
        else:
            lines.append("- None.")
        lines.append("")

    changed = diff_data.get("changed", [])
    lines.append("### Changed readiness gaps")
    lines.append("")
    if changed:
        for item in changed:
            current = item.get("current", {}) if isinstance(item, dict) else {}
            previous = item.get("previous", {}) if isinstance(item, dict) else {}
            lines.append(
                f"- `{current.get('id', previous.get('id', ''))}` - {previous.get('title', '')} -> {current.get('title', '')}"
            )
    else:
        lines.append("- None.")
    lines.append("")
    return lines


def write_diff_report(path: Path, diff_data: dict[str, object]) -> None:
    lines = ["# Arkheionx Baseline Diff Report", ""]
    lines.extend(render_diff_markdown(diff_data))
    lines.extend(
        [
            "## Safety Note",
            "",
            "This diff compares local/static readiness findings. It is not a formal audit and does not confirm vulnerabilities.",
        ]
    )
    write_markdown(path, lines)


def sarif_level(gap: ReadinessGap) -> str:
    text = f"{gap.priority} {gap.severity}".lower()
    if "critical" in text:
        return "error"
    if "high" in text or "medium" in text:
        return "warning"
    return "note"


def sarif_location(gap: ReadinessGap, root: Path) -> dict[str, object]:
    uri = gap.affected_files[0] if gap.affected_files else ("README.md" if (root / "README.md").exists() else ".")
    return {
        "physicalLocation": {
            "artifactLocation": {"uri": uri, "uriBaseId": "%SRCROOT%"},
            "region": {"startLine": 1},
        }
    }


def finding_to_sarif_rule(gap: ReadinessGap) -> dict[str, object]:
    help_text = "\n".join(f"- {check}" for check in (gap.defensive_checks or [gap.recommendation]))
    return {
        "id": gap.id,
        "name": normalize_for_fingerprint(gap.title).replace(" ", "-")[:80],
        "shortDescription": {"text": gap.title},
        "fullDescription": {"text": gap.detail},
        "help": {
            "text": "Defensive readiness checks:\n" + help_text,
            "markdown": "Defensive readiness checks:\n" + help_text,
        },
        "properties": {
            "category": gap.category,
            "tags": gap.tags,
            "readiness_gap": True,
            "not_formal_audit": True,
            "defensive_only": True,
        },
    }


def finding_to_sarif_result(gap: ReadinessGap, root: Path) -> dict[str, object]:
    return {
        "ruleId": gap.id,
        "level": sarif_level(gap),
        "message": {
            "text": f"{gap.title}: {gap.recommendation} This is a pre-audit readiness gap, not a confirmed vulnerability."
        },
        "locations": [sarif_location(gap, root)],
        "partialFingerprints": {
            "arkheionxFingerprint": gap.fingerprint,
        },
        "properties": {
            "priority": gap.priority,
            "confidence": gap.confidence,
            "category": gap.category,
            "historical_pattern_similarity": gap.historical_pattern_similarity,
            "suggested_tests": [gap.suggested_test] if gap.suggested_test else [gap.recommendation],
            "tags": gap.tags,
            "arkheionx_kind": "pre-audit-readiness",
            "readiness_gap": True,
            "not_a_vulnerability_confirmation": True,
            "not_formal_audit": True,
        },
    }


def build_sarif_report(
    root: Path,
    protocol_type: str,
    score: int,
    gaps: list[ReadinessGap],
    suppressed_gaps: list[ReadinessGap],
    diff_data: dict[str, object] | None,
) -> dict[str, object]:
    rules_by_id: dict[str, dict[str, object]] = {}
    for gap in gaps:
        rules_by_id.setdefault(gap.id, finding_to_sarif_rule(gap))
    run_properties: dict[str, object] = {
        "protocol_type": protocol_type,
        "score": score,
        "score_band": score_band(score),
        "suppressed_count": len(suppressed_gaps),
        "suppressed_finding_ids": [gap.id for gap in suppressed_gaps],
        "not_formal_audit": True,
        "defensive_only": True,
    }
    if diff_data:
        run_properties["diff_counts"] = diff_data.get("counts", {})
        run_properties["baseline_path"] = diff_data.get("baseline_path", "")
    return {
        "version": "2.1.0",
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "Arkheionx Pre-Audit Scanner",
                        "informationUri": "https://github.com/Yudis-bit/DeFi-Exploit-PoCs",
                        "semanticVersion": VERSION,
                        "rules": list(rules_by_id.values()),
                    }
                },
                "originalUriBaseIds": {
                    "%SRCROOT%": {"uri": "file://./"},
                },
                "results": [finding_to_sarif_result(gap, root) for gap in gaps],
                "properties": run_properties,
            }
        ],
    }


def write_sarif_report(path: Path, sarif: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(sarif, indent=2, sort_keys=True) + "\n", encoding="utf-8")


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
        add("convertToShares/convertToAssets consistency", "vault", "Conversion functions should be mutually consistent within documented rounding across supply states.")
        add("share price donation resistance", "vault", "Donations, low supply, and external balances should not let one actor distort share value unexpectedly.")
        add("fee accounting conservation", "vault", "Fees should be bounded, documented, and unable to overcharge beyond configured limits.")
        add("strategy balance drift handling", "vault", "Strategy gains, losses, and withdrawals should remain reflected in accounting assumptions.")
        add("withdrawal lifecycle conservation", "vault", "Queued or delayed withdrawals should conserve shares/assets through request, cooldown, claim, and cancellation.")
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
    vault_test_coverage: dict[str, object],
    registry_metadata: dict[str, object],
    historical_patterns: list[HistoricalPattern],
    score: int,
    score_breakdown: dict[str, dict[str, object]],
    gaps: list[ReadinessGap],
    suppressed_gaps: list[ReadinessGap],
    invariants: list[dict[str, str]],
    next_steps: list[str],
    skeleton_path: Path | None,
    generated_outputs: dict[str, str],
    config_warnings: list[str],
    additional_search_tags: list[str],
    max_top_gaps: int,
    diff_data: dict[str, object] | None,
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

    top_gaps = top_findings(gaps, max_top_gaps)
    counts = finding_counts(gaps, suppressed_gaps)

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
    lines.append(f"- Active readiness gaps: `{counts['total_readiness_gaps']}`")
    lines.append(f"- Suppressed readiness gaps: `{counts['suppressed']}`")
    lines.append("- Top readiness gaps:")
    for gap in top_gaps or [ReadinessGap("Informational", "No major automated readiness gaps detected", "Manual review is still required.", "Proceed to manual review and formal audit planning.", ["manual-review"], id="ARK-GEN-000", category="manual-review")]:
        lines.append(f"  - **{gap.id} ({gap.priority}):** {gap.title} - {gap.recommendation}")
    lines.append("- Top recommended actions:")
    for step in next_steps[:5]:
        lines.append(f"  - {step}")
    lines.append("")
    if config_warnings:
        lines.append("## Configuration Warnings")
        lines.append("")
        for warning in config_warnings:
            lines.append(f"- {warning}")
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
    lines.append("## Top Readiness Gaps")
    lines.append("")
    if top_gaps:
        lines.append(markdown_table(gap_table_rows(top_gaps)))
    else:
        lines.append("No active automated readiness gaps were detected. Manual review is still required.")
    lines.append("")
    if diff_data:
        lines.extend(render_diff_markdown(diff_data))
    lines.append("## Risk Signal Summary")
    lines.append("")
    for category in [
        "vault_erc4626",
        "vault_accounting",
        "vault_accounting_risk",
        "vault_strategy",
        "vault_pricing",
        "vault_withdrawal_liquidity",
        "vault_admin_ops",
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
    if protocol_type == "vault":
        lines.append("## Vault Rule Pack Coverage")
        lines.append("")
        lines.append("The v0.2.0 vault rule pack checks ERC4626-like share accounting, totalAssets assumptions, conversion rounding, fee logic, strategies, withdrawal lifecycle, oracle/pricing assumptions, admin controls, and pause/emergency behavior.")
        lines.append("")
        coverage = vault_test_coverage.get("coverage", {})
        matched = vault_test_coverage.get("matched_terms", {})
        rows = [["Vault check", "Covered", "Matched terms"]]
        for key in sorted(coverage):
            rows.append(
                [
                    key.replace("_", " "),
                    "yes" if coverage[key] else "no",
                    ", ".join(matched.get(key, [])) or "-",
                ]
            )
        lines.append(markdown_table(rows))
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
    lines.append("## All Readiness Gaps")
    lines.append("")
    if gaps:
        for gap in gaps:
            lines.append(f"### {gap.id} - {gap.title}")
            lines.append("")
            lines.append(f"- Priority: `{gap.priority}`")
            lines.append(f"- Confidence: `{gap.confidence}`")
            lines.append(f"- Category: `{gap.category}`")
            lines.append("")
            lines.append("Detected signals:")
            if gap.detected:
                for term in gap.detected[:20]:
                    lines.append(f"- `{term}`")
            else:
                lines.append("- scanner signal")
            if gap.affected_files:
                lines.append("")
                lines.append("Affected files:")
                for path in gap.affected_files[:10]:
                    lines.append(f"- `{path}`")
            lines.append("")
            lines.append("What was detected:")
            lines.append("")
            lines.append(gap.detail)
            lines.append("")
            if gap.why_it_matters:
                lines.append("Why it matters:")
                lines.append("")
                lines.append(gap.why_it_matters)
                lines.append("")
            if gap.historical_pattern_similarity:
                lines.append("Historical pattern similarity:")
                lines.append("")
                lines.append(gap.historical_pattern_similarity)
                lines.append("")
            if gap.defensive_checks:
                lines.append("Recommended defensive checks:")
                lines.append("")
                for check in gap.defensive_checks:
                    lines.append(f"- {check}")
                lines.append("")
            lines.append("Suggested tests:")
            lines.append("")
            lines.append(f"- {gap.suggested_test or gap.recommendation}")
            lines.append("")
            lines.append(f"Search tags: `{', '.join(gap.tags)}`")
            lines.append("")
    else:
        lines.append("- No major automated gaps detected. This does not prove safety and should be followed by manual review.")
    lines.append("")
    lines.append("## Suppressed Readiness Gaps")
    lines.append("")
    if suppressed_gaps:
        lines.append("Suppressed findings are not deleted. They are shown here for review and should be revisited before launch.")
        lines.append("")
        lines.append(markdown_table(gap_table_rows(suppressed_gaps)))
        lines.append("")
        for gap in suppressed_gaps:
            reason = gap.suppression.get("reason", "No reason provided.")
            expires = gap.suppression.get("expires", "")
            lines.append(f"- **{gap.id} - {gap.title}:** {reason}" + (f" Expires: `{expires}`." if expires else ""))
    else:
        lines.append("No readiness gaps were suppressed in this run.")
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
    lines.append("## Generated Issue Checklist")
    lines.append("")
    checklist_output = generated_outputs.get("issue_checklist", "")
    if checklist_output:
        lines.append(f"- Generated checklist: `{checklist_output}`")
        lines.append("- Use this as a copyable GitHub Issue body or as a remediation tracker.")
    else:
        lines.append("- No issue checklist file was requested in this run.")
        lines.append("- To generate one: `python3 scripts/pre_audit_scan.py --root . --issue-checklist-output ARKHEIONX_ISSUE_CHECKLIST.md`")
    lines.append("")
    lines.append("## GitHub Action Outputs")
    lines.append("")
    for label, path in generated_outputs.items():
        if path:
            lines.append(f"- {label.replace('_', ' ').title()}: `{path}`")
    if not any(generated_outputs.values()):
        lines.append("- No additional GitHub Action output files were requested.")
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
    search_tags = sorted(set(search_tags + additional_search_tags))
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
    vault_test_coverage: dict[str, object],
    historical_patterns: list[HistoricalPattern],
    gaps: list[ReadinessGap],
    suppressed_gaps: list[ReadinessGap],
    invariants: list[dict[str, str]],
    next_steps: list[str],
    generated_outputs: dict[str, str],
    config_warnings: list[str],
    diff_data: dict[str, object] | None,
) -> dict[str, object]:
    counts = finding_counts(gaps, suppressed_gaps)
    findings = [finding_to_dict(item) for item in gaps]
    suppressed_findings = [finding_to_dict(item) for item in suppressed_gaps]
    return {
        "tool": "Arkheionx Pre-Audit Scanner",
        "version": VERSION,
        "fingerprint_version": FINGERPRINT_VERSION,
        "generated_at": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "repo_root": display_path(root),
        "protocol_type": protocol_type,
        "protocol_confidence": protocol_confidence,
        "score": score,
        "score_band": score_band(score),
        "score_breakdown": score_breakdown,
        "summary": counts,
        "files_scanned": {
            "solidity_sources": [rel(p, root) for p in classified.solidity_sources],
            "solidity_tests": [rel(p, root) for p in classified.solidity_tests],
            "docs": [rel(p, root) for p in classified.docs],
            "configs": [rel(p, root) for p in classified.configs],
            "workflows": [rel(p, root) for p in classified.workflows],
        },
        "signals": signals,
        "vault_rule_pack": vault_test_coverage,
        "historical_patterns": [item.__dict__ for item in historical_patterns],
        "findings": findings,
        "suppressed_findings": suppressed_findings,
        "readiness_gaps": findings,
        "suggested_invariants": invariants,
        "generated_outputs": generated_outputs,
        "diff": diff_data or empty_diff_data(),
        "next_steps": next_steps,
        "config_warnings": config_warnings,
        "disclaimer": DISCLAIMER,
    }


def generate_json_report(path: Path, report: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def generate_summary_output(
    path: Path,
    score: int,
    protocol_type: str,
    gaps: list[ReadinessGap],
    suppressed_gaps: list[ReadinessGap],
    generated_outputs: dict[str, str],
    next_steps: list[str],
    max_top_gaps: int,
    diff_data: dict[str, object] | None,
) -> None:
    counts = finding_counts(gaps, suppressed_gaps)
    lines = [
        "# Arkheionx Pre-Audit Readiness Summary",
        "",
        f"Score: **{score}/100** - {score_band(score)}",
        f"Protocol type: `{protocol_type}`",
        f"Top readiness gaps: `{len(top_findings(gaps, max_top_gaps))}`",
        "",
        "## Top Gaps",
        "",
    ]
    if gaps:
        lines.append(markdown_table([["ID", "Priority", "Title"]] + [[g.id, g.priority, g.title] for g in top_findings(gaps, max_top_gaps)]))
    else:
        lines.append("No active automated readiness gaps were detected. Manual review is still required.")
    lines.extend(
        [
            "",
            "## Counts",
            "",
            f"- Critical: `{counts['critical']}`",
            f"- High: `{counts['high']}`",
            f"- Medium: `{counts['medium']}`",
            f"- Low: `{counts['low']}`",
            f"- Suppressed: `{counts['suppressed']}`",
        ]
    )
    if diff_data:
        counts_diff = diff_data.get("counts", {})
        lines.extend(
            [
                "",
                "## Baseline Diff",
                "",
                f"- New readiness gaps: `{counts_diff.get('new', 0)}`",
                f"- Resolved readiness gaps: `{counts_diff.get('resolved', 0)}`",
                f"- Unchanged readiness gaps: `{counts_diff.get('unchanged', 0)}`",
                f"- Changed readiness gaps: `{counts_diff.get('changed', 0)}`",
            ]
        )
        if generated_outputs.get("diff_report"):
            lines.append(f"- Diff report: `{generated_outputs['diff_report']}`")
    lines.extend(["", "## Outputs", ""])
    for label, output_path in generated_outputs.items():
        if output_path:
            lines.append(f"- {label.replace('_', ' ').title()}: `{output_path}`")
    lines.extend(["", "## Next Steps", ""])
    for step in next_steps[:5]:
        lines.append(f"- {step}")
    lines.extend(["", "Arkheionx is not a formal audit and not a security guarantee."])
    write_markdown(path, lines)


def generate_comment_output(
    path: Path,
    score: int,
    protocol_type: str,
    gaps: list[ReadinessGap],
    generated_outputs: dict[str, str],
    max_top_gaps: int,
    diff_data: dict[str, object] | None,
) -> None:
    lines = [
        COMMENT_MARKER,
        "",
        "## Arkheionx Pre-Audit Readiness",
        "",
        f"Score: **{score}/100** - {score_band(score)}",
        f"Protocol type: `{protocol_type}`",
        "",
        "Top readiness gaps:",
        "",
    ]
    if gaps:
        lines.append(markdown_table([["ID", "Priority", "Gap"]] + [[g.id, g.priority, g.title] for g in top_findings(gaps, max_top_gaps)]))
    else:
        lines.append("No active automated readiness gaps were detected. Manual review is still recommended.")
    report_path = generated_outputs.get("markdown_report", "")
    checklist_path = generated_outputs.get("issue_checklist", "")
    if report_path or checklist_path:
        lines.append("")
    if report_path:
        lines.append(f"Full report: `{report_path}`")
    if checklist_path:
        lines.append(f"Issue checklist: `{checklist_path}`")
    if diff_data:
        counts_diff = diff_data.get("counts", {})
        lines.extend(
            [
                "",
                "Diff vs baseline:",
                f"- New: `{counts_diff.get('new', 0)}`",
                f"- Resolved: `{counts_diff.get('resolved', 0)}`",
                f"- Unchanged: `{counts_diff.get('unchanged', 0)}`",
                f"- Changed: `{counts_diff.get('changed', 0)}`",
            ]
        )
        if generated_outputs.get("diff_report"):
            lines.append(f"Diff report: `{generated_outputs['diff_report']}`")
    lines.extend(["", "Arkheionx is not a formal audit and not a security guarantee."])
    write_markdown(path, lines)


def generate_issue_checklist(
    path: Path,
    protocol_type: str,
    score: int,
    gaps: list[ReadinessGap],
    diff_data: dict[str, object] | None,
) -> None:
    lines = [
        "# Arkheionx Generated Issue Checklist",
        "",
        "Generated from: pre-audit readiness scan",
        f"Protocol type: `{protocol_type}`",
        f"Score: `{score}/100`",
        "",
    ]

    if diff_data:
        new_ids = {str(item.get("id", "")) for item in diff_data.get("new", []) if isinstance(item, dict)}
        unchanged_ids = {str(item.get("id", "")) for item in diff_data.get("unchanged", []) if isinstance(item, dict)}
        if new_ids:
            lines.extend(["## New Findings Since Baseline", ""])
            for gap in gaps:
                if gap.id in new_ids:
                    lines.append(f"- [ ] {gap.id} - {gap.recommendation}")
            lines.append("")
        if unchanged_ids:
            lines.extend(["## Existing Findings From Baseline", ""])
            for gap in gaps:
                if gap.id in unchanged_ids:
                    lines.append(f"- [ ] {gap.id} - {gap.recommendation}")
            lines.append("")

    groups = [
        ("Critical priority readiness gaps", "critical"),
        ("High priority readiness gaps", "high"),
        ("Medium priority readiness gaps", "medium"),
        ("Low priority readiness gaps", "low"),
    ]
    for heading, keyword in groups:
        group_gaps = [gap for gap in gaps if keyword in f"{gap.priority} {gap.severity}".lower()]
        if diff_data:
            new_ids = {str(item.get("id", "")) for item in diff_data.get("new", []) if isinstance(item, dict)}
            unchanged_ids = {str(item.get("id", "")) for item in diff_data.get("unchanged", []) if isinstance(item, dict)}
            group_gaps = [gap for gap in group_gaps if gap.id not in new_ids and gap.id not in unchanged_ids]
        if not group_gaps:
            continue
        lines.extend([f"## {heading}", ""])
        for gap in group_gaps:
            lines.append(f"- [ ] {gap.id} - {gap.recommendation}")
            suggested = gap.suggested_test or gap.recommendation
            lines.append("  - Suggested tests:")
            lines.append(f"    - {suggested}")
            for check in gap.defensive_checks[:5]:
                lines.append(f"    - {check}")
        lines.append("")

    if diff_data and diff_data.get("resolved"):
        lines.extend(["## Resolved Since Baseline", ""])
        for item in diff_data.get("resolved", []):
            if isinstance(item, dict):
                lines.append(f"- [x] {item.get('id', '')} - {item.get('title', '')}")
        lines.append("")

    documentation_tasks = [
        "Document admin role boundaries.",
        "Document oracle and pricing assumptions.",
        "Document known limitations and formal audit scope.",
    ]
    lines.extend(["## Documentation Tasks", ""])
    for task in documentation_tasks:
        lines.append(f"- [ ] {task}")
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "This checklist is generated from static/local readiness signals. It is not a formal audit.",
        ]
    )
    write_markdown(path, lines)


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

    function invariant_convertToSharesConvertToAssetsConsistency() public {
        // TODO: assert conversion functions are consistent within documented rounding.
    }

    function invariant_sharePriceDonationResistance() public {
        // TODO: assert donations and low-supply states cannot distort share value unexpectedly.
    }

    function invariant_feeAccountingDoesNotCreateValue() public {
        // TODO: assert fees remain bounded and do not create or strand value beyond policy.
    }

    function invariant_strategyLossDoesNotBreakAccounting() public {
        // TODO: assert mocked strategy gain/loss keeps totalAssets and shares consistent.
    }

    function invariant_withdrawalLifecycleConservesShares() public {
        // TODO: assert request, cooldown, claim, and cancel flows conserve shares/assets.
    }

    function invariant_adminCannotBypassAccountingWithoutExplicitTrust() public {
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
    parser.add_argument("--sarif-output", default="", help="Optional SARIF v2.1.0 output path.")
    parser.add_argument("--baseline-output", default="", help="Optional compact baseline JSON output path.")
    parser.add_argument("--compare-baseline", default="", help="Optional previous Arkheionx baseline JSON for diff mode.")
    parser.add_argument("--diff-output", default="", help="Optional standalone Markdown diff report output path.")
    parser.add_argument("--diff-json-output", default="", help="Optional standalone JSON diff output path.")
    parser.add_argument("--summary-output", default="", help="Optional GitHub Actions summary Markdown output path.")
    parser.add_argument("--comment-output", default="", help="Optional pull request comment Markdown output path.")
    parser.add_argument("--issue-checklist-output", default="", help="Optional generated issue checklist Markdown output path.")
    parser.add_argument("--config", default=DEFAULT_CONFIG, help="Optional Arkheionx JSON config path.")
    parser.add_argument("--generate-invariant-skeletons", action="store_true", help="Generate safe Foundry invariant skeletons.")
    parser.add_argument("--fail-on-critical-readiness-gap", action="store_true", help="Exit 2 if critical readiness gaps are detected.")
    parser.add_argument("--fail-on-new-high", action="store_true", help="Exit 2 if diff mode detects new high or critical readiness gaps.")
    parser.add_argument("--fail-score-below", type=int, default=None, help="Exit 2 if readiness score is below this threshold.")
    parser.add_argument("--fail-on-unsuppressed-high", action="store_true", help="Exit 2 if unsuppressed high or critical readiness gaps are present.")
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

    config_path = Path(args.config).expanduser() if args.config else None
    config, config_warnings = load_local_config(config_path, root)
    ignore_paths = config_ignore_paths(config)

    files = collect_files(root)
    if ignore_paths:
        files = [path for path in files if not should_ignore_config_path(path, root, ignore_paths)]
    classified = classify_files(files)
    contents = corpus(files)
    requested_protocol = args.protocol_type
    configured_protocol = config.get("protocol_type")
    if requested_protocol == "auto" and isinstance(configured_protocol, str) and configured_protocol in (set(PROTOCOL_WEIGHTS) | {"generic", "auto"}):
        requested_protocol = configured_protocol
    protocol_type, protocol_confidence, protocol_scores = detect_protocol_type(contents, classified, requested_protocol)
    signal_paths = [
        path
        for path in classified.solidity_sources + classified.solidity_tests + classified.configs
        if not is_placeholder_skeleton(contents.get(path, ""))
    ]
    signals = detect_signals(contents, root, signal_paths or contents.keys())
    test_readiness = detect_test_readiness(contents, classified, root)
    vault_test_coverage = detect_vault_test_coverage(contents, classified)
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
    apply_finding_metadata(gaps, signals, protocol_type)
    gaps, suppressed_gaps = apply_suppressions(gaps, config)
    invariants = suggest_invariants(protocol_type, signals)
    skeleton_path = generate_invariant_skeleton(root) if args.generate_invariant_skeletons else None

    output = resolve_output_path(args.output)
    if output is None:
        print("error: --output cannot be empty", file=sys.stderr)
        return 1
    json_output = resolve_output_path(args.json_output)
    sarif_output = resolve_output_path(args.sarif_output)
    baseline_output = resolve_output_path(args.baseline_output)
    compare_baseline = resolve_output_path(args.compare_baseline)
    diff_output = resolve_output_path(args.diff_output)
    diff_json_output = resolve_output_path(args.diff_json_output)
    summary_output = resolve_output_path(args.summary_output)
    comment_output = resolve_output_path(args.comment_output)
    issue_checklist_output = resolve_output_path(args.issue_checklist_output)
    generated_outputs = {
        "markdown_report": display_path(output),
        "json_report": display_path(json_output) if json_output else "",
        "sarif_report": display_path(sarif_output) if sarif_output else "",
        "summary": display_path(summary_output) if summary_output else "",
        "comment": display_path(comment_output) if comment_output else "",
        "issue_checklist": display_path(issue_checklist_output) if issue_checklist_output else "",
        "baseline": display_path(baseline_output) if baseline_output else "",
        "diff_report": display_path(diff_output) if diff_output else "",
        "diff_json": display_path(diff_json_output) if diff_json_output else "",
    }
    additional_search_tags = config_additional_tags(config)
    max_top_gaps = config_max_top_gaps(config)
    diff_data: dict[str, object] | None = None
    if compare_baseline:
        previous_baseline, baseline_warning = load_baseline(compare_baseline)
        if baseline_warning:
            config_warnings.append(baseline_warning)
            diff_data = empty_diff_data()
            diff_data["baseline_path"] = display_path(compare_baseline)
            diff_data["warnings"] = [baseline_warning]
        elif previous_baseline is not None:
            diff_data = compare_findings(compare_baseline, previous_baseline, gaps, suppressed_gaps)

    generate_report(
        root=root,
        output=output,
        classified=classified,
        protocol_type=protocol_type,
        protocol_confidence=protocol_confidence,
        protocol_scores=protocol_scores,
        signals=signals,
        test_readiness=test_readiness,
        vault_test_coverage=vault_test_coverage,
        registry_metadata=registry_metadata,
        historical_patterns=historical_patterns,
        score=score,
        score_breakdown=score_breakdown,
        gaps=gaps,
        suppressed_gaps=suppressed_gaps,
        invariants=invariants,
        next_steps=next_steps,
        skeleton_path=skeleton_path,
        generated_outputs=generated_outputs,
        config_warnings=config_warnings,
        additional_search_tags=additional_search_tags,
        max_top_gaps=max_top_gaps,
        diff_data=diff_data,
    )

    if issue_checklist_output:
        generate_issue_checklist(issue_checklist_output, protocol_type, score, gaps, diff_data)
    if summary_output:
        generate_summary_output(summary_output, score, protocol_type, gaps, suppressed_gaps, generated_outputs, next_steps, max_top_gaps, diff_data)
    if comment_output:
        generate_comment_output(comment_output, score, protocol_type, gaps, generated_outputs, max_top_gaps, diff_data)
    if baseline_output:
        write_baseline(baseline_output, build_baseline(root, protocol_type, score, gaps, suppressed_gaps))
    if diff_output and diff_data:
        write_diff_report(diff_output, diff_data)
    if diff_json_output and diff_data:
        generate_json_report(diff_json_output, diff_data)
    if sarif_output:
        write_sarif_report(sarif_output, build_sarif_report(root, protocol_type, score, gaps, suppressed_gaps, diff_data))

    if json_output:
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
                vault_test_coverage,
                historical_patterns,
                gaps,
                suppressed_gaps,
                invariants,
                next_steps,
                generated_outputs,
                config_warnings,
                diff_data,
            ),
        )

    critical_gaps = [gap for gap in gaps if gap.severity == "Critical readiness gap"]
    print(f"Arkheionx pre-audit report generated: {output}")
    if json_output:
        print(f"Arkheionx JSON report generated: {json_output}")
    if sarif_output:
        print(f"Arkheionx SARIF report generated: {sarif_output}")
    if baseline_output:
        print(f"Arkheionx baseline generated: {baseline_output}")
    if diff_output:
        print(f"Arkheionx diff report generated: {diff_output}")
    if diff_json_output:
        print(f"Arkheionx diff JSON generated: {diff_json_output}")
    if summary_output:
        print(f"Arkheionx summary generated: {summary_output}")
    if comment_output:
        print(f"Arkheionx PR comment body generated: {comment_output}")
    if issue_checklist_output:
        print(f"Arkheionx issue checklist generated: {issue_checklist_output}")
    if skeleton_path:
        print(f"Arkheionx invariant skeleton generated: {skeleton_path}")
    print(f"Readiness score: {score}/100 ({score_band(score)})")

    if args.fail_on_critical_readiness_gap and critical_gaps:
        print("critical readiness gaps detected; failing because --fail-on-critical-readiness-gap was set", file=sys.stderr)
        return 2
    if args.fail_score_below is not None and score < args.fail_score_below:
        print(
            "Arkheionx readiness threshold failed. This is a pre-audit readiness gate, not a formal vulnerability confirmation.",
            file=sys.stderr,
        )
        print(f"score {score}/100 is below threshold {args.fail_score_below}", file=sys.stderr)
        return 2
    if args.fail_on_unsuppressed_high and any(is_high_or_critical(gap) for gap in gaps):
        print(
            "Arkheionx readiness threshold failed. This is a pre-audit readiness gate, not a formal vulnerability confirmation.",
            file=sys.stderr,
        )
        print("unsuppressed high or critical readiness gaps detected", file=sys.stderr)
        return 2
    if args.fail_on_new_high and diff_data and any(is_high_or_critical(item) for item in diff_data.get("new", [])):
        print(
            "Arkheionx readiness threshold failed. This is a pre-audit readiness gate, not a formal vulnerability confirmation.",
            file=sys.stderr,
        )
        print("new high or critical readiness gaps detected against baseline", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

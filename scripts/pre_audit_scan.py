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
import fnmatch
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


PACKAGE_ROOT = Path(__file__).resolve().parent.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from arkheionx.core.constants import (  # noqa: E402
    ARKHEIONX_GENERATED_CONTENT_MARKERS as SHARED_GENERATED_CONTENT_MARKERS,
)
from arkheionx.core.constants import (  # noqa: E402
    COMMENT_MARKER as SHARED_COMMENT_MARKER,
)
from arkheionx.core.constants import (  # noqa: E402
    DEFAULT_CONFIG as SHARED_DEFAULT_CONFIG,
)
from arkheionx.core.constants import (  # noqa: E402
    DEFAULT_GENERATED_ARTIFACT_IGNORE_PATTERNS as SHARED_GENERATED_ARTIFACT_IGNORE_PATTERNS,
)
from arkheionx.core.constants import (  # noqa: E402
    ISSUE_MARKER_PREFIX as SHARED_ISSUE_MARKER_PREFIX,
)
from arkheionx.config.loader import load_and_validate_config  # noqa: E402
from arkheionx.config.schema import PROTOCOL_TYPES as STABLE_PROTOCOL_TYPES  # noqa: E402
from arkheionx.rules.registry import finding_id_to_rule_pack  # noqa: E402
from arkheionx.version import SCANNER_VERSION, SCHEMA_VERSION as PACKAGE_SCHEMA_VERSION  # noqa: E402


VERSION = SCANNER_VERSION
SCHEMA_VERSION = PACKAGE_SCHEMA_VERSION
FINGERPRINT_VERSION = "0.6.0"
MAX_READ_BYTES = 750_000
KNOWLEDGE_MAP_PATH = PACKAGE_ROOT / "metadata" / "finding_knowledge_map.json"
TEST_PLAN_MAP_PATH = PACKAGE_ROOT / "metadata" / "finding_test_plan_map.json"
DEFAULT_CONFIG = SHARED_DEFAULT_CONFIG
COMMENT_MARKER = SHARED_COMMENT_MARKER
ISSUE_MARKER_PREFIX = SHARED_ISSUE_MARKER_PREFIX
DISCLAIMER = (
    "This is an automated pre-audit readiness report. It is not a formal "
    "audit, does not prove the absence or presence of vulnerabilities, does "
    "not authorize live-target testing, and should only be used on repositories "
    "you own or are authorized to review. A formal audit is recommended before "
    "handling real user funds."
)
ISSUE_DISCLAIMER = (
    "This issue was generated from an Arkheionx pre-audit readiness scan. "
    "It is not a formal audit finding. It does not confirm a vulnerability. "
    "It is a defensive remediation task for authorized repository maintainers."
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
    ".forge",
    ".slither",
    ".venv",
    "__pycache__",
    "lib",
    "node_modules",
    "venv",
    "out",
    "cache",
    "broadcast",
    "artifacts",
    "target",
    "dist",
    "build",
}

DEFAULT_GENERATED_ARTIFACT_IGNORE_PATTERNS = list(SHARED_GENERATED_ARTIFACT_IGNORE_PATTERNS)

ARKHEIONX_GENERATED_CONTENT_MARKERS = list(SHARED_GENERATED_CONTENT_MARKERS)


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

ORACLE_RULE_TERMS = [
    "oracle",
    "priceFeed",
    "latestRoundData",
    "latestAnswer",
    "answer",
    "roundId",
    "answeredInRound",
    "updatedAt",
    "decimals",
    "AggregatorV3Interface",
    "Chainlink",
    "getPrice",
    "consult",
    "twap",
    "spot",
    "getReserves",
    "sqrtPriceX96",
    "observe",
    "pool",
    "reserve0",
    "reserve1",
    "stale",
    "heartbeat",
    "minPrice",
    "maxPrice",
    "bounds",
    "sequencer",
    "fallbackOracle",
    "setOracle",
]

ACCESS_UPGRADE_RULE_TERMS = [
    "onlyOwner",
    "Ownable",
    "AccessControl",
    "DEFAULT_ADMIN_ROLE",
    "role",
    "grantRole",
    "revokeRole",
    "hasRole",
    "admin",
    "owner",
    "operator",
    "guardian",
    "multisig",
    "timelock",
    "setFee",
    "setOracle",
    "setStrategy",
    "setTreasury",
    "pause",
    "unpause",
    "emergencyWithdraw",
    "rescue",
    "sweep",
    "upgradeTo",
    "upgradeToAndCall",
    "UUPSUpgradeable",
    "TransparentUpgradeableProxy",
    "initializer",
    "reinitializer",
    "__gap",
    "implementation",
    "proxy",
]

REENTRANCY_RULE_TERMS = [
    "withdraw",
    "redeem",
    "claim",
    "payout",
    "refund",
    "send",
    "transfer",
    "transferFrom",
    "safeTransfer",
    "call{",
    ".call(",
    "delegatecall",
    "onERC721Received",
    "onERC1155Received",
    "ERC777",
    "callback",
    "flashLoan",
    "executeOperation",
    "nonReentrant",
    "ReentrancyGuard",
    "checks-effects-interactions",
]

REWARD_RULE_TERMS = [
    "stake",
    "unstake",
    "withdraw",
    "reward",
    "rewards",
    "claim",
    "claimReward",
    "rewardPerToken",
    "accumulator",
    "index",
    "emission",
    "emissions",
    "epoch",
    "vesting",
    "lock",
    "cooldown",
    "multiplier",
    "boost",
    "shares",
    "totalStaked",
    "pendingReward",
    "earned",
    "notifyRewardAmount",
]

AMM_RULE_TERMS = [
    "swap",
    "addLiquidity",
    "removeLiquidity",
    "mint",
    "burn",
    "liquidity",
    "reserve",
    "reserve0",
    "reserve1",
    "getReserves",
    "kLast",
    "constant product",
    "x * y",
    "stableswap",
    "invariant",
    "LP",
    "poolToken",
    "totalSupply",
    "balanceOf",
    "getAmountOut",
    "quote",
    "spot price",
    "reserve ratio",
    "TWAP",
    "minOut",
    "deadline",
    "slippage",
    "amountIn",
    "amountOut",
    "balanceBefore",
    "balanceAfter",
    "fee-on-transfer",
    "rebasing",
]

LENDING_RULE_TERMS = [
    "borrow",
    "repay",
    "collateral",
    "debt",
    "healthFactor",
    "health factor",
    "LTV",
    "loan-to-value",
    "loanToValue",
    "liquidationThreshold",
    "collateralFactor",
    "liquidate",
    "liquidation",
    "liquidationBonus",
    "closeFactor",
    "seize",
    "interestIndex",
    "borrowIndex",
    "exchangeRate",
    "utilization",
    "accrueInterest",
    "ratePerSecond",
    "principal",
    "scaledBalance",
    "totalBorrows",
    "totalReserves",
    "cash",
    "available liquidity",
    "keeper",
    "liquidator",
    "guardian",
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
        *ORACLE_RULE_TERMS,
        "setOracle",
    ],
    "oracle_rule_pack": ORACLE_RULE_TERMS,
    "access_control": [
        *ACCESS_UPGRADE_RULE_TERMS,
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
        "upgradeToAndCall",
    ],
    "access_upgrade_rule_pack": ACCESS_UPGRADE_RULE_TERMS,
    "reentrancy_value_flow": [
        *REENTRANCY_RULE_TERMS,
        "staticcall",
    ],
    "reentrancy_rule_pack": REENTRANCY_RULE_TERMS,
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
        *AMM_RULE_TERMS,
        "pool",
        "pair",
        "sqrtPriceX96",
    ],
    "amm_rule_pack": AMM_RULE_TERMS,
    "lending": [
        *LENDING_RULE_TERMS,
        "interestRate",
    ],
    "lending_rule_pack": LENDING_RULE_TERMS,
    "staking_rewards": [
        *REWARD_RULE_TERMS,
    ],
    "reward_rule_pack": REWARD_RULE_TERMS,
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
        "reserve0": 5,
        "reserve1": 5,
        "getReserves": 5,
        "kLast": 4,
        "constant product": 5,
        "stableswap": 5,
        "invariant": 3,
        "liquidity": 3,
        "addLiquidity": 4,
        "removeLiquidity": 4,
        "minOut": 4,
        "slippage": 4,
        "quote": 3,
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
        "interestIndex": 4,
        "borrowIndex": 4,
        "accrueInterest": 4,
        "totalBorrows": 4,
        "totalReserves": 4,
        "liquidationThreshold": 4,
        "collateralFactor": 4,
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
    evidence: list[dict[str, object]] = field(default_factory=list)
    evidence_summary: str = ""
    confidence_reason: str = ""
    detection_sources: list[str] = field(default_factory=list)
    affected_functions: list[str] = field(default_factory=list)
    affected_contracts: list[str] = field(default_factory=list)
    false_positive_notes: str = ""
    negative_evidence: list[dict[str, object]] = field(default_factory=list)


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
    ("AMM invariant assumptions not covered by tests", "ARK-AMM-001", "amm-invariant"),
    ("LP share accounting without mint/burn boundary tests", "ARK-AMM-002", "amm-lp-accounting"),
    ("Spot-price or reserve-price dependency without manipulation-resistance tests", "ARK-AMM-003", "amm-pricing"),
    ("Fee-on-transfer or non-standard token assumptions not documented", "ARK-AMM-004", "amm-token-assumptions"),
    ("Slippage/min-output constraints missing or unclear", "ARK-AMM-005", "amm-slippage"),
    ("Collateral/debt solvency invariant not covered by tests", "ARK-LEND-001", "lending-solvency"),
    ("Liquidation boundary tests missing", "ARK-LEND-002", "lending-liquidation"),
    ("Interest/index accounting not covered by rounding and time-step tests", "ARK-LEND-003", "lending-interest-index"),
    ("Oracle-dependent borrowing/liquidation without stale-price tests", "ARK-LEND-004", "lending-oracle"),
    ("Reserve/cash accounting assumptions not covered", "ARK-LEND-005", "lending-liquidity"),
    ("Liquidation/access-control interaction not documented", "ARK-LEND-006", "lending-access-control"),
    ("Vault accounting lacks visible roundtrip or conservation coverage", "ARK-VLT-009", "vault-accounting"),
    ("Oracle-dependent logic without stale-price tests", "ARK-ORC-001", "oracle-pricing"),
    ("Oracle decimals or normalization not covered by tests", "ARK-ORC-002", "oracle-pricing"),
    ("Spot or reserve-based pricing without manipulation-resistance tests", "ARK-ORC-003", "oracle-pricing"),
    ("Oracle setter/admin path without role-boundary tests", "ARK-ORC-004", "oracle-pricing"),
    ("Missing price bounds or fallback assumptions documentation", "ARK-ORC-005", "oracle-pricing"),
    ("Privileged setters without role-boundary tests", "ARK-ACC-001", "access-control"),
    ("Emergency or rescue functions without documented constraints", "ARK-ACC-002", "access-control"),
    ("Admin role concentration not documented", "ARK-ACC-003", "access-control"),
    ("Upgradeable contract without initializer/upgrade tests", "ARK-UPG-001", "upgradeability-initialization"),
    ("Storage layout or upgrade assumptions not documented", "ARK-UPG-002", "upgradeability-initialization"),
    ("Value flow with external calls needs reentrancy review", "ARK-REENT-001", "reentrancy-value-flow"),
    ("Callback-capable token or receiver path detected", "ARK-REENT-002", "reentrancy-value-flow"),
    ("Claim/refund flow without state-transition tests", "ARK-REENT-003", "reentrancy-value-flow"),
    ("External call path without documented ordering assumptions", "ARK-REENT-004", "reentrancy-value-flow"),
    ("Reward accounting without conservation tests", "ARK-RWD-001", "reward-accounting"),
    ("Accumulator/index logic without precision/rounding tests", "ARK-RWD-002", "reward-accounting"),
    ("Claim flow without double-claim prevention tests", "ARK-RWD-003", "reward-accounting"),
    ("Lock/cooldown reward lifecycle not tested", "ARK-RWD-004", "reward-accounting"),
    ("Emission/admin update assumptions not documented", "ARK-RWD-005", "reward-accounting"),
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


def load_finding_knowledge_map() -> dict[str, dict[str, object]]:
    try:
        payload = json.loads(KNOWLEDGE_MAP_PATH.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    findings = payload.get("findings", {})
    if not isinstance(findings, dict):
        return {}
    return {str(key): value for key, value in findings.items() if isinstance(value, dict)}


def load_finding_test_plan_map() -> dict[str, dict[str, object]]:
    try:
        payload = json.loads(TEST_PLAN_MAP_PATH.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    entries = payload.get("findings", {})
    if not isinstance(entries, dict):
        return {}
    return {str(key): value for key, value in entries.items() if isinstance(value, dict)}


def test_plan_for_id(finding_id: str) -> dict[str, object]:
    return load_finding_test_plan_map().get(finding_id, {})


def mapped_suggested_tests(gap: ReadinessGap) -> list[str]:
    plan = test_plan_for_id(gap.id)
    tests = [str(item) for item in plan.get("suggested_tests", []) if str(item).strip()]
    fallback = gap.suggested_test or gap.recommendation
    if fallback:
        tests.insert(0, fallback)
    seen: set[str] = set()
    deduped: list[str] = []
    for item in tests:
        key = normalize_for_fingerprint(item)
        if key and key not in seen:
            seen.add(key)
            deduped.append(item)
    return deduped


def mapped_invariant_candidates(gap: ReadinessGap) -> list[str]:
    plan = test_plan_for_id(gap.id)
    candidates = [str(item) for item in plan.get("invariant_candidates", []) if str(item).strip()]
    if gap.suggested_test and "invariant" in gap.suggested_test.lower():
        candidates.insert(0, gap.suggested_test)
    seen: set[str] = set()
    deduped: list[str] = []
    for item in candidates:
        key = normalize_for_fingerprint(item)
        if key and key not in seen:
            seen.add(key)
            deduped.append(item)
    return deduped


def related_knowledge_for_id(finding_id: str) -> dict[str, object]:
    knowledge = load_finding_knowledge_map().get(finding_id, {})
    if not knowledge:
        return {
            "finding_map_version": "0.9.0",
            "related_patterns": [],
            "related_pocs": [],
            "suggested_tests": [],
            "related_docs": [],
            "search_terms": [],
        }
    return {
        "finding_map_version": "0.9.0",
        "rule_pack": knowledge.get("rule_pack", ""),
        "related_patterns": knowledge.get("historical_patterns", []),
        "root_causes": knowledge.get("root_causes", []),
        "failed_assumptions": knowledge.get("failed_assumptions", []),
        "broken_invariants": knowledge.get("broken_invariants", []),
        "related_pocs": knowledge.get("related_pocs", []),
        "suggested_tests": knowledge.get("suggested_tests", []),
        "related_docs": knowledge.get("related_docs", []),
        "search_terms": knowledge.get("search_terms", []),
    }


def compact_related_knowledge_lines(finding_id: str) -> list[str]:
    knowledge = related_knowledge_for_id(finding_id)
    patterns = [str(item) for item in knowledge.get("related_patterns", [])[:3]]
    tests = [str(item) for item in knowledge.get("suggested_tests", [])[:3]]
    pocs = [str(item) for item in knowledge.get("related_pocs", [])[:3]]
    docs = [str(item) for item in knowledge.get("related_docs", [])[:3]]
    lines: list[str] = []
    if not any([patterns, tests, pocs, docs]):
        return lines
    lines.append("Related Knowledge:")
    if patterns:
        lines.append(f"- Historical patterns: {', '.join(patterns)}")
    if tests:
        lines.append(f"- Suggested defensive tests: {', '.join(tests)}")
    if pocs:
        lines.append(f"- Related PoCs: {', '.join(pocs)}")
    if docs:
        lines.append(f"- Docs: {', '.join(docs)}")
    return lines


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


def load_local_config(path: Path | None, root: Path) -> tuple[dict[str, object], list[str], list[str], str]:
    result = load_and_validate_config(path, root)
    config = dict(result.normalized_config)
    if result.source:
        config["__config_source"] = result.source
    return config, result.warnings, result.errors, result.source


def config_ignore_paths(config: dict[str, object]) -> list[str]:
    raw = config.get("ignore_paths", [])
    if not isinstance(raw, list):
        return []
    return [str(item) for item in raw if isinstance(item, str)]


def config_scan(config: dict[str, object]) -> dict[str, object]:
    raw = config.get("scan", {})
    scan = raw if isinstance(raw, dict) else {}
    extra_ignore_paths = scan.get("extra_ignore_paths", [])
    extra_ignore_globs = scan.get("extra_ignore_globs", [])
    max_file_size_kb = scan.get("max_file_size_kb")
    return {
        "ignore_generated_artifacts": bool(scan.get("ignore_generated_artifacts", True)),
        "include_generated_artifacts": bool(scan.get("include_generated_artifacts", False)),
        "extra_ignore_paths": [str(item) for item in extra_ignore_paths if isinstance(item, str)]
        if isinstance(extra_ignore_paths, list)
        else [],
        "extra_ignore_globs": [str(item) for item in extra_ignore_globs if isinstance(item, str)]
        if isinstance(extra_ignore_globs, list)
        else [],
        "max_file_size_kb": max_file_size_kb if isinstance(max_file_size_kb, int) and max_file_size_kb > 0 else None,
        "include_tests": bool(scan.get("include_tests", True)),
        "include_docs": bool(scan.get("include_docs", True)),
    }


def config_suppressions(config: dict[str, object]) -> dict[str, dict[str, str]]:
    raw = config.get("suppressions", config.get("suppress_findings", []))
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
            "owner": str(item.get("owner", "")),
            "review_after": str(item.get("review_after", "")),
            "path": str(item.get("path", "")),
        }
    return suppressions


def config_additional_tags(config: dict[str, object]) -> list[str]:
    raw = config.get("additional_search_tags", [])
    if not isinstance(raw, list):
        return []
    return sorted({str(item) for item in raw if isinstance(item, str) and item.strip()})


def config_max_top_gaps(config: dict[str, object]) -> int:
    report = config.get("reports", config.get("report", {}))
    if not isinstance(report, dict):
        return 5
    try:
        value = int(report.get("max_top_gaps", 5))
    except (TypeError, ValueError):
        return 5
    return max(1, min(20, value))


def config_analysis(config: dict[str, object]) -> dict[str, object]:
    raw = config.get("analysis", {})
    analysis = raw if isinstance(raw, dict) else {}
    min_confidence = str(
        analysis.get("min_confidence_for_issue_plan", config.get("min_confidence", "low"))
    ).lower()
    if min_confidence not in {"low", "medium", "high"}:
        min_confidence = "low"
    try:
        max_evidence = int(analysis.get("max_evidence_per_finding", 5))
    except (TypeError, ValueError):
        max_evidence = 5
    return {
        "semantic_lite": bool(analysis.get("semantic_lite", True)),
        "slither": bool(analysis.get("slither", False)),
        "min_confidence_for_issue_plan": min_confidence,
        "downgrade_keyword_only": bool(analysis.get("downgrade_keyword_only", True)),
        "max_evidence_per_finding": max(1, min(20, max_evidence)),
    }


def config_enabled_rule_packs(config: dict[str, object]) -> set[str]:
    raw = config.get("rule_packs", [])
    if not isinstance(raw, list) or not raw:
        return {
            "vault",
            "oracle",
            "access-control",
            "reentrancy-value-flow",
            "rewards",
            "testing",
            "docs",
            "amm",
            "lending",
        }
    return {str(item) for item in raw if isinstance(item, str)}


def filter_gaps_by_rule_packs(gaps: list[ReadinessGap], enabled_rule_packs: set[str]) -> list[ReadinessGap]:
    filtered: list[ReadinessGap] = []
    for gap in gaps:
        family = finding_id_to_rule_pack(gap.id)
        if family == "generic" or family in enabled_rule_packs:
            filtered.append(gap)
    return filtered


def config_summary(
    config: dict[str, object],
    source: str,
    protocol_type: str,
    enabled_rule_packs: set[str],
    analysis_config: dict[str, object],
) -> dict[str, object]:
    return {
        "config_source": source,
        "protocol_type_effective": protocol_type,
        "enabled_rule_packs": sorted(enabled_rule_packs),
        "min_confidence": str(config.get("min_confidence", analysis_config.get("min_confidence_for_issue_plan", "low"))),
        "suppressions_count": len(config_suppressions(config)),
        "output_profile": str(config.get("output_profile", "standard")),
    }


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


def scan_relative_path(path: Path, root: Path) -> str:
    try:
        return rel(path, root)
    except ValueError:
        return path.as_posix()


def path_matches_glob(path: str, pattern: str) -> bool:
    return fnmatch.fnmatchcase(path.lower(), normalize_ignore_path(pattern).lower())


def is_generated_artifact_path(path: Path, root: Path | None = None) -> bool:
    relative = scan_relative_path(path, root) if root else normalize_ignore_path(path.as_posix())
    return any(path_matches_glob(relative, pattern) for pattern in DEFAULT_GENERATED_ARTIFACT_IGNORE_PATTERNS)


def is_potential_generated_artifact_candidate(path: Path, root: Path) -> bool:
    relative = scan_relative_path(path, root)
    if is_generated_artifact_path(path, root):
        return True
    if relative.startswith("reports/") and (path.suffix.lower() in {".md", ".json"} or path.name.lower().endswith(".sarif.json")):
        return True
    if path.name.lower().startswith("arkheionx"):
        return True
    return False


def is_arkheionx_generated_artifact(path: Path, root: Path | None = None, text: str | None = None) -> bool:
    if root and is_generated_artifact_path(path, root):
        return True
    if text is None:
        return False
    lower_text = text.lower()
    return any(marker.lower() in lower_text for marker in ARKHEIONX_GENERATED_CONTENT_MARKERS)


def should_ignore_scan_file(path: Path, root: Path, config: dict[str, object] | None = None) -> bool:
    return ignore_reason_for_scan_file(path, root, config) is not None


def ignore_reason_for_scan_file(path: Path, root: Path, config: dict[str, object] | None = None) -> str | None:
    config = config or {}
    scan = config_scan(config)
    ignore_paths = config_ignore_paths(config) + list(scan.get("extra_ignore_paths", []))
    if ignore_paths and should_ignore_config_path(path, root, ignore_paths):
        return "configured-ignore-path"
    max_file_size_kb = scan.get("max_file_size_kb")
    if isinstance(max_file_size_kb, int):
        try:
            if path.stat().st_size > max_file_size_kb * 1024:
                return "configured-max-file-size"
        except OSError:
            return "unreadable"
    lower_parts = {part.lower() for part in path.parts}
    if not bool(scan.get("include_tests", True)) and path.suffix == ".sol" and (path.name.endswith(".t.sol") or "test" in lower_parts):
        return "configured-tests-disabled"
    if not bool(scan.get("include_docs", True)) and path.suffix.lower() == ".md":
        return "configured-docs-disabled"
    relative = scan_relative_path(path, root)
    for pattern in scan.get("extra_ignore_globs", []):
        if path_matches_glob(relative, str(pattern)):
            return "configured-ignore-glob"
    include_generated = bool(scan.get("include_generated_artifacts", False))
    ignore_generated = bool(scan.get("ignore_generated_artifacts", True))
    potential_generated = is_potential_generated_artifact_candidate(path, root)
    text = read_text_safe(path) if potential_generated else None
    generated_artifact = is_arkheionx_generated_artifact(path, root, text)
    if ignore_generated and not include_generated and generated_artifact:
        return "generated-artifact"
    if potential_generated and not generated_artifact and not is_relevant_file(path):
        return "non-source-artifact"
    return None


def filter_scan_files(files: list[Path], root: Path, config: dict[str, object]) -> tuple[list[Path], dict[str, object]]:
    scanned: list[Path] = []
    ignored_paths: list[str] = []
    generated_paths: list[str] = []
    ignored_by_reason: dict[str, int] = {}
    for path in files:
        reason = ignore_reason_for_scan_file(path, root, config)
        if reason is None:
            scanned.append(path)
            continue
        relative = scan_relative_path(path, root)
        ignored_paths.append(relative)
        ignored_by_reason[reason] = ignored_by_reason.get(reason, 0) + 1
        if reason == "generated-artifact":
            generated_paths.append(relative)
    return sorted(set(scanned)), {
        "files_considered": len(files),
        "files_scanned": len(set(scanned)),
        "files_ignored": len(ignored_paths),
        "generated_artifacts_ignored": len(generated_paths),
        "ignored_generated_artifact_paths": sorted(generated_paths),
        "ignored_paths": sorted(ignored_paths),
        "ignored_by_reason": dict(sorted(ignored_by_reason.items())),
        "include_generated_artifacts": bool(config_scan(config).get("include_generated_artifacts", False)),
    }


def collect_files(root: Path) -> list[Path]:
    root = root.resolve()
    included: list[Path] = []

    for current, dirs, files in os.walk(root):
        current_path = Path(current)
        dirs[:] = [
            d
            for d in dirs
            if d not in IGNORED_DIRS and not (d == "lib" and current_path == root)
        ]
        for file_name in files:
            path = current_path / file_name
            if is_relevant_file(path) or is_potential_generated_artifact_candidate(path, root):
                included.append(path)

    return sorted(set(included))


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


NEGATIVE_CONTEXT_TERMS = [
    "intentionally missing",
    "required but missing",
    "currently missing",
    "coverage missing",
    "not covered",
    "not implemented",
    "should include",
    "should add",
    "without",
    "missing",
    "lacks",
    "absent",
    "needs",
    "todo",
    "fixme",
    "no",
]

COVERAGE_CONTEXT_TERMS = [
    "invariant tests",
    "invariant test",
    "invariant",
    "fuzz",
    "stale oracle tests",
    "stale oracle",
    "oracle freshness",
    "updatedAt",
    "heartbeat",
    "access-control negative tests",
    "access-control",
    "unauthorized",
    "onlyOwner test",
    "role-boundary",
    "reward conservation tests",
    "reward conservation",
    "double-claim",
    "reentrancy/callback tests",
    "reentrancy",
    "callback",
    "solvency",
    "liquidation boundary",
    "slippage",
    "constant product",
    "LP share accounting",
    "fee-on-transfer",
    "collateral debt",
    "interest index",
    "borrow index",
    "share accounting",
    "totalAssets",
]


def term_pattern(term: str) -> re.Pattern[str]:
    escaped = re.escape(term).replace(r"\ ", r"[\s_-]+")
    if re.search(r"^[A-Za-z_][A-Za-z0-9_]*$", term):
        return re.compile(rf"(?<![A-Za-z0-9]){escaped}(?![A-Za-z0-9])", flags=re.IGNORECASE)
    return re.compile(escaped, flags=re.IGNORECASE)


def negative_marker_pattern(term: str) -> re.Pattern[str]:
    escaped = re.escape(term).replace(r"\ ", r"[\s_-]+")
    if re.search(r"^[A-Za-z]+$", term):
        return re.compile(rf"(?<![A-Za-z0-9]){escaped}(?![A-Za-z0-9])", flags=re.IGNORECASE)
    return re.compile(escaped, flags=re.IGNORECASE)


NEGATIVE_CONTEXT_PATTERNS = [negative_marker_pattern(term) for term in NEGATIVE_CONTEXT_TERMS]


def has_negative_marker(text: str) -> bool:
    return any(pattern.search(text) for pattern in NEGATIVE_CONTEXT_PATTERNS)


def iter_term_matches(text: str, term: str) -> Iterable[re.Match[str]]:
    if not text or not term:
        return []
    return term_pattern(term).finditer(text)


def is_negative_context(text: str, term: str, window: int = 160) -> bool:
    """Return true when a coverage term appears near missing/negative wording."""
    for match in iter_term_matches(text, term):
        start = max(0, match.start() - window)
        end = min(len(text), match.end() + window)
        if has_negative_marker(text[start:end]):
            return True
    return False


def has_positive_term(text: str, term: str, window: int = 160) -> bool:
    """Return true when at least one occurrence is not in negative context."""
    for match in iter_term_matches(text, term):
        start = max(0, match.start() - window)
        end = min(len(text), match.end() + window)
        if not has_negative_marker(text[start:end]):
            return True
    return False


def positive_count_term(text: str, term: str, window: int = 160) -> int:
    count = 0
    for match in iter_term_matches(text, term):
        start = max(0, match.start() - window)
        end = min(len(text), match.end() + window)
        if not has_negative_marker(text[start:end]):
            count += 1
    return count


def line_snippet_for_offset(text: str, offset: int) -> str:
    line_start = text.rfind("\n", 0, offset) + 1
    line_end = text.find("\n", offset)
    if line_end == -1:
        line_end = len(text)
    return text[line_start:line_end].strip()


def collect_negative_evidence(contents: dict[Path, str], root: Path, window: int = 160) -> list[dict[str, object]]:
    evidence: list[dict[str, object]] = []
    seen: set[tuple[str, int, str]] = set()
    for path, text in contents.items():
        if not text:
            continue
        for term in COVERAGE_CONTEXT_TERMS:
            for match in iter_term_matches(text, term):
                start = max(0, match.start() - window)
                end = min(len(text), match.end() + window)
                context = text[start:end]
                if not has_negative_marker(context):
                    continue
                line = line_for_offset(text, match.start())
                key = (rel(path, root), line, term.lower())
                if key in seen:
                    continue
                seen.add(key)
                snippet = line_snippet_for_offset(text, match.start()) or context.strip()
                evidence.append(
                    {
                        "type": "negative-test-coverage",
                        "file": rel(path, root),
                        "line": line,
                        "term": term,
                        "snippet": snippet[:220],
                        "reason": "Coverage term appears in negative context.",
                    }
                )
    return evidence


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
    negative_evidence: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    usable_tests = [
        path
        for path in classified.solidity_tests
        if not is_placeholder_skeleton(contents.get(path, ""))
    ]
    code_paths = classified.solidity_sources + usable_tests + classified.configs + classified.workflows
    all_text = combined_text(contents, code_paths or contents.keys())
    tests_only_text = collect_text_for_paths(contents, usable_tests)
    test_paths = usable_tests
    lower_paths = [rel(p, root).lower() for p in contents]
    has_test_dir = any("/test/" in f"/{p}" or p.startswith("test/") for p in lower_paths)
    foundry = any(p.name == "foundry.toml" for p in classified.configs) or "forge-std" in all_text
    hardhat = any(p.name.startswith("hardhat.config") for p in classified.configs)
    assert_count = len(re.findall(r"\bassert[A-Za-z_]*\s*\(", tests_only_text))
    invariant_count = positive_count_term(tests_only_text, "invariant") + len(
        [p for p in test_paths if "invariant" in rel(p, root).lower()]
    )
    fuzz_count = positive_count_term(tests_only_text, "fuzz") + len(re.findall(r"\btestFuzz", tests_only_text))
    handler_count = positive_count_term(tests_only_text, "handler") + positive_count_term(tests_only_text, "StdInvariant")
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
    edge_case_count = sum(positive_count_term(tests_only_text, term) for term in edge_case_terms)
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
        "negative_evidence": negative_evidence or [],
        "negative_evidence_count": len(negative_evidence or []),
        "negative_evidence_terms": sorted({str(item.get("term", "")) for item in negative_evidence or [] if item.get("term")}),
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
        matched = sorted({term for term in terms if has_positive_term(test_text, term)})
        coverage[key] = bool(matched)
        matched_terms[key] = matched

    return {
        "coverage": coverage,
        "matched_terms": matched_terms,
        "covered_count": sum(1 for value in coverage.values() if value),
        "total_checks": len(coverage),
        "test_files_considered": len(usable_tests),
    }


def line_for_offset(text: str, offset: int) -> int:
    return text.count("\n", 0, max(0, offset)) + 1


def find_matching_brace(text: str, open_index: int) -> int:
    depth = 0
    in_string = ""
    escaped = False
    for index in range(open_index, len(text)):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == in_string:
                in_string = ""
            continue
        if char in {'"', "'"}:
            in_string = char
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return index
    return len(text) - 1


def normalize_signature_tail(tail: str) -> list[str]:
    stop_words = {
        "external",
        "public",
        "internal",
        "private",
        "payable",
        "view",
        "pure",
        "virtual",
        "override",
        "returns",
        "return",
        "memory",
        "calldata",
        "storage",
    }
    cleaned = re.sub(r"\([^)]*\)", " ", tail)
    tokens = re.findall(r"\b[A-Za-z_][A-Za-z0-9_]*\b", cleaned)
    return [token for token in tokens if token not in stop_words]


def extract_state_variables(contract_body: str) -> list[str]:
    without_functions = re.sub(r"\b(function|constructor)\b[\s\S]*?{[\s\S]*?}", "", contract_body)
    variables: set[str] = set()
    for match in re.finditer(
        r"^\s*(?:mapping\s*\([^;]+?\)|[A-Za-z_][A-Za-z0-9_<>,\[\].]*)\s+"
        r"(?:(?:public|private|internal|external|immutable|constant|override)\s+)*"
        r"([A-Za-z_][A-Za-z0-9_]*)\s*(?:=|;)",
        without_functions,
        flags=re.MULTILINE,
    ):
        name = match.group(1)
        if name not in {"function", "returns", "modifier", "event", "error", "struct"}:
            variables.add(name)
    return sorted(variables)


def extract_calls(function_body: str) -> list[str]:
    ignored = {"if", "for", "while", "require", "assert", "revert", "emit", "return", "new", "delete"}
    calls = {
        match.group(1)
        for match in re.finditer(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(", function_body)
        if match.group(1) not in ignored
    }
    dot_calls = {
        match.group(1)
        for match in re.finditer(r"\.([A-Za-z_][A-Za-z0-9_]*)\s*\(", function_body)
        if match.group(1) not in ignored
    }
    return sorted(calls | dot_calls)


def extract_snippet(body: str, terms: Iterable[str]) -> str:
    for term in terms:
        index = body.lower().find(term.lower())
        if index != -1:
            start = max(0, body.rfind("\n", 0, index) + 1)
            end = body.find("\n", index)
            if end == -1:
                end = min(len(body), index + 120)
            return re.sub(r"\s+", " ", body[start:end].strip())[:180]
    return ""


def parse_functions_from_body(
    contract_body: str,
    file_text: str,
    body_offset: int,
    state_variables: list[str],
) -> list[dict[str, object]]:
    functions: list[dict[str, object]] = []
    pattern = re.compile(r"\b(function|constructor)\s+([A-Za-z_][A-Za-z0-9_]*)?\s*\([^;{]*\)\s*([^;{]*){", re.MULTILINE)
    for match in pattern.finditer(contract_body):
        open_index = body_offset + match.end() - 1
        close_index = find_matching_brace(file_text, open_index)
        body = file_text[open_index + 1 : close_index]
        name = match.group(2) or "constructor"
        tail = match.group(3) or ""
        visibility = "unspecified"
        for candidate in ["external", "public", "internal", "private"]:
            if re.search(rf"\b{candidate}\b", tail):
                visibility = candidate
                break
        modifiers = normalize_signature_tail(tail)
        calls = extract_calls(body)
        external_terms = [
            "transferFrom",
            "safeTransferFrom",
            "safeTransfer",
            "transfer",
            "send",
            ".call(",
            "call{",
            "delegatecall",
            "flashLoan",
            "executeOperation",
        ]
        oracle_terms = [
            "latestRoundData",
            "latestAnswer",
            "getPrice",
            "getReserves",
            "observe",
            "consult",
            "sqrtPriceX96",
        ]
        writes_state = [
            variable
            for variable in state_variables
            if re.search(rf"\b{re.escape(variable)}\b\s*(?:=|\+=|-=|\*=|/=|\+\+|--|\[)", body)
        ]
        reads_state = [variable for variable in state_variables if re.search(rf"\b{re.escape(variable)}\b", body)]
        external_calls = [term for term in external_terms if term in body or term.replace(".", "") in calls]
        oracle_calls = [term for term in oracle_terms if term in body or term in calls]
        line_start = line_for_offset(file_text, body_offset + match.start())
        line_end = line_for_offset(file_text, close_index)
        functions.append(
            {
                "name": name,
                "visibility": visibility,
                "modifiers": modifiers,
                "payable": bool(re.search(r"\bpayable\b", tail)),
                "line_start": line_start,
                "line_end": line_end,
                "body_excerpt_hash": hashlib.sha256(body.strip().encode("utf-8")).hexdigest()[:16],
                "calls": calls[:40],
                "external_calls": sorted(set(external_calls)),
                "oracle_calls": sorted(set(oracle_calls)),
                "writes_state": sorted(set(writes_state)),
                "reads_state": sorted(set(reads_state)),
                "snippet": extract_snippet(body, list(oracle_terms) + list(external_terms) + list(writes_state)),
            }
        )
    return functions


def parse_contracts_from_solidity(text: str, path: Path, root: Path) -> list[dict[str, object]]:
    contracts: list[dict[str, object]] = []
    pattern = re.compile(r"\b(abstract\s+contract|contract|interface|library)\s+([A-Za-z_][A-Za-z0-9_]*)(?:\s+is\s+([^{]+))?\s*{")
    for match in pattern.finditer(text):
        open_index = match.end() - 1
        close_index = find_matching_brace(text, open_index)
        body = text[open_index + 1 : close_index]
        inherits = []
        if match.group(3):
            inherits = [item.strip().split()[0] for item in match.group(3).split(",") if item.strip()]
        state_variables = extract_state_variables(body)
        functions = parse_functions_from_body(body, text, open_index + 1, state_variables)
        contracts.append(
            {
                "name": match.group(2),
                "file": rel(path, root),
                "kind": match.group(1).replace("abstract ", ""),
                "inherits": inherits,
                "line_start": line_for_offset(text, match.start()),
                "line_end": line_for_offset(text, close_index),
                "state_variables": state_variables,
                "functions": functions,
            }
        )
    return contracts


def parse_test_file(text: str, path: Path, root: Path) -> dict[str, object]:
    test_functions = re.findall(r"\bfunction\s+(test[A-Za-z0-9_]*)\s*\(", text)
    invariant_functions = [name for name in re.findall(r"\bfunction\s+([A-Za-z0-9_]*invariant[A-Za-z0-9_]*)\s*\(", text, flags=re.IGNORECASE)]
    fuzz_functions = [name for name in test_functions if "fuzz" in name.lower()]
    coverage_terms = {
        "oracle": ["stale", "updatedat", "heartbeat", "decimals", "bounds", "twap", "spot", "oracle", "price"],
        "access_control": ["unauthorized", "onlyowner", "reverts", "prank", "owner", "role", "admin", "grantrole", "revokerole"],
        "reentrancy": ["reentrant", "attacker", "callback", "malicious", "receiver", "double claim", "doubleclaim"],
        "reward": ["multi-user", "multiuser", "conservation", "claim twice", "claimtwice", "accumulator", "rewardpertoken", "epoch"],
        "vault": ["deposit", "withdraw", "redeem", "donation", "rounding", "totalassets", "preview", "invariant"],
        "amm": ["constant product", "invariant", "reserve", "liquidity", "mint", "burn", "slippage", "minout", "deadline", "twap", "balancebefore", "balanceafter", "fee-on-transfer"],
        "lending": ["collateral", "debt", "solvency", "healthfactor", "liquidation", "just above", "just below", "interest", "borrowindex", "accrue", "oracle", "stale", "cash", "reserves"],
    }
    coverage = {
        key: sorted({term for term in terms if has_positive_term(text, term)})
        for key, terms in coverage_terms.items()
    }
    return {
        "file": rel(path, root),
        "test_functions": sorted(set(test_functions)),
        "invariant_functions": sorted(set(invariant_functions)),
        "fuzz_functions": sorted(set(fuzz_functions)),
        "coverage_terms": coverage,
    }


def flatten_semantic_functions(semantic: dict[str, object]) -> list[dict[str, object]]:
    functions: list[dict[str, object]] = []
    for contract in semantic.get("contracts", []):
        if not isinstance(contract, dict):
            continue
        for function in contract.get("functions", []):
            if isinstance(function, dict):
                item = dict(function)
                item["contract"] = contract.get("name", "")
                item["file"] = contract.get("file", "")
                functions.append(item)
    return functions


def semantic_signal_summary(contracts: list[dict[str, object]], test_files: list[dict[str, object]]) -> dict[str, object]:
    functions: list[dict[str, object]] = []
    state_variables: set[str] = set()
    inherited: set[str] = set()
    for contract in contracts:
        state_variables.update(str(item) for item in contract.get("state_variables", []))
        inherited.update(str(item) for item in contract.get("inherits", []))
        for function in contract.get("functions", []):
            if isinstance(function, dict):
                functions.append(function)
    function_names = {str(function.get("name", "")).lower() for function in functions}
    public_or_external = [
        function
        for function in functions
        if function.get("visibility") in {"public", "external"}
    ]
    admin_prefixes = ("set", "update", "configure", "pause", "unpause", "rescue", "sweep", "upgrade", "initialize")
    admin_setters = [
        function
        for function in public_or_external
        if str(function.get("name", "")).lower().startswith(admin_prefixes)
        or any(str(modifier).lower() in {"onlyowner", "onlyrole"} for modifier in function.get("modifiers", []))
    ]
    value_flow = [
        function
        for function in functions
        if function.get("external_calls")
        and (
            any(term in str(function.get("name", "")).lower() for term in ["withdraw", "redeem", "claim", "refund", "unstake", "payout"])
            or bool(function.get("writes_state"))
        )
    ]
    reward_state = any(term in variable.lower() for variable in state_variables for term in ["reward", "accumulator", "index", "emission", "staked"])
    vault_functions = {"deposit", "withdraw", "redeem", "mint", "totalassets", "converttoshares", "converttoassets", "previewdeposit", "previewwithdraw"}
    amm_functions = {"swap", "addliquidity", "removeliquidity", "getamountout", "quote", "mint", "burn"}
    lending_functions = {"borrow", "repay", "liquidate", "healthfactor", "accrueinterest", "depositcollateral", "withdrawcollateral"}
    amm_state = any(term in variable.lower() for variable in state_variables for term in ["reserve", "klast", "liquidity", "pooltoken"])
    lending_state = any(term in variable.lower() for variable in state_variables for term in ["collateral", "debt", "borrow", "reserve", "cash", "liquidation", "interestindex", "borrowindex"])
    tests_by_pack = {"oracle": set(), "access_control": set(), "reentrancy": set(), "reward": set(), "vault": set(), "amm": set(), "lending": set()}
    for test_file in test_files:
        coverage_terms = test_file.get("coverage_terms", {})
        if isinstance(coverage_terms, dict):
            for key in tests_by_pack:
                terms = coverage_terms.get(key, [])
                if isinstance(terms, list):
                    tests_by_pack[key].update(str(term) for term in terms)
    return {
        "contract_count": len(contracts),
        "function_count": len(functions),
        "has_oracle_calls": any(function.get("oracle_calls") for function in functions),
        "has_admin_setters": bool(admin_setters),
        "has_external_value_flow": bool(value_flow),
        "has_reward_accounting": reward_state or bool(function_names & {"stake", "unstake", "claim", "claimreward", "earned", "rewardpertoken", "notifyrewardamount"}),
        "has_vault_functions": bool(function_names & vault_functions),
        "has_amm_functions": amm_state or bool(function_names & amm_functions),
        "has_lending_functions": lending_state or bool(function_names & lending_functions),
        "has_upgradeability": bool(inherited & {"UUPSUpgradeable", "TransparentUpgradeableProxy"}) or any("upgrade" in str(function.get("name", "")).lower() or "initializer" in [str(mod).lower() for mod in function.get("modifiers", [])] for function in functions),
        "has_invariant_tests": any(test_file.get("invariant_functions") for test_file in test_files),
        "has_fuzz_tests": any(test_file.get("fuzz_functions") for test_file in test_files),
        "test_coverage": {key: sorted(values) for key, values in tests_by_pack.items()},
    }


def extract_solidity_structure(
    contents: dict[Path, str],
    classified: ClassifiedFiles,
    root: Path,
    enabled: bool = True,
) -> dict[str, object]:
    if not enabled:
        return {
            "enabled": False,
            "contracts": [],
            "test_files": [],
            "signals": {},
            "warnings": [],
        }
    contracts: list[dict[str, object]] = []
    test_files: list[dict[str, object]] = []
    warnings: list[str] = []
    for path in classified.solidity_sources:
        try:
            contracts.extend(parse_contracts_from_solidity(contents.get(path, ""), path, root))
        except Exception as exc:  # Defensive parser: never fail the scan.
            warnings.append(f"semantic-lite parse warning for `{rel(path, root)}`: {exc}")
    for path in classified.solidity_tests:
        if is_placeholder_skeleton(contents.get(path, "")):
            continue
        try:
            test_files.append(parse_test_file(contents.get(path, ""), path, root))
        except Exception as exc:
            warnings.append(f"semantic-lite test parse warning for `{rel(path, root)}`: {exc}")
    return {
        "enabled": True,
        "contracts": contracts,
        "test_files": test_files,
        "signals": semantic_signal_summary(contracts, test_files),
        "warnings": warnings,
    }


def normalize_slither_detector(item: dict[str, object], root: Path) -> dict[str, object]:
    elements: list[dict[str, object]] = []
    for element in item.get("elements", []) if isinstance(item.get("elements", []), list) else []:
        if not isinstance(element, dict):
            continue
        source_mapping = element.get("source_mapping", {})
        filename = ""
        line = 1
        if isinstance(source_mapping, dict):
            filename = str(source_mapping.get("filename_relative") or source_mapping.get("filename") or "")
            try:
                lines = source_mapping.get("lines", [1])
                line = int(lines[0] if isinstance(lines, list) and lines else 1)
            except (TypeError, ValueError):
                line = 1
        elements.append(
            {
                "name": str(element.get("name", "")),
                "type": str(element.get("type", "")),
                "file": filename,
                "line": line,
            }
        )
    return {
        "check": str(item.get("check", "")),
        "impact": str(item.get("impact", "")),
        "confidence": str(item.get("confidence", "")),
        "description": str(item.get("description", ""))[:500],
        "elements": elements[:10],
    }


def normalize_slither_json(data: dict[str, object], root: Path, source: str) -> dict[str, object]:
    raw_detectors = []
    results = data.get("results", {})
    if isinstance(results, dict) and isinstance(results.get("detectors"), list):
        raw_detectors = results.get("detectors", [])
    elif isinstance(data.get("detectors"), list):
        raw_detectors = data.get("detectors", [])
    detectors = [
        normalize_slither_detector(item, root)
        for item in raw_detectors
        if isinstance(item, dict)
    ]
    return {
        "enabled": True,
        "available": True,
        "source": source,
        "detectors": detectors,
        "warnings": [],
    }


def load_slither_json(path: Path, root: Path) -> dict[str, object]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {
            "enabled": True,
            "available": False,
            "source": "provided",
            "detectors": [],
            "warnings": [f"Could not parse Slither JSON `{display_path(path)}`: {exc}"],
        }
    return normalize_slither_json(data, root, "provided")


def run_slither(root: Path, timeout: int) -> dict[str, object]:
    slither_path = shutil.which("slither")
    if not slither_path:
        return {
            "enabled": True,
            "available": False,
            "source": "unavailable",
            "detectors": [],
            "warnings": ["Slither was requested but `slither` was not found on PATH."],
        }
    output_path = root / ".arkheionx-slither.json"
    try:
        completed = subprocess.run(
            [slither_path, str(root), "--json", str(output_path)],
            cwd=root,
            text=True,
            capture_output=True,
            timeout=max(1, timeout),
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {
            "enabled": True,
            "available": True,
            "source": "generated",
            "detectors": [],
            "warnings": [f"Slither execution failed or timed out: {exc}"],
        }
    warnings = []
    if completed.returncode not in {0, 255}:
        warnings.append(f"Slither exited with code {completed.returncode}. Arkheionx continued with available output.")
    if not output_path.exists():
        warnings.append("Slither did not produce JSON output.")
        return {
            "enabled": True,
            "available": True,
            "source": "generated",
            "detectors": [],
            "warnings": warnings,
        }
    summary = load_slither_json(output_path, root)
    summary["source"] = "generated"
    summary["warnings"] = list(summary.get("warnings", [])) + warnings
    try:
        output_path.unlink()
    except OSError:
        pass
    return summary


def slither_analysis(
    root: Path,
    enable_slither: bool,
    slither_json: Path | None,
    timeout: int,
) -> dict[str, object]:
    if slither_json:
        return load_slither_json(slither_json, root)
    if enable_slither:
        return run_slither(root, timeout)
    return {
        "enabled": False,
        "available": False,
        "source": "disabled",
        "detectors": [],
        "warnings": [],
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


def apply_negative_evidence_score_penalty(
    score: dict[str, dict[str, object]],
    test_readiness: dict[str, object],
    categories: Iterable[str],
) -> None:
    negative_count = int(test_readiness.get("negative_evidence_count", 0) or 0)
    if negative_count <= 0:
        return
    total_penalty = min(10, max(2, negative_count))
    category_list = [category for category in categories if category in score]
    if not category_list:
        return
    per_category = max(1, total_penalty // len(category_list))
    for category in category_list:
        current = int(score[category].get("score", 0))
        penalty = min(current, per_category)
        if penalty <= 0:
            continue
        score[category]["score"] = current - penalty
        score[category]["notes"].append(
            f"Negative coverage statements detected; removed {penalty} readiness point(s) from this category."
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
    role_covered = text_has_any(lower_text, ["unauthorized", "onlyowner", "accesscontrol", "role", "admin"])
    oracle_controls = text_has_any(lower_text, ["stale", "heartbeat", "twap", "bounds", "sanity", "slippage"])
    upgrade_covered = not upgrade_terms or text_has_any(lower_text, ["initializer", "reinitializer", "upgrade", "storage gap", "__gap"])

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
    if coverage["emergency_pause"] or text_has_any(lower_text, ["pause", "emergency"]):
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
    if text_has_any(lower_text, ["assumption", "invariant", "limitations", "rounding", "oracle"]):
        award("documentation_readiness", 2, "Vault assumptions or limitations are documented.")
    if text_has_any(lower_text, ["owner", "admin", "role", "treasury", "deployment"]):
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

    apply_negative_evidence_score_penalty(
        score,
        test_readiness,
        [
            "vault_accounting_coverage",
            "invariant_fuzz_readiness",
            "oracle_pricing_readiness",
            "admin_operational_readiness",
            "strategy_withdrawal_lifecycle_readiness",
        ],
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
    if has_tests and len(protocol_terms) >= 3 and int(test_readiness.get("negative_evidence_count", 0) or 0) == 0:
        award("test_presence", 5, "Protocol-specific terms appear in the testable codebase.")

    if test_readiness["invariant_tests"]:
        award("invariant_fuzz_readiness", 8, "Invariant tests or invariant terms detected.")
    if test_readiness["fuzz_tests"]:
        award("invariant_fuzz_readiness", 5, "Fuzz tests detected.")
    if test_readiness["handler_contracts"]:
        award("invariant_fuzz_readiness", 4, "Handler or property-style testing terms detected.")
    if test_readiness["edge_case_tests"]:
        award("invariant_fuzz_readiness", 3, "Edge-case testing terms detected.")

    lower_all_text = all_text.lower()
    oracle_documented = has_meaningful_oracle_signal(signals) and text_has_any(lower_all_text, ["stale", "heartbeat", "twap", "bounds", "sanity"])
    accounting_documented = has_any(signals, "vault_accounting") and any(
        has_positive_term(lower_all_text, term) for term in ["roundtrip", "conservation", "totalassets", "shares", "rounding"]
    )
    role_covered = has_any(signals, "access_control") and any(
        has_positive_term(lower_all_text, term) for term in ["unauthorized", "onlyowner", "accesscontrol", "role", "admin"]
    )
    value_flow_covered = has_any(signals, "reentrancy_value_flow") and (
        has_any(signals, "reentrancy_value_flow", ["nonReentrant", "ReentrancyGuard"]) or has_positive_term(lower_all_text, "reentrancy")
    )
    protocol_checklist = protocol_type != "generic" and (
        test_readiness["edge_case_tests"] or test_readiness["invariant_tests"] or has_positive_term(lower_all_text, "checklist")
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
    assumptions_documented = text_has_any(lower_all_text, ["assumption", "invariant", "limitations", "oracle", "roles"])
    roles_documented = text_has_any(lower_all_text, ["deployment", "owner", "admin", "role", "treasury"])
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
    if text_has_any(lower_all_text, ["pause", "emergency", "incident", "runbook"]):
        award("operational_admin_readiness", 3, "Emergency control or incident terms detected.")
    if not has_any(signals, "upgradeability") or text_has_any(lower_all_text, ["initializer", "upgrade", "storage gap", "__gap"]):
        award("operational_admin_readiness", 3, "Upgradeability is absent or has visible documentation/test terms.")
    if any(term in all_text for term in ["setFee", "setOracle", "setStrategy", "setTreasury", "onlyOwner"]):
        award("operational_admin_readiness", 3, "Privileged setters or owner boundaries are visible for review.")
    if text_has_any(lower_all_text, ["monitor", "incident", "limitations", "pause", "emergency"]):
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
    if has_any(signals, "upgradeability") and not has_positive_term(lower_all_text, "initializer"):
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
    if has_any(signals, "staking_rewards", ["stake", "unstake", "reward", "rewards", "claim", "rewardPerToken", "accumulator", "emission", "earned", "pendingReward"]) and not test_readiness["invariant_tests"]:
        add_gap(
            gaps,
            "Medium readiness gap",
            "Reward accounting needs conservation coverage",
            "Reward/index/claim signals were detected without invariant testing.",
            "Add reward conservation and no-overclaim tests across multiple users and timing boundaries.",
            ["reward-accounting", "precision"],
        )
    apply_negative_evidence_score_penalty(
        score,
        test_readiness,
        ["invariant_fuzz_readiness", "defi_risk_coverage", "documentation_readiness"],
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


def test_text(contents: dict[Path, str], classified: ClassifiedFiles) -> str:
    usable_tests = [
        path
        for path in classified.solidity_tests
        if not is_placeholder_skeleton(contents.get(path, ""))
    ]
    return collect_text_for_paths(contents, usable_tests).lower()


def source_and_doc_text(contents: dict[Path, str], classified: ClassifiedFiles) -> str:
    paths = classified.solidity_sources + classified.solidity_tests + classified.docs
    return collect_text_for_paths(contents, paths or contents.keys()).lower()


def source_text(contents: dict[Path, str], classified: ClassifiedFiles) -> str:
    return collect_text_for_paths(contents, classified.solidity_sources).lower()


def text_has_any(text: str, terms: Iterable[str]) -> bool:
    return any(has_positive_term(text, term) for term in terms)


def existing_finding_ids(gaps: list[ReadinessGap]) -> set[str]:
    return {gap.id for gap in gaps if gap.id}


def add_rule_pack_gaps(
    gaps: list[ReadinessGap],
    contents: dict[Path, str],
    classified: ClassifiedFiles,
    signals: dict[str, dict[str, object]],
) -> None:
    """Add v0.5 starter rule-pack findings without replacing existing scoring."""
    tests = test_text(contents, classified)
    corpus_text = source_and_doc_text(contents, classified)
    solidity_text = source_text(contents, classified)
    existing_ids = existing_finding_ids(gaps)

    def maybe_add(finding_id: str, *args: object, **kwargs: object) -> None:
        if finding_id in existing_ids:
            return
        add_gap(gaps, *args, finding_id=finding_id, **kwargs)  # type: ignore[arg-type]
        existing_ids.add(finding_id)

    oracle_terms = detected_terms(signals, "oracle_rule_pack")
    has_oracle = bool(set(oracle_terms) - {"decimals", "answer"})
    has_stale_tests = text_has_any(tests, ["stale", "heartbeat", "updatedat", "answeredInRound", "roundId"])
    has_decimal_tests = text_has_any(tests, ["decimal", "normalize", "scale", "precision"])
    has_spot_pricing = bool(set(oracle_terms) & {"getReserves", "reserve0", "reserve1", "spot", "sqrtPriceX96", "pool"})
    has_spot_tests = text_has_any(tests, ["twap", "manipulation", "bounds", "minprice", "maxprice", "sanity", "reserve"])
    has_oracle_setter = bool(set(oracle_terms) & {"setOracle", "fallbackOracle"})
    has_role_tests = text_has_any(tests, ["unauthorized", "onlyowner", "accesscontrol", "revert", "role"])
    has_price_docs = text_has_any(corpus_text, ["minprice", "maxprice", "bounds", "fallback", "stale", "heartbeat", "oracle assumption"])

    if has_oracle and not has_stale_tests:
        maybe_add(
            "ARK-ORC-001",
            "High readiness gap",
            "Oracle-dependent logic without stale-price tests",
            "Oracle or price-feed signals were detected, but tests do not visibly cover stale rounds, heartbeat, or timestamp behavior.",
            "Add local mock oracle tests for stale round rejection, heartbeat windows, answeredInRound, and updatedAt behavior.",
            ["oracle-risk", "oracle-rule-pack", "pre-audit-readiness"],
            priority="High",
            category="oracle-pricing",
            detected=oracle_terms,
            why_it_matters="Oracle-dependent accounting and control flows can be wrong when price data is stale, incomplete, or outside documented assumptions.",
            historical_pattern_similarity="Maps to historical oracle and pricing failure classes where stale or manipulated price state broke protocol assumptions.",
            defensive_checks=["stale round rejection", "heartbeat checks", "updatedAt validation", "answeredInRound handling"],
            suggested_test="Use a local mock price feed to assert stale or incomplete oracle rounds are rejected or handled according to documented policy.",
        )
    if has_oracle and not has_decimal_tests:
        maybe_add(
            "ARK-ORC-002",
            "Medium readiness gap",
            "Oracle decimals or normalization not covered by tests",
            "Oracle decimals or price normalization signals were detected without visible normalization tests.",
            "Add tests for decimals normalization, precision scaling, and mixed-decimal asset assumptions.",
            ["oracle-risk", "decimals", "precision", "oracle-rule-pack"],
            priority="Medium",
            category="oracle-pricing",
            detected=oracle_terms,
            why_it_matters="Decimals mismatches can distort collateral, share, reward, or pricing calculations even when the oracle value itself is fresh.",
            historical_pattern_similarity="Maps to arithmetic and oracle normalization failure classes.",
            defensive_checks=["decimals normalization", "mixed asset decimals", "precision scaling", "rounding bounds"],
            suggested_test="Mock price feeds with different decimals and assert protocol accounting normalizes every value before use.",
        )
    if has_spot_pricing and not has_spot_tests:
        maybe_add(
            "ARK-ORC-003",
            "High readiness gap",
            "Spot or reserve-based pricing without manipulation-resistance tests",
            "Spot, reserve, pool, or sqrtPriceX96 pricing signals were detected without visible manipulation-resistance tests.",
            "Add local pool/reserve tests for TWAP, bounds, and spot-price movement assumptions.",
            ["oracle-risk", "spot-price", "reserve-pricing", "oracle-rule-pack"],
            priority="High",
            category="oracle-pricing",
            detected=oracle_terms,
            why_it_matters="Same-block spot or reserve-based pricing can drift from fair value unless bounded by the protocol design.",
            historical_pattern_similarity="Maps to historical price-manipulation readiness classes.",
            defensive_checks=["TWAP vs spot behavior", "reserve movement bounds", "price sanity checks", "local pool mocks"],
            suggested_test="Use a local pool mock to move reserves or price and assert protocol actions respect documented bounds.",
        )
    if has_oracle_setter and not has_role_tests:
        maybe_add(
            "ARK-ORC-004",
            "Medium readiness gap",
            "Oracle setter/admin path without role-boundary tests",
            "Oracle setter or fallback oracle signals were detected without visible unauthorized-call tests.",
            "Add tests proving only documented roles can update oracle configuration.",
            ["oracle-risk", "access-control-review", "oracle-rule-pack"],
            priority="Medium",
            category="oracle-pricing",
            detected=oracle_terms,
            why_it_matters="Oracle configuration changes can alter all downstream accounting assumptions.",
            historical_pattern_similarity="Maps to privileged control and oracle configuration readiness classes.",
            defensive_checks=["unauthorized setOracle reverts", "trusted role documentation", "fallback oracle controls"],
            suggested_test="Assert unprivileged callers cannot change oracle or fallback oracle configuration.",
        )
    if has_oracle and not has_price_docs:
        maybe_add(
            "ARK-ORC-005",
            "Medium readiness gap",
            "Missing price bounds or fallback assumptions documentation",
            "Oracle pricing signals were detected without clear documentation for bounds, fallback behavior, or stale price assumptions.",
            "Document min/max bounds, fallback oracle behavior, stale-price policy, and L2 sequencer assumptions if relevant.",
            ["oracle-risk", "documentation-readiness", "oracle-rule-pack"],
            priority="Medium",
            category="oracle-pricing",
            detected=oracle_terms,
            why_it_matters="Auditors and maintainers need explicit pricing assumptions to review whether the design handles oracle failure modes.",
            historical_pattern_similarity="Maps to failed assumption classes where oracle behavior was implied but not enforced or documented.",
            defensive_checks=["price bounds", "fallback policy", "stale-price policy", "sequencer downtime notes"],
            suggested_test="Add documentation plus local tests showing fallback and out-of-bounds price behavior.",
        )

    access_terms = detected_terms(signals, "access_upgrade_rule_pack", "access_control", "upgradeability")
    has_access = bool(access_terms)
    has_privileged_setters = bool(set(access_terms) & {"setFee", "setOracle", "setStrategy", "setTreasury", "grantRole", "revokeRole", "pause", "unpause"})
    has_emergency = bool(set(access_terms) & {"emergencyWithdraw", "rescue", "sweep"})
    has_upgrade = bool(set(access_terms) & {"upgradeTo", "upgradeToAndCall", "UUPSUpgradeable", "TransparentUpgradeableProxy", "initializer", "reinitializer", "proxy"})
    has_storage_docs = text_has_any(corpus_text, ["storage layout", "__gap", "storage gap", "upgrade assumption", "upgrade process"])
    has_admin_docs = text_has_any(corpus_text, ["multisig", "timelock", "guardian", "admin role", "role boundary", "owner powers"])

    if has_privileged_setters and not has_role_tests:
        maybe_add(
            "ARK-ACC-001",
            "Medium readiness gap",
            "Privileged setters without role-boundary tests",
            "Privileged setter or role-management signals were detected without visible unauthorized-call coverage.",
            "Add tests proving unauthorized users cannot call privileged setters or role-management functions.",
            ["access-control-review", "admin-risk", "access-control-rule-pack"],
            priority="Medium",
            category="access-control",
            detected=access_terms,
            why_it_matters="Privileged setters can alter fees, oracles, strategies, treasury, roles, pause state, or accounting assumptions.",
            historical_pattern_similarity="Maps to access-control failure classes where privileged paths were under-specified or incorrectly guarded.",
            defensive_checks=["unauthorized setter tests", "role grant/revoke tests", "pause role tests", "timelock/multisig assumptions"],
            suggested_test="For every privileged function, assert an unprivileged caller reverts and the documented role succeeds only within intended bounds.",
        )
    if has_emergency and not text_has_any(corpus_text, ["constraint", "limit", "emergency policy", "rescue policy", "sweep policy"]):
        maybe_add(
            "ARK-ACC-002",
            "Medium readiness gap",
            "Emergency or rescue functions without documented constraints",
            "Emergency, rescue, or sweep signals were detected without clear constraints or policy documentation.",
            "Document emergency powers, asset constraints, recipient restrictions, and user-impact assumptions.",
            ["access-control-review", "emergency-controls", "access-control-rule-pack"],
            priority="Medium",
            category="access-control",
            detected=access_terms,
            why_it_matters="Emergency functions can be necessary but should be constrained and understandable before launch or audit intake.",
            historical_pattern_similarity="Maps to privileged operational risk readiness classes.",
            defensive_checks=["rescue constraints", "sweep asset allowlist/blocklist", "recipient restrictions", "event coverage"],
            suggested_test="Test emergency/rescue functions against allowed and disallowed assets, callers, and protocol states.",
        )
    if has_access and not has_admin_docs:
        maybe_add(
            "ARK-ACC-003",
            "Low readiness gap",
            "Admin role concentration not documented",
            "Admin, owner, guardian, operator, role, multisig, or timelock signals were detected without clear role-concentration documentation.",
            "Document who can change critical configuration and whether controls use a multisig, timelock, guardian, or single owner.",
            ["access-control-review", "documentation-readiness", "access-control-rule-pack"],
            priority="Low",
            category="access-control",
            detected=access_terms,
            why_it_matters="Role concentration affects operational risk and audit scope even when access control code is syntactically correct.",
            historical_pattern_similarity="Maps to operational control readiness classes.",
            defensive_checks=["role matrix", "owner powers", "timelock assumptions", "multisig assumptions"],
            suggested_test="Add a role matrix to docs and unit tests for critical roles.",
        )
    if has_upgrade and not text_has_any(tests, ["initializer", "reinitializer", "upgrade", "upgradeto"]):
        maybe_add(
            "ARK-UPG-001",
            "Medium readiness gap",
            "Upgradeable contract without initializer/upgrade tests",
            "Upgradeable or proxy signals were detected without visible initializer or upgrade authorization tests.",
            "Add tests for initializer-once behavior, unauthorized upgrade rejection, and post-upgrade invariant preservation.",
            ["upgradeability", "initializer", "access-control-rule-pack"],
            priority="Medium",
            category="upgradeability-initialization",
            detected=access_terms,
            why_it_matters="Initialization and upgrade boundaries can affect every storage, accounting, and role assumption in the protocol.",
            historical_pattern_similarity="Maps to initialization and upgrade boundary readiness classes.",
            defensive_checks=["initializer once", "unauthorized upgrade rejection", "post-upgrade invariant", "implementation ownership"],
            suggested_test="Deploy a local proxy or upgradeable instance and assert initialization and upgrade authorization match the documented process.",
        )
    if has_upgrade and not has_storage_docs:
        maybe_add(
            "ARK-UPG-002",
            "Low readiness gap",
            "Storage layout or upgrade assumptions not documented",
            "Upgradeable/proxy signals were detected without visible storage layout or upgrade-process documentation.",
            "Document storage layout, gaps, upgrade procedure, and operational approval assumptions.",
            ["upgradeability", "documentation-readiness", "access-control-rule-pack"],
            priority="Low",
            category="upgradeability-initialization",
            detected=access_terms,
            why_it_matters="Upgrade documentation helps reviewers understand whether future implementations can preserve state safely.",
            historical_pattern_similarity="Maps to upgrade boundary and storage assumption readiness classes.",
            defensive_checks=["storage layout", "__gap usage", "upgrade runbook", "post-upgrade checks"],
            suggested_test="Add storage layout notes and a local upgrade simulation that preserves key invariants.",
        )

    reent_terms = detected_terms(signals, "reentrancy_rule_pack", "reentrancy_value_flow")
    has_reent_surface = bool(set(reent_terms) & {"withdraw", "redeem", "claim", "refund", "safeTransfer", "transferFrom", ".call(", "call{", "callback", "flashLoan", "executeOperation"})
    has_guard = text_has_any(corpus_text, ["nonReentrant", "ReentrancyGuard"])
    has_ordering_docs = text_has_any(corpus_text, ["checks-effects-interactions", "state update before", "reentrancy", "external call ordering"])
    has_claim_refund = bool(set(reent_terms) & {"claim", "refund", "payout"})

    if has_reent_surface and not has_guard:
        maybe_add(
            "ARK-REENT-001",
            "High readiness gap",
            "Value flow with external calls needs reentrancy review",
            "Withdraw, redeem, claim, transfer, callback, or low-level call signals were detected without a visible reentrancy guard signal.",
            "Review state ordering and add local reentrant receiver tests around every value-flow path.",
            ["reentrancy-review", "value-flow", "reentrancy-rule-pack"],
            priority="High",
            category="reentrancy-value-flow",
            detected=reent_terms,
            why_it_matters="External calls can hand control to untrusted code before accounting reaches a safe state.",
            historical_pattern_similarity="Maps to reentrancy and callback-driven value-flow readiness classes.",
            defensive_checks=["state update before external call", "reentrant receiver mock", "failed external call behavior", "single-claim guarantees"],
            suggested_test="Use a local malicious receiver mock and assert withdraw/redeem/claim cannot be executed twice through reentry.",
        )
    if bool(set(reent_terms) & {"onERC721Received", "onERC1155Received", "ERC777", "callback", "flashLoan", "executeOperation"}) and "callback" not in tests:
        maybe_add(
            "ARK-REENT-002",
            "Medium readiness gap",
            "Callback-capable token or receiver path detected",
            "Callback-capable token, receiver, flash loan, or execution callback signals were detected without visible callback tests.",
            "Add local callback tests for token receiver, flash loan, and callback-capable flows.",
            ["reentrancy-review", "callback", "reentrancy-rule-pack"],
            priority="Medium",
            category="reentrancy-value-flow",
            detected=reent_terms,
            why_it_matters="Callback-capable flows can invalidate assumptions about call ordering and intermediate state.",
            historical_pattern_similarity="Maps to callback and reentrancy-sensitive flow readiness classes.",
            defensive_checks=["callback receiver mock", "flash loan callback state", "ERC777/ERC1155/ERC721 receiver behavior"],
            suggested_test="Create a local callback receiver that attempts repeated entry and assert protocol state remains consistent.",
        )
    if has_claim_refund and not text_has_any(tests, ["double", "already claimed", "claim twice", "refund", "state transition"]):
        maybe_add(
            "ARK-REENT-003",
            "Medium readiness gap",
            "Claim/refund flow without state-transition tests",
            "Claim, refund, or payout signals were detected without visible state-transition or double-claim tests.",
            "Add tests for claim/refund mutual exclusion, repeated calls, and failed external transfers.",
            ["reentrancy-review", "claim-flow", "reentrancy-rule-pack"],
            priority="Medium",
            category="reentrancy-value-flow",
            detected=reent_terms,
            why_it_matters="Claim and refund flows often depend on one-way state transitions that should be explicit before audit intake.",
            historical_pattern_similarity="Maps to duplicate-claim and state-transition readiness classes.",
            defensive_checks=["double claim prevention", "claim/refund mutual exclusion", "failed transfer behavior"],
            suggested_test="Assert claim or refund can only happen once per entitlement and failed transfers cannot leave reusable claim state.",
        )
    if has_reent_surface and not has_ordering_docs:
        maybe_add(
            "ARK-REENT-004",
            "Low readiness gap",
            "External call path without documented ordering assumptions",
            "External call/value-flow signals were detected without clear ordering or reentrancy assumption documentation.",
            "Document state-update ordering, callback assumptions, and why any unguarded external calls are safe by design.",
            ["reentrancy-review", "documentation-readiness", "reentrancy-rule-pack"],
            priority="Low",
            category="reentrancy-value-flow",
            detected=reent_terms,
            why_it_matters="Reviewers need clear state-ordering assumptions to evaluate external call safety.",
            historical_pattern_similarity="Maps to checks-effects-interactions and callback boundary readiness classes.",
            defensive_checks=["ordering documentation", "callback assumptions", "external call failure behavior"],
            suggested_test="Pair ordering documentation with a local receiver test that exercises the documented boundary.",
        )

    reward_terms = detected_terms(signals, "reward_rule_pack", "staking_rewards")
    has_reward = bool(set(reward_terms) & {"stake", "unstake", "reward", "rewards", "claim", "rewardPerToken", "accumulator", "index", "emission", "earned", "pendingReward"})
    has_conservation = text_has_any(tests, ["conservation", "funded", "total reward", "totalrewards", "overclaim"])
    has_precision = text_has_any(tests, ["precision", "rounding", "dust", "accumulator", "index"])
    has_double_claim = text_has_any(tests, ["double", "already claimed", "claim twice", "overclaim"])
    has_lock = bool(set(reward_terms) & {"lock", "cooldown", "epoch", "vesting"})
    has_emission_admin = bool(set(reward_terms) & {"notifyRewardAmount", "emission", "emissions"}) and has_privileged_setters

    if has_reward and not has_conservation:
        maybe_add(
            "ARK-RWD-001",
            "Medium readiness gap",
            "Reward accounting without conservation tests",
            "Reward, stake, claim, or accounting signals were detected without visible reward conservation tests.",
            "Add tests proving total claimed plus remaining claimable cannot exceed funded rewards beyond documented rounding.",
            ["reward-accounting", "staking-rule-pack", "pre-audit-readiness"],
            priority="Medium",
            category="reward-accounting",
            detected=reward_terms,
            why_it_matters="Reward systems can silently over-distribute or under-distribute when stake weights, timing, and funding change.",
            historical_pattern_similarity="Maps to reward accounting mismatch readiness classes.",
            defensive_checks=["funded reward conservation", "multi-user distribution", "stake/unstake around reward updates"],
            suggested_test="Fund rewards, run multiple users through stake/claim/unstake sequences, and assert total claimed remains bounded by funded rewards.",
        )
    if has_reward and not has_precision:
        maybe_add(
            "ARK-RWD-002",
            "Medium readiness gap",
            "Accumulator/index logic without precision/rounding tests",
            "Accumulator, index, rewardPerToken, precision, or share signals were detected without visible precision/rounding tests.",
            "Add precision, dust, rounding, and small-balance tests for accumulator or index logic.",
            ["reward-accounting", "precision", "staking-rule-pack"],
            priority="Medium",
            category="reward-accounting",
            detected=reward_terms,
            why_it_matters="Index and accumulator math can leak value or strand rewards through rounding across many users.",
            historical_pattern_similarity="Maps to precision and accounting mismatch readiness classes.",
            defensive_checks=["index monotonicity", "rounding dust", "small balance behavior", "multi-user precision"],
            suggested_test="Fuzz stake sizes and reward amounts and assert reward indexes are monotonic and bounded by funded rewards.",
        )
    if has_reward and bool(set(reward_terms) & {"claim", "claimReward"}) and not has_double_claim:
        maybe_add(
            "ARK-RWD-003",
            "Medium readiness gap",
            "Claim flow without double-claim prevention tests",
            "Claim or claimReward signals were detected without visible repeated-claim or overclaim tests.",
            "Add tests proving users cannot claim the same reward entitlement twice.",
            ["reward-accounting", "claim-flow", "staking-rule-pack"],
            priority="Medium",
            category="reward-accounting",
            detected=reward_terms,
            why_it_matters="Claim flows depend on updating accrued state at exactly the right time.",
            historical_pattern_similarity="Maps to duplicate-claim and reward accounting mismatch classes.",
            defensive_checks=["double claim prevention", "claim state reset", "multi-user claim ordering"],
            suggested_test="Assert claim twice without new rewards returns zero or reverts according to documented policy.",
        )
    if has_lock and not text_has_any(tests, ["cooldown", "epoch", "vesting", "lock"]):
        maybe_add(
            "ARK-RWD-004",
            "Low readiness gap",
            "Lock/cooldown reward lifecycle not tested",
            "Lock, cooldown, epoch, or vesting signals were detected without visible lifecycle tests.",
            "Add tests for stake, lock/cooldown, reward accrual, claim, and unstake lifecycle transitions.",
            ["reward-accounting", "staking-lifecycle", "staking-rule-pack"],
            priority="Low",
            category="reward-accounting",
            detected=reward_terms,
            why_it_matters="Time or epoch-based reward states are easy to mis-handle around boundary transitions.",
            historical_pattern_similarity="Maps to reward lifecycle and state-transition readiness classes.",
            defensive_checks=["epoch boundaries", "cooldown transitions", "vesting claim timing"],
            suggested_test="Advance local time/epochs and assert reward and withdrawal state transitions follow documented policy.",
        )
    if has_emission_admin and not has_admin_docs:
        maybe_add(
            "ARK-RWD-005",
            "Low readiness gap",
            "Emission/admin update assumptions not documented",
            "Emission or reward funding update signals were detected without clear admin or emission-policy documentation.",
            "Document who can update emissions, how reward funding is bounded, and how changes affect accrued users.",
            ["reward-accounting", "admin-risk", "staking-rule-pack"],
            priority="Low",
            category="reward-accounting",
            detected=reward_terms,
            why_it_matters="Emission controls define reward economics and can affect user expectations even if accounting is correct.",
            historical_pattern_similarity="Maps to operational reward-configuration readiness classes.",
            defensive_checks=["emission role bounds", "notifyRewardAmount constraints", "reward funding assumptions"],
            suggested_test="Assert emission updates are role-gated and do not corrupt already accrued rewards.",
        )

    amm_terms = detected_terms(signals, "amm_rule_pack", "amm")
    has_amm_source = bool(amm_terms) and text_has_any(
        solidity_text,
        ["swap", "addliquidity", "removeliquidity", "reserve0", "reserve1", "getreserves", "klast", "liquidity", "getamountout"],
    )
    has_amm_invariant_tests = text_has_any(
        tests,
        ["constant product", "invariant", "reserve accounting", "swap invariant", "liquidity invariant", "x * y"],
    )
    has_lp_share_surface = has_amm_source and text_has_any(solidity_text, ["totalsupply", "balanceof", "mint", "burn", "shares", "pooltoken", "lp"])
    has_lp_share_tests = text_has_any(tests, ["first liquidity", "proportional", "withdrawal", "rounding", "dust", "lp share"])
    has_reserve_price_surface = has_amm_source and text_has_any(solidity_text, ["getamountout", "quote", "spot price", "reserve ratio", "reserve0", "reserve1", "getreserves"])
    has_manipulation_tests = text_has_any(tests, ["twap", "manipulation", "price movement", "bounds", "reserve manipulation", "delay", "spot"])
    has_token_assumption_surface = has_amm_source and text_has_any(solidity_text, ["transferfrom", "amountin", "safetransferfrom", "balancebefore", "balanceafter"])
    has_received_amount_tests_or_docs = text_has_any(corpus_text, ["balancebefore", "balanceafter", "actual received", "fee-on-transfer", "rebasing", "non-standard token", "unsupported token"])
    has_slippage_surface = has_amm_source and text_has_any(solidity_text, ["swap", "amountout", "getamountout"]) and not text_has_any(solidity_text, ["minout", "amountoutmin", "deadline", "slippage"])
    has_slippage_tests = text_has_any(tests, ["minout", "amountoutmin", "deadline", "slippage", "stale quote"])

    if has_amm_source and not has_amm_invariant_tests:
        maybe_add(
            "ARK-AMM-001",
            "High readiness gap",
            "AMM invariant assumptions not covered by tests",
            "AMM reserve, swap, or liquidity signals were detected without visible invariant or reserve-accounting tests.",
            "Add local tests or invariants showing swaps and liquidity operations preserve documented AMM accounting within fee and rounding bounds.",
            ["amm-invariant", "amm-rule-pack", "pre-audit-readiness"],
            priority="High",
            category="amm-invariant",
            detected=amm_terms,
            why_it_matters="AMM correctness depends on reserve accounting, swap bounds, and invariant preservation staying true under fees, rounding, and repeated operations.",
            historical_pattern_similarity="Maps to historical AMM invariant and pool-price accounting readiness classes. This is defensive test inspiration, not vulnerability confirmation.",
            defensive_checks=["swap invariant conservation", "reserve accounting", "add/remove liquidity consistency", "fee and rounding bounds"],
            suggested_test="Assert swaps preserve the documented constant-product or stableswap invariant within expected fee and rounding bounds.",
        )
    if has_lp_share_surface and not has_lp_share_tests:
        maybe_add(
            "ARK-AMM-002",
            "High readiness gap",
            "LP share accounting without mint/burn boundary tests",
            "LP supply, mint, burn, or share-accounting signals were detected without visible first-provider, proportional mint/burn, or rounding boundary tests.",
            "Add tests for first liquidity provider behavior, proportional LP minting/burning, withdrawal rounding, and dust handling.",
            ["amm-lp-accounting", "amm-rule-pack", "share-accounting"],
            priority="High",
            category="amm-lp-accounting",
            detected=amm_terms,
            why_it_matters="LP share accounting controls who owns pool value; boundary mistakes can distort deposits, withdrawals, or low-liquidity behavior.",
            historical_pattern_similarity="Maps to share inflation and liquidity accounting readiness classes.",
            defensive_checks=["first liquidity provider behavior", "proportional minting", "proportional withdrawal", "dust handling"],
            suggested_test="Test first liquidity, repeated add/remove liquidity, and tiny-liquidity burn cases to verify LP shares remain proportional.",
        )
    if has_reserve_price_surface and not has_manipulation_tests:
        maybe_add(
            "ARK-AMM-003",
            "High readiness gap",
            "Spot-price or reserve-price dependency without manipulation-resistance tests",
            "Reserve-ratio, quote, getAmountOut, or spot-price signals were detected without visible TWAP, delay, bounds, or manipulation-resistance tests.",
            "Add local reserve-movement tests and document whether spot, TWAP, or external oracle assumptions are intended.",
            ["amm-pricing", "spot-price", "oracle-risk", "amm-rule-pack"],
            priority="High",
            category="amm-pricing",
            detected=amm_terms,
            why_it_matters="Same-block reserve prices and spot quotes can be poor readiness evidence unless manipulation boundaries are tested or explicitly documented.",
            historical_pattern_similarity="Maps to spot-price and pool-price accounting readiness classes.",
            defensive_checks=["TWAP or delay assumption", "reserve manipulation sanity test", "price movement bounds"],
            suggested_test="Move reserves in a local pool test and assert dependent protocol decisions respect documented price bounds or TWAP assumptions.",
        )
    if has_token_assumption_surface and not has_received_amount_tests_or_docs:
        maybe_add(
            "ARK-AMM-004",
            "Medium readiness gap",
            "Fee-on-transfer or non-standard token assumptions not documented",
            "Token transfer and amountIn accounting signals were detected without clear received-amount tests or non-standard token assumptions.",
            "Document supported token assumptions or add balanceBefore/balanceAfter accounting tests for fee-on-transfer and non-standard token behavior.",
            ["amm-token-assumptions", "fee-on-transfer", "amm-rule-pack"],
            priority="Medium",
            category="amm-token-assumptions",
            detected=amm_terms,
            why_it_matters="AMM pools that assume amountIn equals tokens received may mis-account non-standard tokens unless explicitly unsupported or handled.",
            historical_pattern_similarity="Maps to fee-on-transfer and token accounting assumption readiness classes.",
            defensive_checks=["actual received amount accounting", "fee-on-transfer simulation", "unsupported token documentation"],
            suggested_test="Use a local fee-on-transfer token mock or document that such tokens are unsupported and guarded by configuration.",
        )
    if has_slippage_surface and not has_slippage_tests:
        maybe_add(
            "ARK-AMM-005",
            "Medium readiness gap",
            "Slippage/min-output constraints missing or unclear",
            "Swap path signals were detected without clear minOut, deadline, slippage, or stale-quote constraints.",
            "Add user-provided min-output and stale-quote tests, or document why swaps are not user-facing and how price movement is bounded.",
            ["amm-slippage", "min-output", "amm-rule-pack"],
            priority="Medium",
            category="amm-slippage",
            detected=amm_terms,
            why_it_matters="Slippage and stale quote controls help users and integrations bound expected outcomes around swaps.",
            historical_pattern_similarity="Maps to price boundary and quote freshness readiness classes.",
            defensive_checks=["minOut enforcement", "deadline behavior", "stale quote handling"],
            suggested_test="Assert swaps revert or follow documented policy when amountOut falls below a user-provided bound or quote is stale.",
        )

    lending_terms = detected_terms(signals, "lending_rule_pack", "lending")
    has_lending_source = bool(lending_terms) and text_has_any(
        solidity_text,
        ["borrow", "repay", "collateral", "debt", "healthfactor", "liquidate", "liquidation", "totalborrows"],
    )
    has_solvency_tests = text_has_any(tests, ["solvency", "collateral debt", "healthfactor", "ltv", "collateralization", "unsafe withdrawal"])
    has_liquidation_surface = has_lending_source and text_has_any(solidity_text, ["liquidate", "liquidation", "liquidationthreshold", "liquidationbonus", "closefactor", "seize"])
    has_liquidation_tests = text_has_any(tests, ["just above", "just below", "threshold", "liquidation bonus", "closefactor", "partial liquidation", "over-seizure"])
    has_interest_surface = has_lending_source and text_has_any(solidity_text, ["interestindex", "borrowindex", "exchangerate", "utilization", "accrueinterest", "ratepersecond", "scaledbalance", "principal"])
    has_interest_tests = text_has_any(tests, ["monotonic", "rounding", "small balance", "time-step", "accrual", "borrowindex", "interest"])
    has_lending_oracle_surface = has_lending_source and has_meaningful_oracle_signal(signals) and text_has_any(solidity_text, ["healthfactor", "collateralvalue", "borrow", "liquidate", "liquidation"])
    has_lending_oracle_tests = text_has_any(tests, ["stale", "updatedat", "heartbeat", "decimals", "price shock", "invalid price", "oracle"])
    has_cash_surface = has_lending_source and text_has_any(solidity_text, ["cash", "reserves", "totalborrows", "totalreserves", "available liquidity", "utilization"])
    has_cash_tests = text_has_any(tests, ["available liquidity", "cash", "reserve", "repay updates", "utilization", "cannot exceed liquidity"])
    has_liquidation_roles = has_liquidation_surface and text_has_any(solidity_text, ["liquidator", "keeper", "owner", "guardian", "pause", "whitelist", "onlyowner", "onlyrole"])
    has_liquidation_role_docs = text_has_any(corpus_text, ["liquidator role", "keeper", "paused market", "guardian", "whitelist", "liquidation role", "emergency control"])

    if has_lending_source and not has_solvency_tests:
        maybe_add(
            "ARK-LEND-001",
            "High readiness gap",
            "Collateral/debt solvency invariant not covered by tests",
            "Collateral, debt, borrow, repay, or health-factor signals were detected without visible solvency invariant tests.",
            "Add collateral/debt invariants and boundary tests for borrow, repay, deposit, withdrawal, and liquidation readiness.",
            ["lending-solvency", "lending-rule-pack", "pre-audit-readiness"],
            priority="High",
            category="lending-solvency",
            detected=lending_terms,
            why_it_matters="Lending systems depend on collateral and debt accounting staying aligned across every user action.",
            historical_pattern_similarity="Maps to collateral/debt invariant and oracle-dependent lending readiness classes. This is defensive review context, not vulnerability confirmation.",
            defensive_checks=["collateral debt invariant", "unsafe withdrawal rejection", "borrow limit boundary", "repay/deposit accounting"],
            suggested_test="Assert debt cannot exceed documented collateral constraints and collateral withdrawals cannot make a position unsafe unless intended and tested.",
        )
    if has_liquidation_surface and not has_liquidation_tests:
        maybe_add(
            "ARK-LEND-002",
            "High readiness gap",
            "Liquidation boundary tests missing",
            "Liquidation, threshold, bonus, close factor, or seize signals were detected without visible just-above/just-below boundary tests.",
            "Add tests for liquidation thresholds, partial liquidation, bonus bounds, and over-seizure prevention.",
            ["lending-liquidation", "liquidation-boundary", "lending-rule-pack"],
            priority="High",
            category="lending-liquidation",
            detected=lending_terms,
            why_it_matters="Liquidation boundary errors can reject valid liquidations, liquidate solvent positions, or distort seized collateral accounting.",
            historical_pattern_similarity="Maps to liquidation boundary and collateral accounting readiness classes.",
            defensive_checks=["just-above threshold", "just-below threshold", "bonus bounds", "partial liquidation math"],
            suggested_test="Test a position just above threshold cannot be liquidated and a position just below threshold can be liquidated within documented bonus bounds.",
        )
    if has_interest_surface and not has_interest_tests:
        maybe_add(
            "ARK-LEND-003",
            "Medium readiness gap",
            "Interest/index accounting not covered by rounding and time-step tests",
            "Interest index, borrow index, exchange rate, utilization, or accrual signals were detected without visible rounding and time-step tests.",
            "Add tests for accrual monotonicity, small-balance rounding, borrow/repay around accrual, and repeated accrual drift.",
            ["lending-interest-index", "precision", "lending-rule-pack"],
            priority="Medium",
            category="lending-interest-index",
            detected=lending_terms,
            why_it_matters="Interest/index accounting can drift when rates, time steps, small balances, and repeated accrual interact.",
            historical_pattern_similarity="Maps to accounting index drift and precision readiness classes.",
            defensive_checks=["index monotonicity", "small-balance rounding", "borrow/repay around accrual", "drift bound"],
            suggested_test="Advance local time across multiple accrual steps and assert borrow indexes and balances remain monotonic and bounded by documented rounding.",
        )
    if has_lending_oracle_surface and not has_lending_oracle_tests:
        maybe_add(
            "ARK-LEND-004",
            "High readiness gap",
            "Oracle-dependent borrowing/liquidation without stale-price tests",
            "Borrowing, collateral valuation, health-factor, or liquidation logic appears oracle-dependent without visible stale-price or price-shock tests.",
            "Add local oracle tests for stale prices, decimals normalization, price shocks, invalid prices, and liquidation after oracle updates.",
            ["lending-oracle", "oracle-risk", "lending-rule-pack"],
            priority="High",
            category="lending-oracle",
            detected=sorted(set(lending_terms + oracle_terms)),
            why_it_matters="Lending solvency can be distorted when collateral values depend on stale, invalid, or mis-normalized prices.",
            historical_pattern_similarity="Maps to oracle-dependent liquidation and collateral valuation readiness classes.",
            defensive_checks=["stale oracle rejection", "decimals normalization", "price shock boundary", "borrow blocked on invalid price"],
            suggested_test="Mock stale, invalid, and sharply moved prices and assert borrow/liquidation behavior follows documented policy.",
        )
    if has_cash_surface and not has_cash_tests:
        maybe_add(
            "ARK-LEND-005",
            "Medium readiness gap",
            "Reserve/cash accounting assumptions not covered",
            "Cash, reserves, total borrows, utilization, or available-liquidity signals were detected without visible cash/debt consistency tests.",
            "Add tests proving borrow cannot exceed available liquidity and repay/reserve updates keep cash and debt accounting consistent.",
            ["lending-liquidity", "reserve-accounting", "lending-rule-pack"],
            priority="Medium",
            category="lending-liquidity",
            detected=lending_terms,
            why_it_matters="Reserve and cash accounting define whether borrowers can draw liquidity and whether repayments restore accounting state.",
            historical_pattern_similarity="Maps to cash/debt mismatch and liquidity accounting readiness classes.",
            defensive_checks=["available liquidity bound", "repay updates cash/debt", "reserve withdrawal constraints", "utilization bounds"],
            suggested_test="Assert borrow reverts above available liquidity and repay updates cash, debt, reserves, and utilization consistently.",
        )
    if has_liquidation_roles and not (has_role_tests or has_liquidation_role_docs):
        maybe_add(
            "ARK-LEND-006",
            "Low readiness gap",
            "Liquidation/access-control interaction not documented",
            "Liquidation role, keeper, guardian, pause, whitelist, or owner signals were detected without clear role-boundary tests or documentation.",
            "Document liquidation role boundaries and add tests for unauthorized liquidator restrictions, pause behavior, and emergency controls where applicable.",
            ["lending-access-control", "liquidation-boundary", "access-control-review", "lending-rule-pack"],
            priority="Low",
            category="lending-access-control",
            detected=lending_terms,
            why_it_matters="Liquidation and pause controls can change who may act during stressed market states.",
            historical_pattern_similarity="Maps to privileged operation and liquidation boundary readiness classes.",
            defensive_checks=["liquidator authorization", "paused-market behavior", "guardian bounds", "role documentation"],
            suggested_test="Assert paused-market and liquidation role behavior matches documented policy for authorized and unauthorized callers.",
        )


RULE_PACK_DEFINITIONS = {
    "vault": {
        "label": "Vault Rule Pack",
        "signal_categories": ["vault_erc4626", "vault_accounting", "vault_accounting_risk", "vault_strategy", "vault_withdrawal_liquidity", "vault_admin_ops"],
        "finding_prefixes": ["ARK-VLT"],
        "docs": "docs/VAULT_RULE_PACK.md",
        "suggested_tests": ["totalAssets consistency", "deposit/withdraw roundtrip", "share conversion rounding", "strategy gain/loss lifecycle"],
    },
    "oracle": {
        "label": "Oracle Rule Pack",
        "signal_categories": ["oracle_rule_pack", "oracle", "vault_pricing"],
        "finding_prefixes": ["ARK-ORC"],
        "docs": "docs/ORACLE_RULE_PACK.md",
        "suggested_tests": ["stale price rejection", "decimals normalization", "price bounds", "TWAP vs spot behavior"],
    },
    "access_control_upgradeability": {
        "label": "Access Control / Upgradeability Rule Pack",
        "signal_categories": ["access_upgrade_rule_pack", "access_control", "upgradeability"],
        "finding_prefixes": ["ARK-ACC", "ARK-UPG"],
        "docs": "docs/ACCESS_CONTROL_RULE_PACK.md",
        "suggested_tests": ["unauthorized setter tests", "pause/emergency boundaries", "initializer once", "upgrade authorization"],
    },
    "reentrancy_value_flow": {
        "label": "Reentrancy / Value Flow Rule Pack",
        "signal_categories": ["reentrancy_rule_pack", "reentrancy_value_flow"],
        "finding_prefixes": ["ARK-REENT"],
        "docs": "docs/REENTRANCY_VALUE_FLOW_RULE_PACK.md",
        "suggested_tests": ["reentrant receiver mock", "state update ordering", "double claim prevention", "failed external call behavior"],
    },
    "reward_accounting": {
        "label": "Staking / Reward Accounting Rule Pack",
        "signal_categories": ["reward_rule_pack", "staking_rewards", "accounting_complexity"],
        "finding_prefixes": ["ARK-RWD"],
        "docs": "docs/REWARD_ACCOUNTING_RULE_PACK.md",
        "suggested_tests": ["reward conservation", "no overclaim", "index monotonicity", "stake/unstake/claim lifecycle"],
    },
    "amm": {
        "label": "AMM Rule Pack",
        "signal_categories": ["amm_rule_pack", "amm"],
        "finding_prefixes": ["ARK-AMM"],
        "docs": "docs/AMM_RULE_PACK.md",
        "suggested_tests": ["swap invariant conservation", "LP share proportionality", "TWAP or reserve bounds", "minOut enforcement"],
    },
    "lending": {
        "label": "Lending Rule Pack",
        "signal_categories": ["lending_rule_pack", "lending"],
        "finding_prefixes": ["ARK-LEND"],
        "docs": "docs/LENDING_RULE_PACK.md",
        "suggested_tests": ["collateral/debt invariant", "liquidation boundary tests", "interest index monotonicity", "oracle shock tests"],
    },
}


def build_rule_packs(
    signals: dict[str, dict[str, object]],
    gaps: list[ReadinessGap],
    suppressed_gaps: list[ReadinessGap],
) -> dict[str, dict[str, object]]:
    all_findings = gaps + suppressed_gaps
    rule_packs: dict[str, dict[str, object]] = {}
    for key, definition in RULE_PACK_DEFINITIONS.items():
        signal_terms_found: set[str] = set()
        signal_files: set[str] = set()
        for category in definition["signal_categories"]:
            data = signals.get(category, {})
            signal_terms_found.update(str(term) for term in data.get("terms", []))
            signal_files.update(str(path) for path in data.get("files", []))
        prefixes = tuple(definition["finding_prefixes"])
        pack_findings = [finding_to_dict(gap) for gap in all_findings if gap.id.startswith(prefixes)]
        rule_packs[key] = {
            "label": definition["label"],
            "detected": bool(signal_terms_found or pack_findings),
            "signal_count": len(signal_terms_found),
            "signals": sorted(signal_terms_found),
            "files": sorted(signal_files)[:25],
            "findings": pack_findings,
            "finding_count": len(pack_findings),
            "suggested_tests": definition["suggested_tests"],
            "docs": definition["docs"],
        }
    return rule_packs


CONFIDENCE_ORDER = {"low": 0, "medium": 1, "high": 2}


def confidence_meets(value: str, minimum: str) -> bool:
    return CONFIDENCE_ORDER.get(value.lower(), 0) >= CONFIDENCE_ORDER.get(minimum.lower(), 0)


def downgrade_priority(priority: str, target: str = "Low") -> str:
    if "critical" in priority.lower() or "high" in priority.lower() or "medium" in priority.lower():
        return f"{target} readiness gap"
    return priority


def semantic_functions_for_gap(gap: ReadinessGap, semantic: dict[str, object]) -> list[dict[str, object]]:
    functions = flatten_semantic_functions(semantic)
    category = gap.category.lower()
    title = gap.title.lower()

    def name_has(function: dict[str, object], terms: Iterable[str]) -> bool:
        name = str(function.get("name", "")).lower()
        return any(term in name for term in terms)

    if "oracle" in category or "oracle" in title:
        return [function for function in functions if function.get("oracle_calls")]
    if "reentrancy" in category or "value flow" in title:
        return [
            function
            for function in functions
            if function.get("external_calls")
            and (name_has(function, ["withdraw", "redeem", "claim", "refund", "unstake", "payout"]) or function.get("writes_state"))
        ]
    if "access" in category or "admin" in title or "privileged" in title:
        return [
            function
            for function in functions
            if function.get("visibility") in {"public", "external"}
            and (
                name_has(function, ["set", "update", "configure", "pause", "unpause", "rescue", "sweep"])
                or any(str(modifier).lower() in {"onlyowner", "onlyrole"} for modifier in function.get("modifiers", []))
            )
        ]
    if "upgrade" in category or "initializer" in title:
        return [
            function
            for function in functions
            if name_has(function, ["upgrade", "initialize"])
            or any("initializer" in str(modifier).lower() for modifier in function.get("modifiers", []))
        ]
    if "reward" in category or "reward" in title or "staking" in gap.tags:
        return [
            function
            for function in functions
            if name_has(function, ["stake", "unstake", "claim", "reward", "earned", "notify"])
            or any("reward" in str(item).lower() or "accumulator" in str(item).lower() for item in function.get("reads_state", []) + function.get("writes_state", []))
        ]
    if "amm" in category or "amm" in title or "liquidity" in title:
        return [
            function
            for function in functions
            if name_has(function, ["swap", "addliquidity", "removeliquidity", "getamountout", "quote", "mint", "burn"])
            or any("reserve" in str(item).lower() or "liquidity" in str(item).lower() or "klast" in str(item).lower() for item in function.get("reads_state", []) + function.get("writes_state", []))
        ]
    if "lending" in category or "liquidation" in category or "collateral" in title or "borrow" in title:
        return [
            function
            for function in functions
            if name_has(function, ["borrow", "repay", "liquidate", "healthfactor", "accrueinterest", "withdrawcollateral", "depositcollateral"])
            or any("collateral" in str(item).lower() or "debt" in str(item).lower() or "borrow" in str(item).lower() for item in function.get("reads_state", []) + function.get("writes_state", []))
        ]
    if "vault" in category or "vault" in title or "erc4626" in gap.tags:
        return [
            function
            for function in functions
            if name_has(function, ["deposit", "withdraw", "redeem", "mint", "totalassets", "convert", "preview"])
        ]
    return []


def semantic_evidence_from_function(gap: ReadinessGap, function: dict[str, object]) -> dict[str, object]:
    if function.get("oracle_calls"):
        reason = "Solidity function contains oracle or price-feed call evidence."
        snippet = str(function.get("snippet") or ", ".join(str(item) for item in function.get("oracle_calls", [])))
    elif function.get("external_calls"):
        reason = "Solidity function contains external value-flow call evidence."
        snippet = str(function.get("snippet") or ", ".join(str(item) for item in function.get("external_calls", [])))
    elif function.get("modifiers"):
        reason = "Solidity function contains access-control or lifecycle modifier evidence."
        snippet = ", ".join(str(item) for item in function.get("modifiers", []))
    else:
        reason = "Solidity function shape matches this readiness finding."
        snippet = str(function.get("snippet") or function.get("name", ""))
    return {
        "type": "semantic-lite",
        "file": str(function.get("file", "")),
        "contract": str(function.get("contract", "")),
        "function": str(function.get("name", "")),
        "line": int(function.get("line_start", 1) or 1),
        "snippet": snippet[:180],
        "reason": reason,
    }


def test_coverage_for_gap(gap: ReadinessGap, semantic: dict[str, object]) -> tuple[bool, str]:
    signals = semantic.get("signals", {})
    coverage = signals.get("test_coverage", {}) if isinstance(signals, dict) else {}
    if not isinstance(coverage, dict):
        return False, ""
    category = gap.category.lower()
    title = gap.title.lower()
    mapping = [
        ("oracle", ["oracle", "stale", "price"]),
        ("access_control", ["access", "admin", "privileged", "upgrade", "initializer"]),
        ("reentrancy", ["reentrancy", "value flow", "external call", "claim/refund"]),
        ("reward", ["reward", "staking", "accumulator", "claim flow"]),
        ("vault", ["vault", "erc4626", "share", "totalassets"]),
        ("amm", ["amm", "liquidity", "reserve", "slippage", "lp share"]),
        ("lending", ["lending", "liquidation", "collateral", "debt", "borrow"]),
    ]
    for key, terms in mapping:
        if any(term in category or term in title for term in terms):
            matched = coverage.get(key, [])
            if isinstance(matched, list) and matched:
                return True, f"Matching test coverage terms detected: {', '.join(str(item) for item in matched[:8])}."
            return False, f"No semantic-lite {key.replace('_', ' ')} test coverage terms were detected."
    return False, ""


def slither_evidence_for_gap(gap: ReadinessGap, slither: dict[str, object]) -> list[dict[str, object]]:
    detectors = slither.get("detectors", [])
    if not isinstance(detectors, list):
        return []
    category = gap.category.lower()
    keywords: list[str] = []
    if "reentrancy" in category:
        keywords = ["reentrancy"]
    elif "access" in category:
        keywords = ["access", "controlled", "owner", "privilege"]
    elif "upgrade" in category:
        keywords = ["upgrade", "initialize", "proxy"]
    elif "oracle" in category:
        keywords = ["oracle", "price", "timestamp"]
    elif "reward" in category:
        keywords = ["divide", "precision", "erc20"]
    elif "amm" in category:
        keywords = ["divide", "precision", "erc20", "price", "constant", "unused"]
    elif "lending" in category or "liquidation" in category:
        keywords = ["divide", "precision", "price", "timestamp", "erc20"]
    evidence = []
    for detector in detectors:
        if not isinstance(detector, dict):
            continue
        text = f"{detector.get('check', '')} {detector.get('description', '')}".lower()
        if keywords and not any(keyword in text for keyword in keywords):
            continue
        element = {}
        elements = detector.get("elements", [])
        if isinstance(elements, list) and elements and isinstance(elements[0], dict):
            element = elements[0]
        evidence.append(
            {
                "type": "slither",
                "file": str(element.get("file", "")),
                "function": str(element.get("name", "")),
                "line": int(element.get("line", 1) or 1),
                "snippet": str(detector.get("check", "")),
                "reason": f"Optional local Slither detector signal: {detector.get('impact', '')}/{detector.get('confidence', '')}.",
            }
        )
    return evidence[:3]


def keyword_evidence_for_gap(gap: ReadinessGap) -> list[dict[str, object]]:
    evidence = []
    for path in gap.affected_files[:3]:
        evidence.append(
            {
                "type": "keyword",
                "file": path,
                "function": "",
                "line": 1,
                "snippet": ", ".join(gap.detected[:8]),
                "reason": "Keyword signal matched this readiness finding.",
            }
        )
    return evidence


NEGATIVE_EVIDENCE_GAP_TERMS = {
    "oracle": ["stale oracle", "oracle freshness", "updatedAt", "heartbeat", "stale oracle tests"],
    "access": ["access-control", "unauthorized", "onlyOwner test", "role-boundary"],
    "upgrade": ["access-control", "onlyOwner test", "role-boundary"],
    "reentrancy": ["reentrancy", "callback", "reentrancy/callback tests"],
    "reward": ["reward conservation", "reward conservation tests", "double-claim"],
    "vault": ["invariant", "invariant tests", "share accounting", "totalAssets", "solvency"],
    "testing": ["invariant", "invariant tests", "fuzz"],
    "amm": ["constant product", "amm invariant", "slippage", "lp share accounting", "fee-on-transfer"],
    "lending": ["liquidation boundary", "collateral debt", "solvency", "interest index", "borrow index"],
}


def negative_evidence_for_gap(
    gap: ReadinessGap,
    negative_evidence: list[dict[str, object]],
    limit: int = 5,
) -> list[dict[str, object]]:
    category = gap.category.lower()
    title = gap.title.lower()
    keys = [
        key
        for key in NEGATIVE_EVIDENCE_GAP_TERMS
        if key in category or key in title or (key == "testing" and ("test" in category or "test" in title))
    ]
    if not keys:
        keys = ["testing"]
    wanted = {term.lower() for key in keys for term in NEGATIVE_EVIDENCE_GAP_TERMS.get(key, [])}
    matched: list[dict[str, object]] = []
    for item in negative_evidence:
        term = str(item.get("term", "")).lower()
        if term in wanted or any(part in term or term in part for part in wanted):
            matched.append(item)
    return matched[:limit]


def finding_has_semantic_support(gap: ReadinessGap, semantic: dict[str, object]) -> bool:
    signals = semantic.get("signals", {}) if isinstance(semantic.get("signals"), dict) else {}
    category = gap.category.lower()
    title = gap.title.lower()
    if "oracle" in category or "oracle" in title:
        return bool(signals.get("has_oracle_calls"))
    if "reentrancy" in category or "value flow" in title:
        return bool(signals.get("has_external_value_flow"))
    if "access" in category or "admin" in title or "privileged" in title:
        return bool(signals.get("has_admin_setters"))
    if "upgrade" in category:
        return bool(signals.get("has_upgradeability"))
    if "reward" in category or "reward" in title:
        return bool(signals.get("has_reward_accounting"))
    if "vault" in category or "vault" in title:
        return bool(signals.get("has_vault_functions"))
    if "amm" in category or "amm" in title or "liquidity" in title:
        return bool(signals.get("has_amm_functions"))
    if "lending" in category or "liquidation" in category or "collateral" in title or "borrow" in title:
        return bool(signals.get("has_lending_functions"))
    return False


def confidence_reason_for(
    has_semantic: bool,
    has_test_coverage: bool,
    slither_evidence: list[dict[str, object]],
    keyword_only: bool,
    negative_items: list[dict[str, object]] | None = None,
) -> str:
    if negative_items and has_semantic and not has_test_coverage:
        return "Semantic-lite Solidity evidence was detected, and explicit missing-test coverage statements were found."
    if negative_items and not has_test_coverage:
        return "Explicit missing-test coverage statements were detected; Arkheionx did not count them as positive coverage."
    if negative_items and has_test_coverage:
        return "Related test coverage terms were found, but conflicting missing-coverage statements require manual review."
    if has_semantic and not has_test_coverage:
        return "Semantic-lite Solidity evidence was detected and matching test coverage evidence was not found."
    if has_semantic and has_test_coverage:
        return "Semantic-lite Solidity evidence was detected, and related test coverage terms were also found; priority may be reduced."
    if slither_evidence:
        return "Optional local Slither evidence was attached to this readiness finding."
    if keyword_only:
        return "Keyword-only signal detected without Solidity function-level evidence; manual review is recommended before remediation."
    return "Evidence was derived from local/static repository signals."


def attach_evidence_and_calibrate(
    gaps: list[ReadinessGap],
    semantic: dict[str, object],
    slither: dict[str, object],
    analysis_config: dict[str, object],
    protocol_type: str,
    negative_evidence: list[dict[str, object]] | None = None,
) -> list[ReadinessGap]:
    max_evidence = int(analysis_config.get("max_evidence_per_finding", 5))
    downgrade_keyword_only = bool(analysis_config.get("downgrade_keyword_only", True))
    for gap in gaps:
        semantic_functions = semantic_functions_for_gap(gap, semantic) if semantic.get("enabled") else []
        semantic_evidence = [semantic_evidence_from_function(gap, function) for function in semantic_functions[:max_evidence]]
        has_test_coverage, coverage_note = test_coverage_for_gap(gap, semantic)
        test_evidence: list[dict[str, object]] = []
        if coverage_note:
            test_evidence.append(
                {
                    "type": "test-coverage",
                    "file": "",
                    "function": "",
                    "line": 1,
                    "snippet": "",
                    "reason": coverage_note,
                }
            )
        slither_items = slither_evidence_for_gap(gap, slither)
        keyword_items = keyword_evidence_for_gap(gap)
        negative_items = negative_evidence_for_gap(gap, negative_evidence or [], max_evidence)
        evidence = (semantic_evidence + test_evidence + slither_items + keyword_items)[:max_evidence]
        gap.evidence = evidence
        gap.negative_evidence = negative_items
        gap.detection_sources = sorted({str(item.get("type", "")) for item in evidence if item.get("type")})
        if negative_items and "negative-test-coverage" not in gap.detection_sources:
            gap.detection_sources.append("negative-test-coverage")
            gap.detection_sources = sorted(gap.detection_sources)
        gap.affected_functions = sorted({str(item.get("function", "")) for item in evidence if item.get("function")})
        gap.affected_contracts = sorted({str(item.get("contract", "")) for item in evidence if item.get("contract")})
        if evidence:
            first = evidence[0]
            location = str(first.get("file", ""))
            function = str(first.get("function", ""))
            gap.evidence_summary = f"{location}" + (f" in `{function}`" if function else "")
            if first.get("reason"):
                gap.evidence_summary += f": {first.get('reason')}"
        has_semantic = bool(semantic_evidence) or finding_has_semantic_support(gap, semantic)
        keyword_only = not has_semantic and not slither_items
        if has_semantic and not has_test_coverage:
            gap.confidence = "high" if gap.confidence != "low" else "medium"
        elif has_semantic and has_test_coverage:
            gap.confidence = "medium"
            if "high" in gap.priority.lower():
                gap.priority = "Medium readiness gap"
                gap.severity = "Medium readiness gap"
        elif keyword_only and downgrade_keyword_only:
            gap.confidence = "low"
            gap.priority = downgrade_priority(gap.priority, "Low")
            if "critical" in gap.severity.lower() or "high" in gap.severity.lower() or "medium" in gap.severity.lower():
                gap.severity = "Low readiness gap"
            gap.false_positive_notes = (
                "Keyword-only signal without Solidity function-level evidence. Review manually before creating remediation tasks."
            )
        gap.confidence_reason = confidence_reason_for(has_semantic, has_test_coverage, slither_items, keyword_only, negative_items)
        if negative_items and not gap.false_positive_notes:
            gap.false_positive_notes = "Explicit missing coverage was detected in local files. Review whether the missing coverage has since been added before suppressing this finding."
        gap.fingerprint = compute_finding_fingerprint(gap, protocol_type)
    return gaps


def analysis_quality(
    semantic: dict[str, object],
    slither: dict[str, object],
    test_readiness: dict[str, object],
) -> dict[str, object]:
    slither_status = "disabled"
    if slither.get("enabled") and slither.get("available"):
        slither_status = f"enabled ({slither.get('source', 'unknown')})"
    elif slither.get("enabled"):
        slither_status = "unavailable"
    return {
        "keyword_scan": "enabled",
        "semantic_lite": "enabled" if semantic.get("enabled") else "disabled",
        "semantic_contracts": len(semantic.get("contracts", [])) if isinstance(semantic.get("contracts"), list) else 0,
        "semantic_test_files": len(semantic.get("test_files", [])) if isinstance(semantic.get("test_files"), list) else 0,
        "slither": slither_status,
        "slither_detector_count": len(slither.get("detectors", [])) if isinstance(slither.get("detectors"), list) else 0,
        "test_coverage_mapping": "enabled",
        "invariant_tests": bool(test_readiness.get("invariant_tests")),
        "fuzz_tests": bool(test_readiness.get("fuzz_tests")),
        "negative_evidence_count": int(test_readiness.get("negative_evidence_count", 0) or 0),
        "warnings": list(semantic.get("warnings", [])) + list(slither.get("warnings", [])),
    }


def write_slither_summary(path: Path, summary: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def apply_suppressions(
    gaps: list[ReadinessGap],
    config: dict[str, object],
) -> tuple[list[ReadinessGap], list[ReadinessGap]]:
    suppressions = config_suppressions(config)

    def matching_suppression(gap: ReadinessGap) -> dict[str, str] | None:
        for configured_id, suppression in suppressions.items():
            prefix = configured_id.rstrip("*")
            id_matches = gap.id == configured_id or (prefix and gap.id.startswith(prefix))
            if not id_matches:
                continue
            path_filter = suppression.get("path", "").strip()
            if path_filter:
                affected = gap.affected_files or []
                if not any(path_matches_glob(path, path_filter) or path.startswith(path_filter.rstrip("/") + "/") for path in affected):
                    continue
            return suppression
        return None

    active: list[ReadinessGap] = []
    suppressed: list[ReadinessGap] = []
    for gap in gaps:
        suppression = matching_suppression(gap)
        if suppression and gap.suppressible:
            gap.suppression = suppression
            suppressed.append(gap)
        else:
            active.append(gap)
    return active, suppressed


def finding_to_dict(gap: ReadinessGap) -> dict[str, object]:
    test_plan = test_plan_for_id(gap.id)
    data: dict[str, object] = {
        "id": gap.id,
        "fingerprint": gap.fingerprint,
        "title": gap.title,
        "category": gap.category,
        "priority": gap.priority,
        "severity": gap.severity,
        "confidence": gap.confidence,
        "confidence_reason": gap.confidence_reason,
        "evidence": gap.evidence,
        "negative_evidence": gap.negative_evidence,
        "evidence_summary": gap.evidence_summary,
        "evidence_count": len(gap.evidence),
        "negative_evidence_count": len(gap.negative_evidence),
        "detection_sources": gap.detection_sources,
        "detected_signals": gap.detected,
        "affected_files": gap.affected_files,
        "affected_functions": gap.affected_functions,
        "affected_contracts": gap.affected_contracts,
        "false_positive_notes": gap.false_positive_notes,
        "why_it_matters": gap.why_it_matters,
        "historical_pattern_similarity": gap.historical_pattern_similarity,
        "recommended_defensive_checks": gap.defensive_checks,
        "suggested_tests": mapped_suggested_tests(gap),
        "invariant_candidates": mapped_invariant_candidates(gap),
        "test_plan": {
            "mapped": bool(test_plan),
            "rule_family": test_plan.get("rule_family", ""),
            "foundry_skeleton_functions": test_plan.get("foundry_skeleton_functions", []),
            "required_project_bindings": test_plan.get("required_project_bindings", []),
            "manual_review_notes": test_plan.get("manual_review_notes", []),
            "safety_notes": test_plan.get("safety_notes", []),
        },
        "knowledge": related_knowledge_for_id(gap.id),
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
        "confidence_reason": gap.confidence_reason,
        "fingerprint": gap.fingerprint,
        "affected_files": gap.affected_files,
        "affected_functions": gap.affected_functions,
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
        "schema_version": SCHEMA_VERSION,
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
        "schema_version": SCHEMA_VERSION,
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
        "schema_version": SCHEMA_VERSION,
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
    best_evidence = next(
        (
            item
            for item in gap.evidence
            if item.get("type") in {"semantic-lite", "slither"} and item.get("file")
        ),
        None,
    )
    if best_evidence:
        uri = str(best_evidence.get("file", ""))
        try:
            line = int(best_evidence.get("line", 1) or 1)
        except (TypeError, ValueError):
            line = 1
    else:
        uri = gap.affected_files[0] if gap.affected_files else ("README.md" if (root / "README.md").exists() else ".")
        line = 1
    return {
        "physicalLocation": {
            "artifactLocation": {"uri": uri, "uriBaseId": "%SRCROOT%"},
            "region": {"startLine": max(1, line)},
        }
    }


def finding_to_sarif_rule(gap: ReadinessGap) -> dict[str, object]:
    checks = list(gap.defensive_checks or [gap.recommendation])
    tests = mapped_suggested_tests(gap)[:3]
    candidates = mapped_invariant_candidates(gap)[:3]
    help_lines = [f"- {check}" for check in checks]
    if tests:
        help_lines.append("")
        help_lines.append("Suggested defensive tests:")
        help_lines.extend(f"- {test}" for test in tests)
    if candidates:
        help_lines.append("")
        help_lines.append("Invariant candidates:")
        help_lines.extend(f"- {candidate}" for candidate in candidates)
    help_text = "\n".join(help_lines)
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
            "confidence_reason": gap.confidence_reason,
            "evidence_count": len(gap.evidence),
            "negative_evidence_count": len(gap.negative_evidence),
            "detection_sources": gap.detection_sources,
            "affected_functions": gap.affected_functions,
            "false_positive_notes": gap.false_positive_notes,
            "category": gap.category,
            "historical_pattern_similarity": gap.historical_pattern_similarity,
            "knowledge": related_knowledge_for_id(gap.id),
            "suggested_tests": mapped_suggested_tests(gap),
            "invariant_candidates": mapped_invariant_candidates(gap),
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
    rule_packs: dict[str, dict[str, object]],
    analysis_quality_data: dict[str, object],
    scan_sources: dict[str, object],
    score: int,
    score_breakdown: dict[str, dict[str, object]],
    gaps: list[ReadinessGap],
    suppressed_gaps: list[ReadinessGap],
    invariants: list[dict[str, str]],
    next_steps: list[str],
    skeleton_path: Path | None,
    generated_outputs: dict[str, str],
    config_summary_data: dict[str, object],
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
    lines.append("## Config Summary")
    lines.append("")
    lines.append(f"- Config source: `{config_summary_data.get('config_source', '') or 'defaults'}`")
    lines.append(f"- Effective protocol type: `{config_summary_data.get('protocol_type_effective', protocol_type)}`")
    lines.append(f"- Enabled rule packs: `{', '.join(str(item) for item in config_summary_data.get('enabled_rule_packs', []))}`")
    lines.append(f"- Minimum confidence: `{config_summary_data.get('min_confidence', 'low')}`")
    lines.append(f"- Suppressions configured: `{config_summary_data.get('suppressions_count', 0)}`")
    lines.append(f"- Output profile: `{config_summary_data.get('output_profile', 'standard')}`")
    lines.append("")
    lines.append("## Scan Source Summary")
    lines.append("")
    lines.append(f"- Files considered: `{scan_sources.get('files_considered', 0)}`")
    lines.append(f"- Files scanned: `{scan_sources.get('files_scanned', 0)}`")
    lines.append(f"- Files ignored: `{scan_sources.get('files_ignored', 0)}`")
    lines.append(f"- Generated Arkheionx artifacts ignored: `{scan_sources.get('generated_artifacts_ignored', 0)}`")
    if int(scan_sources.get("generated_artifacts_ignored", 0) or 0) > 0:
        lines.append("- Generated artifacts were ignored to prevent previous Arkheionx outputs from influencing this scan.")
    lines.append("")
    lines.append("## Disclaimer")
    lines.append("")
    lines.append(DISCLAIMER)
    lines.append("")
    lines.append("## Analysis Quality")
    lines.append("")
    lines.append(
        markdown_table(
            [
                ["Source", "Status"],
                ["Keyword scan", str(analysis_quality_data.get("keyword_scan", "enabled"))],
                ["Semantic-lite extraction", str(analysis_quality_data.get("semantic_lite", "enabled"))],
                ["Semantic contracts", str(analysis_quality_data.get("semantic_contracts", 0))],
                ["Semantic test files", str(analysis_quality_data.get("semantic_test_files", 0))],
                ["Slither", str(analysis_quality_data.get("slither", "disabled"))],
                ["Slither detectors", str(analysis_quality_data.get("slither_detector_count", 0))],
                ["Test coverage mapping", str(analysis_quality_data.get("test_coverage_mapping", "enabled"))],
                ["Negative evidence", str(analysis_quality_data.get("negative_evidence_count", 0))],
            ]
        )
    )
    if analysis_quality_data.get("warnings"):
        lines.append("")
        lines.append("Analysis warnings:")
        for warning in analysis_quality_data.get("warnings", []):
            lines.append(f"- {warning}")
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
    negative_evidence_items = [
        item
        for item in test_readiness.get("negative_evidence", [])
        if isinstance(item, dict)
    ]
    if negative_evidence_items:
        lines.append("## Negative Evidence")
        lines.append("")
        lines.append("Arkheionx found coverage terms in missing/negative context. These statements are not counted as positive test coverage.")
        lines.append("")
        for item in negative_evidence_items[:20]:
            location = f"`{item.get('file', '')}:{item.get('line', 1)}`"
            lines.append(
                f"- {location} `{item.get('term', '')}` - {item.get('reason', '')} Snippet: `{item.get('snippet', '')}`"
            )
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
    lines.append("## Rule Pack Coverage")
    lines.append("")
    rule_rows = [["Rule Pack", "Detected", "Findings", "Docs"]]
    for pack in rule_packs.values():
        rule_rows.append(
            [
                str(pack.get("label", "")),
                "yes" if pack.get("detected") else "no",
                str(pack.get("finding_count", 0)),
                str(pack.get("docs", "")),
            ]
        )
    lines.append(markdown_table(rule_rows))
    lines.append("")
    for pack in rule_packs.values():
        if not pack.get("detected") and not pack.get("findings"):
            continue
        lines.append(f"### {pack.get('label', 'Rule Pack')}")
        lines.append("")
        lines.append(f"- Signals detected: `{pack.get('signal_count', 0)}`")
        if pack.get("signals"):
            lines.append(f"- Signal terms: `{', '.join(str(item) for item in pack.get('signals', [])[:20])}`")
        lines.append(f"- Findings: `{pack.get('finding_count', 0)}`")
        lines.append(f"- Docs: `{pack.get('docs', '')}`")
        lines.append("- Suggested tests:")
        for test in pack.get("suggested_tests", []):
            lines.append(f"  - {test}")
        lines.append("")
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
        if key not in {"test_files", "negative_evidence"}:
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
            lines.append(f"- Confidence reason: {gap.confidence_reason or 'Local/static signals were used.'}")
            lines.append(f"- Detection sources: `{', '.join(gap.detection_sources) or 'keyword'}`")
            lines.append(f"- Category: `{gap.category}`")
            lines.append("")
            if gap.evidence:
                lines.append("Evidence:")
                for item in gap.evidence[:5]:
                    location = str(item.get("file", ""))
                    function = str(item.get("function", ""))
                    line = item.get("line", 1)
                    snippet = str(item.get("snippet", ""))
                    reason = str(item.get("reason", ""))
                    label = f"`{location}:{line}`" if location else "`test/documentation coverage`"
                    if function:
                        label += f" in `{function}`"
                    lines.append(f"- {label}: {reason}" + (f" Snippet: `{snippet}`" if snippet else ""))
                lines.append("")
            if gap.negative_evidence:
                lines.append("Negative evidence:")
                for item in gap.negative_evidence[:5]:
                    lines.append(
                        f"- `{item.get('file', '')}:{item.get('line', 1)}` `{item.get('term', '')}`: {item.get('reason', '')} Snippet: `{item.get('snippet', '')}`"
                    )
                lines.append("")
            if gap.false_positive_notes:
                lines.append("False-positive notes:")
                lines.append("")
                lines.append(gap.false_positive_notes)
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
            related_lines = compact_related_knowledge_lines(gap.id)
            if related_lines:
                lines.append("Related Knowledge:")
                lines.append("")
                for item in related_lines[1:]:
                    lines.append(item)
            lines.append("")
            lines.append("Suggested tests:")
            lines.append("")
            for test in mapped_suggested_tests(gap)[:6]:
                lines.append(f"- {test}")
            invariant_candidates = mapped_invariant_candidates(gap)
            if invariant_candidates:
                lines.append("")
                lines.append("Invariant candidates:")
                lines.append("")
                for candidate in invariant_candidates[:5]:
                    lines.append(f"- {candidate}")
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
    issue_plan_output = generated_outputs.get("issue_plan", "")
    if checklist_output:
        lines.append(f"- Generated checklist: `{checklist_output}`")
        lines.append("- Use this as a copyable GitHub Issue body or as a remediation tracker.")
    else:
        lines.append("- No issue checklist file was requested in this run.")
        lines.append("- To generate one: `python3 scripts/pre_audit_scan.py --root . --issue-checklist-output ARKHEIONX_ISSUE_CHECKLIST.md`")
    if issue_plan_output:
        lines.append(f"- Generated issue plan: `{issue_plan_output}`")
        lines.append("- Issue plan JSON can be used with `scripts/create_github_issues.py` in dry-run, create, or update mode.")
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
    rule_packs: dict[str, dict[str, object]],
    semantic: dict[str, object],
    slither: dict[str, object],
    analysis_quality_data: dict[str, object],
    scan_sources: dict[str, object],
    negative_evidence: list[dict[str, object]],
    historical_patterns: list[HistoricalPattern],
    gaps: list[ReadinessGap],
    suppressed_gaps: list[ReadinessGap],
    invariants: list[dict[str, str]],
    next_steps: list[str],
    generated_outputs: dict[str, str],
    delivery_outputs: dict[str, str],
    delivery_summary_data: dict[str, object],
    config_summary_data: dict[str, object],
    config_warnings: list[str],
    diff_data: dict[str, object] | None,
) -> dict[str, object]:
    counts = finding_counts(gaps, suppressed_gaps)
    findings = [finding_to_dict(item) for item in gaps]
    suppressed_findings = [finding_to_dict(item) for item in suppressed_gaps]
    return {
        "tool": "Arkheionx Pre-Audit Scanner",
        "version": VERSION,
        "schema_version": SCHEMA_VERSION,
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
        "analysis_quality": analysis_quality_data,
        "scan_sources": scan_sources,
        "negative_evidence": negative_evidence,
        "semantic_lite": semantic,
        "slither": slither,
        "vault_rule_pack": vault_test_coverage,
        "rule_packs": rule_packs,
        "historical_patterns": [item.__dict__ for item in historical_patterns],
        "knowledge": {
            "finding_map_version": "0.9.0",
            "mapped_findings": sorted(load_finding_knowledge_map().keys()),
            "security_memory_graph": "metadata/security_memory_graph.json",
            "finding_knowledge_map": "metadata/finding_knowledge_map.json",
            "rule_calibration_matrix": "metadata/rule_calibration_matrix.json",
            "finding_test_plan_map": "metadata/finding_test_plan_map.json",
        },
        "findings": findings,
        "suppressed_findings": suppressed_findings,
        "readiness_gaps": findings,
        "suggested_invariants": invariants,
        "generated_outputs": generated_outputs,
        "delivery_outputs": delivery_outputs,
        "delivery_summary": delivery_summary_data,
        "config_summary": config_summary_data,
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


def priority_slug(priority: str) -> str:
    text = priority.lower()
    if "critical" in text:
        return "critical"
    if "high" in text:
        return "high"
    if "medium" in text:
        return "medium"
    if "low" in text:
        return "low"
    return "informational"


def issue_marker(finding_id: str) -> str:
    return f"{ISSUE_MARKER_PREFIX}{finding_id} -->"


def issue_title_for_gap(gap: ReadinessGap) -> str:
    priority = priority_slug(gap.priority).title()
    return f"[Arkheionx][{priority}] {gap.id} - {gap.title}"


def issue_labels_for_gap(gap: ReadinessGap) -> list[str]:
    labels = {
        "arkheionx",
        "pre-audit-readiness",
        f"{priority_slug(gap.priority)}-readiness-gap",
        gap.category.replace("_", "-"),
    }
    labels.update(tag.replace("_", "-") for tag in gap.tags[:6])
    if gap.confidence == "low":
        labels.add("low-confidence")
    if gap.negative_evidence:
        labels.add("negative-evidence")
    return sorted(label for label in labels if label)


def issue_body_for_gap(gap: ReadinessGap, generated_outputs: dict[str, str]) -> str:
    lines = [
        issue_marker(gap.id),
        "",
        f"# Arkheionx readiness gap: {gap.id}",
        "",
        ISSUE_DISCLAIMER,
        "",
        "## Finding Summary",
        "",
        f"- ID: `{gap.id}`",
        f"- Priority: `{gap.priority}`",
        f"- Category: `{gap.category}`",
        f"- Confidence: `{gap.confidence}`",
        f"- Confidence reason: {gap.confidence_reason or 'Local/static evidence was used.'}",
        f"- Fingerprint: `{gap.fingerprint}`",
        "",
        "## Evidence",
        "",
    ]
    if gap.evidence:
        for item in gap.evidence[:5]:
            location = str(item.get("file", ""))
            function = str(item.get("function", ""))
            line = item.get("line", 1)
            reason = str(item.get("reason", ""))
            snippet = str(item.get("snippet", ""))
            label = f"`{location}:{line}`" if location else "`test/documentation coverage`"
            if function:
                label += f" in `{function}`"
            lines.append(f"- {label}: {reason}" + (f" Snippet: `{snippet}`" if snippet else ""))
    else:
        lines.append("- No structured evidence was attached. Manual review recommended.")
    if gap.false_positive_notes:
        lines.extend(["", "False-positive notes:", "", gap.false_positive_notes])
    if gap.negative_evidence:
        lines.extend(["", "## Negative Evidence", ""])
        lines.append("These missing-coverage statements were not counted as positive test coverage:")
        for item in gap.negative_evidence[:5]:
            lines.append(
                f"- `{item.get('file', '')}:{item.get('line', 1)}` `{item.get('term', '')}`: {item.get('snippet', '')}"
            )
    related_lines = compact_related_knowledge_lines(gap.id)
    if related_lines:
        lines.extend(["", "## Related Knowledge", ""])
        lines.extend(related_lines[1:])
    lines.extend(
        [
            "",
            "## Why It Matters",
            "",
            gap.why_it_matters or gap.detail,
            "",
            "## Historical Pattern Similarity",
            "",
            gap.historical_pattern_similarity or "Historical pattern similarity was not strong enough for a specific automated mapping. Manual review is still recommended.",
            "",
            "## Recommended Defensive Checks",
            "",
        ]
    )
    for check in gap.defensive_checks or [gap.recommendation]:
        lines.append(f"- {check}")
    lines.extend(["", "## Suggested Tests", ""])
    for test in mapped_suggested_tests(gap)[:8]:
        lines.append(f"- {test}")
    invariant_candidates = mapped_invariant_candidates(gap)
    if invariant_candidates:
        lines.extend(["", "## Invariant Candidates", ""])
        for candidate in invariant_candidates[:6]:
            lines.append(f"- {candidate}")
    lines.extend(
        [
            "",
            "## Suggested Owner Notes",
            "",
            "- Assign this to the maintainer responsible for the affected contract or test area.",
            "- Keep remediation defensive and local to this repository.",
            "- Re-run Arkheionx after changes and compare against the latest baseline if available.",
            "",
            "## Acceptance Checklist",
            "",
            "- [ ] Add or update tests.",
            "- [ ] Document assumptions.",
            "- [ ] Review privileged roles if relevant.",
            "- [ ] Re-run Arkheionx.",
            "- [ ] Compare against baseline if relevant.",
            "",
            "## Generated Artifacts",
            "",
        ]
    )
    for label, path in generated_outputs.items():
        if path:
            lines.append(f"- {label.replace('_', ' ').title()}: `{path}`")
    lines.extend(["", "## Safety Boundary", "", "Do not add live-target testing, exploit payloads, private keys, RPC requirements, or bounty-claim language to this issue."])
    return "\n".join(lines) + "\n"


def summary_issue_body(
    gaps: list[ReadinessGap],
    score: int,
    protocol_type: str,
    generated_outputs: dict[str, str],
) -> str:
    lines = [
        issue_marker("summary"),
        "",
        "# Arkheionx pre-audit readiness remediation plan",
        "",
        ISSUE_DISCLAIMER,
        "",
        f"- Score: `{score}/100`",
        f"- Score band: `{score_band(score)}`",
        f"- Protocol type: `{protocol_type}`",
        f"- Active readiness gaps: `{len(gaps)}`",
        "",
        "## Top Readiness Gaps",
        "",
    ]
    for gap in top_findings(gaps, 10):
        lines.append(f"- [ ] `{gap.id}` - {gap.title} ({gap.priority})")
    lines.extend(["", "## Generated Artifacts", ""])
    for label, path in generated_outputs.items():
        if path:
            lines.append(f"- {label.replace('_', ' ').title()}: `{path}`")
    lines.extend(["", "This plan is a readiness tracker, not a formal audit report."])
    return "\n".join(lines) + "\n"


def build_issue_plan(
    root: Path,
    protocol_type: str,
    score: int,
    gaps: list[ReadinessGap],
    generated_outputs: dict[str, str],
    grouping: str = "one-per-finding",
    min_confidence: str = "low",
) -> dict[str, object]:
    issues = []
    excluded = []
    for gap in sorted(gaps, key=lambda item: (gap_priority_rank(item), item.id, item.title)):
        if not confidence_meets(gap.confidence, min_confidence):
            excluded.append(finding_to_dict(gap))
            continue
        issues.append(
            {
                "marker": issue_marker(gap.id),
                "finding_id": gap.id,
                "title": issue_title_for_gap(gap),
                "labels": issue_labels_for_gap(gap),
                "body": issue_body_for_gap(gap, generated_outputs),
                "priority": gap.priority,
                "category": gap.category,
                "confidence": gap.confidence,
                "confidence_reason": gap.confidence_reason,
                "related_knowledge": related_knowledge_for_id(gap.id),
                "evidence_summary": gap.evidence_summary,
                "evidence": gap.evidence[:5],
                "negative_evidence": gap.negative_evidence[:5],
                "negative_evidence_count": len(gap.negative_evidence),
                "detection_sources": gap.detection_sources,
                "affected_functions": gap.affected_functions,
                "fingerprint": gap.fingerprint,
                "suggested_tests": mapped_suggested_tests(gap),
                "invariant_candidates": mapped_invariant_candidates(gap),
                "recommended_defensive_checks": gap.defensive_checks,
                "disclaimer": ISSUE_DISCLAIMER,
            }
        )
    return {
        "tool": "Arkheionx Pre-Audit Scanner",
        "version": VERSION,
        "schema_version": SCHEMA_VERSION,
        "generated_at": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "repo_root": display_path(root),
        "protocol_type": protocol_type,
        "score": score,
        "score_band": score_band(score),
        "mode": "dry-run",
        "issue_grouping": grouping,
        "min_confidence": min_confidence,
        "issues": issues,
        "excluded_low_confidence_findings": excluded,
        "summary_issue": {
            "marker": issue_marker("summary"),
            "title": "[Arkheionx] Pre-audit readiness remediation plan",
            "labels": ["arkheionx", "pre-audit-readiness", "remediation-plan"],
            "body": summary_issue_body(gaps, score, protocol_type, generated_outputs),
            "disclaimer": ISSUE_DISCLAIMER,
        },
        "disclaimer": ISSUE_DISCLAIMER,
    }


def write_issue_plan(path: Path, plan: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def generate_issue_checklist(
    path: Path,
    protocol_type: str,
    score: int,
    gaps: list[ReadinessGap],
    diff_data: dict[str, object] | None,
    generated_outputs: dict[str, str] | None = None,
) -> None:
    generated_outputs = generated_outputs or {}
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
            lines.append(f"  - Suggested issue title: `{issue_title_for_gap(gap)}`")
            lines.append(f"  - Suggested labels: `{', '.join(issue_labels_for_gap(gap))}`")
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
            "## Convert This Checklist Into GitHub Issues",
            "",
        ]
    )
    issue_plan_path = generated_outputs.get("issue_plan", "")
    if issue_plan_path:
        lines.append(f"Issue plan: `{issue_plan_path}`")
        lines.append("")
        lines.extend(
            [
                "Dry run:",
                "",
                "```sh",
                f"python3 scripts/create_github_issues.py --issue-plan {issue_plan_path} --mode dry-run",
                "```",
                "",
                "Create issues:",
                "",
                "```sh",
                f"python3 scripts/create_github_issues.py --issue-plan {issue_plan_path} --mode create --max-issues 5",
                "```",
                "",
                "Only run issue creation in repositories you own or are authorized to manage.",
                "",
            ]
        )
    else:
        lines.append("No issue plan path was provided for this run.")
        lines.append("")
    lines.extend(
        [
            "## Notes",
            "",
            "This checklist is generated from static/local readiness signals. It is not a formal audit.",
        ]
    )
    write_markdown(path, lines)


DELIVERY_NOTICE = (
    "This is not a formal audit. It does not guarantee security. It does not "
    "confirm the absence or presence of vulnerabilities. It is a defensive "
    "pre-audit readiness artifact for authorized repositories."
)


def status_from_score(score: int) -> str:
    if score < 40:
        return "Needs work"
    if score < 60:
        return "Needs review"
    if score < 75:
        return "Improving"
    if score < 90:
        return "Ready-ish"
    return "Strong pre-audit hygiene"


def area_status(area: str, gaps: list[ReadinessGap], score: int) -> tuple[str, str]:
    area_terms = {
        "testing": ["test", "invariant", "fuzz"],
        "oracle": ["oracle", "price"],
        "access": ["access", "admin", "upgrade"],
        "reentrancy": ["reentrancy", "value flow", "external call"],
        "reward": ["reward", "staking"],
        "vault": ["vault", "erc4626", "accounting"],
        "documentation": ["documentation", "docs"],
    }
    terms = area_terms.get(area, [area])
    matching = [
        gap
        for gap in gaps
        if any(term in f"{gap.id} {gap.title} {gap.category} {' '.join(gap.tags)}".lower() for term in terms)
    ]
    if not matching:
        return ("Covered / not strongly signaled", "No active high-signal readiness gap was generated for this area.")
    high = [gap for gap in matching if is_high_or_critical(gap)]
    if high:
        return ("Needs review", f"{len(high)} high/critical readiness gap(s) detected.")
    if score >= 75:
        return ("Improving", f"{len(matching)} lower-priority readiness gap(s) remain.")
    return ("Needs work", f"{len(matching)} readiness gap(s) detected.")


def launch_readiness_status(score: int, gaps: list[ReadinessGap]) -> str:
    if any("critical" in gap.priority.lower() for gap in gaps):
        return "Not ready"
    if score < 50 or any(is_high_or_critical(gap) and gap.confidence == "high" for gap in gaps):
        return "Needs hardening"
    if score < 75:
        return "Improving"
    return "Ready-ish for formal audit preparation"


def contest_readiness_status(score: int, gaps: list[ReadinessGap]) -> str:
    high_confidence = [gap for gap in gaps if gap.confidence == "high" and is_high_or_critical(gap)]
    if score < 45 or len(high_confidence) >= 3:
        return "Not ready"
    if score < 65 or high_confidence:
        return "Needs hardening"
    if score < 80:
        return "Improving"
    if score < 90:
        return "Ready for limited review"
    return "Ready for broader review"


def recommended_next_step(score: int, gaps: list[ReadinessGap]) -> str:
    top = top_findings(gaps, 1)
    if top:
        return f"Address `{top[0].id}` first, then re-run Arkheionx and compare against a baseline."
    if score < 75:
        return "Improve tests, invariants, and documentation, then re-run Arkheionx."
    return "Prepare the formal audit package and keep tracking readiness with baselines."


def remediation_phase(gap: ReadinessGap) -> str:
    text = f"{gap.priority} {gap.confidence} {gap.category} {gap.title}".lower()
    if "critical" in text or ("high" in text and gap.confidence == "high"):
        return "Phase 1 - Launch blockers"
    if "high" in text or "medium" in text:
        return "Phase 2 - High-priority readiness gaps"
    if "documentation" in text or "docs" in text:
        return "Phase 3 - Documentation and test hardening"
    return "Phase 4 - Before formal audit / contest"


def effort_estimate(gap: ReadinessGap) -> str:
    text = f"{gap.title} {gap.category} {gap.suggested_test}".lower()
    if any(term in text for term in ["invariant", "strategy", "upgrade", "oracle", "reward conservation", "withdrawal"]):
        return "Large"
    if any(term in text for term in ["test", "access", "role", "document", "pause"]):
        return "Medium"
    if "low" in gap.priority.lower() or gap.confidence == "low":
        return "Small"
    return "Unknown"


def delivery_summary(score: int, protocol_type: str, gaps: list[ReadinessGap]) -> dict[str, object]:
    phases = sorted({remediation_phase(gap) for gap in gaps})
    return {
        "recommended_next_step": recommended_next_step(score, gaps),
        "launch_readiness_status": launch_readiness_status(score, gaps),
        "contest_readiness_status": contest_readiness_status(score, gaps),
        "protocol_type": protocol_type,
        "top_remediation_phases": phases,
    }


def delivery_artifact_table(generated_outputs: dict[str, str]) -> list[str]:
    rows = [["Artifact", "Path"]]
    labels = [
        "markdown_report",
        "json_report",
        "sarif_report",
        "baseline",
        "diff_report",
        "issue_checklist",
        "issue_plan",
        "executive_summary",
        "remediation_roadmap",
        "launch_report",
        "sprint_plan",
        "contest_readiness",
    ]
    for label in labels:
        path = generated_outputs.get(label, "")
        if path:
            rows.append([label.replace("_", " ").title(), f"`{path}`"])
    return [markdown_table(rows)] if len(rows) > 1 else ["No additional artifact paths were requested."]


def render_top_delivery_gaps(gaps: list[ReadinessGap], limit: int = 8) -> list[str]:
    lines: list[str] = []
    for gap in top_findings(gaps, limit):
        lines.extend(
            [
                f"### {gap.id} - {gap.title}",
                "",
                f"- Priority: `{gap.priority}`",
                f"- Confidence: `{gap.confidence}`",
                f"- Evidence summary: {gap.evidence_summary or 'Local/static signal evidence.'}",
                f"- Why it matters: {gap.why_it_matters or gap.detail}",
                f"- Recommended remediation: {gap.recommendation}",
                "",
            ]
        )
        related_lines = compact_related_knowledge_lines(gap.id)
        if related_lines:
            lines.extend(related_lines)
            lines.append("")
    if not lines:
        lines.append("No active automated readiness gaps were detected. Manual review is still required.")
        lines.append("")
    return lines


def roadmap_tasks_by_phase(gaps: list[ReadinessGap]) -> dict[str, list[ReadinessGap]]:
    phases = {
        "Phase 1 - Launch blockers": [],
        "Phase 2 - High-priority readiness gaps": [],
        "Phase 3 - Documentation and test hardening": [],
        "Phase 4 - Before formal audit / contest": [],
    }
    for gap in top_findings(gaps, 20):
        phases.setdefault(remediation_phase(gap), []).append(gap)
    return phases


def generate_launch_report(
    path: Path,
    root: Path,
    protocol_type: str,
    score: int,
    gaps: list[ReadinessGap],
    analysis_quality_data: dict[str, object],
    generated_outputs: dict[str, str],
) -> None:
    lines = [
        "# Arkheionx Launch Readiness Report",
        "",
        "## Important Notice",
        "",
        DELIVERY_NOTICE,
        "",
        "## Executive Summary",
        "",
        f"- Project path: `{display_path(root)}`",
        f"- Protocol type: `{protocol_type}`",
        f"- Readiness score: `{score}/100`",
        f"- Score band: `{score_band(score)}`",
        f"- Analysis date: `{dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()}`",
        f"- Scanner version: `{VERSION}`",
        f"- Semantic-lite status: `{analysis_quality_data.get('semantic_lite', 'enabled')}`",
        f"- Slither status: `{analysis_quality_data.get('slither', 'disabled')}`",
        f"- Launch readiness status: `{launch_readiness_status(score, gaps)}`",
        f"- Recommended next action: {recommended_next_step(score, gaps)}",
        "",
        "Top readiness themes:",
    ]
    for gap in top_findings(gaps, 5):
        lines.append(f"- `{gap.id}` - {gap.title} ({gap.priority}, {gap.confidence} confidence)")
    if not gaps:
        lines.append("- No active automated readiness gap detected. Manual review remains required.")
    lines.extend(["", "## Launch Readiness Snapshot", ""])
    rows = [["Area", "Status", "Notes"]]
    for label, key in [
        ("Testing readiness", "testing"),
        ("Invariant coverage", "testing"),
        ("Oracle assumptions", "oracle"),
        ("Access control", "access"),
        ("Reentrancy/value flow", "reentrancy"),
        ("Reward accounting", "reward"),
        ("Vault accounting", "vault"),
        ("Documentation", "documentation"),
    ]:
        status, notes = area_status(key, gaps, score)
        rows.append([label, status, notes])
    lines.append(markdown_table(rows))
    lines.extend(["", "## Top Readiness Gaps", ""])
    lines.extend(render_top_delivery_gaps(gaps, 8))
    lines.extend(["## Relevant Security Memory", ""])
    memory_added = False
    for gap in top_findings(gaps, 5):
        related_lines = compact_related_knowledge_lines(gap.id)
        if related_lines:
            memory_added = True
            lines.append(f"### {gap.id} - {gap.title}")
            lines.append("")
            lines.extend(related_lines)
            lines.append("")
    if not memory_added:
        lines.append("No curated related-knowledge mapping was available for the top findings in this run.")
        lines.append("")
    lines.extend(["## Recommended Remediation Roadmap", ""])
    for phase, phase_gaps in roadmap_tasks_by_phase(gaps).items():
        lines.extend([f"### {phase}", ""])
        if phase_gaps:
            for gap in phase_gaps:
                lines.append(f"- [ ] `{gap.id}` - {gap.recommendation}")
        else:
            lines.append("- No automated task assigned to this phase.")
        lines.append("")
    lines.extend(
        [
            "## Suggested Pre-Launch Checklist",
            "",
            "- [ ] Fix launch blockers.",
            "- [ ] Add missing invariants.",
            "- [ ] Add oracle staleness/bounds tests if applicable.",
            "- [ ] Add access-control negative tests if applicable.",
            "- [ ] Add reentrancy/value-flow tests if applicable.",
            "- [ ] Add reward/vault accounting conservation tests if applicable.",
            "- [ ] Re-run Arkheionx and compare baseline.",
            "- [ ] Prepare formal audit package.",
            "",
            "## Generated Artifacts",
            "",
        ]
    )
    lines.extend(delivery_artifact_table(generated_outputs))
    lines.extend(["", "## Limitations", "", DELIVERY_NOTICE, "Formal audit remains recommended before mainnet, material TVL, or user funds."])
    write_markdown(path, lines)


def sprint_schedule(days: int) -> list[tuple[str, str]]:
    schedules = {
        3: [
            ("Day 1", "Launch blockers and issue plan triage."),
            ("Day 2", "Tests/invariants plus access, oracle, and reentrancy gaps."),
            ("Day 3", "Re-run, diff, documentation, and audit package."),
        ],
        5: [
            ("Day 1", "Triage, owner assignment, and baseline snapshot."),
            ("Day 2", "High-priority tests and invariants."),
            ("Day 3", "Accounting, oracle, access, and value-flow hardening."),
            ("Day 4", "Documentation, issue closure, and baseline diff."),
            ("Day 5", "Final readiness report and audit handoff package."),
        ],
        7: [
            ("Day 1", "Triage, scope confirmation, owner assignment."),
            ("Day 2", "Launch blockers and high-confidence findings."),
            ("Day 3", "Accounting and invariant implementation."),
            ("Day 4", "Oracle, access-control, and upgradeability review."),
            ("Day 5", "Reentrancy/value-flow and reward lifecycle tests."),
            ("Day 6", "Documentation, limitations, and issue-plan cleanup."),
            ("Day 7", "Final scan, baseline diff, and audit handoff package."),
        ],
        10: [
            ("Day 1", "Triage, scope confirmation, and baseline snapshot."),
            ("Day 2", "Launch blockers."),
            ("Day 3", "High-confidence invariant work."),
            ("Day 4", "Accounting and precision tests."),
            ("Day 5", "Oracle/pricing assumption tests."),
            ("Day 6", "Access-control, upgradeability, and emergency flows."),
            ("Day 7", "Reentrancy/value-flow and reward lifecycle review."),
            ("Day 8", "Documentation, known limitations, and scope package."),
            ("Day 9", "Re-run Arkheionx, compare baseline, close issues."),
            ("Day 10", "Final readiness report and audit/contest handoff."),
        ],
    }
    return schedules[days]


def generate_sprint_plan(
    path: Path,
    protocol_type: str,
    score: int,
    gaps: list[ReadinessGap],
    rule_packs: dict[str, dict[str, object]],
    analysis_quality_data: dict[str, object],
    generated_outputs: dict[str, str],
    days: int,
) -> None:
    high_confidence = [gap for gap in gaps if gap.confidence == "high"]
    lines = [
        "# Arkheionx Pre-Audit Sprint Plan",
        "",
        "## Important Notice",
        "",
        "Not a formal audit. Not a security guarantee. A defensive remediation planning document.",
        "",
        "## Sprint Goal",
        "",
        "Prepare this repository for a stronger formal audit, contest, or bug bounty readiness review.",
        "",
        "## Sprint Inputs",
        "",
        f"- Readiness score: `{score}/100`",
        f"- Score band: `{score_band(score)}`",
        f"- Number of findings: `{len(gaps)}`",
        f"- Number of high confidence findings: `{len(high_confidence)}`",
        f"- Number of issue-plan tasks: `{len(gaps)}`",
        f"- Rule packs detected: `{', '.join(name for name, pack in rule_packs.items() if pack.get('detected')) or 'none'}`",
        f"- Baseline available: `{'yes' if generated_outputs.get('baseline') else 'no'}`",
        f"- Semantic-lite enabled: `{analysis_quality_data.get('semantic_lite', 'enabled')}`",
        "",
        "## Day-by-Day Plan",
        "",
    ]
    for day, task in sprint_schedule(days):
        lines.append(f"- **{day}:** {task}")
    lines.extend(["", "## Sprint Backlog", ""])
    for phase, phase_gaps in roadmap_tasks_by_phase(gaps).items():
        lines.extend([f"### {phase}", ""])
        if not phase_gaps:
            lines.append("- No automated backlog item assigned.")
        for gap in phase_gaps:
            lines.extend(
                [
                    f"- [ ] `{gap.id}` - {issue_title_for_gap(gap)}",
                    "  - Suggested owner: `TBD`",
                    f"  - Expected output: {gap.suggested_test or gap.recommendation}",
                    "  - Acceptance checklist:",
                    "    - [ ] Tests or docs updated.",
                    "    - [ ] Arkheionx re-run completed.",
                    "    - [ ] Remaining assumptions documented.",
                ]
            )
        lines.append("")
    lines.extend(
        [
            "## Sprint Exit Criteria",
            "",
            "- [ ] All high-confidence high-priority gaps addressed or documented.",
            "- [ ] Invariant tests added where applicable.",
            "- [ ] Oracle/access/reentrancy/reward/vault assumptions documented.",
            "- [ ] Issue plan reviewed.",
            "- [ ] Baseline diff generated.",
            "- [ ] Remaining risks documented.",
            "- [ ] Formal audit package prepared.",
            "",
            "## What This Sprint Does Not Do",
            "",
            "- It does not replace a formal audit.",
            "- It does not guarantee security.",
            "- It does not test deployed contracts.",
            "- It does not run live-chain transactions.",
        ]
    )
    write_markdown(path, lines)


def generate_contest_readiness(
    path: Path,
    protocol_type: str,
    score: int,
    gaps: list[ReadinessGap],
) -> None:
    high_confidence = [gap for gap in gaps if gap.confidence == "high"]
    docs_gaps = [gap for gap in gaps if "doc" in f"{gap.category} {gap.title}".lower()]
    invariant_gaps = [gap for gap in gaps if "invariant" in f"{gap.title} {gap.recommendation}".lower()]
    lines = [
        "# Arkheionx Contest Readiness Report",
        "",
        "## Important Notice",
        "",
        "This is not a contest strategy document for exploiting systems. This is a defensive readiness document for authorized maintainers preparing a repository for external security review.",
        "It is not a formal audit, not a security guarantee, and not a bounty guarantee.",
        "",
        "## Contest Readiness Summary",
        "",
        f"- Protocol type: `{protocol_type}`",
        f"- Readiness score: `{score}/100`",
        f"- High-confidence gaps: `{len(high_confidence)}`",
        f"- Documentation gaps: `{len(docs_gaps)}`",
        f"- Missing invariants: `{len(invariant_gaps)}`",
        f"- Scope clarity: `Needs maintainer confirmation`",
        f"- Researcher onboarding readiness: `{status_from_score(score)}`",
        f"- Suggested contest readiness status: `{contest_readiness_status(score, gaps)}`",
        "",
        "## Scope Preparation Checklist",
        "",
        "- [ ] Contracts in scope listed.",
        "- [ ] Contracts out of scope listed.",
        "- [ ] Known limitations documented.",
        "- [ ] Privileged roles documented.",
        "- [ ] Oracle assumptions documented.",
        "- [ ] Upgradeability assumptions documented.",
        "- [ ] Test commands documented.",
        "- [ ] Existing known issues documented.",
        "- [ ] Previous audit reports linked if applicable.",
        "- [ ] Emergency/admin procedures documented.",
        "",
        "## Researcher Onboarding Checklist",
        "",
        "- [ ] Build instructions work locally.",
        "- [ ] Test instructions work locally.",
        "- [ ] Architecture overview exists.",
        "- [ ] Invariants are documented.",
        "- [ ] Key state machines are documented.",
        "- [ ] Threat model assumptions are documented.",
        "- [ ] Known false positives are documented.",
        "",
        "## Pre-Contest Remediation Priorities",
        "",
    ]
    lines.extend(render_top_delivery_gaps(gaps, 8))
    lines.extend(["## Historical Pattern Similarity", ""])
    memory_added = False
    for gap in top_findings(gaps, 5):
        related_lines = compact_related_knowledge_lines(gap.id)
        if related_lines:
            memory_added = True
            lines.append(f"### {gap.id} - {gap.title}")
            lines.append("")
            lines.extend(related_lines)
            lines.append("")
    if not memory_added:
        lines.append("No curated related-knowledge mapping was available for the top findings in this run.")
        lines.append("")
    lines.extend(["## What To Fix Before Opening A Contest", ""])
    groups = {
        "Must fix before contest": [gap for gap in gaps if is_high_or_critical(gap) and gap.confidence in {"high", "medium"}],
        "Should fix before contest": [gap for gap in gaps if "medium" in gap.priority.lower()],
        "Document before contest": docs_gaps,
        "Acceptable to defer with explicit notes": [gap for gap in gaps if gap.confidence == "low"],
    }
    for heading, group in groups.items():
        lines.extend([f"### {heading}", ""])
        if group:
            for gap in group[:8]:
                lines.append(f"- `{gap.id}` - {gap.title}")
        else:
            lines.append("- No automated item assigned.")
        lines.append("")
    lines.extend(
        [
            "## Contest Safety Notes",
            "",
            "- No exploit instructions.",
            "- No bounty guarantee.",
            "- No live target testing.",
            "- Respect platform rules.",
        ]
    )
    write_markdown(path, lines)


def generate_executive_summary(
    path: Path,
    root: Path,
    protocol_type: str,
    score: int,
    gaps: list[ReadinessGap],
) -> None:
    lines = [
        "# Arkheionx Executive Readiness Summary",
        "",
        DELIVERY_NOTICE,
        "",
        f"- Project path: `{display_path(root)}`",
        f"- Protocol type: `{protocol_type}`",
        f"- Readiness score: `{score}/100`",
        f"- Score band: `{score_band(score)}`",
        f"- Launch readiness status: `{launch_readiness_status(score, gaps)}`",
        f"- Contest readiness status: `{contest_readiness_status(score, gaps)}`",
        "",
        "## Top Themes",
        "",
    ]
    for gap in top_findings(gaps, 5):
        lines.append(f"- `{gap.id}` - {gap.title} ({gap.priority}, {gap.confidence} confidence)")
    if not gaps:
        lines.append("- No active automated readiness gap detected. Manual review remains required.")
    lines.extend(["", "## Top 3 Actions", ""])
    for gap in top_findings(gaps, 3):
        lines.append(f"- {gap.recommendation}")
    if not gaps:
        lines.append("- Prepare formal audit scope and continue manual review.")
    lines.extend(["", "## Next Recommended Step", "", recommended_next_step(score, gaps)])
    write_markdown(path, lines)


def generate_remediation_roadmap(
    path: Path,
    gaps: list[ReadinessGap],
    generated_outputs: dict[str, str],
) -> None:
    lines = [
        "# Arkheionx Remediation Roadmap",
        "",
        DELIVERY_NOTICE,
        "",
        "| Task ID | Finding ID | Phase | Priority | Confidence | Effort | Expected Output |",
        "|---|---|---|---|---|---|---|",
    ]
    for index, gap in enumerate(top_findings(gaps, 30), 1):
        lines.append(
            f"| ARK-TASK-{index:03d} | `{gap.id}` | {remediation_phase(gap)} | {gap.priority} | {gap.confidence} | {effort_estimate(gap)} | {gap.suggested_test or gap.recommendation} |"
        )
    if not gaps:
        lines.append("| ARK-TASK-000 | `none` | Manual review | Informational | medium | Unknown | Prepare audit scope and manual review plan. |")
    lines.extend(["", "## Acceptance Criteria", ""])
    for gap in top_findings(gaps, 12):
        lines.extend(
            [
                f"### {gap.id} - {gap.title}",
                "",
                f"- Evidence summary: {gap.evidence_summary or 'Local/static signal evidence.'}",
                "- [ ] Tests or documentation updated.",
                "- [ ] Assumptions documented.",
                "- [ ] Arkheionx re-run completed.",
                "- [ ] Baseline diff reviewed if available.",
                "",
            ]
        )
    lines.extend(["## Related Artifacts", ""])
    lines.extend(delivery_artifact_table(generated_outputs))
    write_markdown(path, lines)


SKELETON = """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// Arkheionx defensive readiness skeleton.
// This file is generated for local pre-audit preparation only.
// It contains no live addresses, no RPC calls, and no exploit payloads.

contract ArkheionxReadinessInvariants {
    struct WithdrawalLifecycleSnapshot {
        uint256 activeShares;
        uint256 pendingShares;
        uint256 burnedShares;
        uint256 vaultAssets;
        uint256 claimableAssets;
        uint256 claimedAssets;
    }

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
        WithdrawalLifecycleSnapshot memory beforeFlow = _withdrawalLifecycleSnapshot();

        _exerciseWithdrawalRequestCooldownClaimCancel();

        WithdrawalLifecycleSnapshot memory afterFlow = _withdrawalLifecycleSnapshot();

        assert(_sharesUnderWithdrawalLifecycle(beforeFlow) == _sharesUnderWithdrawalLifecycle(afterFlow));
        assert(_assetsUnderWithdrawalLifecycle(beforeFlow) == _assetsUnderWithdrawalLifecycle(afterFlow));
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

    function _withdrawalLifecycleSnapshot()
        internal
        view
        virtual
        returns (WithdrawalLifecycleSnapshot memory snapshot)
    {}

    function _exerciseWithdrawalRequestCooldownClaimCancel() internal virtual {}

    function _sharesUnderWithdrawalLifecycle(WithdrawalLifecycleSnapshot memory snapshot) internal pure returns (uint256) {
        return snapshot.activeShares + snapshot.pendingShares + snapshot.burnedShares;
    }

    function _assetsUnderWithdrawalLifecycle(WithdrawalLifecycleSnapshot memory snapshot) internal pure returns (uint256) {
        return snapshot.vaultAssets + snapshot.claimableAssets + snapshot.claimedAssets;
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
        choices=list(STABLE_PROTOCOL_TYPES),
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
    parser.add_argument("--issue-plan-output", default="", help="Optional generated GitHub issue plan JSON output path.")
    parser.add_argument("--launch-report-output", default="", help="Optional Launch Readiness Report Markdown output path.")
    parser.add_argument("--sprint-plan-output", default="", help="Optional Pre-Audit Sprint Plan Markdown output path.")
    parser.add_argument("--sprint-days", type=int, choices=[3, 5, 7, 10], default=5, help="Pre-Audit Sprint length in days.")
    parser.add_argument("--contest-readiness-output", default="", help="Optional Contest Readiness Report Markdown output path.")
    parser.add_argument("--executive-summary-output", default="", help="Optional one-page executive summary Markdown output path.")
    parser.add_argument("--remediation-roadmap-output", default="", help="Optional remediation roadmap Markdown output path.")
    parser.add_argument("--semantic-lite", dest="semantic_lite", action="store_true", default=True, help="Enable semantic-lite Solidity structure extraction.")
    parser.add_argument("--no-semantic-lite", dest="semantic_lite", action="store_false", help="Disable semantic-lite Solidity structure extraction.")
    parser.add_argument("--slither", action="store_true", help="Enable optional local Slither integration if available.")
    parser.add_argument("--slither-json", default="", help="Optional pre-generated Slither JSON file.")
    parser.add_argument("--slither-output", default="", help="Optional normalized Arkheionx Slither summary output path.")
    parser.add_argument("--slither-timeout", type=int, default=60, help="Slither timeout in seconds.")
    parser.add_argument("--slither-strict", action="store_true", help="Fail if Slither is requested but unavailable or fails.")
    parser.add_argument("--min-confidence-for-issue-plan", default="", choices=["", "low", "medium", "high"], help="Minimum finding confidence included in generated issue plans.")
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
    config, config_warnings, config_errors, config_source = load_local_config(config_path, root)
    if config_errors:
        for error in config_errors:
            print(f"error: {error}", file=sys.stderr)
        return 1
    analysis_config = config_analysis(config)
    scan_config = config_scan(config)
    enabled_rule_packs = config_enabled_rule_packs(config)
    if scan_config.get("include_generated_artifacts"):
        config_warnings.append(
            "Generated Arkheionx artifacts are included by config. This is advanced/debug behavior and may affect readiness scoring."
        )
    if args.semantic_lite is False:
        analysis_config["semantic_lite"] = False
    if args.slither:
        analysis_config["slither"] = True
    if args.min_confidence_for_issue_plan:
        analysis_config["min_confidence_for_issue_plan"] = args.min_confidence_for_issue_plan

    files_considered = collect_files(root)
    files, scan_sources = filter_scan_files(files_considered, root, config)
    classified = classify_files(files)
    contents = corpus(files)
    requested_protocol = args.protocol_type
    configured_protocol = config.get("protocol_type")
    if requested_protocol == "auto" and isinstance(configured_protocol, str) and configured_protocol in set(STABLE_PROTOCOL_TYPES):
        requested_protocol = configured_protocol
    protocol_type, protocol_confidence, protocol_scores = detect_protocol_type(contents, classified, requested_protocol)
    signal_paths = [
        path
        for path in classified.solidity_sources + classified.solidity_tests + classified.configs
        if not is_placeholder_skeleton(contents.get(path, ""))
    ]
    signals = detect_signals(contents, root, signal_paths or contents.keys())
    negative_evidence = collect_negative_evidence(contents, root)
    test_readiness = detect_test_readiness(contents, classified, root, negative_evidence)
    vault_test_coverage = detect_vault_test_coverage(contents, classified)
    semantic = extract_solidity_structure(contents, classified, root, bool(analysis_config.get("semantic_lite", True)))
    slither_json_path = resolve_output_path(args.slither_json)
    slither = slither_analysis(
        root,
        bool(analysis_config.get("slither", False)),
        slither_json_path,
        args.slither_timeout,
    )
    slither_output = resolve_output_path(args.slither_output)
    if slither_output:
        write_slither_summary(slither_output, slither)
    if args.slither_strict and slither.get("enabled") and (not slither.get("available") or slither.get("warnings")):
        print("error: Slither strict mode requested but Slither evidence was unavailable or produced warnings.", file=sys.stderr)
        for warning in slither.get("warnings", []):
            print(f"slither: {warning}", file=sys.stderr)
        return 1
    config_warnings.extend(str(warning) for warning in semantic.get("warnings", []))
    config_warnings.extend(str(warning) for warning in slither.get("warnings", []))
    quality = analysis_quality(semantic, slither, test_readiness)
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
    add_rule_pack_gaps(gaps, contents, classified, signals)
    apply_finding_metadata(gaps, signals, protocol_type)
    attach_evidence_and_calibrate(gaps, semantic, slither, analysis_config, protocol_type, negative_evidence)
    gaps = filter_gaps_by_rule_packs(gaps, enabled_rule_packs)
    gaps, suppressed_gaps = apply_suppressions(gaps, config)
    rule_packs = build_rule_packs(signals, gaps, suppressed_gaps)
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
    issue_plan_output = resolve_output_path(args.issue_plan_output)
    launch_report_output = resolve_output_path(args.launch_report_output)
    sprint_plan_output = resolve_output_path(args.sprint_plan_output)
    contest_readiness_output = resolve_output_path(args.contest_readiness_output)
    executive_summary_output = resolve_output_path(args.executive_summary_output)
    remediation_roadmap_output = resolve_output_path(args.remediation_roadmap_output)
    delivery_outputs = {
        "launch_report": display_path(launch_report_output) if launch_report_output else "",
        "sprint_plan": display_path(sprint_plan_output) if sprint_plan_output else "",
        "contest_readiness": display_path(contest_readiness_output) if contest_readiness_output else "",
        "executive_summary": display_path(executive_summary_output) if executive_summary_output else "",
        "remediation_roadmap": display_path(remediation_roadmap_output) if remediation_roadmap_output else "",
    }
    generated_outputs = {
        "markdown_report": display_path(output),
        "json_report": display_path(json_output) if json_output else "",
        "sarif_report": display_path(sarif_output) if sarif_output else "",
        "summary": display_path(summary_output) if summary_output else "",
        "comment": display_path(comment_output) if comment_output else "",
        "issue_checklist": display_path(issue_checklist_output) if issue_checklist_output else "",
        "issue_plan": display_path(issue_plan_output) if issue_plan_output else "",
        "slither_summary": display_path(slither_output) if slither_output else "",
        "baseline": display_path(baseline_output) if baseline_output else "",
        "diff_report": display_path(diff_output) if diff_output else "",
        "diff_json": display_path(diff_json_output) if diff_json_output else "",
        "launch_report": delivery_outputs["launch_report"],
        "sprint_plan": delivery_outputs["sprint_plan"],
        "contest_readiness": delivery_outputs["contest_readiness"],
        "executive_summary": delivery_outputs["executive_summary"],
        "remediation_roadmap": delivery_outputs["remediation_roadmap"],
    }
    delivery_summary_data = delivery_summary(score, protocol_type, gaps)
    config_summary_data = config_summary(config, config_source, protocol_type, enabled_rule_packs, analysis_config)
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
        rule_packs=rule_packs,
        analysis_quality_data=quality,
        scan_sources=scan_sources,
        score=score,
        score_breakdown=score_breakdown,
        gaps=gaps,
        suppressed_gaps=suppressed_gaps,
        invariants=invariants,
        next_steps=next_steps,
        skeleton_path=skeleton_path,
        generated_outputs=generated_outputs,
        config_summary_data=config_summary_data,
        config_warnings=config_warnings,
        additional_search_tags=additional_search_tags,
        max_top_gaps=max_top_gaps,
        diff_data=diff_data,
    )

    if issue_plan_output:
        write_issue_plan(
            issue_plan_output,
            build_issue_plan(
                root,
                protocol_type,
                score,
                gaps,
                generated_outputs,
                min_confidence=str(analysis_config.get("min_confidence_for_issue_plan", "low")),
            ),
        )
    if issue_checklist_output:
        generate_issue_checklist(issue_checklist_output, protocol_type, score, gaps, diff_data, generated_outputs)
    if summary_output:
        generate_summary_output(summary_output, score, protocol_type, gaps, suppressed_gaps, generated_outputs, next_steps, max_top_gaps, diff_data)
    if comment_output:
        generate_comment_output(comment_output, score, protocol_type, gaps, generated_outputs, max_top_gaps, diff_data)
    if launch_report_output:
        generate_launch_report(launch_report_output, root, protocol_type, score, gaps, quality, generated_outputs)
    if sprint_plan_output:
        generate_sprint_plan(sprint_plan_output, protocol_type, score, gaps, rule_packs, quality, generated_outputs, args.sprint_days)
    if contest_readiness_output:
        generate_contest_readiness(contest_readiness_output, protocol_type, score, gaps)
    if executive_summary_output:
        generate_executive_summary(executive_summary_output, root, protocol_type, score, gaps)
    if remediation_roadmap_output:
        generate_remediation_roadmap(remediation_roadmap_output, gaps, generated_outputs)
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
                rule_packs,
                semantic,
                slither,
                quality,
                scan_sources,
                negative_evidence,
                historical_patterns,
                gaps,
                suppressed_gaps,
                invariants,
                next_steps,
                generated_outputs,
                delivery_outputs,
                delivery_summary_data,
                config_summary_data,
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
    if issue_plan_output:
        print(f"Arkheionx issue plan generated: {issue_plan_output}")
    if launch_report_output:
        print(f"Arkheionx launch report generated: {launch_report_output}")
    if sprint_plan_output:
        print(f"Arkheionx sprint plan generated: {sprint_plan_output}")
    if contest_readiness_output:
        print(f"Arkheionx contest readiness report generated: {contest_readiness_output}")
    if executive_summary_output:
        print(f"Arkheionx executive summary generated: {executive_summary_output}")
    if remediation_roadmap_output:
        print(f"Arkheionx remediation roadmap generated: {remediation_roadmap_output}")
    if slither_output:
        print(f"Arkheionx Slither summary generated: {slither_output}")
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

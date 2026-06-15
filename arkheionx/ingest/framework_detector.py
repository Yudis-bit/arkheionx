"""Framework detection from repository layout signals."""
from __future__ import annotations

from pathlib import Path

FOUNDRY_STYLE = "foundry_style"
HARDHAT_STYLE = "hardhat_style"
TRUFFLE_STYLE = "truffle_style"
BROWNIE_STYLE = "brownie_style"
GENERIC_SOLIDITY = "generic_solidity"
UNKNOWN = "unknown"

FRAMEWORKS = (
    FOUNDRY_STYLE,
    HARDHAT_STYLE,
    TRUFFLE_STYLE,
    BROWNIE_STYLE,
    GENERIC_SOLIDITY,
    UNKNOWN,
)


def _has(root: Path, *names: str) -> bool:
    return any((root / name).exists() for name in names)


def detect_framework(root: Path | str, override: str = "auto") -> str:
    root = Path(root)
    normalized = (override or "auto").strip().lower().replace("-", "_")
    aliases = {
        "foundry": FOUNDRY_STYLE,
        "hardhat": HARDHAT_STYLE,
        "truffle": TRUFFLE_STYLE,
        "brownie": BROWNIE_STYLE,
        "generic": GENERIC_SOLIDITY,
    }
    if normalized != "auto":
        return aliases.get(normalized, normalized if normalized in FRAMEWORKS else UNKNOWN)
    if not root.exists():
        return UNKNOWN
    probe = root if root.is_dir() else root.parent
    if (probe / "foundry.toml").is_file():
        return FOUNDRY_STYLE
    if _has(probe, "hardhat.config.js", "hardhat.config.ts"):
        return HARDHAT_STYLE
    if _has(probe, "truffle-config.js", "truffle.js"):
        return TRUFFLE_STYLE
    if (probe / "brownie-config.yaml").is_file():
        return BROWNIE_STYLE
    try:
        if probe.is_dir() and any(probe.rglob("*.sol")):
            return GENERIC_SOLIDITY
    except OSError:
        pass
    return UNKNOWN

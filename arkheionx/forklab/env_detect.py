"""Fork environment detection (Layer 8).

Reports only the *names* of relevant env vars and whether they are set. Never
reads or prints a value.
"""
from __future__ import annotations

import os


def env_for_chain(chain: str) -> str:
    c = (chain or "").strip().lower()
    table = {
        "arbitrum": "ARBITRUM_RPC_URL", "arb": "ARBITRUM_RPC_URL",
        "ethereum": "MAINNET_RPC_URL", "mainnet": "MAINNET_RPC_URL", "eth": "MAINNET_RPC_URL",
        "optimism": "OPTIMISM_RPC_URL", "base": "BASE_RPC_URL", "polygon": "POLYGON_RPC_URL",
    }
    return table.get(c, "FORK_RPC_URL")


def detect_env(names) -> dict:
    """Return which of ``names`` are set, by NAME only (never values)."""
    present, missing = [], []
    for name in names:
        if os.environ.get(name):
            present.append(name)
        else:
            missing.append(name)
    return {"present": present, "missing": missing}

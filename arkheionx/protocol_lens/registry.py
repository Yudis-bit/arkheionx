"""Protocol-lens registry: look up an implemented lens by id.

The architecture is general; the registry is how a CLI command resolves a
``--lens <id>`` flag to a concrete :class:`~arkheionx.protocol_lens.base.ProtocolLens`.
Today exactly one lens is implemented (``fixed-credit-market``). The registry also
advertises *planned* lens ids so the surface is discoverable without pretending
they exist yet.
"""
from __future__ import annotations

from .base import ProtocolLens

# Lens ids that are designed-for but intentionally not implemented yet. Listing
# them documents the roadmap without faking capability.
PLANNED_LENSES: tuple[tuple[str, str], ...] = (
    ("generic-erc4626", "Generic ERC-4626 vault (planned)"),
    ("generic-lending", "Generic lending market (planned)"),
    ("generic-amm", "Generic AMM / DEX pool (planned)"),
    ("generic-staking", "Generic staking / reward vault (planned)"),
)

_REGISTRY: dict[str, ProtocolLens] = {}


def register_lens(lens: ProtocolLens) -> None:
    """Register a lens instance under its ``lens_id`` (idempotent by id)."""
    _REGISTRY[lens.lens_id] = lens


def _ensure_loaded() -> None:
    """Lazily import and register the built-in lenses (avoids import cycles)."""
    if _REGISTRY:
        return
    # Import here so the package can be imported without eagerly building lenses.
    from .lenses.fixed_credit_market import FixedCreditMarketLens

    register_lens(FixedCreditMarketLens())


def is_registered(lens_id: str) -> bool:
    _ensure_loaded()
    return lens_id in _REGISTRY


def get_lens(lens_id: str) -> ProtocolLens:
    """Return the registered lens, or raise ``KeyError`` with a helpful message."""
    _ensure_loaded()
    key = (lens_id or "").strip()
    if key not in _REGISTRY:
        available = ", ".join(sorted(_REGISTRY)) or "(none)"
        raise KeyError(
            f"unknown protocol lens '{lens_id}'. Implemented: {available}. "
            f"Planned: {', '.join(pid for pid, _ in PLANNED_LENSES)}."
        )
    return _REGISTRY[key]


def available_lenses() -> list[ProtocolLens]:
    """All implemented lenses, sorted by id."""
    _ensure_loaded()
    return [_REGISTRY[k] for k in sorted(_REGISTRY)]


def lens_ids() -> list[str]:
    """Ids of all implemented lenses, sorted."""
    _ensure_loaded()
    return sorted(_REGISTRY)

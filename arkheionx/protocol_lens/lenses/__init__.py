"""Built-in protocol lenses.

Today this holds exactly one implemented lens, Fixed Credit Market. The architecture
supports future lenses (see :data:`arkheionx.protocol_lens.registry.PLANNED_LENSES`),
but none of those are implemented yet.
"""
from __future__ import annotations

from .fixed_credit_market import LENS_ID as FIXED_CREDIT_MARKET_ID
from .fixed_credit_market import FixedCreditMarketLens

__all__ = ["FixedCreditMarketLens", "FIXED_CREDIT_MARKET_ID"]

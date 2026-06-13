"""Built-in protocol lenses.

Today this holds exactly one implemented lens, Morpho Midnight. The architecture
supports future lenses (see :data:`arkheionx.protocol_lens.registry.PLANNED_LENSES`),
but none of those are implemented yet.
"""
from __future__ import annotations

from .morpho_midnight import LENS_ID as MORPHO_MIDNIGHT_ID
from .morpho_midnight import MorphoMidnightLens

__all__ = ["MorphoMidnightLens", "MORPHO_MIDNIGHT_ID"]

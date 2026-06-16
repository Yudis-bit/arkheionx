"""Arkheionx V10 state transition engine (Layer 3)."""
from __future__ import annotations

from . import transitions
from .transitions import StateTransition, TransitionMap
from .transition_detector import build_transitions
from .contradictions import Contradiction, ContradictionSet, find_contradictions

__all__ = ["transitions", "StateTransition", "TransitionMap", "build_transitions",
           "Contradiction", "ContradictionSet", "find_contradictions"]

"""Arkheionx V10 GodEye war-run orchestrator (Layer 10).

Public-safe name: Arkheionx V10 Semantic DeFi Review Engine.

Ties the semantic core, DeFi entities, state transitions, invariants, attack
graph, PoC skeletons, economic severity gate, fork lab, and root-cause memory
into one local-first run that emits machine-readable artifacts and a concise
verdict — and never a report.
"""
from __future__ import annotations

from .command import war_run_command
from .orchestrator import WarRunError, default_out_dir, run_war_run
from .scope import ScopeModel, load_scope

__all__ = [
    "war_run_command", "run_war_run", "default_out_dir", "WarRunError",
    "load_scope", "ScopeModel",
]

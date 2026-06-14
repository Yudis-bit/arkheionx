"""Arkheionx V10 semantic core (Layer 1).

Reconstructs a Solidity codebase as a semantic object: contracts, functions,
storage access, call graph, external calls, and calldata->sink data flow. The
fallback parser is the primary path; AST mode is a pluggable interface.

Local/static, read-only. Everything here is review context, not a finding.
"""
from __future__ import annotations

from . import models
from .core import build_semantic_map
from .models import (
    SCHEMA_VERSION,
    CallEdge,
    ContractSemantic,
    DataFlowHint,
    ExternalCall,
    FunctionSemantic,
    SemanticMap,
    StateVariable,
    StorageAccess,
)

__all__ = [
    "models",
    "build_semantic_map",
    "SemanticMap",
    "ContractSemantic",
    "FunctionSemantic",
    "StateVariable",
    "StorageAccess",
    "CallEdge",
    "ExternalCall",
    "DataFlowHint",
    "SCHEMA_VERSION",
]

"""Semantic data models for the V10 GodEye War Engine (Layer 1).

These models describe a Solidity codebase as a *semantic* object — contracts,
functions, storage access, call edges, external calls, and calldata->sink data
flow — rather than a flat regex match. Every fact carries a ``confidence`` and
optional ``warnings`` because the primary extraction path is a robust fallback
parser, not a full compiler AST.

Generic on purpose: nothing about any specific protocol, token, or company is
encoded here. Read-only; produced from local source only.
"""
from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field

SCHEMA_VERSION = "v10-semantic"

# Extraction modes.
MODE_AST = "ast"
MODE_FALLBACK = "fallback"

# Confidence ladder (string, to match the rest of the codebase).
LOW = "LOW"
MEDIUM = "MEDIUM"
HIGH = "HIGH"

# Contract kinds.
KIND_CONTRACT = "contract"
KIND_INTERFACE = "interface"
KIND_LIBRARY = "library"
KIND_ABSTRACT = "abstract"

# Call-edge kinds.
CALL_INTERNAL = "internal"
CALL_EXTERNAL = "external"
CALL_INTERFACE = "interface"
CALL_LOWLEVEL = "low-level"
CALL_LIBRARY = "library"

# Data-flow source/sink kinds.
SRC_CALLDATA = "calldata"
SRC_MSG_SENDER = "msg.sender"
SRC_MSG_VALUE = "msg.value"
SRC_STORAGE = "storage"
SRC_CONSTANT = "constant"
SRC_RETURN = "function_return"

SINK_TRANSFER_AMOUNT = "transfer_amount"
SINK_CALL_ARG = "call_arg"
SINK_HASH_INPUT = "hash_input"
SINK_STATE_WRITE = "state_write"
SINK_EXTERNAL_CALL = "external_call"

# Notable cross-cutting data-flow tags (generic, pattern-derived).
TAG_CALLDATA_TO_SWAP_ROUTE = "BORROWER_CONTROLLED_CALLDATA_REACHES_SWAP_ROUTE"
TAG_CALLDATA_TO_TRANSFER = "CALLDATA_REACHES_TRANSFER_AMOUNT"
TAG_CALLDATA_TO_EXTERNAL = "CALLDATA_REACHES_EXTERNAL_CALL"
TAG_EXTERNAL_BEFORE_WRITE = "EXTERNAL_CALL_BEFORE_STATE_WRITE"


def _to_dict(obj) -> dict:
    return dataclasses.asdict(obj)


@dataclass
class Parameter:
    """A function parameter (or return slot)."""

    name: str = ""
    type: str = ""
    location: str = ""  # calldata | memory | storage | ""

    def to_dict(self) -> dict:
        return _to_dict(self)


@dataclass
class StateVariable:
    """A contract-level storage variable."""

    name: str = ""
    type: str = ""
    visibility: str = "internal"
    line: int = 0
    is_mapping: bool = False
    is_array: bool = False
    constant: bool = False

    def to_dict(self) -> dict:
        return _to_dict(self)


@dataclass
class StorageAccess:
    """A single read/write/delete of a state variable inside a function."""

    variable: str = ""
    kind: str = "read"  # read | write | delete
    function: str = ""  # Contract.function
    line: int = 0
    expression: str = ""
    confidence: str = MEDIUM

    def to_dict(self) -> dict:
        return _to_dict(self)


@dataclass
class CallEdge:
    """A call relationship between functions/contracts."""

    caller: str = ""  # Contract.function
    callee: str = ""  # Contract.function | <external>.method
    kind: str = CALL_INTERNAL
    arguments: str = ""
    line: int = 0
    confidence: str = MEDIUM

    def to_dict(self) -> dict:
        return _to_dict(self)


@dataclass
class ExternalCall:
    """An external/low-level call site, with state-write ordering context."""

    contract: str = ""
    function: str = ""  # Contract.function the call lives in
    target_expr: str = ""
    selector: str = ""  # method name if known
    value_sent: bool = False
    arguments: str = ""
    line: int = 0
    writes_before: list = field(default_factory=list)
    writes_after: list = field(default_factory=list)
    reentrancy_relevant: bool = False
    confidence: str = MEDIUM

    def to_dict(self) -> dict:
        return _to_dict(self)


@dataclass
class DataFlowHint:
    """A source-expression -> sink-expression flow inside a function."""

    function: str = ""  # Contract.function
    source_expr: str = ""
    sink_expr: str = ""
    source_kind: str = SRC_CALLDATA
    sink_kind: str = SINK_CALL_ARG
    source_line: int = 0
    sink_line: int = 0
    tag: str = ""
    confidence: str = LOW

    def to_dict(self) -> dict:
        return _to_dict(self)


@dataclass
class FunctionSemantic:
    """A function with its semantic effects."""

    contract: str = ""
    name: str = ""
    visibility: str = "public"
    mutability: str = ""  # view | pure | payable | ""
    parameters: list = field(default_factory=list)   # Parameter
    returns: list = field(default_factory=list)       # Parameter
    modifiers: list = field(default_factory=list)
    line_start: int = 0
    line_end: int = 0
    internal_calls: list = field(default_factory=list)
    external_calls: list = field(default_factory=list)
    storage_reads: list = field(default_factory=list)
    storage_writes: list = field(default_factory=list)
    events_emitted: list = field(default_factory=list)
    transfers: list = field(default_factory=list)
    low_level_calls: list = field(default_factory=list)
    calldata_fields: list = field(default_factory=list)
    uses_msg_sender: bool = False
    uses_msg_value: bool = False
    role_gates: list = field(default_factory=list)
    value_effects: list = field(default_factory=list)
    confidence: str = MEDIUM
    warnings: list = field(default_factory=list)

    @property
    def qualified_name(self) -> str:
        return f"{self.contract}.{self.name}"

    def to_dict(self) -> dict:
        return _to_dict(self)


@dataclass
class ContractSemantic:
    """A contract/interface/library with its members."""

    name: str = ""
    file: str = ""
    line_start: int = 0
    line_end: int = 0
    kind: str = KIND_CONTRACT
    inheritance: list = field(default_factory=list)
    state_variables: list = field(default_factory=list)  # StateVariable
    functions: list = field(default_factory=list)          # FunctionSemantic
    modifiers: list = field(default_factory=list)
    events: list = field(default_factory=list)
    structs: list = field(default_factory=list)
    enums: list = field(default_factory=list)
    confidence: str = MEDIUM
    warnings: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return _to_dict(self)


@dataclass
class SemanticMap:
    """The top-level semantic object for a target."""

    root: str = ""
    mode: str = MODE_FALLBACK
    confidence: str = MEDIUM
    contracts: list = field(default_factory=list)        # ContractSemantic
    call_edges: list = field(default_factory=list)        # CallEdge
    external_calls: list = field(default_factory=list)    # ExternalCall
    storage_accesses: list = field(default_factory=list)  # StorageAccess
    dataflow_hints: list = field(default_factory=list)    # DataFlowHint
    files_indexed: int = 0
    warnings: list = field(default_factory=list)

    # -- convenience accessors (operate on dataclass instances) -------------
    def iter_functions(self):
        for c in self.contracts:
            for fn in c.functions:
                yield fn

    def function(self, qualified_name: str):
        for fn in self.iter_functions():
            if fn.qualified_name == qualified_name:
                return fn
        return None

    def contract(self, name: str):
        for c in self.contracts:
            if c.name == name:
                return c
        return None

    def to_dict(self) -> dict:
        return {
            "schema_version": SCHEMA_VERSION,
            "root": self.root,
            "mode": self.mode,
            "confidence": self.confidence,
            "files_indexed": self.files_indexed,
            "contracts": [c.to_dict() for c in self.contracts],
            "call_edges": [e.to_dict() for e in self.call_edges],
            "external_calls": [x.to_dict() for x in self.external_calls],
            "storage_accesses": [s.to_dict() for s in self.storage_accesses],
            "dataflow_hints": [d.to_dict() for d in self.dataflow_hints],
            "warnings": list(self.warnings),
        }

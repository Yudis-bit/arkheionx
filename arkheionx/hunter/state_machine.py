"""State-machine value-flow detector for hunter mode.

Detects state machines (enums, status/phase/queue/round/epoch/cursor variables) and,
crucially, only treats them as a priority lead when the state machine actually *gates
value* — a withdrawal/claim/reward/fee/queue/migration/oracle-round/coverage/maturity/
bridge/validator/lock-unlock state that moves or releases value. A benign status enum
that never touches value is recorded but not boosted.

Local/static and read-only.
"""
from __future__ import annotations

import re

from . import models as M
from . import source_scan

_ENUM_RE = re.compile(r"\benum\s+([A-Za-z_]\w*)\s*\{([^}]*)\}")
_STATE_VAR_RE = re.compile(
    r"\b([A-Za-z_]\w*(?:Status|Phase|State|Stage|Round|Epoch|Cursor|Index|Nonce|Queue|"
    r"Pending|Request|Coverage|Deficit|Shortfall|Maturity|Checkpoint))\b"
)
_STATE_WORDS = (
    "status", "phase", "pending", "queued", "exited", "withdrawn", "claimed",
    "released", "activated", "finalized", "migrated", "locked", "unlocked", "cursor",
    "index", "checkpoint", "round", "epoch", "nonce", "request", "coverage",
    "deficit", "shortfall", "maturity",
)
_VALUE_WORDS = (
    "withdraw", "claim", "reward", "fee", "share", "mint", "burn", "oracle", "rate",
    "migrat", "queue", "coverage", "bridge", "message", "validator", "key", "adapter",
    "redeem", "release", "unstake",
)

# (keyword fragment -> subtype). First match wins.
_SUBTYPES = (
    ("withdraw", M.WITHDRAWAL_STATE),
    ("unstake", M.WITHDRAWAL_STATE),
    ("claim", M.CLAIM_STATE),
    ("reward", M.REWARD_STATE),
    ("fee", M.FEE_STATE),
    ("commission", M.FEE_STATE),
    ("queue", M.QUEUE_STATE),
    ("migrat", M.MIGRATION_STATE),
    ("finaliz", M.MIGRATION_STATE),
    ("oracle", M.ORACLE_ROUND_STATE),
    ("round", M.ORACLE_ROUND_STATE),
    ("coverage", M.COVERAGE_STATE),
    ("deficit", M.COVERAGE_STATE),
    ("shortfall", M.COVERAGE_STATE),
    ("maturity", M.MATURITY_STATE),
    ("bridge", M.BRIDGE_MESSAGE_STATE),
    ("message", M.BRIDGE_MESSAGE_STATE),
    ("validator", M.VALIDATOR_KEY_STATE),
    ("lock", M.LOCK_UNLOCK_STATE),
)


def _subtype(blob_low: str) -> str:
    for frag, subtype in _SUBTYPES:
        if frag in blob_low:
            return subtype
    return ""


def detect_state_machines(review_map, sources: dict, value_paths: list) -> list:
    value_contracts = {}
    for vp in value_paths:
        c = (vp.entry_function or vp.exit_function or "").split(".")[0]
        if c:
            value_contracts.setdefault(c, []).append(vp.path_id)

    machines: list = []
    counter = 0

    def _next_id() -> str:
        nonlocal counter
        counter += 1
        return f"SM-{counter:03d}"

    for contract, (path, text) in sorted(sources.items()):
        clean = source_scan.strip_comments(text)
        low = clean.lower()
        enums = [(m.group(1), m.group(2)) for m in _ENUM_RE.finditer(clean)]
        state_var_names = sorted({m.group(1) for m in _STATE_VAR_RE.finditer(clean)})
        state_words_here = sorted({w for w in _STATE_WORDS if w in low})
        if not (enums or state_var_names or len(state_words_here) >= 2):
            continue

        state_vars = sorted({e[0] for e in enums} | set(state_var_names))[:24]
        transitions: list = []
        for ename, body in enums:
            members = [s.strip() for s in body.split(",") if s.strip()]
            transitions.append(f"{ename}: {' -> '.join(members[:8])}")

        value_surfaces = value_contracts.get(contract, [])
        # Touches value only if the contract actually moves value AND a value word
        # co-occurs with the state machine (not a benign status enum).
        has_value_word = any(w in low for w in _VALUE_WORDS)
        touches_value = bool(value_surfaces) and has_value_word

        blob = (" ".join(state_vars) + " " + " ".join(state_words_here) + " " + low[:4000]).lower()
        subtype = _subtype(blob) if touches_value else ""

        notes: list = []
        if touches_value:
            notes.append("State machine gates value movement; transitions should be exercised against value.")
        else:
            notes.append("State machine detected but no value movement is gated by it (not boosted).")

        machines.append(M.StateMachine(
            state_machine_id=_next_id(),
            contract=contract,
            subtype=subtype,
            state_variables=state_vars,
            transitions=transitions[:8],
            touches_value=touches_value,
            value_surfaces=value_surfaces,
            source_lines=[f"{path}:L1"],
            notes=notes,
        ))
    return machines


def value_state_machine_contracts(machines: list) -> set:
    return {m.contract for m in machines if m.touches_value}


def state_machines_for_contract(machines: list, contract: str) -> list:
    contract = (contract or "").lower()
    return [m.state_machine_id for m in machines if m.contract.lower() == contract and m.touches_value]

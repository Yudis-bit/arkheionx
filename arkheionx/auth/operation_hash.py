"""Executed-field versus signed-field binding analysis."""
from __future__ import annotations

import re

from . import models as M

_ALIASES = {
    "destination": ("destination", "dest", "target"),
    "value": ("value", "amount"),
    "calldata": ("data", "calldata", "payload"),
    "operation_type": ("operationtype", "operation_type", "calldelegate", "usedelegate"),
    "nonce_or_sequence": ("nonce", "sequence"),
    "chain_id": ("block.chainid", "chainid", "chain_id"),
    "wallet_address": ("address(this)", "wallet", "accountaddress"),
    "expiry": ("expiry", "deadline", "validuntil"),
    "gas_payment": ("gasprice", "gaslimit", "gas_payment", "payment"),
    "refund_receiver": ("refundreceiver", "refund_receiver"),
    "token": ("token",),
    "asset": ("asset",),
    "batch_contents": ("batch", "transactions", "calls"),
    "signer_set": ("owners", "signers", "signer_set"),
    "threshold": ("threshold",),
    "receiver": ("receiver", "recipient"),
    "implementation": ("implementation", "logic"),
    "init_data": ("initdata", "init_data", "initializerdata"),
}

_VALUE_FIELDS = {"destination", "value", "calldata", "token", "asset", "receiver", "batch_contents"}
_CONTROL_FIELDS = {
    "operation_type", "nonce_or_sequence", "chain_id", "wallet_address", "expiry",
    "signer_set", "threshold", "implementation", "init_data", "refund_receiver",
}


def _normalized(value: str) -> str:
    return re.sub(r"\s+", "", value or "").lower()


def _mentions(text: str, field: str) -> bool:
    value = _normalized(text)
    return any(alias in value for alias in _ALIASES[field])


def extract_hash_expression(body: str) -> tuple[str, list[str]]:
    marker = re.search(r"keccak256\s*\(\s*abi\.encode(?:Packed)?\s*\(", body, re.I)
    if not marker:
        return "", []
    start = marker.end()
    depth = 1
    index = start
    while index < len(body) and depth:
        if body[index] == "(":
            depth += 1
        elif body[index] == ")":
            depth -= 1
        index += 1
    args = body[start:index - 1] if depth == 0 else body[start:]
    inputs = [part.strip() for part in args.split(",") if part.strip()]
    return body[marker.start():index], inputs


def build_binding_matrix(body: str, hash_expression: str) -> M.HashBindingMatrix:
    fields = {}
    for name in M.MATRIX_FIELDS:
        executed = _mentions(body, name)
        signed = _mentions(hash_expression, name)
        affects_value = name in _VALUE_FIELDS
        affects_control = name in _CONTROL_FIELDS
        bound_elsewhere = executed and not signed and name in ("signer_set", "threshold")
        if executed and (signed or bound_elsewhere):
            verdict = M.BOUND
        elif executed and not signed and name in ("destination", "calldata", "implementation", "init_data"):
            verdict = M.UNBOUND_CRITICAL
        elif executed and not signed and affects_value:
            verdict = M.UNBOUND_VALUE_FIELD
        elif executed and not signed and affects_control:
            verdict = M.UNBOUND_CONTROL_FIELD
        elif executed and not signed:
            verdict = M.UNBOUND_BUT_NON_VALUE
        else:
            verdict = M.UNKNOWN
        evidence = []
        if executed:
            evidence.append("field affects execution")
        if signed:
            evidence.append("field appears in operation hash")
        fields[name] = M.HashBindingField(
            field=name,
            executed=executed,
            signed=signed,
            affects_value=affects_value,
            affects_control=affects_control,
            bound_elsewhere=bound_elsewhere,
            verdict=verdict,
            evidence=evidence,
        )
    return M.HashBindingMatrix(fields=fields)


def analyze_operation(contract: str, function: str, body: str) -> M.SignedOperation | None:
    hash_expression, hash_inputs = extract_hash_expression(body)
    if not hash_expression:
        return None
    matrix = build_binding_matrix(body, hash_expression)
    value_bound = [
        name for name, field in matrix.fields.items()
        if field.affects_value and field.executed and field.signed
    ]
    value_unbound = [
        name for name, field in matrix.fields.items()
        if field.affects_value and field.executed and not field.signed
    ]
    control_bound = [
        name for name, field in matrix.fields.items()
        if field.affects_control and field.executed and (field.signed or field.bound_elsewhere)
    ]
    control_unbound = [
        name for name, field in matrix.fields.items()
        if field.affects_control and field.executed and not field.signed and not field.bound_elsewhere
    ]
    return M.SignedOperation(
        contract=contract,
        function=function,
        hash_expression=hash_expression,
        hash_inputs=hash_inputs,
        execution_inputs=[
            name for name, field in matrix.fields.items() if field.executed
        ],
        signer_source="ecrecover" if "ecrecover" in body else "signature checker",
        threshold_source="threshold" if "threshold" in body.lower() else "",
        nonce_source="nonce" if "nonce" in body.lower() else (
            "sequence" if "sequence" in body.lower() else ""
        ),
        chain_binding=matrix.field("chain_id").signed,
        wallet_binding=matrix.field("wallet_address").signed,
        value_fields_bound=value_bound,
        value_fields_unbound=value_unbound,
        control_fields_bound=control_bound,
        control_fields_unbound=control_unbound,
        replay_protection="nonce_or_sequence" if matrix.field("nonce_or_sequence").signed else "none",
        evidence=[f"{contract}.{function}: operation hash and execution fields compared"],
        confidence="HIGH",
        binding_matrix=matrix,
    )

"""Delegated-execution control binding analysis."""
from __future__ import annotations

from . import models as M


def analyze_delegatecall(operation: M.SignedOperation, body: str) -> M.DelegatecallAnalysis | None:
    if "delegatecall" not in body.lower():
        return None
    operation_bound = operation.binding_matrix.field("operation_type").signed
    target_bound = operation.binding_matrix.field("destination").signed
    calldata_bound = operation.binding_matrix.field("calldata").signed
    storage_risk = not (operation_bound and target_bound and calldata_bound)
    return M.DelegatecallAnalysis(
        contract=operation.contract,
        function=operation.function,
        delegatecall_present=True,
        operation_type_bound=operation_bound,
        target_bound=target_bound,
        calldata_bound=calldata_bound,
        storage_control_risk=storage_risk,
        threshold_required=bool(operation.threshold_source),
        verdict="DELEGATECALL_STORAGE_CONTROL" if storage_risk else "DELEGATECALL_BOUND",
        evidence=[f"{operation.contract}.{operation.function}: delegatecall binding"],
    )

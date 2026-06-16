"""Realism dimension of the severity gate (Step 5)."""
from __future__ import annotations

REALISM = {
    "DEBT_REPAYMENT_RECONCILIATION":
        "Only meaningful for low-decimal (e.g. 6) currencies; 18-decimal assets immune; "
        "no attacker profit (loss is lender dust, not attacker gain).",
    "LENDER_CONSENT_VALUE_AFFECTING_CALLDATA":
        "Requires cross-token predeposit and real AMM liquidity; same-token path immune; "
        "official buffers may be small; capture must be proven on a fork.",
    "BORROW_CONSERVATION":
        "Depends on real ordering/escrow; prove with a local PoC.",
    "DEPOSIT_CONSUMPTION":
        "Realistic if the token can reenter or the key is replayable; standard tokens may not reenter.",
    "VAULT_SHARE_ASSET_RECONCILIATION":
        "Realistic on an empty vault; mitigated by dead shares / virtual offset if present.",
    "COLLATERAL_STATUS_RELEASE":
        "Realistic only if the release path is reachable before settlement.",
    "ACCESS_CONTROLLED_VALUE_MOVEMENT":
        "Not realistic for an unprivileged attacker (trusted role).",
}


def realism(family: str, candidate=None) -> str:
    return REALISM.get(family, "Bound realism with real token/decimals/liquidity before submitting.")

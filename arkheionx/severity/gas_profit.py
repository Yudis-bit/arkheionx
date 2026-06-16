"""Gas / profitability dimension of the severity gate (Step 4)."""
from __future__ import annotations

GAS = {
    "DEBT_REPAYMENT_RECONCILIATION":
        "Not gas-profitable: per-call gain is dust and accrues to no attacker.",
    "DEPOSIT_CONSUMPTION":
        "Gas-profitable if the deposit exceeds gas (typical).",
    "VAULT_SHARE_ASSET_RECONCILIATION":
        "Gas-profitable if the victim deposit exceeds the attacker's seed + gas.",
    "LENDER_CONSENT_VALUE_AFFECTING_CALLDATA":
        "Profitability depends on whether the attacker captures the diverted value (often not).",
}


def gas(family: str) -> str:
    return GAS.get(family, "Profitability unclear; estimate attacker gain vs gas.")

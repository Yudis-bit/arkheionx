"""Impact dimension of the economic severity gate (Step 2)."""
from __future__ import annotations

IMPACT = {
    "DEBT_REPAYMENT_RECONCILIATION": ("victim loss (lenders)",
        "Lenders are under-credited by the rounding remainder while the loan closes."),
    "LENDER_CONSENT_VALUE_AFFECTING_CALLDATA": ("victim loss (predepositor)",
        "Victim's refund/buffer can decrease under an unconsented counterparty route."),
    "BORROW_CONSERVATION": ("protocol insolvency / value leak",
        "Funds released beyond what lenders funded, or without collateral escrow."),
    "DEPOSIT_CONSUMPTION": ("direct fund theft",
        "A deposit consumed twice / reentrantly drains funds."),
    "VAULT_SHARE_ASSET_RECONCILIATION": ("victim loss (next depositor)",
        "Share-price inflation steals a later depositor's assets."),
    "COLLATERAL_STATUS_RELEASE": ("victim loss / under-collateralization",
        "Collateral released before lenders are fully settled."),
    "SWAP_ACTUAL_RECEIVED_VS_CREDITED": ("accounting corruption",
        "Credited output diverges from actual received."),
    "ORACLE_DECIMAL_NORMALIZATION": ("mispricing",
        "Inconsistent decimals mis-price an asset."),
    "CROSS_CHAIN_SUPPLY_CONSERVATION": ("supply inflation",
        "Mint/burn/lock/unlock fails to conserve supply."),
    "ACCESS_CONTROLLED_VALUE_MOVEMENT": ("none (privileged)",
        "Value movement is restricted to a trusted role."),
}


def impact(family: str):
    return IMPACT.get(family, ("accounting corruption", "Impact unclear; classify by hand."))

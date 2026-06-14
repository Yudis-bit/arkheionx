"""Cap dimension of the economic severity gate (Step 3).

The cap is what bounds the loss. A small cap is the single biggest reason a
technically valid candidate is economically low.
"""
from __future__ import annotations

CAP = {
    "DEBT_REPAYMENT_RECONCILIATION": ("capped by rounding base units",
        "Loss <= per-tranche rounding (token base units). 18-decimal assets are "
        "effectively immune; only low-decimal currencies show meaningful dust."),
    "LENDER_CONSENT_VALUE_AFFECTING_CALLDATA": ("capped by deposit buffer",
        "Loss <= the predeposit/refund buffer; same-token path is immune; attacker "
        "capture is not proven without a fork."),
    "BORROW_CONSERVATION": ("uncapped / systemic if it breaks",
        "If conservation truly breaks, loss can be systemic."),
    "DEPOSIT_CONSUMPTION": ("uncapped (per deposit, repeatable)",
        "Loss can equal the deposit, repeatable across deposits."),
    "VAULT_SHARE_ASSET_RECONCILIATION": ("capped by victim deposit size",
        "Loss <= the victim's deposit; repeatable per victim."),
    "COLLATERAL_STATUS_RELEASE": ("capped by collateral / settlement gap",
        "Loss <= released collateral beyond the settlement gap."),
    "SWAP_ACTUAL_RECEIVED_VS_CREDITED": ("capped by slippage / fee",
        "Loss <= mis-credited delta; depends on real token behavior."),
    "ORACLE_DECIMAL_NORMALIZATION": ("capped by mispricing magnitude",
        "Loss <= the mispricing window."),
    "CROSS_CHAIN_SUPPLY_CONSERVATION": ("uncapped / systemic if it breaks",
        "Supply inflation can be systemic."),
    "ACCESS_CONTROLLED_VALUE_MOVEMENT": ("capped by user consent (role)",
        "Only a trusted role can move value."),
}

# Families whose cap is small enough that the default ceiling is LOW.
SMALL_CAP_FAMILIES = {"DEBT_REPAYMENT_RECONCILIATION"}


def cap(family: str):
    return CAP.get(family, ("unknown cap", "Cap not determined; bound it before submitting."))

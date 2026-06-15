"""Impact dimension of the economic severity gate (Step 2)."""
from __future__ import annotations

IMPACT = {
    "SIGNATURE_OPERATION_BINDING": ("unauthorized value redirection",
        "An executed value or control field is not bound by signer approval."),
    "THRESHOLD_AUTHORIZATION_BYPASS": ("unauthorized wallet control",
        "Fewer unique signers than the configured threshold can authorize execution."),
    "NONCE_SEQUENCE_REPLAY": ("repeated unauthorized execution",
        "A signed operation can execute more than once in the same domain."),
    "DELEGATECALL_STORAGE_CONTROL": ("wallet storage takeover",
        "Unsigned delegated-execution controls can mutate authorization storage."),
    "FACTORY_INITIALIZATION_TAKEOVER": ("account ownership takeover",
        "A deployed account can be initialized by an unauthorized caller."),
    "KEY_REUSE_REPLAY": ("cross-domain replay dependent on reused authority",
        "Replay requires the same signing authority in another domain."),
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

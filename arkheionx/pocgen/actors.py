"""Actor helpers for PoC skeletons (Layer 6)."""
from __future__ import annotations

# Family -> the actors a PoC needs.
_FAMILY_ACTORS = {
    "DEBT_REPAYMENT_RECONCILIATION": ["borrower", "lenderA", "lenderB"],
    "LENDER_CONSENT_VALUE_AFFECTING_CALLDATA": ["borrower", "lender", "attackerRoute"],
    "BORROW_CONSERVATION": ["borrower", "lender"],
    "DEPOSIT_CONSUMPTION": ["depositor", "attacker"],
    "VAULT_SHARE_ASSET_RECONCILIATION": ["attacker", "victim"],
    "COLLATERAL_STATUS_RELEASE": ["borrower", "lender"],
    "SWAP_ACTUAL_RECEIVED_VS_CREDITED": ["user"],
    "ACCESS_CONTROLLED_VALUE_MOVEMENT": ["attacker", "owner"],
}


def actors_for(family: str) -> list:
    return list(_FAMILY_ACTORS.get(family, ["actor"]))


def actor_decls(names) -> list:
    return [f"address internal {n} = makeAddr(\"{n}\");" for n in names]

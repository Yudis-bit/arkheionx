"""setUp() builders for PoC skeletons (Layer 6)."""
from __future__ import annotations

_SETUP = {
    "DEBT_REPAYMENT_RECONCILIATION": [
        "// TODO: deploy {contract} and a mock 6-decimal asset (realistic currency).",
        "// TODO: open an active loan funded by two tranches with principals that do",
        "//       NOT divide repayment evenly (e.g. 1 and 2 units), so flooring bites.",
    ],
    "LENDER_CONSENT_VALUE_AFFECTING_CALLDATA": [
        "// TODO: fork the chain (see required env) and bind the real swap venue.",
        "// TODO: lender predeposits token T; borrower will supply swapData (route).",
    ],
    "BORROW_CONSERVATION": [
        "// TODO: deploy {contract}; fund a lender deposit and borrower collateral.",
    ],
    "DEPOSIT_CONSUMPTION": [
        "// TODO: deploy {contract} and a mock token whose transfer can reenter.",
        "// TODO: create a deposit keyed as the contract expects.",
    ],
    "VAULT_SHARE_ASSET_RECONCILIATION": [
        "// TODO: deploy {contract} with an empty (first-depositor) state.",
        "// TODO: prepare a victim deposit and an attacker donation amount.",
    ],
    "COLLATERAL_STATUS_RELEASE": [
        "// TODO: deploy {contract}; open a collateralized position with live debt.",
    ],
    "SWAP_ACTUAL_RECEIVED_VS_CREDITED": [
        "// TODO: deploy {contract} and a fee-on-transfer / rebasing mock token.",
    ],
    "ACCESS_CONTROLLED_VALUE_MOVEMENT": [
        "// TODO: deploy {contract}; this path is gated by a trusted role.",
    ],
}


def setup_solidity(family: str, contract: str) -> list:
    lines = _SETUP.get(family, ["// TODO: deploy {contract} and set up actors/balances."])
    return [ln.replace("{contract}", contract) for ln in lines]


def setup_steps(family: str, contract: str) -> list:
    return [ln.lstrip("/ ").replace("{contract}", contract)
            for ln in setup_solidity(family, contract)]

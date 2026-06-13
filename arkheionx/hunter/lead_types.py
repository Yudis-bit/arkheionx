"""Universal lead-type classification for hunter mode.

Maps a research surface (plus its value-flow, state-machine, deployment, registry, and
source signals) onto one of the universal V9 lead types. Generic and protocol-agnostic:
the keywords describe value-flow behavior families, not any specific target.
"""
from __future__ import annotations

from . import models as M

# (keyword fragments) -> lead type. Order matters: earlier wins.
_KEYWORD_TYPES = (
    (("queue", "withdraw"), M.WITHDRAWAL_QUEUE),
    (("queue", "claim"), M.CLAIM_QUEUE),
    (("withdraw", "cooldown"), M.WITHDRAWAL_QUEUE),
    (("share", "inflation"), M.SHARE_ACCOUNTING),
    (("totalassets",), M.SHARE_ACCOUNTING),
    (("erc4626",), M.SHARE_ACCOUNTING),
    (("oracle",), M.ORACLE_RATE_ACCOUNTING),
    (("price",), M.ORACLE_RATE_ACCOUNTING),
    (("exchangerate",), M.ORACLE_RATE_ACCOUNTING),
    (("fee",), M.FEE_DISPATCH),
    (("commission",), M.FEE_DISPATCH),
    (("dispatch",), M.FEE_DISPATCH),
    (("reward",), M.REWARD_ACCOUNTING),
    (("validator", "key"), M.VALIDATOR_KEY_ACCOUNTING),
    (("validator",), M.VALIDATOR_KEY_ACCOUNTING),
    (("bridge",), M.BRIDGE_MESSAGE_ACCOUNTING),
    (("message", "domain"), M.CROSS_CHAIN_DOMAIN_SEPARATION),
    (("crosschain",), M.CROSS_CHAIN_DOMAIN_SEPARATION),
    (("isolation",), M.CROSS_POOL_ISOLATION),
    (("adapter",), M.ADAPTER_WITHDRAWABILITY),
    (("migrat",), M.MIGRATION_ACCOUNTING),
    (("vesting",), M.LOCK_UNLOCK_ACCOUNTING),
    (("lock",), M.LOCK_UNLOCK_ACCOUNTING),
    (("emergency",), M.EMERGENCY_EXIT_ACCOUNTING),
    (("rescue",), M.EMERGENCY_EXIT_ACCOUNTING),
    (("sweep",), M.EMERGENCY_EXIT_ACCOUNTING),
    (("initial",), M.INITIALIZATION_WIRING),
    (("clone",), M.INITIALIZATION_WIRING),
    (("factory",), M.INITIALIZATION_WIRING),
)


def classify_lead_type(
    *,
    surface: str,
    notes: list,
    title: str = "",
    state_machine_touches_value: bool = False,
    deployment_status: str = "",
    ordering: str = "",
) -> str:
    blob = " ".join([surface or "", title or "", " ".join(notes or [])]).lower()

    if deployment_status in M.DEPLOYMENT_MISMATCH_STATUSES:
        return M.DEPLOYMENT_MISMATCH
    if state_machine_touches_value:
        return M.STATE_MACHINE_VALUE_FLOW
    if "reentran" in blob or "external-call-before-state-update" in (ordering or ""):
        return M.REENTRANCY_ORDERING

    for fragments, lead_type in _KEYWORD_TYPES:
        if all(f in blob for f in fragments):
            return lead_type

    if "value-out" in (notes or []) or any(w in blob for w in ("withdraw", "redeem", "unstake", "claim")):
        return M.VALUE_OUT_PATH
    return M.GENERIC_VALUE_SURFACE

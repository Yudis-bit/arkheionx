"""Universal bug-lane templates for hunter mode.

These are research *lenses*, not findings. Each template encodes generic patterns,
value-flow and state-machine indicators, a severity ceiling (a planning ceiling, never
a severity claim), common kill conditions, and a minimal PoC shape. No template encodes
a line number, a known bug, or any target-specific knowledge, and none runs against a
live chain. They give the lead builder and PoC planner protocol-aware structure while
the engine stays generic.
"""
from __future__ import annotations

from . import models as M


def _t(patterns, value, state, ceiling, kills, poc):
    return {
        "patterns": patterns,
        "value_flow_indicators": value,
        "state_machine_indicators": state,
        "severity_ceiling": ceiling,
        "common_kill_conditions": kills,
        "minimal_poc_shape": poc,
    }


TEMPLATES = {
    "erc4626_share_inflation": _t(
        ["deposit", "mint", "totalAssets", "convertToShares", "first depositor"],
        ["share mint on first deposit", "totalAssets read"],
        ["none required"],
        M.HIGH_POSSIBLE,
        ["First deposit is protected by a dead-shares / virtual-offset mechanism.",
         "A local test shows the first depositor cannot steal a later depositor's assets."],
        "Deposit 1 wei, donate assets to inflate the share price, then show a second "
        "depositor mints 0 shares and loses value.",
    ),
    "vault_donation_totalassets": _t(
        ["totalAssets", "balanceOf(address(this))", "donate", "exchangeRate"],
        ["totalAssets uses raw balance", "exchange rate derived from balance"],
        ["none required"],
        M.HIGH_POSSIBLE,
        ["totalAssets tracks internal accounting, not raw balance.",
         "A donation does not change the redeemable rate."],
        "Donate assets directly, then show redeem returns more/less than deposited.",
    ),
    "withdrawal_queue_claim_replay": _t(
        ["requestWithdrawal", "claimWithdrawal", "queue", "cursor", "processed"],
        ["value released on claim"],
        ["WITHDRAWAL_STATE: requested -> claimable -> claimed"],
        M.HIGH_POSSIBLE,
        ["A claimed request is marked processed before value leaves (CEI).",
         "A request cannot be claimed twice."],
        "Request a withdrawal, claim it, then attempt a second claim and assert it reverts.",
    ),
    "reward_accumulator_checkpoint_desync": _t(
        ["rewardPerToken", "checkpoint", "accRewardPerShare", "userRewardDebt"],
        ["reward accrual on stake/unstake"],
        ["REWARD_STATE: checkpoint advances per action"],
        M.HIGH_POSSIBLE,
        ["Reward debt is checkpointed before balance changes.",
         "A local test shows reward cannot be double-claimed across a checkpoint."],
        "Stake, advance the accumulator, transfer/withdraw, and show double-counted rewards.",
    ),
    "fee_dispatch_commission_misallocation": _t(
        ["feeRecipient", "commission", "distribute", "split", "bps"],
        ["fee taken from value flow", "commission routed to recipient"],
        ["FEE_STATE: pending -> distributed"],
        M.MEDIUM_POSSIBLE,
        ["Fee math rounds in the protocol's favor and cannot exceed the principal.",
         "Recipient is fixed/authorized."],
        "Route a payment, then show fee/commission is mis-split or sent to an attacker-chosen recipient.",
    ),
    "oracle_rate_stale_or_manipulated": _t(
        ["latestAnswer", "latestRoundData", "getPrice", "twap", "updatedAt"],
        ["price/rate feeds a value conversion"],
        ["ORACLE_ROUND_STATE: round freshness"],
        M.HIGH_POSSIBLE,
        ["Oracle staleness and bounds are checked and a stale/zero/negative answer reverts.",
         "A local test shows out-of-range input cannot move value."],
        "Feed a stale or manipulated price, then show value is mispriced on the way out.",
    ),
    "proxy_implementation_mismatch": _t(
        ["EIP-1967 implementation slot", "upgradeTo", "expected_implementation"],
        ["proxy routes value-bearing calls"],
        ["none required"],
        M.HIGH_POSSIBLE,
        ["Live implementation matches the audited/expected implementation.",
         "Read-only RPC confirms no implementation change."],
        "Compare the live EIP-1967 implementation slot to the audited implementation (read-only).",
    ),
    "beacon_implementation_mismatch": _t(
        ["EIP-1967 beacon slot", "beacon.implementation()", "UpgradeableBeacon"],
        ["beacon governs many proxies' value logic"],
        ["none required"],
        M.HIGH_POSSIBLE,
        ["Beacon implementation matches the audited implementation."],
        "Read the beacon slot, call implementation() (read-only), and compare to audited.",
    ),
    "live_registry_changed": _t(
        ["getPools", "registry", "isListed", "poolCount"],
        ["registry routes value to listed contracts"],
        ["none required"],
        M.MEDIUM_POSSIBLE,
        ["Live registry set equals the listed in-scope set.",
         "Program confirms live registry entries are in scope."],
        "Read the live registry set (read-only) and diff it against the listed scope set.",
    ),
    "adapter_withdrawability_mismatch": _t(
        ["adapter", "pull", "withdrawTo", "maxWithdraw", "available"],
        ["adapter routes value out to a yield source"],
        ["none required"],
        M.HIGH_POSSIBLE,
        ["Adapter withdrawability matches accounting and cannot be drained beyond deposits."],
        "Deposit through the adapter, then show withdraw can pull more than deposited.",
    ),
    "cross_pool_isolation": _t(
        ["poolId", "isolated", "shared balance", "global accumulator"],
        ["value shared across pools that should be isolated"],
        ["none required"],
        M.HIGH_POSSIBLE,
        ["Per-pool accounting is fully isolated; one pool cannot drain another."],
        "Fund pool A, then show pool B can withdraw value belonging to pool A.",
    ),
    "cross_chain_domain_separation": _t(
        ["chainId", "domainSeparator", "sourceChain", "messageId"],
        ["cross-chain message authorizes value"],
        ["BRIDGE_MESSAGE_STATE: domain-scoped"],
        M.CRITICAL_POSSIBLE,
        ["Messages are domain/chain-scoped and cannot be replayed across chains."],
        "Replay a message from another domain/chain and show it authorizes value.",
    ),
    "bridge_message_replay": _t(
        ["relayMessage", "processed[messageId]", "nonce", "merkleRoot"],
        ["bridge releases value on message"],
        ["BRIDGE_MESSAGE_STATE: pending -> processed"],
        M.CRITICAL_POSSIBLE,
        ["A processed message id cannot be replayed.",
         "Nonces are strictly monotonic and bound to the domain."],
        "Process a message, then replay it and assert the second release reverts.",
    ),
    "factory_clone_initialization": _t(
        ["clone", "initialize", "init", "factory.create"],
        ["clone holds value after init"],
        ["INITIALIZATION_WIRING"],
        M.HIGH_POSSIBLE,
        ["Clones are initialized atomically at creation and cannot be re-initialized."],
        "Front-run or re-call initialize on a fresh clone and show takeover before funding.",
    ),
    "uninitialized_implementation": _t(
        ["_disableInitializers", "initializer", "implementation"],
        ["implementation could be initialized + selfdestruct/upgrade"],
        ["INITIALIZATION_WIRING"],
        M.HIGH_POSSIBLE,
        ["The implementation disables initializers in its constructor."],
        "Initialize the implementation directly and show control of a value path.",
    ),
    "migration_finalization_accounting": _t(
        ["migrate", "finalize", "snapshot", "merkleRoot"],
        ["migration moves value to a new system"],
        ["MIGRATION_STATE: pending -> finalized"],
        M.HIGH_POSSIBLE,
        ["Migration accounting conserves value and cannot be claimed twice across systems."],
        "Migrate, then claim in both old and new systems and show double-credit.",
    ),
    "emergency_withdraw_accounting": _t(
        ["emergencyWithdraw", "rescue", "sweep", "skim"],
        ["emergency path moves value out, often skipping accounting"],
        ["none required"],
        M.HIGH_POSSIBLE,
        ["Emergency exit updates accounting and cannot be used to bypass user balances."],
        "Trigger the emergency path and show it withdraws more than the caller's balance.",
    ),
    "lock_unlock_vesting": _t(
        ["lock", "unlock", "vest", "release", "cliff"],
        ["vesting releases value over time"],
        ["LOCK_UNLOCK_STATE: locked -> unlocked"],
        M.MEDIUM_POSSIBLE,
        ["Unlock math is monotonic and cannot release more than vested."],
        "Advance time partially and show unlock releases more than the vested amount.",
    ),
    "recipient_callback_reentrancy": _t(
        [".call{value:", "onERC777", "tokensReceived", "before state update"],
        ["value sent before state update"],
        ["none required"],
        M.HIGH_POSSIBLE,
        ["Checks-effects-interactions ordering holds; state updates before the external call.",
         "A reentrancy guard protects the path."],
        "Reenter through the recipient callback before state update and drain value.",
    ),
    "validator_key_accounting": _t(
        ["pubkey", "deposit_data_root", "validatorCount", "depositContract"],
        ["validator deposits move staked value"],
        ["VALIDATOR_KEY_STATE: registered -> activated"],
        M.HIGH_POSSIBLE,
        ["Validator keys cannot be reused and deposits map 1:1 to keys."],
        "Register a key, then reuse/duplicate it and show double-counted stake.",
    ),
    "maturity_valuation": _t(
        ["maturity", "matured", "redeemAtMaturity", "yieldToMaturity"],
        ["value released at maturity"],
        ["MATURITY_STATE: active -> matured"],
        M.MEDIUM_POSSIBLE,
        ["Maturity valuation is monotonic and cannot be gamed by timing."],
        "Redeem just before/after maturity and show over-valuation.",
    ),
    "role_gated_trusted_trap": _t(
        ["onlyOwner", "onlyRole", "onlyGovernance", "trusted"],
        ["value path reachable only by a trusted role"],
        ["none required"],
        M.NOT_ELIGIBLE,
        ["The only trigger is a trusted role the scope marks out of scope -> KILL unless "
         "an unprivileged path exists."],
        "Find an unprivileged path to the same effect; if none, do not pursue.",
    ),
    "public_test_covered_trap": _t(
        ["t.sol", "testRevert", "invariant", "regression"],
        ["behavior already exercised by a public test"],
        ["none required"],
        M.NOT_ELIGIBLE,
        ["A public/local test already exercises the behavior -> KILL unless a fresh "
         "post-test variant exists."],
        "Confirm the public test covers the exact behavior before spending time.",
    ),
    "scope_collision_trap": _t(
        ["V1 vs V2", "two products", "two programs", "chain mismatch"],
        ["wrong-surface risk"],
        ["none required"],
        M.NOT_ELIGIBLE,
        ["Scope collision unresolved -> PARK_SCOPE until the exact product/version/chain "
         "is confirmed."],
        "Resolve which product/version/chain is in scope before any PoC.",
    ),
    "dedup_blind_trap": _t(
        ["empty corpus", "no known", "no audits"],
        ["unknown duplicate risk"],
        ["none required"],
        M.NOT_ELIGIBLE,
        ["No known/audit corpus -> DEDUP_BLIND; normal leads capped to PARK_DEDUP unless "
         "a hard deployment mismatch or explicit post-audit freshness exists."],
        "Add known issues / audits / public tests before trusting a 'no duplicate' result.",
    ),
}

# Map a lead type to the most relevant template ids.
_LEAD_TYPE_TEMPLATES = {
    M.SHARE_ACCOUNTING: ["erc4626_share_inflation", "vault_donation_totalassets"],
    M.WITHDRAWAL_QUEUE: ["withdrawal_queue_claim_replay"],
    M.CLAIM_QUEUE: ["withdrawal_queue_claim_replay"],
    M.REWARD_ACCOUNTING: ["reward_accumulator_checkpoint_desync"],
    M.FEE_DISPATCH: ["fee_dispatch_commission_misallocation"],
    M.ORACLE_RATE_ACCOUNTING: ["oracle_rate_stale_or_manipulated"],
    M.DEPLOYMENT_MISMATCH: ["proxy_implementation_mismatch", "beacon_implementation_mismatch"],
    M.LIVE_REGISTRY_DIFF: ["live_registry_changed"],
    M.ADAPTER_WITHDRAWABILITY: ["adapter_withdrawability_mismatch"],
    M.CROSS_POOL_ISOLATION: ["cross_pool_isolation"],
    M.CROSS_CHAIN_DOMAIN_SEPARATION: ["cross_chain_domain_separation", "bridge_message_replay"],
    M.BRIDGE_MESSAGE_ACCOUNTING: ["bridge_message_replay"],
    M.INITIALIZATION_WIRING: ["factory_clone_initialization", "uninitialized_implementation"],
    M.MIGRATION_ACCOUNTING: ["migration_finalization_accounting"],
    M.EMERGENCY_EXIT_ACCOUNTING: ["emergency_withdraw_accounting"],
    M.LOCK_UNLOCK_ACCOUNTING: ["lock_unlock_vesting"],
    M.REENTRANCY_ORDERING: ["recipient_callback_reentrancy"],
    M.VALIDATOR_KEY_ACCOUNTING: ["validator_key_accounting"],
    M.STATE_MACHINE_VALUE_FLOW: ["withdrawal_queue_claim_replay", "reward_accumulator_checkpoint_desync"],
    M.SOURCE_RECOVERY_GAP: [],
    M.VALUE_OUT_PATH: ["recipient_callback_reentrancy"],
    M.GENERIC_VALUE_SURFACE: [],
}


def templates_for_lead_type(lead_type: str) -> list:
    return [TEMPLATES[t] for t in _LEAD_TYPE_TEMPLATES.get(lead_type, []) if t in TEMPLATES]


def template_ids_for_lead_type(lead_type: str) -> list:
    return list(_LEAD_TYPE_TEMPLATES.get(lead_type, []))


def all_templates() -> dict:
    return dict(TEMPLATES)

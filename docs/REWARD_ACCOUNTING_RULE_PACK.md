# Staking / Reward Accounting Rule Pack

This rule pack helps staking and reward systems prepare for review by detecting
reward indexes, accumulators, emissions, claims, locks, cooldowns, and lifecycle
signals.

It emits pre-audit readiness tasks, not vulnerability confirmations.

## Signals

- `stake`, `unstake`, `reward`, `claimReward`, `rewardPerToken`
- `accumulator`, `index`, `emission`, `epoch`, `vesting`
- `lock`, `cooldown`, `multiplier`, `boost`, `totalStaked`
- `pendingReward`, `earned`, `notifyRewardAmount`

## Readiness Findings

- `ARK-RWD-001`: Reward accounting without conservation tests.
- `ARK-RWD-002`: Accumulator/index logic without precision/rounding tests.
- `ARK-RWD-003`: Claim flow without double-claim prevention tests.
- `ARK-RWD-004`: Lock/cooldown reward lifecycle not tested.
- `ARK-RWD-005`: Emission/admin update assumptions not documented.

## Suggested Defensive Tests

- total rewards distributed do not exceed funded rewards,
- no overclaim across multiple users,
- accumulator monotonicity,
- stake/unstake/claim lifecycle,
- rounding dust behavior,
- admin emission update constraints.

## Limitations

The rule pack is heuristic. It cannot validate economic design, reward solvency,
or all edge cases without deeper manual review and formal audit preparation.


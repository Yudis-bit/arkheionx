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

## Related Security Memory

- Finding IDs: `ARK-RWD-001`, `ARK-RWD-002`, `ARK-RWD-003`, `ARK-RWD-004`, `ARK-RWD-005`
- Historical patterns: reward overclaim, accounting index drift, stale reward
  state.
- Suggested searches:

```sh
python3 scripts/search_knowledge.py "reward overclaim"
python3 scripts/search_knowledge.py "accumulator precision"
```

Use results to prioritize conservation, double-claim, and accumulator
monotonicity tests.

## Test Plan Mapping

Reward and staking findings map to conservation, no-double-claim, accumulator
precision, lifecycle boundary, and emission-admin tests in
`metadata/finding_test_plan_map.json`.

# Access Control / Upgradeability Rule Pack

This rule pack checks local/static signals for privileged setters, emergency
controls, role concentration, proxies, initializers, and upgrade boundaries.

It emits readiness gaps, not formal audit findings.

## Signals

- `onlyOwner`, `Ownable`, `AccessControl`, `DEFAULT_ADMIN_ROLE`
- `grantRole`, `revokeRole`, `hasRole`, `admin`, `owner`, `guardian`
- `multisig`, `timelock`, `setFee`, `setOracle`, `setStrategy`
- `pause`, `unpause`, `emergencyWithdraw`, `rescue`, `sweep`
- `upgradeTo`, `upgradeToAndCall`, `UUPSUpgradeable`, `initializer`
- `reinitializer`, `__gap`, `implementation`, `proxy`

## Readiness Findings

- `ARK-ACC-001`: Privileged setters without role-boundary tests.
- `ARK-ACC-002`: Emergency or rescue functions without documented constraints.
- `ARK-ACC-003`: Admin role concentration not documented.
- `ARK-UPG-001`: Upgradeable contract without initializer/upgrade tests.
- `ARK-UPG-002`: Storage layout or upgrade assumptions not documented.

## Suggested Defensive Tests

- unauthorized users cannot call privileged setters,
- admin changes are bounded,
- pause/unpause behavior matches docs,
- emergency controls are constrained,
- initializer cannot be called twice,
- upgrade authorization works as intended,
- timelock or multisig assumptions are documented.

## Limitations

The scanner cannot determine whether a real multisig policy is operationally
safe. It only highlights missing local tests and documentation signals.

## Related Security Memory

- Finding IDs: `ARK-ACC-001`, `ARK-ACC-002`, `ARK-ACC-003`, `ARK-UPG-001`, `ARK-UPG-002`
- Historical patterns: unprotected initializer, privileged operation boundary,
  upgrade authorization gap.
- Suggested searches:

```sh
python3 scripts/search_knowledge.py "admin setter risk"
python3 scripts/search_knowledge.py "initializer protection"
python3 scripts/search_knowledge.py "upgrade authorization"
```

Use these mappings to plan authorization tests and documentation, not to claim
a confirmed access-control bug.

## Test Plan Mapping

Access-control and upgradeability findings map to unauthorized-caller,
role-boundary, initializer-once, upgrade-authorization, and post-upgrade state
checks in `metadata/finding_test_plan_map.json`.

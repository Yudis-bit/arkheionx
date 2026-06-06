# Arkheionx Rule Packs

Arkheionx rule packs are local/static readiness heuristics. They map repository
signals to defensive review prompts, suggested tests, and remediation tasks.

They do not prove the presence or absence of vulnerabilities. They are not a
formal audit. They are designed to help authorized maintainers prepare for one.

## Current Rule Packs

| Rule Pack | Focus | Example Finding IDs |
|---|---|---|
| Vault Rule Pack | ERC4626-like accounting, strategy vaults, withdrawals, fees | `ARK-VLT-*` |
| Oracle Rule Pack | price feeds, TWAP/spot assumptions, stale rounds, bounds | `ARK-ORC-*` |
| Access Control / Upgradeability | privileged setters, emergency paths, initializers, proxies | `ARK-ACC-*`, `ARK-UPG-*` |
| Reentrancy / Value Flow | withdraw, redeem, claim, callbacks, external calls | `ARK-REENT-*` |
| Staking / Reward Accounting | reward indexes, emissions, claims, cooldowns, overclaim risks | `ARK-RWD-*` |
| AMM Rule Pack | swaps, reserves, LP shares, slippage, pool pricing | `ARK-AMM-*` |
| Lending Rule Pack | collateral/debt, borrow/repay, liquidations, interest indexes | `ARK-LEND-*` |

## How Rule Packs Work

Arkheionx reads local repository files and detects signals such as
`latestRoundData`, `convertToShares`, `onlyOwner`, `claimReward`,
`getReserves`, `borrow`, `liquidate`, or `nonReentrant`. In v0.6.0,
semantic-lite extraction adds function-level
evidence and test coverage mapping so weak keyword-only findings can be
downgraded instead of treated like stronger Solidity evidence.

When a gap is detected, Arkheionx emits a readiness finding with:

- stable finding ID,
- priority and confidence,
- detected signals,
- why it matters,
- historical pattern similarity,
- recommended defensive checks,
- suggested tests,
- evidence records,
- confidence reasons,
- detection sources,
- GitHub issue-plan metadata.

## What Rule Packs Do Not Prove

Rule packs do not provide full semantic Solidity analysis, call graph
verification, stateful exploit confirmation, or formal audit coverage. They
intentionally do not call live chains, scan deployed contracts, submit
transactions, or produce exploit payloads.

Use rule pack findings as a pre-audit readiness map.

## v0.9.0 Knowledge Map

Rule packs are now connected to `metadata/finding_knowledge_map.json` and
`metadata/security_memory_graph.json`.

Search examples:

```sh
python3 scripts/search_knowledge.py "oracle stale price"
python3 scripts/search_knowledge.py "vault accounting invariant"
python3 scripts/search_knowledge.py "reentrancy value flow"
python3 scripts/search_knowledge.py "AMM invariant"
python3 scripts/search_knowledge.py "liquidation boundary"
python3 scripts/search_knowledge.py "missing invariant"
```

The results show related finding IDs, historical pattern categories, suggested
defensive tests, and docs. They are readiness context only.

## AMM And Lending Packs

v1.4.0 prepares first-class AMM and lending readiness packs:

- [`docs/AMM_RULE_PACK.md`](AMM_RULE_PACK.md) covers invariant assumptions,
  LP share accounting, reserve-price dependence, non-standard token assumptions,
  and slippage/min-output controls.
- [`docs/LENDING_RULE_PACK.md`](LENDING_RULE_PACK.md) covers collateral/debt
  solvency, liquidation boundaries, interest/index accounting, oracle-dependent
  borrow/liquidation paths, reserve/cash accounting, and liquidation role
  boundaries.

These packs are heuristic and static. They help identify audit-preparation
gaps and suggested defensive tests; they do not confirm vulnerabilities.

## Test Plan Mapping

v1.5.0 adds `metadata/finding_test_plan_map.json` and
`scripts/generate_test_plan.py`. Rule-pack findings can now map to suggested
tests, invariant candidates, and Foundry skeleton function names.

Generated plans are defensive starter scaffolds. They are not formal
verification and require project-specific review.

## Configuration

v1.7.0 makes rule-pack keys stable for `.arkheionx.json`:

```json
{
  "schema_version": "1.7.0",
  "rule_packs": ["oracle", "access-control", "testing", "docs", "amm", "lending"]
}
```

See [`RULE_PACK_CONFIGURATION.md`](RULE_PACK_CONFIGURATION.md) and
[`CONFIG_REFERENCE.md`](CONFIG_REFERENCE.md). Empty `rule_packs` means the
default defensive set is enabled.

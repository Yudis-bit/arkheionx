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

## How Rule Packs Work

Arkheionx reads local repository files and detects term-based signals such as
`latestRoundData`, `convertToShares`, `onlyOwner`, `claimReward`, or
`nonReentrant`. The scanner then compares those signals against visible test,
documentation, and configuration coverage.

When a gap is detected, Arkheionx emits a readiness finding with:

- stable finding ID,
- priority and confidence,
- detected signals,
- why it matters,
- historical pattern similarity,
- recommended defensive checks,
- suggested tests,
- GitHub issue-plan metadata.

## What Rule Packs Do Not Prove

Rule packs do not provide semantic Solidity analysis, call graph verification,
stateful exploit confirmation, or formal audit coverage. They intentionally do
not call live chains, scan deployed contracts, submit transactions, or produce
exploit payloads.

Use rule pack findings as a pre-audit readiness map.


# Arkheionx Contest Readiness Report

## Important Notice

This is not a contest strategy document for exploiting systems. This is a defensive readiness document for authorized maintainers preparing a repository for external security review.
It is not a formal audit, not a security guarantee, and not a bounty guarantee.

## Contest Readiness Summary

- Protocol type: `staking`
- Readiness score: `52/100`
- High-confidence gaps: `7`
- Documentation gaps: `3`
- Missing invariants: `2`
- Scope clarity: `Needs maintainer confirmation`
- Researcher onboarding readiness: `Needs review`
- Suggested contest readiness status: `Needs hardening`

## Scope Preparation Checklist

- [ ] Contracts in scope listed.
- [ ] Contracts out of scope listed.
- [ ] Known limitations documented.
- [ ] Privileged roles documented.
- [ ] Oracle assumptions documented.
- [ ] Upgradeability assumptions documented.
- [ ] Test commands documented.
- [ ] Existing known issues documented.
- [ ] Previous audit reports linked if applicable.
- [ ] Emergency/admin procedures documented.

## Researcher Onboarding Checklist

- [ ] Build instructions work locally.
- [ ] Test instructions work locally.
- [ ] Architecture overview exists.
- [ ] Invariants are documented.
- [ ] Key state machines are documented.
- [ ] Threat model assumptions are documented.
- [ ] Known false positives are documented.

## Pre-Contest Remediation Priorities

### ARK-ORC-001 - Oracle-dependent logic without stale-price tests

- Priority: `High readiness gap`
- Confidence: `high`
- Evidence summary: src/OracleRewardFixture.sol in `getPrice`: Solidity function contains oracle or price-feed call evidence.
- Why it matters: Oracle-dependent accounting and control flows can be wrong when price data is stale, incomplete, or outside documented assumptions.
- Recommended remediation: Add local mock oracle tests for stale round rejection, heartbeat windows, answeredInRound, and updatedAt behavior.

Related Knowledge:
- Historical patterns: pattern-oracle-stale-price, pattern-spot-price-manipulation, pattern-pool-price-accounting
- Suggested defensive tests: stale-round-rejection, heartbeat-bound-test, decimal-normalization-test
- Related PoCs: poc-2025-11-moonwell, poc-2020-10-harvest, poc-2021-02-yearn-v1-dai
- Docs: docs/ORACLE_RULE_PACK.md, docs/RULE_PACKS.md, docs/SEARCH_GUIDE.md

### ARK-ORC-002 - Oracle usage lacks visible staleness, TWAP, bounds, or sanity coverage

- Priority: `High readiness gap`
- Confidence: `medium`
- Evidence summary: src/OracleRewardFixture.sol in `getPrice`: Solidity function contains oracle or price-feed call evidence.
- Why it matters: Oracle and price-feed signals were detected without enough freshness or sanity-check language.
- Recommended remediation: Document and test oracle freshness, decimals normalization, price bounds, and fallback behavior.

### ARK-TST-002 - No invariant tests detected for DeFi protocol shape

- Priority: `High readiness gap`
- Confidence: `medium`
- Evidence summary: src/OracleRewardFixture.sol in `rewardPerToken`: Solidity function contains oracle or price-feed call evidence.
- Why it matters: Protocol-like value flows were detected, but no invariant/property testing signal was found.
- Recommended remediation: Add Foundry invariant tests for accounting, oracle, role, and value-flow assumptions.

Related Knowledge:
- Historical patterns: pattern-missing-invariant-coverage, pattern-assumption-not-encoded-in-tests
- Suggested defensive tests: foundry-invariant-skeleton, stateful-fuzz-sequence, roundtrip-or-conservation-invariant
- Related PoCs: poc-2020-08-opyn, poc-2020-09-bzx-ifusdc, poc-2021-10-indexed-finance
- Docs: docs/READINESS_SCORE.md, templates/invariant_skeletons/ArkheionxReadinessInvariants.t.sol

### ARK-ACC-001 - Privileged setters without role-boundary tests

- Priority: `Medium readiness gap`
- Confidence: `high`
- Evidence summary: src/OracleRewardFixture.sol in `setOracle`: Solidity function contains access-control or lifecycle modifier evidence.
- Why it matters: Privileged setters can alter fees, oracles, strategies, treasury, roles, pause state, or accounting assumptions.
- Recommended remediation: Add tests proving unauthorized users cannot call privileged setters or role-management functions.

Related Knowledge:
- Historical patterns: pattern-unprotected-initializer, pattern-privileged-operation-boundary
- Suggested defensive tests: unauthorized-setter-reverts, role-boundary-negative-tests, admin-change-event-and-bounds-test
- Related PoCs: poc-2017-07-parity-multisig, poc-2020-06-balancer-deflationary, poc-2022-02-dexible
- Docs: docs/ACCESS_CONTROL_RULE_PACK.md, docs/RULE_PACKS.md

### ARK-ORC-004 - Oracle setter/admin path without role-boundary tests

- Priority: `Medium readiness gap`
- Confidence: `high`
- Evidence summary: src/OracleRewardFixture.sol in `getPrice`: Solidity function contains oracle or price-feed call evidence.
- Why it matters: Oracle configuration changes can alter all downstream accounting assumptions.
- Recommended remediation: Add tests proving only documented roles can update oracle configuration.

### ARK-ORC-005 - Missing price bounds or fallback assumptions documentation

- Priority: `Medium readiness gap`
- Confidence: `high`
- Evidence summary: src/OracleRewardFixture.sol in `getPrice`: Solidity function contains oracle or price-feed call evidence.
- Why it matters: Auditors and maintainers need explicit pricing assumptions to review whether the design handles oracle failure modes.
- Recommended remediation: Document min/max bounds, fallback oracle behavior, stale-price policy, and L2 sequencer assumptions if relevant.

### ARK-REENT-001 - External-call value flow needs reentrancy review

- Priority: `Medium readiness gap`
- Confidence: `medium`
- Evidence summary: src/OracleRewardFixture.sol in `stake`: Solidity function contains external value-flow call evidence.
- Why it matters: External call or token transfer terms were detected without guard or reentrancy-review signals.
- Recommended remediation: Review state update order and add local malicious-receiver tests where callbacks are possible.

Related Knowledge:
- Historical patterns: pattern-external-call-before-state-update, pattern-callback-capable-token
- Suggested defensive tests: reentrant-receiver-mock, state-update-before-external-call-test, double-claim-prevention
- Related PoCs: poc-2018-10-spankchain, poc-2020-04-uniswap-imbtc, poc-2021-03-dodo-crowdpool
- Docs: docs/REENTRANCY_VALUE_FLOW_RULE_PACK.md, docs/RULE_PACKS.md

### ARK-RWD-001 - Reward accounting needs conservation coverage

- Priority: `Medium readiness gap`
- Confidence: `medium`
- Evidence summary: src/OracleRewardFixture.sol in `rewardPerToken`: Solidity function contains oracle or price-feed call evidence.
- Why it matters: Reward/index/claim signals were detected without invariant testing.
- Recommended remediation: Add reward conservation and no-overclaim tests across multiple users and timing boundaries.

Related Knowledge:
- Historical patterns: pattern-reward-overclaim, pattern-accounting-index-drift
- Suggested defensive tests: reward-conservation-multi-user, claim-twice-reverts-or-noops, rewardPerToken-monotonicity
- Related PoCs: poc-2020-12-warp-finance, poc-2020-08-opyn, poc-2020-09-bzx-ifusdc
- Docs: docs/REWARD_ACCOUNTING_RULE_PACK.md, docs/RULE_PACKS.md

## Historical Pattern Similarity

### ARK-ORC-001 - Oracle-dependent logic without stale-price tests

Related Knowledge:
- Historical patterns: pattern-oracle-stale-price, pattern-spot-price-manipulation, pattern-pool-price-accounting
- Suggested defensive tests: stale-round-rejection, heartbeat-bound-test, decimal-normalization-test
- Related PoCs: poc-2025-11-moonwell, poc-2020-10-harvest, poc-2021-02-yearn-v1-dai
- Docs: docs/ORACLE_RULE_PACK.md, docs/RULE_PACKS.md, docs/SEARCH_GUIDE.md

### ARK-TST-002 - No invariant tests detected for DeFi protocol shape

Related Knowledge:
- Historical patterns: pattern-missing-invariant-coverage, pattern-assumption-not-encoded-in-tests
- Suggested defensive tests: foundry-invariant-skeleton, stateful-fuzz-sequence, roundtrip-or-conservation-invariant
- Related PoCs: poc-2020-08-opyn, poc-2020-09-bzx-ifusdc, poc-2021-10-indexed-finance
- Docs: docs/READINESS_SCORE.md, templates/invariant_skeletons/ArkheionxReadinessInvariants.t.sol

### ARK-ACC-001 - Privileged setters without role-boundary tests

Related Knowledge:
- Historical patterns: pattern-unprotected-initializer, pattern-privileged-operation-boundary
- Suggested defensive tests: unauthorized-setter-reverts, role-boundary-negative-tests, admin-change-event-and-bounds-test
- Related PoCs: poc-2017-07-parity-multisig, poc-2020-06-balancer-deflationary, poc-2022-02-dexible
- Docs: docs/ACCESS_CONTROL_RULE_PACK.md, docs/RULE_PACKS.md

## What To Fix Before Opening A Contest

### Must fix before contest

- `ARK-TST-002` - No invariant tests detected for DeFi protocol shape
- `ARK-ORC-002` - Oracle usage lacks visible staleness, TWAP, bounds, or sanity coverage
- `ARK-ORC-001` - Oracle-dependent logic without stale-price tests

### Should fix before contest

- `ARK-REENT-001` - External-call value flow needs reentrancy review
- `ARK-RWD-001` - Reward accounting needs conservation coverage
- `ARK-ORC-004` - Oracle setter/admin path without role-boundary tests
- `ARK-ORC-005` - Missing price bounds or fallback assumptions documentation
- `ARK-ACC-001` - Privileged setters without role-boundary tests
- `ARK-RWD-002` - Accumulator/index logic without precision/rounding tests
- `ARK-RWD-003` - Claim flow without double-claim prevention tests

### Document before contest

- `ARK-ORC-005` - Missing price bounds or fallback assumptions documentation
- `ARK-ACC-003` - Admin role concentration not documented
- `ARK-REENT-004` - External call path without documented ordering assumptions

### Acceptable to defer with explicit notes

- `ARK-VLT-009` - Vault accounting lacks visible roundtrip or conservation coverage

## Contest Safety Notes

- No exploit instructions.
- No bounty guarantee.
- No live target testing.
- Respect platform rules.

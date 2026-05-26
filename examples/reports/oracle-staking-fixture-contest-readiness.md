# Arkheionx Contest Readiness Report

## Important Notice

This is not a contest strategy document for exploiting systems. This is a defensive readiness document for authorized maintainers preparing a repository for external security review.
It is not a formal audit, not a security guarantee, and not a bounty guarantee.

## Contest Readiness Summary

- Protocol type: `staking`
- Readiness score: `65/100`
- High-confidence gaps: `3`
- Documentation gaps: `3`
- Missing invariants: `2`
- Scope clarity: `Needs maintainer confirmation`
- Researcher onboarding readiness: `Improving`
- Suggested contest readiness status: `Improving`

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

### ARK-TST-002 - No invariant tests detected for DeFi protocol shape

- Priority: `High readiness gap`
- Confidence: `medium`
- Evidence summary: src/OracleRewardFixture.sol in `rewardPerToken`: Solidity function contains oracle or price-feed call evidence.
- Why it matters: Protocol-like value flows were detected, but no invariant/property testing signal was found.
- Recommended remediation: Add Foundry invariant tests for accounting, oracle, role, and value-flow assumptions.

### ARK-ORC-001 - Oracle-dependent logic without stale-price tests

- Priority: `Medium readiness gap`
- Confidence: `medium`
- Evidence summary: src/OracleRewardFixture.sol in `getPrice`: Solidity function contains oracle or price-feed call evidence.
- Why it matters: Oracle-dependent accounting and control flows can be wrong when price data is stale, incomplete, or outside documented assumptions.
- Recommended remediation: Add local mock oracle tests for stale round rejection, heartbeat windows, answeredInRound, and updatedAt behavior.

### ARK-ORC-002 - Oracle usage lacks visible staleness, TWAP, bounds, or sanity coverage

- Priority: `Medium readiness gap`
- Confidence: `medium`
- Evidence summary: src/OracleRewardFixture.sol in `getPrice`: Solidity function contains oracle or price-feed call evidence.
- Why it matters: Oracle and price-feed signals were detected without enough freshness or sanity-check language.
- Recommended remediation: Document and test oracle freshness, decimals normalization, price bounds, and fallback behavior.

### ARK-ORC-005 - Missing price bounds or fallback assumptions documentation

- Priority: `Medium readiness gap`
- Confidence: `medium`
- Evidence summary: src/OracleRewardFixture.sol in `getPrice`: Solidity function contains oracle or price-feed call evidence.
- Why it matters: Auditors and maintainers need explicit pricing assumptions to review whether the design handles oracle failure modes.
- Recommended remediation: Document min/max bounds, fallback oracle behavior, stale-price policy, and L2 sequencer assumptions if relevant.

### ARK-REENT-001 - External-call value flow needs reentrancy review

- Priority: `Medium readiness gap`
- Confidence: `medium`
- Evidence summary: src/OracleRewardFixture.sol in `stake`: Solidity function contains external value-flow call evidence.
- Why it matters: External call or token transfer terms were detected without guard or reentrancy-review signals.
- Recommended remediation: Review state update order and add local malicious-receiver tests where callbacks are possible.

### ARK-RWD-001 - Reward accounting needs conservation coverage

- Priority: `Medium readiness gap`
- Confidence: `medium`
- Evidence summary: src/OracleRewardFixture.sol in `rewardPerToken`: Solidity function contains oracle or price-feed call evidence.
- Why it matters: Reward/index/claim signals were detected without invariant testing.
- Recommended remediation: Add reward conservation and no-overclaim tests across multiple users and timing boundaries.

### ARK-RWD-002 - Accumulator/index logic without precision/rounding tests

- Priority: `Medium readiness gap`
- Confidence: `high`
- Evidence summary: src/OracleRewardFixture.sol in `rewardPerToken`: Solidity function contains oracle or price-feed call evidence.
- Why it matters: Index and accumulator math can leak value or strand rewards through rounding across many users.
- Recommended remediation: Add precision, dust, rounding, and small-balance tests for accumulator or index logic.

### ARK-RWD-003 - Claim flow without double-claim prevention tests

- Priority: `Medium readiness gap`
- Confidence: `high`
- Evidence summary: src/OracleRewardFixture.sol in `rewardPerToken`: Solidity function contains oracle or price-feed call evidence.
- Why it matters: Claim flows depend on updating accrued state at exactly the right time.
- Recommended remediation: Add tests proving users cannot claim the same reward entitlement twice.

## What To Fix Before Opening A Contest

### Must fix before contest

- `ARK-TST-002` - No invariant tests detected for DeFi protocol shape

### Should fix before contest

- `ARK-ORC-002` - Oracle usage lacks visible staleness, TWAP, bounds, or sanity coverage
- `ARK-REENT-001` - External-call value flow needs reentrancy review
- `ARK-RWD-001` - Reward accounting needs conservation coverage
- `ARK-ORC-001` - Oracle-dependent logic without stale-price tests
- `ARK-ORC-005` - Missing price bounds or fallback assumptions documentation
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

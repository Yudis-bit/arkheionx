# Arkheionx Launch Readiness Report

## Important Notice

This is not a formal audit. It does not guarantee security. It does not confirm the absence or presence of vulnerabilities. It is a defensive pre-audit readiness artifact for authorized repositories.

## Executive Summary

- Project path: `examples/oracle-staking-fixture`
- Protocol type: `staking`
- Readiness score: `65/100`
- Score band: `Improving`
- Analysis date: `2026-05-26T01:50:21+00:00`
- Scanner version: `0.8.0`
- Semantic-lite status: `enabled`
- Slither status: `disabled`
- Launch readiness status: `Improving`
- Recommended next action: Address `ARK-TST-002` first, then re-run Arkheionx and compare against a baseline.

Top readiness themes:
- `ARK-TST-002` - No invariant tests detected for DeFi protocol shape (High readiness gap, medium confidence)
- `ARK-ORC-001` - Oracle-dependent logic without stale-price tests (Medium readiness gap, medium confidence)
- `ARK-ORC-002` - Oracle usage lacks visible staleness, TWAP, bounds, or sanity coverage (Medium readiness gap, medium confidence)
- `ARK-ORC-005` - Missing price bounds or fallback assumptions documentation (Medium readiness gap, medium confidence)
- `ARK-REENT-001` - External-call value flow needs reentrancy review (Medium readiness gap, medium confidence)

## Launch Readiness Snapshot

| Area                  | Status       | Notes                                      |
| --------------------- | ------------ | ------------------------------------------ |
| Testing readiness     | Needs review | 1 high/critical readiness gap(s) detected. |
| Invariant coverage    | Needs review | 1 high/critical readiness gap(s) detected. |
| Oracle assumptions    | Needs work   | 3 readiness gap(s) detected.               |
| Access control        | Needs work   | 1 readiness gap(s) detected.               |
| Reentrancy/value flow | Needs work   | 2 readiness gap(s) detected.               |
| Reward accounting     | Needs review | 1 high/critical readiness gap(s) detected. |
| Vault accounting      | Needs work   | 4 readiness gap(s) detected.               |
| Documentation         | Needs work   | 3 readiness gap(s) detected.               |

## Top Readiness Gaps

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

## Recommended Remediation Roadmap

### Phase 1 - Launch blockers

- [ ] `ARK-RWD-002` - Add precision, dust, rounding, and small-balance tests for accumulator or index logic.
- [ ] `ARK-RWD-003` - Add tests proving users cannot claim the same reward entitlement twice.
- [ ] `ARK-ACC-003` - Document who can change critical configuration and whether controls use a multisig, timelock, guardian, or single owner.

### Phase 2 - High-priority readiness gaps

- [ ] `ARK-TST-002` - Add Foundry invariant tests for accounting, oracle, role, and value-flow assumptions.
- [ ] `ARK-ORC-001` - Add local mock oracle tests for stale round rejection, heartbeat windows, answeredInRound, and updatedAt behavior.
- [ ] `ARK-ORC-002` - Document and test oracle freshness, decimals normalization, price bounds, and fallback behavior.
- [ ] `ARK-ORC-005` - Document min/max bounds, fallback oracle behavior, stale-price policy, and L2 sequencer assumptions if relevant.
- [ ] `ARK-REENT-001` - Review state update order and add local malicious-receiver tests where callbacks are possible.
- [ ] `ARK-RWD-001` - Add reward conservation and no-overclaim tests across multiple users and timing boundaries.
- [ ] `ARK-REENT-004` - Document state-update ordering, callback assumptions, and why any unguarded external calls are safe by design.

### Phase 3 - Documentation and test hardening

- No automated task assigned to this phase.

### Phase 4 - Before formal audit / contest

- [ ] `ARK-VLT-009` - Add deposit/withdraw roundtrip tests and totalAssets/share accounting invariants.

## Suggested Pre-Launch Checklist

- [ ] Fix launch blockers.
- [ ] Add missing invariants.
- [ ] Add oracle staleness/bounds tests if applicable.
- [ ] Add access-control negative tests if applicable.
- [ ] Add reentrancy/value-flow tests if applicable.
- [ ] Add reward/vault accounting conservation tests if applicable.
- [ ] Re-run Arkheionx and compare baseline.
- [ ] Prepare formal audit package.

## Generated Artifacts

| Artifact            | Path                                                             |
| ------------------- | ---------------------------------------------------------------- |
| Markdown Report     | `examples/reports/oracle-staking-fixture-pre-audit-report.md`    |
| Json Report         | `examples/reports/oracle-staking-fixture-pre-audit-report.json`  |
| Sarif Report        | `examples/reports/oracle-staking-fixture.sarif.json`             |
| Baseline            | `examples/reports/oracle-staking-fixture.baseline.json`          |
| Issue Checklist     | `examples/reports/oracle-staking-fixture-issue-checklist.md`     |
| Issue Plan          | `examples/reports/oracle-staking-fixture-issue-plan.json`        |
| Executive Summary   | `examples/reports/oracle-staking-fixture-executive-summary.md`   |
| Remediation Roadmap | `examples/reports/oracle-staking-fixture-remediation-roadmap.md` |
| Launch Report       | `examples/reports/oracle-staking-fixture-launch-report.md`       |
| Sprint Plan         | `examples/reports/oracle-staking-fixture-sprint-plan.md`         |
| Contest Readiness   | `examples/reports/oracle-staking-fixture-contest-readiness.md`   |

## Limitations

This is not a formal audit. It does not guarantee security. It does not confirm the absence or presence of vulnerabilities. It is a defensive pre-audit readiness artifact for authorized repositories.
Formal audit remains recommended before mainnet, material TVL, or user funds.

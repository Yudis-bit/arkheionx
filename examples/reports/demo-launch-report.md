# Arkheionx Launch Readiness Report

## Important Notice

This is not a formal audit. It does not guarantee security. It does not confirm the absence or presence of vulnerabilities. It is a defensive pre-audit readiness artifact for authorized repositories.

## Executive Summary

- Project path: `examples/oracle-staking-fixture`
- Protocol type: `staking`
- Readiness score: `52/100`
- Score band: `Early readiness`
- Analysis date: `2026-05-26T15:46:19+00:00`
- Scanner version: `1.0.0`
- Semantic-lite status: `enabled`
- Slither status: `disabled`
- Launch readiness status: `Needs hardening`
- Recommended next action: Address `ARK-ORC-001` first, then re-run Arkheionx and compare against a baseline.

Top readiness themes:
- `ARK-ORC-001` - Oracle-dependent logic without stale-price tests (High readiness gap, high confidence)
- `ARK-ORC-002` - Oracle usage lacks visible staleness, TWAP, bounds, or sanity coverage (High readiness gap, medium confidence)
- `ARK-TST-002` - No invariant tests detected for DeFi protocol shape (High readiness gap, medium confidence)
- `ARK-ACC-001` - Privileged setters without role-boundary tests (Medium readiness gap, high confidence)
- `ARK-ORC-004` - Oracle setter/admin path without role-boundary tests (Medium readiness gap, high confidence)

## Launch Readiness Snapshot

| Area                  | Status       | Notes                                      |
| --------------------- | ------------ | ------------------------------------------ |
| Testing readiness     | Needs review | 2 high/critical readiness gap(s) detected. |
| Invariant coverage    | Needs review | 2 high/critical readiness gap(s) detected. |
| Oracle assumptions    | Needs review | 2 high/critical readiness gap(s) detected. |
| Access control        | Needs work   | 3 readiness gap(s) detected.               |
| Reentrancy/value flow | Needs work   | 2 readiness gap(s) detected.               |
| Reward accounting     | Needs review | 1 high/critical readiness gap(s) detected. |
| Vault accounting      | Needs work   | 4 readiness gap(s) detected.               |
| Documentation         | Needs work   | 3 readiness gap(s) detected.               |

## Top Readiness Gaps

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

## Relevant Security Memory

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

## Recommended Remediation Roadmap

### Phase 1 - Launch blockers

- [ ] `ARK-ORC-001` - Add local mock oracle tests for stale round rejection, heartbeat windows, answeredInRound, and updatedAt behavior.
- [ ] `ARK-ACC-001` - Add tests proving unauthorized users cannot call privileged setters or role-management functions.
- [ ] `ARK-ORC-004` - Add tests proving only documented roles can update oracle configuration.
- [ ] `ARK-ORC-005` - Document min/max bounds, fallback oracle behavior, stale-price policy, and L2 sequencer assumptions if relevant.
- [ ] `ARK-RWD-002` - Add precision, dust, rounding, and small-balance tests for accumulator or index logic.
- [ ] `ARK-RWD-003` - Add tests proving users cannot claim the same reward entitlement twice.
- [ ] `ARK-ACC-003` - Document who can change critical configuration and whether controls use a multisig, timelock, guardian, or single owner.

### Phase 2 - High-priority readiness gaps

- [ ] `ARK-ORC-002` - Document and test oracle freshness, decimals normalization, price bounds, and fallback behavior.
- [ ] `ARK-TST-002` - Add Foundry invariant tests for accounting, oracle, role, and value-flow assumptions.
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

| Artifact            | Path                                           |
| ------------------- | ---------------------------------------------- |
| Markdown Report     | `examples/reports/demo-pre-audit-report.md`    |
| Json Report         | `examples/reports/demo-report.json`            |
| Sarif Report        | `examples/reports/demo.sarif.json`             |
| Baseline            | `examples/reports/demo.baseline.json`          |
| Issue Checklist     | `examples/reports/demo-issue-checklist.md`     |
| Issue Plan          | `examples/reports/demo-issue-plan.json`        |
| Executive Summary   | `examples/reports/demo-executive-summary.md`   |
| Remediation Roadmap | `examples/reports/demo-remediation-roadmap.md` |
| Launch Report       | `examples/reports/demo-launch-report.md`       |
| Sprint Plan         | `examples/reports/demo-sprint-plan.md`         |
| Contest Readiness   | `examples/reports/demo-contest-readiness.md`   |

## Limitations

This is not a formal audit. It does not guarantee security. It does not confirm the absence or presence of vulnerabilities. It is a defensive pre-audit readiness artifact for authorized repositories.
Formal audit remains recommended before mainnet, material TVL, or user funds.

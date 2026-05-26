# Arkheionx Remediation Roadmap

This is not a formal audit. It does not guarantee security. It does not confirm the absence or presence of vulnerabilities. It is a defensive pre-audit readiness artifact for authorized repositories.

| Task ID | Finding ID | Phase | Priority | Confidence | Effort | Expected Output |
|---|---|---|---|---|---|---|
| ARK-TASK-001 | `ARK-TST-002` | Phase 2 - High-priority readiness gaps | High readiness gap | medium | Large | Add Foundry invariant tests for accounting, oracle, role, and value-flow assumptions. |
| ARK-TASK-002 | `ARK-ORC-001` | Phase 2 - High-priority readiness gaps | Medium readiness gap | medium | Large | Use a local mock price feed to assert stale or incomplete oracle rounds are rejected or handled according to documented policy. |
| ARK-TASK-003 | `ARK-ORC-002` | Phase 2 - High-priority readiness gaps | Medium readiness gap | medium | Large | Document and test oracle freshness, decimals normalization, price bounds, and fallback behavior. |
| ARK-TASK-004 | `ARK-ORC-005` | Phase 2 - High-priority readiness gaps | Medium readiness gap | medium | Large | Add documentation plus local tests showing fallback and out-of-bounds price behavior. |
| ARK-TASK-005 | `ARK-REENT-001` | Phase 2 - High-priority readiness gaps | Medium readiness gap | medium | Unknown | Review state update order and add local malicious-receiver tests where callbacks are possible. |
| ARK-TASK-006 | `ARK-RWD-001` | Phase 2 - High-priority readiness gaps | Medium readiness gap | medium | Unknown | Add reward conservation and no-overclaim tests across multiple users and timing boundaries. |
| ARK-TASK-007 | `ARK-RWD-002` | Phase 1 - Launch blockers | Medium readiness gap | high | Medium | Fuzz stake sizes and reward amounts and assert reward indexes are monotonic and bounded by funded rewards. |
| ARK-TASK-008 | `ARK-RWD-003` | Phase 1 - Launch blockers | Medium readiness gap | high | Medium | Assert claim twice without new rewards returns zero or reverts according to documented policy. |
| ARK-TASK-009 | `ARK-ACC-003` | Phase 1 - Launch blockers | Low readiness gap | high | Medium | Add a role matrix to docs and unit tests for critical roles. |
| ARK-TASK-010 | `ARK-REENT-004` | Phase 2 - High-priority readiness gaps | Low readiness gap | medium | Medium | Pair ordering documentation with a local receiver test that exercises the documented boundary. |
| ARK-TASK-011 | `ARK-VLT-009` | Phase 4 - Before formal audit / contest | Low readiness gap | low | Small | Add deposit/withdraw roundtrip tests and totalAssets/share accounting invariants. |

## Acceptance Criteria

### ARK-TST-002 - No invariant tests detected for DeFi protocol shape

- Evidence summary: src/OracleRewardFixture.sol in `rewardPerToken`: Solidity function contains oracle or price-feed call evidence.
- [ ] Tests or documentation updated.
- [ ] Assumptions documented.
- [ ] Arkheionx re-run completed.
- [ ] Baseline diff reviewed if available.

### ARK-ORC-001 - Oracle-dependent logic without stale-price tests

- Evidence summary: src/OracleRewardFixture.sol in `getPrice`: Solidity function contains oracle or price-feed call evidence.
- [ ] Tests or documentation updated.
- [ ] Assumptions documented.
- [ ] Arkheionx re-run completed.
- [ ] Baseline diff reviewed if available.

### ARK-ORC-002 - Oracle usage lacks visible staleness, TWAP, bounds, or sanity coverage

- Evidence summary: src/OracleRewardFixture.sol in `getPrice`: Solidity function contains oracle or price-feed call evidence.
- [ ] Tests or documentation updated.
- [ ] Assumptions documented.
- [ ] Arkheionx re-run completed.
- [ ] Baseline diff reviewed if available.

### ARK-ORC-005 - Missing price bounds or fallback assumptions documentation

- Evidence summary: src/OracleRewardFixture.sol in `getPrice`: Solidity function contains oracle or price-feed call evidence.
- [ ] Tests or documentation updated.
- [ ] Assumptions documented.
- [ ] Arkheionx re-run completed.
- [ ] Baseline diff reviewed if available.

### ARK-REENT-001 - External-call value flow needs reentrancy review

- Evidence summary: src/OracleRewardFixture.sol in `stake`: Solidity function contains external value-flow call evidence.
- [ ] Tests or documentation updated.
- [ ] Assumptions documented.
- [ ] Arkheionx re-run completed.
- [ ] Baseline diff reviewed if available.

### ARK-RWD-001 - Reward accounting needs conservation coverage

- Evidence summary: src/OracleRewardFixture.sol in `rewardPerToken`: Solidity function contains oracle or price-feed call evidence.
- [ ] Tests or documentation updated.
- [ ] Assumptions documented.
- [ ] Arkheionx re-run completed.
- [ ] Baseline diff reviewed if available.

### ARK-RWD-002 - Accumulator/index logic without precision/rounding tests

- Evidence summary: src/OracleRewardFixture.sol in `rewardPerToken`: Solidity function contains oracle or price-feed call evidence.
- [ ] Tests or documentation updated.
- [ ] Assumptions documented.
- [ ] Arkheionx re-run completed.
- [ ] Baseline diff reviewed if available.

### ARK-RWD-003 - Claim flow without double-claim prevention tests

- Evidence summary: src/OracleRewardFixture.sol in `rewardPerToken`: Solidity function contains oracle or price-feed call evidence.
- [ ] Tests or documentation updated.
- [ ] Assumptions documented.
- [ ] Arkheionx re-run completed.
- [ ] Baseline diff reviewed if available.

### ARK-ACC-003 - Admin role concentration not documented

- Evidence summary: src/OracleRewardFixture.sol in `setOracle`: Solidity function contains access-control or lifecycle modifier evidence.
- [ ] Tests or documentation updated.
- [ ] Assumptions documented.
- [ ] Arkheionx re-run completed.
- [ ] Baseline diff reviewed if available.

### ARK-REENT-004 - External call path without documented ordering assumptions

- Evidence summary: src/OracleRewardFixture.sol in `stake`: Solidity function contains external value-flow call evidence.
- [ ] Tests or documentation updated.
- [ ] Assumptions documented.
- [ ] Arkheionx re-run completed.
- [ ] Baseline diff reviewed if available.

### ARK-VLT-009 - Vault accounting lacks visible roundtrip or conservation coverage

- Evidence summary: : No semantic-lite vault test coverage terms were detected.
- [ ] Tests or documentation updated.
- [ ] Assumptions documented.
- [ ] Arkheionx re-run completed.
- [ ] Baseline diff reviewed if available.

## Related Artifacts

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

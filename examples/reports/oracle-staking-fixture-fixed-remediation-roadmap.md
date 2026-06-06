# Arkheionx Remediation Roadmap

This is not a formal audit. It does not guarantee security. It does not confirm the absence or presence of vulnerabilities. It is a defensive pre-audit readiness artifact for authorized repositories.

| Task ID | Finding ID | Phase | Priority | Confidence | Effort | Expected Output |
|---|---|---|---|---|---|---|
| ARK-TASK-001 | `ARK-TST-002` | Phase 2 - High-priority readiness gaps | High readiness gap | medium | Large | Add Foundry invariant tests for accounting, oracle, role, and value-flow assumptions. |
| ARK-TASK-002 | `ARK-REENT-001` | Phase 2 - High-priority readiness gaps | Medium readiness gap | medium | Unknown | Use a local malicious receiver mock and assert withdraw/redeem/claim cannot be executed twice through reentry. |
| ARK-TASK-003 | `ARK-RWD-001` | Phase 2 - High-priority readiness gaps | Medium readiness gap | medium | Unknown | Add reward conservation and no-overclaim tests across multiple users and timing boundaries. |
| ARK-TASK-004 | `ARK-ACC-003` | Phase 2 - High-priority readiness gaps | Low readiness gap | medium | Medium | Add a role matrix to docs and unit tests for critical roles. |
| ARK-TASK-005 | `ARK-REENT-004` | Phase 2 - High-priority readiness gaps | Low readiness gap | medium | Medium | Pair ordering documentation with a local receiver test that exercises the documented boundary. |

## Acceptance Criteria

### ARK-TST-002 - No invariant tests detected for DeFi protocol shape

- Evidence summary: src/OracleRewardFixtureFixed.sol in `rewardPerToken`: Solidity function contains oracle or price-feed call evidence.
- [ ] Tests or documentation updated.
- [ ] Assumptions documented.
- [ ] Arkheionx re-run completed.
- [ ] Baseline diff reviewed if available.

### ARK-REENT-001 - Value flow with external calls needs reentrancy review

- Evidence summary: src/OracleRewardFixtureFixed.sol in `stake`: Solidity function contains external value-flow call evidence.
- [ ] Tests or documentation updated.
- [ ] Assumptions documented.
- [ ] Arkheionx re-run completed.
- [ ] Baseline diff reviewed if available.

### ARK-RWD-001 - Reward accounting needs conservation coverage

- Evidence summary: src/OracleRewardFixtureFixed.sol in `rewardPerToken`: Solidity function contains oracle or price-feed call evidence.
- [ ] Tests or documentation updated.
- [ ] Assumptions documented.
- [ ] Arkheionx re-run completed.
- [ ] Baseline diff reviewed if available.

### ARK-ACC-003 - Admin role concentration not documented

- Evidence summary: src/OracleRewardFixtureFixed.sol in `setOracle`: Solidity function contains access-control or lifecycle modifier evidence.
- [ ] Tests or documentation updated.
- [ ] Assumptions documented.
- [ ] Arkheionx re-run completed.
- [ ] Baseline diff reviewed if available.

### ARK-REENT-004 - External call path without documented ordering assumptions

- Evidence summary: src/OracleRewardFixtureFixed.sol in `stake`: Solidity function contains external value-flow call evidence.
- [ ] Tests or documentation updated.
- [ ] Assumptions documented.
- [ ] Arkheionx re-run completed.
- [ ] Baseline diff reviewed if available.

## Related Artifacts

| Artifact            | Path                                                                   |
| ------------------- | ---------------------------------------------------------------------- |
| Markdown Report     | `examples/reports/oracle-staking-fixture-fixed-pre-audit-report.md`    |
| Json Report         | `examples/reports/oracle-staking-fixture-fixed-pre-audit-report.json`  |
| Baseline            | `examples/reports/oracle-staking-fixture-fixed.baseline.json`          |
| Remediation Roadmap | `examples/reports/oracle-staking-fixture-fixed-remediation-roadmap.md` |
| Launch Report       | `examples/reports/oracle-staking-fixture-fixed-launch-report.md`       |

# Arkheionx Pre-Audit Sprint Plan

## Important Notice

Not a formal audit. Not a security guarantee. A defensive remediation planning document.

## Sprint Goal

Prepare this repository for a stronger formal audit, contest, or bug bounty readiness review.

## Sprint Inputs

- Readiness score: `52/100`
- Score band: `Early readiness`
- Number of findings: `13`
- Number of high confidence findings: `7`
- Number of issue-plan tasks: `13`
- Rule packs detected: `vault, oracle, access_control_upgradeability, reentrancy_value_flow, reward_accounting`
- Baseline available: `yes`
- Semantic-lite enabled: `enabled`

## Day-by-Day Plan

- **Day 1:** Triage, owner assignment, and baseline snapshot.
- **Day 2:** High-priority tests and invariants.
- **Day 3:** Accounting, oracle, access, and value-flow hardening.
- **Day 4:** Documentation, issue closure, and baseline diff.
- **Day 5:** Final readiness report and audit handoff package.

## Sprint Backlog

### Phase 1 - Launch blockers

- [ ] `ARK-ORC-001` - [Arkheionx][High] ARK-ORC-001 - Oracle-dependent logic without stale-price tests
  - Suggested owner: `TBD`
  - Expected output: Use a local mock price feed to assert stale or incomplete oracle rounds are rejected or handled according to documented policy.
  - Acceptance checklist:
    - [ ] Tests or docs updated.
    - [ ] Arkheionx re-run completed.
    - [ ] Remaining assumptions documented.
- [ ] `ARK-ACC-001` - [Arkheionx][Medium] ARK-ACC-001 - Privileged setters without role-boundary tests
  - Suggested owner: `TBD`
  - Expected output: For every privileged function, assert an unprivileged caller reverts and the documented role succeeds only within intended bounds.
  - Acceptance checklist:
    - [ ] Tests or docs updated.
    - [ ] Arkheionx re-run completed.
    - [ ] Remaining assumptions documented.
- [ ] `ARK-ORC-004` - [Arkheionx][Medium] ARK-ORC-004 - Oracle setter/admin path without role-boundary tests
  - Suggested owner: `TBD`
  - Expected output: Assert unprivileged callers cannot change oracle or fallback oracle configuration.
  - Acceptance checklist:
    - [ ] Tests or docs updated.
    - [ ] Arkheionx re-run completed.
    - [ ] Remaining assumptions documented.
- [ ] `ARK-ORC-005` - [Arkheionx][Medium] ARK-ORC-005 - Missing price bounds or fallback assumptions documentation
  - Suggested owner: `TBD`
  - Expected output: Add documentation plus local tests showing fallback and out-of-bounds price behavior.
  - Acceptance checklist:
    - [ ] Tests or docs updated.
    - [ ] Arkheionx re-run completed.
    - [ ] Remaining assumptions documented.
- [ ] `ARK-RWD-002` - [Arkheionx][Medium] ARK-RWD-002 - Accumulator/index logic without precision/rounding tests
  - Suggested owner: `TBD`
  - Expected output: Fuzz stake sizes and reward amounts and assert reward indexes are monotonic and bounded by funded rewards.
  - Acceptance checklist:
    - [ ] Tests or docs updated.
    - [ ] Arkheionx re-run completed.
    - [ ] Remaining assumptions documented.
- [ ] `ARK-RWD-003` - [Arkheionx][Medium] ARK-RWD-003 - Claim flow without double-claim prevention tests
  - Suggested owner: `TBD`
  - Expected output: Assert claim twice without new rewards returns zero or reverts according to documented policy.
  - Acceptance checklist:
    - [ ] Tests or docs updated.
    - [ ] Arkheionx re-run completed.
    - [ ] Remaining assumptions documented.
- [ ] `ARK-ACC-003` - [Arkheionx][Low] ARK-ACC-003 - Admin role concentration not documented
  - Suggested owner: `TBD`
  - Expected output: Add a role matrix to docs and unit tests for critical roles.
  - Acceptance checklist:
    - [ ] Tests or docs updated.
    - [ ] Arkheionx re-run completed.
    - [ ] Remaining assumptions documented.

### Phase 2 - High-priority readiness gaps

- [ ] `ARK-ORC-002` - [Arkheionx][High] ARK-ORC-002 - Oracle usage lacks visible staleness, TWAP, bounds, or sanity coverage
  - Suggested owner: `TBD`
  - Expected output: Document and test oracle freshness, decimals normalization, price bounds, and fallback behavior.
  - Acceptance checklist:
    - [ ] Tests or docs updated.
    - [ ] Arkheionx re-run completed.
    - [ ] Remaining assumptions documented.
- [ ] `ARK-TST-002` - [Arkheionx][High] ARK-TST-002 - No invariant tests detected for DeFi protocol shape
  - Suggested owner: `TBD`
  - Expected output: Add Foundry invariant tests for accounting, oracle, role, and value-flow assumptions.
  - Acceptance checklist:
    - [ ] Tests or docs updated.
    - [ ] Arkheionx re-run completed.
    - [ ] Remaining assumptions documented.
- [ ] `ARK-REENT-001` - [Arkheionx][Medium] ARK-REENT-001 - External-call value flow needs reentrancy review
  - Suggested owner: `TBD`
  - Expected output: Review state update order and add local malicious-receiver tests where callbacks are possible.
  - Acceptance checklist:
    - [ ] Tests or docs updated.
    - [ ] Arkheionx re-run completed.
    - [ ] Remaining assumptions documented.
- [ ] `ARK-RWD-001` - [Arkheionx][Medium] ARK-RWD-001 - Reward accounting needs conservation coverage
  - Suggested owner: `TBD`
  - Expected output: Add reward conservation and no-overclaim tests across multiple users and timing boundaries.
  - Acceptance checklist:
    - [ ] Tests or docs updated.
    - [ ] Arkheionx re-run completed.
    - [ ] Remaining assumptions documented.
- [ ] `ARK-REENT-004` - [Arkheionx][Low] ARK-REENT-004 - External call path without documented ordering assumptions
  - Suggested owner: `TBD`
  - Expected output: Pair ordering documentation with a local receiver test that exercises the documented boundary.
  - Acceptance checklist:
    - [ ] Tests or docs updated.
    - [ ] Arkheionx re-run completed.
    - [ ] Remaining assumptions documented.

### Phase 3 - Documentation and test hardening

- No automated backlog item assigned.

### Phase 4 - Before formal audit / contest

- [ ] `ARK-VLT-009` - [Arkheionx][Low] ARK-VLT-009 - Vault accounting lacks visible roundtrip or conservation coverage
  - Suggested owner: `TBD`
  - Expected output: Add deposit/withdraw roundtrip tests and totalAssets/share accounting invariants.
  - Acceptance checklist:
    - [ ] Tests or docs updated.
    - [ ] Arkheionx re-run completed.
    - [ ] Remaining assumptions documented.

## Sprint Exit Criteria

- [ ] All high-confidence high-priority gaps addressed or documented.
- [ ] Invariant tests added where applicable.
- [ ] Oracle/access/reentrancy/reward/vault assumptions documented.
- [ ] Issue plan reviewed.
- [ ] Baseline diff generated.
- [ ] Remaining risks documented.
- [ ] Formal audit package prepared.

## What This Sprint Does Not Do

- It does not replace a formal audit.
- It does not guarantee security.
- It does not test deployed contracts.
- It does not run live-chain transactions.

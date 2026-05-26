# Arkheionx Demo Case Study: Oracle Staking Before/After

This is an internal toy before/after case study. It compares two demo fixtures:

- before: `examples/oracle-staking-fixture`
- after: `examples/oracle-staking-fixture-fixed`

It is not a real external validation case study and not a formal audit.

## Goal

Show how adding visible readiness evidence can improve Arkheionx output:

- stale oracle handling tests;
- decimals normalization and price bounds tests;
- access-control negative tests;
- reward conservation and no-overclaim tests;
- invariant and fuzz test names;
- documented assumptions.

## Before Fixture

The original fixture intentionally has thin tests and broad readiness gaps.

Current demo score: `65/100` (`Improving`) on this branch.

Key themes:

- oracle-dependent reward math;
- admin-controlled oracle/emission settings;
- value-flow paths;
- limited invariant/fuzz coverage;
- limited documentation.

Artifacts:

- [Before report](../../examples/reports/oracle-staking-fixture-pre-audit-report.md)
- [Before Launch Report](../../examples/reports/oracle-staking-fixture-launch-report.md)
- [Before issue plan](../../examples/reports/oracle-staking-fixture-issue-plan.json)

## After Fixture

The fixed fixture is still toy code, but it adds explicit readiness evidence.

Current demo score: `83/100` (`Near audit-ready`) on this branch.

Artifacts:

- `examples/reports/oracle-staking-fixture-fixed-pre-audit-report.md`
- `examples/reports/oracle-staking-fixture-fixed-pre-audit-report.json`
- `examples/reports/oracle-staking-fixture-fixed-launch-report.md`
- `examples/reports/oracle-staking-fixture-fixed-remediation-roadmap.md`

## What Changed

| Area | Before | After |
|---|---|---|
| Oracle tests | Placeholder positive answer test | Stale round, heartbeat, decimals, and bounds terms visible |
| Access control | Owner setters present | Unauthorized setter and onlyOwner boundary terms visible |
| Reward accounting | Placeholder claim test | Conservation, no-overclaim, accumulator, and rounding terms visible |
| Invariants/fuzz | No invariant/fuzz terms | Invariant and fuzz lifecycle terms visible |
| Documentation | Minimal demo explanation | Assumptions and limitations described in fixture README |

## Score Snapshot

| Metric | Before | After |
|---|---:|---:|
| Readiness score | 65 | 83 |
| Score band | Improving | Near audit-ready |

The score improvement is a demo signal. It does not prove security.

## What This Demonstrates

- Readiness reports improve when tests and docs make assumptions explicit.
- Rule calibration can reduce priority when matching defensive evidence exists.
- Before/after demo artifacts make scanner behavior easier to evaluate.

## What This Does Not Demonstrate

- It does not prove the fixed fixture is secure.
- It does not prove real-world risk is removed.
- It does not replace expert review or formal audit.
- It does not claim external adoption.

## How To Reproduce

Run the normal demo scan against both fixture directories and compare JSON
scores, finding IDs, confidence reasons, and generated delivery artifacts.

# Arkheionx Demo Case Study: Oracle + Staking Fixture

This is an internal reproducible demo case study. It is not a real protocol
case study, not external validation, and not a formal audit.

## Demo Scope

- Fixture: `examples/oracle-staking-fixture`
- Protocol shape: staking/reward accounting with oracle dependency
- Analysis mode: local/static Arkheionx scan
- Live-chain behavior: none

## What The Fixture Simulates

The toy fixture contains:

- `latestRoundData` oracle usage;
- staking, unstaking, and reward claiming;
- reward accumulator/index-style accounting;
- owner-controlled oracle and emission settings;
- external token transfer paths;
- intentionally thin tests.

## What Arkheionx Detects

The demo report shows readiness prompts such as:

- missing invariant/property test coverage;
- oracle stale-price and bounds test gaps;
- reward conservation and no-overclaim test gaps;
- reentrancy/value-flow review prompts;
- admin-role documentation prompts.

These are readiness findings, not vulnerability confirmations.

## Evidence Examples

- `src/OracleRewardFixture.sol` in `getPrice`: oracle price-feed call evidence.
- `src/OracleRewardFixture.sol` in `stake`: external value-flow call evidence.
- `test/OracleRewardFixture.t.sol`: limited placeholder test coverage.

## Readiness Score

The exact score may change as rule calibration improves. The generated demo
report is the source of truth for the current branch.

## Generated Artifacts

- [Pre-audit report](../../examples/reports/oracle-staking-fixture-pre-audit-report.md)
- [Launch Report](../../examples/reports/oracle-staking-fixture-launch-report.md)
- [Issue plan](../../examples/reports/oracle-staking-fixture-issue-plan.json)
- [Sprint plan](../../examples/reports/oracle-staking-fixture-sprint-plan.md)
- [Contest Readiness report](../../examples/reports/oracle-staking-fixture-contest-readiness.md)
- [Remediation roadmap](../../examples/reports/oracle-staking-fixture-remediation-roadmap.md)

## Launch Report Summary

The Launch Report turns technical findings into a client-facing readiness
artifact with:

- executive summary;
- launch readiness snapshot;
- top readiness gaps;
- phased remediation roadmap;
- pre-launch checklist.

## Contest Readiness Summary

The Contest Readiness report prompts maintainers to prepare:

- contracts in and out of scope;
- oracle and role assumptions;
- build/test instructions;
- known limitations;
- researcher onboarding material.

## Before / After Remediation Idea

The companion fixed fixture shows how visible stale oracle tests, access-control
negative tests, reward conservation checks, and invariant/fuzz test names can
improve readiness output.

See [Oracle Staking Before/After](ORACLE_STAKING_BEFORE_AFTER.md).

## What This Proves

- Arkheionx can generate reproducible local/static demo artifacts.
- Findings include evidence and confidence context.
- Technical outputs can be converted into delivery artifacts.

## What This Does Not Prove

- It does not prove a real protocol is safe.
- It does not prove Arkheionx has external users or customers.
- It does not replace a formal audit.
- It does not confirm exploitable vulnerabilities.

## Related Knowledge Search

Use the v0.9.0 security memory graph to connect the demo findings to defensive
test ideas and historical pattern categories:

```sh
python3 scripts/search_knowledge.py "oracle stale price"
python3 scripts/search_knowledge.py "reward overclaim"
python3 scripts/search_knowledge.py "missing invariant"
```

Related findings include `ARK-ORC-001`, `ARK-RWD-001`, and `ARK-TST-002`.
These mappings explain readiness context only; they do not claim the toy
fixture has the same issue as any historical protocol.

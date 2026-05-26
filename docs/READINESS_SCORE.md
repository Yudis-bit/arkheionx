# Readiness Score

The Arkheionx readiness score is a 100-point heuristic for audit preparation.
It is designed to help indie DeFi builders identify gaps before formal audit
intake.

It is not a security rating, not a guarantee, and not evidence that a protocol
is safe.

## Score Bands

| Score | Band | Meaning |
|---:|---|---|
| 0-39 | Not audit-ready | Basic repository, testing, or documentation gaps are likely blocking audit intake. |
| 40-59 | Early readiness | Some structure exists, but important test or assumption coverage is missing. |
| 60-74 | Improving | Useful foundation with several readiness gaps still worth fixing. |
| 75-89 | Near audit-ready | Good hygiene, but manual review and targeted improvements are still needed. |
| 90-100 | Strong pre-audit hygiene | Strong preparation signals. Still not a formal audit result. |

## Categories

Generic/non-vault scoring:

| Category | Max | What It Rewards |
|---|---:|---|
| Repository structure | 15 | Solidity sources, recognized config, clear src/test/docs shape, CI. |
| Test presence | 20 | Test files, assertions, Foundry/Hardhat, protocol-specific tests. |
| Invariant/fuzz readiness | 20 | Invariants, fuzz tests, handlers, edge-case coverage. |
| DeFi risk coverage | 20 | Oracle, accounting, role, value-flow, and protocol-specific coverage. |
| Documentation readiness | 10 | README, security docs, assumptions, deployment/role notes. |
| Operational/admin readiness | 15 | Access control, emergency controls, upgrade notes, privileged setter coverage, incident/monitoring notes. |

Vault-specific scoring:

| Category | Max | What It Rewards |
|---|---:|---|
| Repository structure | 10 | Solidity vault-like sources, config, src/test/docs shape, CI. |
| Test presence | 15 | Test files, assertions, Foundry/Hardhat, deposit/withdraw, mint/preview coverage. |
| Vault accounting coverage | 20 | ERC4626/share accounting signals, totalAssets tests, conversion tests, roundtrip tests, donation/rounding tests. |
| Invariant/fuzz readiness | 20 | Invariants, fuzzing, handlers, edge cases, broad vault test vocabulary. |
| Oracle/pricing readiness | 10 | Stale price, bounds, decimals, oracle/pool pricing tests or no explicit pricing dependency. |
| Strategy/withdrawal lifecycle readiness | 10 | Strategy gain/loss tests, debt/harvest tests, withdrawal queue/cooldown lifecycle tests. |
| Admin/operational readiness | 10 | Role boundaries, pause/emergency behavior, upgrade coverage, fee accounting. |
| Documentation readiness | 5 | README, assumptions, limitations, roles, treasury, deployment notes. |

## Deductions And Gaps

The scanner reports readiness gaps when it sees patterns such as:

- no tests;
- no invariant tests for a DeFi-shaped protocol;
- oracle usage without visible staleness, TWAP, bounds, or sanity coverage;
- vault accounting without roundtrip or conservation coverage;
- ERC4626-like interface without preview function tests;
- shares/assets conversion without rounding tests;
- totalAssets external dependency without manipulation-resistance tests;
- strategy accounting without gain/loss tests;
- withdrawal queue/cooldown without lifecycle tests;
- fee logic without fee accounting tests;
- pause/emergency controls without operational tests;
- external-call value flow without guard or reentrancy-review signals;
- upgradeability without initializer review signals;
- admin setters without role documentation or tests;
- reward accounting without conservation or index tests;
- AMM math without invariant tests.

The gaps are review prompts. They are not confirmed vulnerabilities.

v0.3.0 assigns stable finding IDs to readiness gaps. Examples:

- `ARK-VLT-001` for vault accounting without invariant coverage;
- `ARK-ORC-001` for oracle-dependent vault pricing gaps;
- `ARK-TST-001` for missing Solidity tests;
- `ARK-ACC-001` for admin role-boundary gaps.

Use finding IDs in false-positive reports, PR comments, generated issue
checklists, and `.arkheionx.json` suppressions. Suppression does not change the
meaning of the score and does not prove safety.

v0.4.0 adds baseline diff mode. Diff status and score answer different
questions:

- score estimates current pre-audit hygiene;
- baseline diff shows what changed since a previous scan;
- resolved means "not detected now," not "formally proven fixed."

v0.6.0 adds semantic-lite evidence and confidence calibration. Stronger
function-level evidence can increase confidence, while matching test coverage
or weak keyword-only evidence can reduce priority. This affects issue-plan
selection and reviewer focus, but it does not turn the score into a security
guarantee.

v0.7.0 delivery artifacts use the score to choose launch-readiness status,
contest-readiness status, recommended next step, sprint priorities, and
remediation phases. These labels are planning aids, not safety claims.

v0.9.1 fixes negative-context calibration. A comment like "missing invariant
tests" or "no stale oracle tests" is no longer counted as positive coverage.
Those statements can reduce or cap relevant score categories and appear as
`negative_evidence` in JSON so teams can see why readiness credit was not
awarded.

## How To Improve The Score

Practical improvements:

- add Foundry or Hardhat tests for every core user flow;
- add Foundry invariant tests for accounting and roles;
- add fuzz tests for rounding, boundary values, and user sequences;
- document oracle assumptions and failure behavior;
- document privileged roles and emergency controls;
- write a formal audit scope with commit hash, contracts, assumptions, and
  known limitations;
- add CI that runs tests and static checks;
- add a `SECURITY.md` or docs page for disclosure and scope.

## Examples

Vault score improvements:

- deposit/withdraw roundtrip tests;
- totalAssets consistency invariant;
- donation/inflation resistance tests;
- fee accounting conservation tests;
- pause behavior tests.

Oracle score improvements:

- stale round rejection tests;
- decimals normalization tests;
- price bound tests;
- TWAP or sanity-check tests;
- oracle setter authorization tests.

Reward score improvements:

- reward conservation invariant;
- no-overclaim tests;
- index monotonicity tests;
- stake/unstake roundtrip tests;
- small-balance precision tests.

## Limitations

The score is useful because it is fast, local, and repeatable. It is limited
because it is heuristic. A repository can score well and still contain serious
bugs. A repository can score poorly because it uses naming patterns the scanner
does not understand yet.

Use the score to prioritize preparation, not to claim safety.

## Security Memory Context

In v0.9.0, readiness findings may include Related Knowledge from
`metadata/finding_knowledge_map.json`.

This can connect a score-impacting finding to historical pattern categories,
root-cause classes, failed assumptions, broken invariants, suggested defensive
tests, and related docs.

Historical similarity explains why a readiness check exists. It does not mean a
scanned repository has the same vulnerability as a historical PoC.

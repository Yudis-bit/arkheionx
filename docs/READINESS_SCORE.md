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

| Category | Max | What It Rewards |
|---|---:|---|
| Repository structure | 15 | Solidity sources, recognized config, clear src/test/docs shape, CI. |
| Test presence | 20 | Test files, assertions, Foundry/Hardhat, protocol-specific tests. |
| Invariant/fuzz readiness | 20 | Invariants, fuzz tests, handlers, edge-case coverage. |
| DeFi risk coverage | 20 | Oracle, accounting, role, value-flow, and protocol-specific coverage. |
| Documentation readiness | 10 | README, security docs, assumptions, deployment/role notes. |
| Operational/admin readiness | 15 | Access control, emergency controls, upgrade notes, privileged setter coverage, incident/monitoring notes. |

## Deductions And Gaps

The scanner reports readiness gaps when it sees patterns such as:

- no tests;
- no invariant tests for a DeFi-shaped protocol;
- oracle usage without visible staleness, TWAP, bounds, or sanity coverage;
- vault accounting without roundtrip or conservation coverage;
- external-call value flow without guard or reentrancy-review signals;
- upgradeability without initializer review signals;
- admin setters without role documentation or tests;
- reward accounting without conservation or index tests;
- AMM math without invariant tests.

The gaps are review prompts. They are not confirmed vulnerabilities.

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

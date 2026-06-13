# Toy Credit Market — Scope Note (synthetic)

Fully synthetic scope note for the `tests/fixtures/morpho_midnight_toy` demo. It
uses invented contract names (`CreditMarket`, `OfferBook`, `PeripheryBundler`,
`MarketGate`) and generic fixed-maturity credit-market patterns only. It does not
describe any real protocol, sponsor, or contest.

## Scope Summary

A synthetic fixed-maturity credit market: a `CreditMarket` with credit/debt unit
accounting, an `OfferBook` for settlement-time liquidity with maker group budgets,
a `PeripheryBundler` for composed target-based actions, and a `MarketGate` for
gated access.

## In Scope

- src/CreditMarket.sol
- src/OfferBook.sol
- src/PeripheryBundler.sol
- src/MarketGate.sol

## Out of Scope

- src/MockLoanToken.sol (test mock)
- test/ helpers and mocks
- Gas-only optimizations

## Valid Severity

- Only Medium and High impact findings qualify for a reward.
- Low and informational issues are not valid for this program.

## Trusted Roles

- The `owner` of CreditMarket is trusted and assumed to act honestly.
- The `admin` of MarketGate is a trusted allowlist operator.

## Trusted Integrations

- The loan token is a standard ERC20 and is a trusted dependency.

## Known Issues

- Rounding dust of a few wei in continuous-fee accrual is known and acknowledged.

## Accepted Risks

- Lazy loss-factor realization may briefly lag for an inactive position; accepted.

## Invariants To Preserve

- withdrawable must never exceed the loan-token value owed to lenders.
- Collateral withdrawal must keep the final position healthy.
- A maker's group budget caps exposure across offers and markets.
- A blocked party cannot enter, but can still repay and be liquidated.

## Focus Areas

- Periphery target accounting and caps (targetUnits, maxAssets, maxUnits).
- Collateral movement after a composed bundle target.
- Settlement-time liquidity and offer payment finality.
- Bad debt and loss-factor realization ordering.
- Maker group exposure caps.
- Gates: entry restriction without trapping safe exits.
- Fee correctness across settlement and continuous fees.

## Invalid Findings

- Centralization risk from the trusted owner/admin is invalid.
- Findings that rely on the trusted owner acting maliciously are invalid.

## Low-Only Patterns

- Pure event or metadata spec deviations with no value impact are low-only.

## Report Candidate Requirements

- A local proof-of-concept test demonstrating Medium/High impact.
- A clear loss, lock, incorrect-accounting, unauthorized-action, or invariant-break path.
- Confirmation the issue is not a known issue, accepted risk, or out-of-scope area.

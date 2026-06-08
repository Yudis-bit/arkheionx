# ExampleContestScope — Scope Note (synthetic)

This is a fully synthetic scope note for the `examples/scope-fixture` demo. It uses
invented `Example*` contract names and generic DeFi patterns only. It does not
describe any real protocol, sponsor, or contest.

## Scope Summary

ExampleProtocol is a synthetic stablecoin + savings-vault system: an
`ExampleStablecoin` minted against backing, an ERC4626-style `ExampleSavingsVault`,
an `ExampleRewardsDistributor`, an `ExampleWithdrawalNFT` claim queue, an
`ExampleOracle` price feed, an `ExampleManager` for signed mints and admin, an
`ExampleAdapter` to an external lending-like protocol, an `ExampleCrossChainComposer`,
and an `ExampleComplianceList`.

## In Scope

- src/ExampleStablecoin.sol
- src/ExampleSavingsVault.sol
- src/ExampleRewardsDistributor.sol
- src/ExampleWithdrawalNFT.sol
- src/ExampleOracle.sol
- src/ExampleManager.sol
- src/ExampleAdapter.sol
- src/ExampleCrossChainComposer.sol
- src/ExampleComplianceList.sol

## Out of Scope

- test/ helpers and mocks
- Any deployment scripts
- Gas-only optimizations

## Valid Severity

- Only Medium and High impact findings qualify for a reward.
- Low and informational issues are not valid for this program.

## Trusted Roles

- The `admin` / `owner` role is trusted and is assumed to act honestly.
- The signed-mint signer in ExampleManager is a trusted custodian.

## Trusted Integrations

- The external lending protocol behind ExampleAdapter is a trusted dependency.
- The cross-chain messaging layer used by ExampleCrossChainComposer is trusted for liveness.

## Off-Chain Assumptions

- The oracle price publisher is an honest off-chain operator.
- Compliance/blocklist updates are pushed by an honest off-chain compliance service.

## External Dependency Assumptions

- The external lending protocol remains solvent and returns honest balances.
- The messaging layer eventually delivers or fails a message deterministically.

## Known Issues

- First-deposit share rounding in ExampleSavingsVault is known and acknowledged.
- Reward dust of a few wei per epoch in ExampleRewardsDistributor is known.

## Accepted Risks

- Oracle latency of up to 1 hour is an accepted risk.
- Admin can pause the system; temporary pausing is an accepted risk.

## Prior Audit Notes

- A prior review covered the core mint/redeem path; the withdrawal NFT queue is new.

## Changed Since Audit

- ExampleWithdrawalNFT claim queue and ExampleCrossChainComposer were added after the prior review.

## Design Choices That Affect Validity

- ExampleSavingsVault rounds in favor of the vault by design.
- ExampleManager intentionally allows batched signed mints.

## Invariants To Preserve

- Total ExampleStablecoin supply is always fully backed by collateral.
- ExampleSavingsVault share price is non-decreasing under honest operation.
- A withdrawal claim cannot pay more than the queue funded for it.
- A blocked party cannot send or receive value on any path.

## Focus Areas

- Withdrawal queue and claim NFT accounting.
- Oracle decimals and staleness handling.
- Cross-chain compose refund and quarantine edges.
- Compliance enforcement across token, vault, NFT, and bridge.

## Invalid Findings

- Centralization risk from the trusted admin is invalid.
- Findings that rely on the trusted signer acting maliciously are invalid.

## Low-Only Patterns

- Pure ERC20 metadata or event spec deviations with no value impact are low-only.

## Report Candidate Requirements

- A local proof-of-concept test demonstrating Medium/High impact.
- A clear loss, lock, incorrect-accounting, unauthorized-action, or invariant-break path.
- Confirmation the issue is not a known issue, accepted risk, or out-of-scope area.

# AMM Rule Pack

Arkheionx AMM findings are defensive pre-audit readiness signals for authorized repositories. They are not formal audit findings, vulnerability confirmations, or exploit instructions.

Use this rule pack when a repository contains pool, swap, reserve, quote, or LP share accounting logic. The goal is to identify missing tests, missing documentation, and review areas before a formal audit, contest, or bug bounty launch.

## ARK-AMM-001 - AMM Invariant Assumptions Not Covered By Tests

Signals:
- `reserve0`, `reserve1`, `getReserves`, `kLast`
- `swap`, `addLiquidity`, `removeLiquidity`
- `constant product`, `x * y`, `stableswap`, `invariant`
- LP reserve or liquidity accounting terms

Why it matters:
AMM integrations should test reserve accounting, swap bounds, and invariant preservation under fees, rounding, and repeated operations.

Suggested tests:
- Swap preserves invariant within expected fee and rounding bounds.
- Add/remove liquidity updates reserves and LP supply consistently.
- Repeated swaps do not break reserve accounting.
- Zero or low liquidity behavior is documented and tested.

Calibration:
- High confidence requires Solidity-level swap or reserve evidence plus missing invariant/reserve accounting tests.
- Downgrade when invariant tests, reserve accounting tests, or explicit fee/rounding bounds are present.
- Common false positive: adapter-only references to an external AMM.

## ARK-AMM-002 - LP Share Accounting Without Mint/Burn Boundary Tests

Signals:
- `totalSupply`, `balanceOf`, `mint`, `burn`
- `liquidity`, `shares`, `poolToken`, `LP`

Why it matters:
LP share accounting determines who owns pool value. Low-liquidity and first-provider states often need explicit review.

Suggested tests:
- First liquidity provider behavior.
- Proportional minting.
- Proportional withdrawal.
- Rounding edge cases.
- Dust handling.

Calibration:
- High confidence requires LP supply or mint/burn evidence and missing proportionality tests.
- Downgrade when first-provider, proportional mint/burn, and dust tests are visible.

## ARK-AMM-003 - Spot-Price Or Reserve-Price Dependency Without Manipulation-Resistance Tests

Signals:
- `getAmountOut`, `quote`, reserve ratio, spot price
- reserve-derived pricing
- AMM pricing used for protocol decisions
- TWAP terms absent

Why it matters:
Spot or reserve-derived prices can be unstable readiness inputs unless bounded by protocol design.

Suggested tests:
- Price movement bounds.
- TWAP or delay assumption tests.
- Reserve movement scenario as a local unit test.
- Oracle/AMM price dependency documented clearly.

Calibration:
- High confidence requires reserve pricing evidence plus missing TWAP, delay, bounds, or reserve movement tests.
- Downgrade when TWAP, bounds, delay, or explicit spot-price assumptions are tested and documented.

## ARK-AMM-004 - Fee-On-Transfer Or Non-Standard Token Assumptions Not Documented

Signals:
- `transferFrom`, `safeTransferFrom`
- `amountIn` assumed equal to received amount
- `balanceBefore` or `balanceAfter` absent
- token transfer accounting terms

Why it matters:
Pools that account by requested input rather than actual received balance can have readiness gaps around fee-on-transfer or non-standard tokens.

Suggested tests:
- Actual received amount accounting.
- Fee-on-transfer token simulation.
- Rebasing/non-standard token documented as unsupported if not handled.

Calibration:
- Medium confidence when token transfer and amount accounting signals are present without balance-delta tests or unsupported-token documentation.
- Downgrade when non-standard token assumptions are explicit or balance-delta accounting is tested.

## ARK-AMM-005 - Slippage/Min-Output Constraints Missing Or Unclear

Signals:
- swap function without `minOut`, `amountOutMin`, deadline, or slippage terms
- `amountOut` calculated but no user bound appears visible

Why it matters:
Slippage and stale quote controls help users and integrations bound outcomes around swaps.

Suggested tests:
- `minOut` enforcement.
- Deadline or stale quote behavior.
- User-provided slippage bounds.

Calibration:
- Medium confidence when user-facing swap paths lack visible output bounds.
- Downgrade when swaps are internal-only and documented, or min-output/deadline behavior is tested.

## False-Positive Notes

AMM terms in documentation, interfaces, or external adapter mocks can be noisy. Arkheionx downgrades weak keyword-only signals when semantic-lite function evidence is absent. Manual review remains required.

## Related Search Queries

```sh
python3 scripts/search_knowledge.py "AMM invariant"
python3 scripts/search_knowledge.py "slippage boundary"
python3 scripts/search_knowledge.py "LP share accounting"
python3 scripts/search_knowledge.py "reserve price"
```

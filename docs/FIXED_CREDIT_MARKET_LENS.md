# Fixed Credit Market Protocol Lens

`fixed-credit-market` is the first Arkheionx [protocol lens](archive/versions/V7_5_PROTOCOL_LENS.md). It
models Fixed Credit Market as a protocol-specific economic system rather than generic
DeFi, so the review lanes, tasks, evidence requirements, and blind-spot ranking are
shaped by how the protocol actually moves value.

> Arkheionx protocol lenses help structure research.
> They do not confirm vulnerabilities.
> They do not replace audits.
> They do not run on live chains.
> They do not auto-submit reports.

The lens encodes **no line numbers** and **no specific known bug**. It is a model
of expected behavior. Human review is required for every conclusion.

## Why a protocol lens for this protocol

A fixed-maturity credit market with offer-based settlement and periphery bundles
does not behave like a generic vault or AMM. Treating it generically misses the
parts where value actually moves. The lens models it as:

- a fixed-maturity credit market;
- a credit/debt unit accounting system;
- a settlement-time liquidity protocol;
- an offer-based market with no locked maker capital;
- a multi-market maker exposure system;
- a collateralized borrowing system;
- a lazy bad-debt / loss-factor accounting system;
- a gated access-control system;
- a periphery-composed action system.

## Extraction

The lens searches local Solidity for five term groups and marks anything it cannot
find as `UNKNOWN_IN_LOCAL_REPO` (it never invents symbols):

- **Markets** — market, maturity, loanToken, collateral, lltv, lif, maxLIF, gate,
  tickSpacing, settlementFee, continuousFee, claimableSettlementFee.
- **Positions** — credit, debt, pendingFee, lastLossFactor, lastAccrual,
  collateral, collateralBitmap.
- **Market state** — totalUnits, withdrawable, lossFactor, continuousFeeCredit,
  consumed, group.
- **Offers** — maker, taker, buy, tick, price, start, expiry, maxAssets, maxUnits,
  group, callback, receiver, ratifier, ratifierData, reduceOnly.
- **Periphery / bundles** — bundle, targetAssets, targetUnits, maxAssets, maxUnits,
  repay, withdrawCollateral, supplyCollateral, referral, fee, skip, revert,
  callback, receiver.

## Behavior promises (PROMISE-MM-01 .. 14)

The lens ships 14 default behavior promises, each with evidence placeholders and
source mappings. Summary:

| ID | Promise |
|----|---------|
| PROMISE-MM-01 | Fixed maturity — no new debt after maturity, unwind stays possible |
| PROMISE-MM-02 | Credit/debt unit conservation with actual asset settlement |
| PROMISE-MM-03 | Settlement-time liquidity — no finalization without required payment |
| PROMISE-MM-04 | Maker group exposure cap across offers and markets |
| PROMISE-MM-05 | Multi-collateral solvency on final position health |
| PROMISE-MM-06 | Bad-debt socialization reduces lender credit consistently |
| PROMISE-MM-07 | Liquidation consistency across input modes |
| PROMISE-MM-08 | Post-maturity debt remains unwindable / liquidatable |
| PROMISE-MM-09 | Gates restrict entry without trapping safe exits |
| PROMISE-MM-10 | Fees never create unbacked value |
| PROMISE-MM-11 | Periphery target correctness (unit / side / net-gross) |
| PROMISE-MM-12 | Cap correctness binds the economically relevant amount |
| PROMISE-MM-13 | Callback finality — final invariants still hold |
| PROMISE-MM-14 | Market identity isolation — no cross-market reuse |

## Economic invariants (INV-MM-01 .. 12)

Each invariant carries a statement, a mathematical form, relevant
functions/state, missing-test placeholders, and impact-if-broken. Highlights:

- **INV-MM-01** — payment (or a valid position reduction) backs every value-out.
- **INV-MM-03** — collateral withdrawal only when final position health is valid.
- **INV-MM-05** — `withdrawable` never exceeds the loan value owed to lenders.
- **INV-MM-06** — maker/group exposure never exceeds the signed budget.
- **INV-MM-07** — a target-based periphery path stops only when the user-intended
  target (correct dimension) is met.
- **INV-MM-08** — caps/targets bind the correct gross/net amount under fees.
- **INV-MM-10** — one market's accounting/authorization cannot affect another.
- **INV-MM-12** — candidates near known families are tested against a patch model.

## Review lanes (LANE-01 .. 10)

Lane priority is review order, not severity.

1. **LANE-01** Periphery target accounting
2. **LANE-02** Collateral movement after composed target
3. **LANE-03** Settlement-time liquidity
4. **LANE-04** Maker group cap
5. **LANE-05** Bad debt and lossFactor
6. **LANE-06** Liquidation consistency
7. **LANE-07** Gates
8. **LANE-08** Authorization / ratifier / signatures
9. **LANE-09** Fee correctness
10. **LANE-10** Callback temporal windows

## Temporal windows

The lens models four observation windows: the settlement callback window, the
periphery bundle composition window, the maturity boundary window, and the
loss-factor realization window.

## Try it on the synthetic fixture

A fully synthetic toy fixture lives at `tests/fixtures/fixed_credit_market_toy/`
(invented contracts, not real-protocol source). Run:

```bash
arkheionx lens-pack tests/fixtures/fixed_credit_market_toy \
  --lens fixed-credit-market \
  --scope-file tests/fixtures/fixed_credit_market_toy/scope.md \
  --out .arkheionx/lens-pack
```

## Boundary

A lens is not a finding. A review lane is not a vulnerability. An evidence score is
not vulnerability validity. A candidate with evidence is not confirmed. Lane and
task priority are not severity. No RPC, no live-chain calls, no exploit automation.
Human review is required.

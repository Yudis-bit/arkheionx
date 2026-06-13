# Protocol Lens Packs

Protocol Lens Packs let Arkheionx model a **protocol family** without making the
core engine target-specific. A lens encodes a family's value flows, behavior
promises, economic invariants, temporal windows, and periphery composition, so the
review lanes, tasks, and evidence requirements become protocol-aware.

A lens is a planning model, not a finding. It does not name or target any specific
deployed protocol. It does not confirm vulnerabilities, assign severity, or replace
an audit.

## Using a lens

Add `--lens <id>` to `arkheionx review`, or use the standalone lens commands:

```bash
arkheionx lens-list
arkheionx review . --scope-file scope.md --lens fixed-credit-market --out .arkheionx/review
```

When a lens is selected, the review pack gains protocol-aware artifacts:
`10-protocol-model.md`, `11-behavior-promises.md`, `12-economic-invariants.md`,
`13-temporal-windows.md`, `14-lens-review-lanes.md`, and `15-lens-evidence-tasks.md`.

## The Fixed Credit Market lens

The first shipped lens is the generic **Fixed Credit Market** family
(`fixed-credit-market`). It models a fixed-maturity credit market: credit/debt unit
accounting, settlement-time liquidity, maker/taker offer settlement, maker group
exposure, multi-collateral solvency, bad-debt / loss-factor accounting, fees, gated
access, and periphery bundle composition. See
[`FIXED_CREDIT_MARKET_LENS.md`](FIXED_CREDIT_MARKET_LENS.md).

## Standalone lens commands

`lens-list`, `lens-map`, `lens-lanes`, `lens-tasks`, `lens-pack`, `lens-evidence`,
and `lens-report-filter`. The full deep-dive lens pack is `arkheionx lens-pack`; the
one-command `arkheionx review --lens` embeds the same protocol-aware artifacts in a
single review pack.

## Boundary

A lens is a planning artifact, not a finding. A review lane is not a vulnerability.
Evidence quality is not vulnerability validity. Local/static only — no RPC, no
live-chain scanning, no auto-submit. Human review is required.

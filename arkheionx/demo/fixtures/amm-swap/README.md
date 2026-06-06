# Arkheionx AMM Swap Fixture

A minimal toy constant-product AMM fixture for Arkheionx demonstrations.

## What it demonstrates

- swap-style value flow (`swapAForB` / `swapBForA`),
- reserves and a constant-product `getAmountOut`,
- liquidity add/remove paths,
- a slippage (`minOut`) check and an owner-only fee control surface,
- surfaces worth ranking around swap/removeLiquidity/sync paths.

## What it does not demonstrate

- a production AMM, real pricing, or oracle integration,
- a real vulnerability, a bounty submission, or any severity claim.

## Try it

```sh
arkheionx demo --copy amm-swap ./demo-amm
arkheionx open ./demo-amm
arkheionx hunt ./demo-amm --top 5
```

Recommended target: `AMMSwapFixture.swapAForB`.

## Safety

Local-only toy fixture. No RPC, no private keys, no secrets, no real deployed
addresses, no mainnet fork. Not a real vulnerability report, not a bounty
submission, not a severity claim. Human review is always required.

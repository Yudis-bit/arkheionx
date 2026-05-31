# Arkheionx Lending Vault Fixture

A minimal toy lending/vault fixture for Arkheionx demonstrations.

## What it demonstrates

- deposit / withdraw / borrow / repay value flow,
- collateral and debt accounting,
- an owner-set local price and a health-factor review surface,
- a `liquidate` path gated by health,
- surfaces worth ranking around borrow/withdraw/liquidate/setPrice.

## What it does not demonstrate

- a production lending market, real assets, or an external oracle,
- a real vulnerability, a bounty submission, or any severity claim.

## Try it

```sh
arkheionx demo --copy lending-vault ./demo-lending
arkheionx open ./demo-lending
arkheionx hunt ./demo-lending --top 5
```

Recommended target: `LendingVaultFixture.borrow`.

## Safety

Local-only toy fixture. No RPC, no private keys, no secrets, no real deployed
addresses, no mainnet fork. The price is a local owner-set value, not a live
feed. Not a real vulnerability report, not a bounty submission, not a severity
claim. Human review is always required.

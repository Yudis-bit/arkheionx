# Vault / Strategy / Oracle demo fixture

A small **multi-contract** DeFi fixture for the ArkheionX review-map demo. It
exists to show the core idea on more than one contract:

> Foundry tells you whether the tests you wrote pass.
> ArkheionX shows the value paths you may have forgotten to test.

This is local/static demo code only. It is **not** production code, not a
deployable recommendation, and not an exploit target. There is no planted bug.
The demo works by leaving real value paths untested, not by hiding a
vulnerability.

## The contracts

| Contract | Role | Value behavior |
|---|---|---|
| `Vault.sol` | Share vault (entry/exit) | `deposit` pulls value in; `withdraw` / `emergencyWithdraw` push value out |
| `Strategy.sol` | Yield strategy | `invest` pulls value in from the vault; `divest` returns it |
| `PriceOracle.sol` | Trust assumption | admin-set `setPrice`; `getPrice` guards accounting |
| `MockToken.sol` | Asset | ERC20-like token moved between the above |

## The value flow

```
deposit ──▶ Vault ──rebalance──▶ Strategy ──harvest (oracle)──▶ accounting
   ▲                                  │
   │                                  ▼
caller ◀──withdraw / emergencyWithdraw / divest── value exits
```

## What the test covers (and what it does not)

`test/Vault.t.sol` covers the **deposit** entry path and an oracle price sanity
check. It deliberately leaves the value **exits** (`withdraw`,
`emergencyWithdraw`, `divest`) and the **admin** trust setters (`setOracle`,
`setPrice`) untested. That is the whole point: a green test run that still has
uncovered value paths.

## Run it

```sh
arkheionx review-map examples/vault-strategy-oracle-fixture
```

Real output (abridged) at the time of writing:

```
OK    Map review surface  3 contracts, 14 functions, 3 value paths, 5 test gaps

Inspect first
1  HIGH   Strategy.divest            Signals  external-call, value-out
2  HIGH   Vault.emergencyWithdraw    Signals  external-call, privileged, value-out
3  HIGH   Vault.withdraw             Signals  external-call, value-out
```

Focused value paths (`arkheionx value-paths examples/vault-strategy-oracle-fixture`):

```
1. Strategy: invest -> divest          [high; HEURISTIC; coverage none]
2. Vault: deposit -> emergencyWithdraw  [high; HEURISTIC; coverage none]
3. Vault: deposit -> withdraw           [high; HEURISTIC; coverage none]
```

Test gaps (`arkheionx test-gap-map examples/vault-strategy-oracle-fixture`):

```
gap-vault-withdraw        (exit)   proof: proof-vault-withdraw
gap-vault-emergencywithdraw (exit) proof: proof-vault-emergencywithdraw
gap-strategy-divest       (exit)   proof: proof-strategy-divest
gap-vault-setoracle       (admin)  proof: proof-vault-setoracle
gap-priceoracle-setprice  (admin)  proof: proof-priceoracle-setprice
```

Every value path links to the assumptions that guard it (oracle freshness,
share proportionality, no-reentrancy, standard ERC20) and to a proof suggestion
you can scaffold with `arkheionx prove`. Output is review guidance, not confirmed
vulnerabilities. Human review is required.

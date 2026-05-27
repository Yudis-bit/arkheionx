# Vault Rule Pack

The Arkheionx v0.2.0 Vault Rule Pack improves pre-audit readiness reporting for
vault builders: ERC4626-like vaults, strategy vaults, yield vaults, staking
vaults, and share/accounting systems.

It is defensive and local-only. It does not inspect deployed contracts, call
RPC endpoints, submit transactions, or prove exploitability.

For the full rule-pack map, see [RULE_PACKS.md](RULE_PACKS.md).

## Why Vaults Are High-Risk

Vaults compress many security assumptions into a small interface:

- shares and assets must convert consistently;
- `totalAssets` must reflect reality according to documented policy;
- fees must not silently break conservation;
- strategies can report gains, losses, debt, and liquidity changes;
- withdrawals may become queues or state machines;
- oracle or pool pricing can influence share value;
- admin roles can change strategy, oracle, fee, limits, pause state, and
  emergency behavior.

Those assumptions are exactly what formal reviewers will ask about. Arkheionx
helps builders find missing readiness evidence before audit intake.

## Supported Signals

ERC4626/share accounting:

- `ERC4626`
- `asset()`
- `totalAssets()`
- `convertToShares()`
- `convertToAssets()`
- `previewDeposit()`
- `previewMint()`
- `previewWithdraw()`
- `previewRedeem()`
- `maxDeposit()`
- `maxMint()`
- `maxWithdraw()`
- `maxRedeem()`
- `deposit()`
- `mint()`
- `withdraw()`
- `redeem()`
- `shares`
- `assets`
- `pricePerShare`
- `exchangeRate`
- `sharePrice`

Vault accounting risk:

- rounding direction;
- donation/inflation sensitivity;
- fee-on-transfer and rebasing token assumptions;
- decimals mismatch;
- precision and `mulDiv`;
- performance, management, withdrawal, and deposit fees;
- treasury and fee recipient accounting.

Strategy lifecycle:

- strategy allocation;
- strategy withdrawal;
- harvest/report;
- debt, credit, gain, loss, profit;
- migration;
- emergency exit.

Oracle and pricing:

- oracle/price feed use;
- Chainlink-style round data;
- reserve or spot pricing;
- TWAP;
- stale price and heartbeat terms;
- LP token and pool pricing terms.

Withdrawal lifecycle:

- withdrawal queue;
- request/claim/cancel withdrawal;
- cooldown and epoch;
- pending withdrawals;
- available liquidity and liquidity buffers;
- instant or delayed withdrawals.

Admin and operations:

- strategy/oracle/fee/treasury setters;
- deposit/withdraw limits;
- max loss and slippage setters;
- pause/unpause;
- emergency withdraw;
- sweep/rescue;
- upgrade and initialization terms.

## Readiness Gaps

The vault rule pack can report:

- Vault accounting without invariant tests.
- ERC4626-like interface without preview function tests.
- Shares/assets conversion without rounding tests.
- `totalAssets` external dependency without manipulation-resistance tests.
- Strategy accounting without gain/loss tests.
- Withdrawal queue/cooldown without lifecycle tests.
- Oracle-dependent vault without stale-price or bounds tests.
- Fee logic without fee accounting tests.
- Admin setters without role-boundary tests.
- Pause/emergency controls without operational tests.
- Upgradeable vault without initializer/upgrade tests.

These are readiness gaps, not confirmed vulnerabilities.

## Suggested Invariants

Useful vault invariants:

- `totalAssets` consistency;
- deposit/withdraw roundtrip does not create value;
- `convertToShares` and `convertToAssets` consistency;
- share price donation resistance;
- fee accounting does not create value;
- strategy loss does not break accounting;
- withdrawal lifecycle conserves shares;
- pause blocks risky flows;
- admin cannot bypass accounting without explicit documented trust.

Generate a safe skeleton:

```sh
python3 scripts/pre_audit_scan.py \
  --root . \
  --protocol-type vault \
  --generate-invariant-skeletons
```

## How To Improve A Vault Score

High-leverage improvements:

- add Foundry invariants for totalAssets and share conservation;
- test preview/action equivalence for ERC4626-like functions;
- test rounding direction and decimals mismatch;
- test donation and low-supply states;
- test fee accounting and fee recipient balances;
- use mock strategies for gain, loss, debt, harvest, and migration;
- test withdrawal request, cooldown, claim, and cancellation;
- test stale and bounded oracle behavior with local mocks;
- document roles, trusted assumptions, and emergency behavior.

## False Positive Limits

The scanner is heuristic. It reads local files and matches terms. It can
over-report when:

- code uses vault-like names for non-vault concepts;
- docs mention risks that the protocol does not implement;
- tests use different vocabulary from the scanner;
- a generated skeleton exists but has not been filled in.

Open a `False Positive Report` issue with the report section, code reference,
and suggested improvement.

## What It Does Not Prove

The vault rule pack does not prove:

- protocol safety;
- absence of bugs;
- exploitability;
- audit readiness in a formal sense;
- mainnet launch readiness.

It is a practical pre-audit preparation layer. Formal audit is still
recommended before handling real user funds.

## Related Security Memory

- Finding IDs: `ARK-VLT-001` through `ARK-VLT-009`
- Historical patterns: vault accounting drift, share inflation or donation
  sensitivity, pool-price accounting assumptions.
- Suggested searches:

```sh
python3 scripts/search_knowledge.py "vault accounting invariant"
python3 scripts/search_knowledge.py "vault donation attack"
python3 scripts/search_knowledge.py "share accounting invariant"
```

Search results connect this rule pack to suggested defensive tests and related
historical pattern categories.

## Test Plan Mapping

Vault findings map to share accounting, totalAssets, conversion rounding,
strategy lifecycle, fee, and withdrawal lifecycle properties in
`metadata/finding_test_plan_map.json`.

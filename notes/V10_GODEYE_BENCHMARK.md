# V10 GodEye Benchmark — working log (private)

Canonical benchmark table and failure-condition checks live in
[`docs/V10_GODEYE_BENCHMARK.md`](../docs/V10_GODEYE_BENCHMARK.md). This note is the
working log: the fixture-to-case mapping and the exact gate outputs observed.

## Fixture -> case mapping

- `loan_repay_rounding_fixture` -> #567 per-tranche repayment reconciliation
  (+ collateral release on a rounding-affected debt counter).
- `borrow_swapdata_consent_fixture` -> route-buffer: borrower-controlled swap
  calldata reaches a value path; terms hash does not bind it. Carries a `scope.yaml`
  (chain: arbitrum) to exercise scope + fork-chain inference.
- `vault_share_inflation_fixture` -> ERC4626-like first-depositor / donation inflation.
- `deposit_double_use_fixture` -> deposit consumed via external transfer before the
  active flag is cleared (reentrancy / double-use window).
- `trusted_role_fixture` -> value move gated by `onlyOwner` (must be killed).
- `adapter_actual_received_vs_credited_fixture` -> a credit adapter pulls a
  fee-on-transfer token via transferFrom then credits the NOMINAL amount instead of
  the measured balance delta (`credit_no_balance_delta` shape flag).
- `oracle_decimal_normalization_fixture` -> a borrow path reads an oracle price via an
  internal view (`maxBorrow`) and applies a hardcoded `1e18` scale while ignoring the
  feed/token `decimals()` (`oracle_value_math` + `oracle_hardcoded_scale` flags).
- `cross_chain_supply_conservation_fixture` -> a destination bridge mints on an
  incoming message id with no `processed`/consumed guard (`xchain_overmint` flag),
  so the message can be replayed to mint repeatedly.

## Observed gate outputs (war-run, fallback mode)

- loan repay: DEBT_REPAYMENT_RECONCILIATION = VALID_BUT_LOW (default / 6-dec),
  KILL_DUST (`--asset-decimals 18`); COLLATERAL_STATUS_RELEASE = SUBMIT_MEDIUM_CANDIDATE.
- borrow consent: LENDER_CONSENT_VALUE_AFFECTING_CALLDATA = NEEDS_FORK_PROOF;
  fork plan chain = arbitrum, env var name = ARBITRUM_RPC_URL.
- vault: VAULT_SHARE_ASSET_RECONCILIATION = SUBMIT_MEDIUM_CANDIDATE.
- deposit: DEPOSIT_CONSUMPTION = SUBMIT_HIGH_CANDIDATE.
- trusted: ACCESS_CONTROLLED_VALUE_MOVEMENT = KILL_TRUSTED_ROLE.
- adapter: SWAP_ACTUAL_RECEIVED_VS_CREDITED = SUBMIT_MEDIUM_CANDIDATE (local; exactly
  one candidate — not misclassified as a DEPOSIT_CONSUMPTION reentrancy high).
- oracle: ORACLE_DECIMAL_NORMALIZATION = SUBMIT_HIGH_CANDIDATE (local; unprivileged
  over-borrow from a mis-scaled price).
- cross-chain: CROSS_CHAIN_SUPPLY_CONSERVATION = SUBMIT_HIGH_CANDIDATE (local; the
  bridged token is correctly NOT detected as a vault).

## Benchmark gate (informal)

The slice is considered acceptable for private use when: (a) all nine cases replay
as above (9/9 PASS), (b) no failure condition in the docs table is triggered, and (c)
the full `unittest` suite is green with the V10 tests included (129 V10 tests at the
time of writing). All three held.

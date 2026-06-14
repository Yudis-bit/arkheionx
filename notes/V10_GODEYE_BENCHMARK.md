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

## Observed gate outputs (war-run, fallback mode)

- loan repay: DEBT_REPAYMENT_RECONCILIATION = VALID_BUT_LOW (default / 6-dec),
  KILL_DUST (`--asset-decimals 18`); COLLATERAL_STATUS_RELEASE = SUBMIT_MEDIUM_CANDIDATE.
- borrow consent: LENDER_CONSENT_VALUE_AFFECTING_CALLDATA = NEEDS_FORK_PROOF;
  fork plan chain = arbitrum, env var name = ARBITRUM_RPC_URL.
- vault: VAULT_SHARE_ASSET_RECONCILIATION = SUBMIT_MEDIUM_CANDIDATE.
- deposit: DEPOSIT_CONSUMPTION = SUBMIT_HIGH_CANDIDATE.
- trusted: ACCESS_CONTROLLED_VALUE_MOVEMENT = KILL_TRUSTED_ROLE.

## Benchmark gate (informal)

The slice is considered acceptable for private use when: (a) the two headline cases
replay as above, (b) no failure condition in the docs table is triggered, and (c)
the full `unittest` suite is green with the 104 V10 tests included. All three held at
the time of writing.

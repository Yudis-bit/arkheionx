# V10 GodEye War Engine — Benchmark (private, internal)

Internal benchmark for the V10 vertical slice. Each case runs `arkheionx war-run`
on a generic synthetic fixture under `tests/fixtures/godeye/` (no protocol/token
names are hardcoded). "PASS" means the required behavior is produced and tested;
"PARTIAL" means the template/classifier exist and are exercised by a unit test, but
there is no dedicated end-to-end fixture yet.

## A/B. Cases and required results

| Case | Fixture | Invariant generated | Candidate | Severity (not overclaimed) | PoC skeleton | Fork req | Result |
| --- | --- | --- | --- | --- | --- | --- | --- |
| #567 repayment reconciliation | loan_repay_rounding_fixture | DEBT_REPAYMENT_RECONCILIATION (suspicious) | yes | VALID_BUT_LOW (6-dec) / KILL_DUST (18-dec) | yes | no (local) | PASS |
| Route-buffer consent/refund | borrow_swapdata_consent_fixture | LENDER_CONSENT_VALUE_AFFECTING_CALLDATA (suspicious) | yes | NEEDS_FORK_PROOF | yes (honest vs attacker route) | yes (chain from scope) | PASS |
| ERC4626 share inflation | vault_share_inflation_fixture | VAULT_SHARE_ASSET_RECONCILIATION (suspicious) | yes | SUBMIT_MEDIUM_CANDIDATE | yes | no | PASS |
| Deposit double-use | deposit_double_use_fixture | DEPOSIT_CONSUMPTION (suspicious) | yes | SUBMIT_HIGH_CANDIDATE | yes | no | PASS |
| Collateral release before settlement | loan_repay_rounding_fixture | COLLATERAL_STATUS_RELEASE (suspicious) | yes | SUBMIT_MEDIUM_CANDIDATE | yes | no | PASS |
| Trusted-role value move | trusted_role_fixture | (access-controlled) | yes | KILL_TRUSTED_ROLE | no (killed) | no | PASS |
| Adapter actual-received-vs-credited | (no dedicated fixture) | SWAP_ACTUAL_RECEIVED_VS_CREDITED | via synthetic candidate | NEEDS_FORK_PROOF (with fork flag) | n/a | yes | PARTIAL |
| Oracle decimal mismatch | (no dedicated fixture) | ORACLE_DECIMAL_NORMALIZATION | template + suspicion logic | SUBMIT_MEDIUM_CANDIDATE | n/a | no | PARTIAL |
| Cross-chain mint/burn mismatch | (no dedicated fixture) | CROSS_CHAIN_SUPPLY_CONSERVATION | template + suspicion logic | NEEDS_FORK_PROOF (with fork flag) | n/a | yes | PARTIAL |

The two headline real-inspired cases (#567 reconciliation and route-buffer consent)
replay exactly as required: invariant found, candidate produced, severity capped
(not High), PoC skeleton generated, and fork required only where real external
state matters.

## C. Failure conditions (must NOT happen) — checked

| Failure condition | Guard | Status |
| --- | --- | --- |
| Classifies dust as High | severity gate caps DEBT_RECON to VALID_BUT_LOW / KILL_DUST | held |
| Classifies trusted role as unprivileged | reachability step -> KILL_TRUSTED_ROLE | held |
| Generates a report before PoC/invariant | no report path exists; `report_generated: false` | held |
| Misses attacker/victim/asset | every candidate carries attacker, victim, asset, invariant, PoC path | held |
| Cannot explain the broken invariant | invariants carry assertion + reasons; candidates carry root cause | held |
| Cannot generate a useful test skeleton | Foundry skeleton per top candidate with invariant assertions | held |
| Leaks RPC/secrets | redaction + secret scan; env var names only; tests cover it | held |
| Duplicates a prior root cause | semantic root-cause hash + dedup classifier | held |

## How to reproduce

```bash
arkheionx war-run tests/fixtures/godeye/borrow_swapdata_consent_fixture \
  --scope tests/fixtures/godeye/borrow_swapdata_consent_fixture/scope.yaml \
  --out /tmp/war-run-demo
arkheionx war-run tests/fixtures/godeye/loan_repay_rounding_fixture --asset-decimals 18
```

The unit tests under `tests/test_v10_*.py` assert each benchmark behavior
(104 tests). Full suite: `python3 -m unittest discover -s tests -p "test_*.py"`.

## Honest gaps

- Adapter / oracle / cross-chain families have templates, suspicion logic, and unit
  coverage, but no dedicated end-to-end fixture in this slice (PARTIAL).
- Semantic extraction is fallback (regex + brace/paren matching), medium confidence;
  full solc AST ingestion is deferred (interface only).
- Severity sharpening for the reconciliation family uses an `--asset-decimals`
  context hint; without it the default is the conservative VALID_BUT_LOW.

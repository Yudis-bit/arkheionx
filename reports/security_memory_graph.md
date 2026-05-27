# Arkheionx Security Memory Graph

This repository-native graph connects readiness findings to historical
pattern classes, root causes, failed assumptions, broken invariants,
suggested defensive tests, docs, and delivery artifacts.

This is local/static security memory. It is not a formal audit, not a
vulnerability confirmation, and not proof that a scanned repository has
the same issue as any historical PoC.

- Schema version: `1.0.0`
- Nodes: `356`
- Edges: `664`

## Node Counts

| Type | Count |
|---|---:|
| `broken_invariant` | 63 |
| `delivery_artifact` | 6 |
| `doc` | 16 |
| `exploit_primitive` | 18 |
| `failed_assumption` | 46 |
| `finding` | 22 |
| `historical_pattern` | 21 |
| `poc` | 18 |
| `root_cause` | 64 |
| `rule_pack` | 11 |
| `suggested_test` | 71 |

## Finding To Pattern Map

| Finding | Rule Pack | Historical Patterns | Suggested Tests |
|---|---|---|---|
| `ARK-ACC-001` Privileged setters without role-boundary tests | `access_control` | Privileged operation boundary failure, Initializer or privileged setup boundary failure | Admin Change Event And Bounds Test, Role Boundary Negative Tests, Unauthorized Setter Reverts |
| `ARK-AMM-001` AMM invariant assumptions not covered by tests | `amm` | AMM invariant steering or liquidity manipulation, Spot or reserve price manipulation risk class | Fee Rounding Bound, Liquidity Proportionality, Reserve Accounting Test, Swap Invariant Conservation |
| `ARK-AMM-002` LP share accounting without mint/burn boundary tests | `amm` | AMM invariant steering or liquidity manipulation, Vault share inflation or donation sensitivity | Dust Rounding Test, First Liquidity Provider Test, Proportional Minting Test, Proportional Withdrawal Test |
| `ARK-AMM-003` Spot-price or reserve-price dependency without manipulation-resistance tests | `amm` | Pool price or external balance used as accounting truth, Spot or reserve price manipulation risk class | Price Movement Bounds, Reserve Manipulation Sanity Test, Twap Vs Spot Behavior |
| `ARK-AMM-004` Fee-on-transfer or non-standard token assumptions not documented | `amm` | Pool price or external balance used as accounting truth, Precision, rounding, or normalization failure | Balance Before After Accounting, Fee On Transfer Token Simulation, Unsupported Token Documentation |
| `ARK-AMM-005` Slippage/min-output constraints missing or unclear | `amm` | Failed assumption not represented in tests, Spot or reserve price manipulation risk class | Deadline Or Stale Quote Test, Min Out Enforcement, Slippage Boundary Test |
| `ARK-DOC-001` Documentation assumptions are incomplete | `documentation` | External review scope ambiguity, Undocumented trust or operational assumption | Assumption Table Review, Known Limitations Section, Scope Checklist |
| `ARK-LEND-001` Collateral/debt solvency invariant not covered by tests | `lending` | Collateral and debt invariant failure, Oracle stale price or freshness assumption failure | Borrow Limit Boundary Test, Collateral Debt Invariant, Unsafe Withdrawal Rejection |
| `ARK-LEND-002` Liquidation boundary tests missing | `lending` | Collateral and debt invariant failure, Oracle stale price or freshness assumption failure | Bonus Bound Test, Just Above Threshold Test, Just Below Threshold Test, Partial Liquidation Math |
| `ARK-LEND-003` Interest/index accounting not covered by rounding and time-step tests | `lending` | Accounting index or accumulator drift, Precision, rounding, or normalization failure | Borrow Repay Around Accrual, Interest Index Monotonicity, Repeated Accrual Drift Bound, Small Balance Rounding Test |
| `ARK-LEND-004` Oracle-dependent borrowing/liquidation without stale-price tests | `lending` | Collateral and debt invariant failure, Oracle stale price or freshness assumption failure | Borrow Blocked On Invalid Price, Decimals Normalization Test, Price Shock Boundary Test, Stale Oracle Rejection |
| `ARK-LEND-005` Reserve/cash accounting assumptions not covered | `lending` | Accounting index or accumulator drift, Collateral and debt invariant failure | Available Liquidity Bound, Repay Cash Debt Consistency, Reserve Withdrawal Constraints, Utilization Bound Test |
| `ARK-LEND-006` Liquidation/access-control interaction not documented | `lending` | Collateral and debt invariant failure, Privileged operation boundary failure | Guardian Permission Test, Liquidator Role Boundary Test, Paused Market Liquidation Test |
| `ARK-ORC-001` Oracle-dependent logic without stale-price tests | `oracle` | Oracle stale price or freshness assumption failure, Pool price or external balance used as accounting truth, Spot or reserve price manipulation risk class | Decimal Normalization Test, Heartbeat Bound Test, Price Bounds Test, Stale Round Rejection |
| `ARK-ORC-003` Spot or reserve-based pricing without manipulation-resistance tests | `oracle` | AMM invariant steering or liquidity manipulation, Spot or reserve price manipulation risk class | Price Bounds Test, Reserve Manipulation Sanity Test, Twap Vs Spot Behavior |
| `ARK-REENT-001` Value flow with external calls needs reentrancy review | `reentrancy_value_flow` | Callback-capable token or receiver assumption failure, External call before state update | Double Claim Prevention, Reentrant Receiver Mock, State Update Before External Call Test |
| `ARK-RWD-001` Reward accounting without conservation tests | `reward_accounting` | Accounting index or accumulator drift, Reward overclaim or emission accounting mismatch | Claim Twice Reverts Or Noops, Reward Conservation Multi User, Rewardpertoken Monotonicity |
| `ARK-TST-002` No invariant tests detected for DeFi protocol shape | `testing` | Failed assumption not represented in tests, Critical assumption not encoded as invariant | Foundry Invariant Skeleton, Roundtrip Or Conservation Invariant, Stateful Fuzz Sequence |
| `ARK-UPG-001` Upgradeable contract without initializer or upgrade tests | `access_control` | Initializer or privileged setup boundary failure, Upgrade authorization or storage assumption gap | Initializer Cannot Run Twice, Storage Layout Documentation Check, Upgrade Authorization Test |
| `ARK-VLT-001` Vault accounting without invariant coverage | `vault` | Pool price or external balance used as accounting truth, Vault share inflation or donation sensitivity, Vault accounting drift or share/asset mismatch | Deposit Withdraw Roundtrip, Donation Resistance, Share Conversion Rounding, Total Assets Consistency |
| `ARK-VLT-003` Shares/assets conversion without rounding tests | `vault` | Precision, rounding, or normalization failure, Vault share inflation or donation sensitivity | Converttoshares Converttoassets Consistency, Donation After First Deposit, Low Supply Rounding Test |
| `ARK-XCH-900` Cross-chain validation readiness mapping | `cross_chain` | Cross-chain message validation failure, Replay or trusted-source assumption failure | Endpoint Configuration Documentation, Replay Rejection Test, Trusted Source Validation |

## Historical PoC Nodes

| PoC | Category | Path |
|---|---|---|
| `poc-2017-07-parity-multisig` Parity Multisig — initWallet hijack | `access-control-failure` | `EVM/test/2017-07/Exploit_2017-07.t.sol` |
| `poc-2017-11-parity-suicide` Parity Wallet Library — suicide | `access-control-failure` | `EVM/test/2017-11/Exploit_2017-11.t.sol` |
| `poc-2018-04-bec-token` BeautyChain (BEC) — batchTransfer overflow | `arithmetic-precision-rounding` | `EVM/test/2018-04/Exploit_2018-04.t.sol` |
| `poc-2018-10-spankchain` SpankChain — payment channel reentrancy | `reentrancy` | `EVM/test/2018-10/Exploit_2018-10.t.sol` |
| `poc-2020-04-uniswap-imbtc` Uniswap V1 — imBTC reentrancy | `reentrancy` | `EVM/test/2020-04/Exploit_2020-04.t.sol` |
| `poc-2020-06-balancer-deflationary` Bancor — public safeTransferFrom on newly deployed contract | `access-control-failure` | `EVM/test/2020-06/Exploit_2020-06.t.sol` |
| `poc-2020-08-opyn` Opyn — duplicate ETH option exercise | `invariant-bypass` | `EVM/test/2020-08/Exploit_2020-08.t.sol` |
| `poc-2020-09-bzx-ifusdc` bZx — iETH self-transfer double-write | `accounting-mismatch` | `EVM/test/2020-09/Exploit_2020-09.t.sol` |
| `poc-2020-10-harvest` Harvest Finance — fUSDT/fUSDC oracle manipulation | `flash-loan-price-manipulation` | `EVM/test/2020-10/Exploit_2020-10.t.sol` |
| `poc-2020-11-cheese-bank` Pickle Finance — swapExactJarForJar arbitrary-call cDAI strategy asset loss | `unsafe-external-call` | `EVM/test/2020-11/Exploit_2020-11.t.sol` |
| `poc-2020-12-warp-finance` Cover Protocol — Blacksmith claimRewards infinite mint | `accounting-mismatch` | `EVM/test/2020-12/Exploit_2020-12.t.sol` |
| `poc-2021-01-saddle` SushiSwap SushiMaker — DIGG/WBTC missing-bridge convert exploit | `amm-invariant-manipulation` | `EVM/test/2021-01/Exploit_2021-01.t.sol` |
| `poc-2021-02-yearn-v1-dai` Yearn v1 DAI vault — Curve 3pool oracle manipulation | `flash-loan-price-manipulation` | `EVM/test/2021-02/Exploit_2021-02.t.sol` |
| `poc-2021-03-dodo-crowdpool` DODO — CrowdPooling init reentrancy | `initialization-bug` | `EVM/test/2021-03/Exploit_2021-03.t.sol` |
| `poc-2021-10-indexed-finance` Indexed Finance — DEFI5/CC10 reweight manipulation | `amm-invariant-manipulation` | `EVM/test/2021-10/Exploit_2021-10.t.sol` |
| `poc-2022-02-dexible` BUILD Finance — governance takeover via low-quorum proposal | `governance-attack` | `EVM/test/2022-02/Exploit_2022-02.t.sol` |
| `poc-2025-11-moonwell` Moonwell — Chainlink oracle staleness on Base | `oracle-manipulation` | `EVM/test/2025-11/Exploit_2025-11.t.sol` |
| `poc-2025-12-yeth` yETH — pool invariant manipulation | `amm-invariant-manipulation` | `EVM/test/2025-12/Exploit_2025-12.t.sol` |

## How To Search

```sh
python3 scripts/search_knowledge.py "oracle stale price"
python3 scripts/search_knowledge.py "vault accounting invariant"
python3 scripts/search_knowledge.py "missing invariant" --json
```

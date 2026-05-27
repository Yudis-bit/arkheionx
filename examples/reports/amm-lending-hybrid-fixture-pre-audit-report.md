# Arkheionx Pre-Audit Readiness Report

## Scope

- Repository root: `examples/amm-lending-hybrid-fixture`
- Generated at: `2026-05-27T03:46:53+00:00`
- Protocol type: `amm`
- Protocol confidence: `medium`
- Files scanned: `4`
- Scanner version: `1.4.0`

| File class       | Count |
| ---------------- | ----- |
| Solidity sources | 1     |
| Solidity tests   | 1     |
| Docs             | 1     |
| Configs          | 1     |
| Workflows        | 0     |

## Scan Source Summary

- Files considered: `4`
- Files scanned: `4`
- Files ignored: `0`
- Generated Arkheionx artifacts ignored: `0`

## Disclaimer

This is an automated pre-audit readiness report. It is not a formal audit, does not prove the absence or presence of vulnerabilities, does not authorize live-target testing, and should only be used on repositories you own or are authorized to review. A formal audit is recommended before handling real user funds.

## Analysis Quality

| Source                   | Status   |
| ------------------------ | -------- |
| Keyword scan             | enabled  |
| Semantic-lite extraction | enabled  |
| Semantic contracts       | 2        |
| Semantic test files      | 1        |
| Slither                  | disabled |
| Slither detectors        | 0        |
| Test coverage mapping    | enabled  |
| Negative evidence        | 0        |

## Executive Summary

- Readiness score: **38/100**
- Score band: **Not audit-ready**
- Active readiness gaps: `13`
- Suppressed readiness gaps: `0`
- Top readiness gaps:
  - **ARK-AMM-001 (High readiness gap):** AMM invariant assumptions not covered by tests - Add local tests or invariants showing swaps and liquidity operations preserve documented AMM accounting within fee and rounding bounds.
  - **ARK-AMM-003 (High readiness gap):** Spot-price or reserve-price dependency without manipulation-resistance tests - Add local reserve-movement tests and document whether spot, TWAP, or external oracle assumptions are intended.
  - **ARK-AMM-004 (Medium readiness gap):** Fee-on-transfer or non-standard token assumptions not documented - Document supported token assumptions or add balanceBefore/balanceAfter accounting tests for fee-on-transfer and non-standard token behavior.
  - **ARK-AMM-005 (Medium readiness gap):** Slippage/min-output constraints missing or unclear - Add user-provided min-output and stale-quote tests, or document why swaps are not user-facing and how price movement is bounded.
  - **ARK-LEND-001 (Medium readiness gap):** Collateral/debt solvency invariant not covered by tests - Add collateral/debt invariants and boundary tests for borrow, repay, deposit, withdrawal, and liquidation readiness.
- Top recommended actions:
  - Add Foundry invariant tests for accounting, roles, and value-flow boundaries.
  - Document and test oracle freshness, decimals normalization, bounds, and fallback behavior.
  - Write a formal audit scope with contracts, roles, assumptions, known limitations, and test commands.
  - Run a formal smart contract audit before mainnet launch or before handling real user funds.

## Detected Protocol Shape

- Detected protocol type: `amm`
- Confidence: `medium`
- Protocol score signals: `{"amm": 102, "lending": 94, "oracle": 0, "staking": 0, "vault": 0}`
- Arkheionx memory metadata loaded: `18` entries

## Readiness Score Breakdown

| Category                    | Score | Max | Notes                                                                                                                                                          |
| --------------------------- | ----- | --- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Repository Structure        | 12    | 15  | Solidity sources detected.; Recognized build or analysis config detected.; Clear src/test/docs structure detected.                                             |
| Test Presence               | 20    | 20  | Solidity test files detected.; Assert usage detected.; Foundry or Hardhat test environment detected.; Protocol-specific terms appear in the testable codebase. |
| Invariant Fuzz Readiness    | 0     | 20  | No positive signal detected.                                                                                                                                   |
| Defi Risk Coverage          | 0     | 20  | No positive signal detected.                                                                                                                                   |
| Documentation Readiness     | 3     | 10  | README detected.                                                                                                                                               |
| Operational Admin Readiness | 3     | 15  | Upgradeability is absent or has visible documentation/test terms.                                                                                              |

## Top Readiness Gaps

| ID           | Priority             | Category              | Title                                                                        |
| ------------ | -------------------- | --------------------- | ---------------------------------------------------------------------------- |
| ARK-AMM-001  | High readiness gap   | amm-invariant         | AMM invariant assumptions not covered by tests                               |
| ARK-AMM-003  | High readiness gap   | amm-pricing           | Spot-price or reserve-price dependency without manipulation-resistance tests |
| ARK-AMM-004  | Medium readiness gap | amm-token-assumptions | Fee-on-transfer or non-standard token assumptions not documented             |
| ARK-AMM-005  | Medium readiness gap | amm-slippage          | Slippage/min-output constraints missing or unclear                           |
| ARK-LEND-001 | Medium readiness gap | lending-solvency      | Collateral/debt solvency invariant not covered by tests                      |

## Rule Pack Coverage

| Rule Pack                                 | Detected | Findings | Docs                                    |
| ----------------------------------------- | -------- | -------- | --------------------------------------- |
| Vault Rule Pack                           | yes      | 0        | docs/VAULT_RULE_PACK.md                 |
| Oracle Rule Pack                          | yes      | 4        | docs/ORACLE_RULE_PACK.md                |
| Access Control / Upgradeability Rule Pack | no       | 0        | docs/ACCESS_CONTROL_RULE_PACK.md        |
| Reentrancy / Value Flow Rule Pack         | no       | 0        | docs/REENTRANCY_VALUE_FLOW_RULE_PACK.md |
| Staking / Reward Accounting Rule Pack     | yes      | 0        | docs/REWARD_ACCOUNTING_RULE_PACK.md     |
| AMM Rule Pack                             | yes      | 4        | docs/AMM_RULE_PACK.md                   |
| Lending Rule Pack                         | yes      | 4        | docs/LENDING_RULE_PACK.md               |

### Vault Rule Pack

- Signals detected: `1`
- Signal terms: `debt`
- Findings: `0`
- Docs: `docs/VAULT_RULE_PACK.md`
- Suggested tests:
  - totalAssets consistency
  - deposit/withdraw roundtrip
  - share conversion rounding
  - strategy gain/loss lifecycle

### Oracle Rule Pack

- Signals detected: `4`
- Signal terms: `getReserves, pool, reserve0, reserve1`
- Findings: `4`
- Docs: `docs/ORACLE_RULE_PACK.md`
- Suggested tests:
  - stale price rejection
  - decimals normalization
  - price bounds
  - TWAP vs spot behavior

### Staking / Reward Accounting Rule Pack

- Signals detected: `2`
- Signal terms: `collateral, debt`
- Findings: `0`
- Docs: `docs/REWARD_ACCOUNTING_RULE_PACK.md`
- Suggested tests:
  - reward conservation
  - no overclaim
  - index monotonicity
  - stake/unstake/claim lifecycle

### AMM Rule Pack

- Signals detected: `9`
- Signal terms: `amountIn, amountOut, getReserves, kLast, pool, quote, reserve0, reserve1, swap`
- Findings: `4`
- Docs: `docs/AMM_RULE_PACK.md`
- Suggested tests:
  - swap invariant conservation
  - LP share proportionality
  - TWAP or reserve bounds
  - minOut enforcement

### Lending Rule Pack

- Signals detected: `9`
- Signal terms: `borrow, cash, collateral, debt, healthFactor, liquidate, liquidationThreshold, repay, totalBorrows`
- Findings: `4`
- Docs: `docs/LENDING_RULE_PACK.md`
- Suggested tests:
  - collateral/debt invariant
  - liquidation boundary tests
  - interest index monotonicity
  - oracle shock tests

## Risk Signal Summary

### Vault Strategy

- Detected signals: `debt`
- Files with signals: `2`
- Example files: `src/ToyHybridMarket.sol, test/ToyHybridMarket.t.sol`

### Vault Pricing

- Detected signals: `getReserves`
- Files with signals: `1`
- Example files: `src/ToyHybridMarket.sol`

### Oracle

- Detected signals: `getReserves, pool, reserve0, reserve1`
- Files with signals: `2`
- Example files: `src/ToyHybridMarket.sol, test/ToyHybridMarket.t.sol`

### Accounting Complexity

- Detected signals: `collateral, debt`
- Files with signals: `2`
- Example files: `src/ToyHybridMarket.sol, test/ToyHybridMarket.t.sol`

### Amm

- Detected signals: `amountIn, amountOut, getReserves, kLast, pool, quote, reserve0, reserve1, swap`
- Files with signals: `2`
- Example files: `src/ToyHybridMarket.sol, test/ToyHybridMarket.t.sol`

### Lending

- Detected signals: `borrow, cash, collateral, debt, healthFactor, liquidate, liquidationThreshold, repay, totalBorrows`
- Files with signals: `2`
- Example files: `src/ToyHybridMarket.sol, test/ToyHybridMarket.t.sol`

### Testing And Documentation

- Test Directory: `True`
- Foundry Tests: `True`
- Hardhat Tests: `False`
- Test File Count: `1`
- Invariant Tests: `False`
- Fuzz Tests: `False`
- Handler Contracts: `False`
- Assert Usage: `True`
- Assert Count: `2`
- Forge Std: `True`
- Echidna: `False`
- Slither: `False`
- Ci Workflow: `False`
- Edge Case Tests: `False`
- Negative Evidence Count: `0`
- Negative Evidence Terms: `[]`
- Test files: `test/ToyHybridMarket.t.sol`

## Historical Exploit-Pattern Similarity

### AMM invariant manipulation review recommended

- Confidence: `high`
- Detected signals: `amountIn, amountOut, getReserves, kLast, pool, quote, reserve0, reserve1, swap`
- Why it matters: AMM integrations need invariant and reserve assumptions tested under swaps, liquidity changes, fees, and price movements.
- Failed assumption class: Pool reserves and quote functions remain representative for protocol decisions.
- Broken invariant class: Swaps and liquidity changes cannot create value outside documented fee mechanics.
- Recommended defensive checks:
  - Add invariant conservation tests.
  - Test add/remove liquidity proportionality.
  - Avoid relying on same-block spot reserves without documented controls.
- Suggested test/invariant: Invariant: swaps and liquidity operations preserve the AMM invariant within fee and rounding bounds.
- Search tags: `amm-invariant, liquidity, spot-price, reserve-manipulation`

### Liquidation and collateral accounting review recommended

- Confidence: `high`
- Detected signals: `borrow, cash, collateral, debt, getReserves, healthFactor, liquidate, liquidationThreshold, pool, repay, reserve0, reserve1, totalBorrows`
- Why it matters: Lending systems depend on collateral, debt, oracle, and liquidation assumptions staying consistent through edge cases.
- Failed assumption class: Collateral value and debt state stay aligned with liquidation and solvency rules.
- Broken invariant class: Borrowers cannot become undercollateralized without expected liquidation or protocol accounting response.
- Recommended defensive checks:
  - Test collateralization and liquidation boundaries.
  - Test oracle movement around borrow and liquidation flows.
  - Check interest index monotonicity and debt accounting.
- Suggested test/invariant: Invariant: positions below required collateralization are liquidatable and solvent positions are not incorrectly liquidated.
- Search tags: `lending, liquidation, collateral, oracle-risk`

## All Readiness Gaps

### ARK-TST-002 - No invariant tests detected for DeFi protocol shape

- Priority: `Low readiness gap`
- Confidence: `low`
- Confidence reason: Keyword-only signal detected without Solidity function-level evidence; manual review is recommended before remediation.
- Detection sources: `keyword`
- Category: `testing-readiness`

Evidence:
- `src/ToyHybridMarket.sol:1`: Keyword signal matched this readiness finding.
- `test/ToyHybridMarket.t.sol:1`: Keyword signal matched this readiness finding.

False-positive notes:

Keyword-only signal without Solidity function-level evidence. Review manually before creating remediation tasks.

Detected signals:
- scanner signal

Affected files:
- `src/ToyHybridMarket.sol`
- `test/ToyHybridMarket.t.sol`

What was detected:

Protocol-like value flows were detected, but no invariant/property testing signal was found.

Related Knowledge:

- Historical patterns: pattern-missing-invariant-coverage, pattern-assumption-not-encoded-in-tests
- Suggested defensive tests: foundry-invariant-skeleton, stateful-fuzz-sequence, roundtrip-or-conservation-invariant
- Related PoCs: poc-2020-08-opyn, poc-2020-09-bzx-ifusdc, poc-2021-10-indexed-finance
- Docs: docs/READINESS_SCORE.md, templates/invariant_skeletons/ArkheionxReadinessInvariants.t.sol

Suggested tests:

- Add Foundry invariant tests for accounting, oracle, role, and value-flow assumptions.

Search tags: `invariant-testing, amm`

### ARK-ORC-002 - Oracle usage lacks visible staleness, TWAP, bounds, or sanity coverage

- Priority: `Low readiness gap`
- Confidence: `low`
- Confidence reason: Keyword-only signal detected without Solidity function-level evidence; manual review is recommended before remediation.
- Detection sources: `keyword, test-coverage`
- Category: `oracle-pricing`

Evidence:
- `test/documentation coverage`: No semantic-lite oracle test coverage terms were detected.
- `src/ToyHybridMarket.sol:1`: Keyword signal matched this readiness finding.
- `test/ToyHybridMarket.t.sol:1`: Keyword signal matched this readiness finding.

False-positive notes:

Keyword-only signal without Solidity function-level evidence. Review manually before creating remediation tasks.

Detected signals:
- scanner signal

Affected files:
- `src/ToyHybridMarket.sol`
- `test/ToyHybridMarket.t.sol`

What was detected:

Oracle and price-feed signals were detected without enough freshness or sanity-check language.

Suggested tests:

- Document and test oracle freshness, decimals normalization, price bounds, and fallback behavior.

Search tags: `oracle-risk, price-assumptions`

### ARK-ORC-001 - Oracle-dependent logic without stale-price tests

- Priority: `Low readiness gap`
- Confidence: `low`
- Confidence reason: Keyword-only signal detected without Solidity function-level evidence; manual review is recommended before remediation.
- Detection sources: `keyword, test-coverage`
- Category: `oracle-pricing`

Evidence:
- `test/documentation coverage`: No semantic-lite oracle test coverage terms were detected.
- `src/ToyHybridMarket.sol:1`: Keyword signal matched this readiness finding. Snippet: `getReserves, pool, reserve0, reserve1`
- `test/ToyHybridMarket.t.sol:1`: Keyword signal matched this readiness finding. Snippet: `getReserves, pool, reserve0, reserve1`

False-positive notes:

Keyword-only signal without Solidity function-level evidence. Review manually before creating remediation tasks.

Detected signals:
- `getReserves`
- `pool`
- `reserve0`
- `reserve1`

Affected files:
- `src/ToyHybridMarket.sol`
- `test/ToyHybridMarket.t.sol`

What was detected:

Oracle or price-feed signals were detected, but tests do not visibly cover stale rounds, heartbeat, or timestamp behavior.

Why it matters:

Oracle-dependent accounting and control flows can be wrong when price data is stale, incomplete, or outside documented assumptions.

Historical pattern similarity:

Maps to historical oracle and pricing failure classes where stale or manipulated price state broke protocol assumptions.

Recommended defensive checks:

- stale round rejection
- heartbeat checks
- updatedAt validation
- answeredInRound handling

Related Knowledge:

- Historical patterns: pattern-oracle-stale-price, pattern-spot-price-manipulation, pattern-pool-price-accounting
- Suggested defensive tests: stale-round-rejection, heartbeat-bound-test, decimal-normalization-test
- Related PoCs: poc-2025-11-moonwell, poc-2020-10-harvest, poc-2021-02-yearn-v1-dai
- Docs: docs/ORACLE_RULE_PACK.md, docs/RULE_PACKS.md, docs/SEARCH_GUIDE.md

Suggested tests:

- Use a local mock price feed to assert stale or incomplete oracle rounds are rejected or handled according to documented policy.

Search tags: `oracle-risk, oracle-rule-pack, pre-audit-readiness`

### ARK-ORC-003 - Spot or reserve-based pricing without manipulation-resistance tests

- Priority: `Low readiness gap`
- Confidence: `low`
- Confidence reason: Keyword-only signal detected without Solidity function-level evidence; manual review is recommended before remediation.
- Detection sources: `keyword, test-coverage`
- Category: `oracle-pricing`

Evidence:
- `test/documentation coverage`: No semantic-lite oracle test coverage terms were detected.
- `src/ToyHybridMarket.sol:1`: Keyword signal matched this readiness finding. Snippet: `getReserves, pool, reserve0, reserve1`
- `test/ToyHybridMarket.t.sol:1`: Keyword signal matched this readiness finding. Snippet: `getReserves, pool, reserve0, reserve1`

False-positive notes:

Keyword-only signal without Solidity function-level evidence. Review manually before creating remediation tasks.

Detected signals:
- `getReserves`
- `pool`
- `reserve0`
- `reserve1`

Affected files:
- `src/ToyHybridMarket.sol`
- `test/ToyHybridMarket.t.sol`

What was detected:

Spot, reserve, pool, or sqrtPriceX96 pricing signals were detected without visible manipulation-resistance tests.

Why it matters:

Same-block spot or reserve-based pricing can drift from fair value unless bounded by the protocol design.

Historical pattern similarity:

Maps to historical price-manipulation readiness classes.

Recommended defensive checks:

- TWAP vs spot behavior
- reserve movement bounds
- price sanity checks
- local pool mocks

Related Knowledge:

- Historical patterns: pattern-spot-price-manipulation, pattern-amm-invariant-steering
- Suggested defensive tests: twap-vs-spot-behavior, reserve-manipulation-sanity-test, price-bounds-test
- Related PoCs: poc-2020-10-harvest, poc-2021-01-saddle, poc-2025-12-yeth
- Docs: docs/ORACLE_RULE_PACK.md, docs/RULE_PACKS.md

Suggested tests:

- Use a local pool mock to move reserves or price and assert protocol actions respect documented bounds.

Search tags: `oracle-risk, spot-price, reserve-pricing, oracle-rule-pack`

### ARK-ORC-005 - Missing price bounds or fallback assumptions documentation

- Priority: `Low readiness gap`
- Confidence: `low`
- Confidence reason: Keyword-only signal detected without Solidity function-level evidence; manual review is recommended before remediation.
- Detection sources: `keyword, test-coverage`
- Category: `oracle-pricing`

Evidence:
- `test/documentation coverage`: No semantic-lite oracle test coverage terms were detected.
- `src/ToyHybridMarket.sol:1`: Keyword signal matched this readiness finding. Snippet: `getReserves, pool, reserve0, reserve1`
- `test/ToyHybridMarket.t.sol:1`: Keyword signal matched this readiness finding. Snippet: `getReserves, pool, reserve0, reserve1`

False-positive notes:

Keyword-only signal without Solidity function-level evidence. Review manually before creating remediation tasks.

Detected signals:
- `getReserves`
- `pool`
- `reserve0`
- `reserve1`

Affected files:
- `src/ToyHybridMarket.sol`
- `test/ToyHybridMarket.t.sol`

What was detected:

Oracle pricing signals were detected without clear documentation for bounds, fallback behavior, or stale price assumptions.

Why it matters:

Auditors and maintainers need explicit pricing assumptions to review whether the design handles oracle failure modes.

Historical pattern similarity:

Maps to failed assumption classes where oracle behavior was implied but not enforced or documented.

Recommended defensive checks:

- price bounds
- fallback policy
- stale-price policy
- sequencer downtime notes

Suggested tests:

- Add documentation plus local tests showing fallback and out-of-bounds price behavior.

Search tags: `oracle-risk, documentation-readiness, oracle-rule-pack`

### ARK-AMM-001 - AMM invariant assumptions not covered by tests

- Priority: `High readiness gap`
- Confidence: `high`
- Confidence reason: Semantic-lite Solidity evidence was detected and matching test coverage evidence was not found.
- Detection sources: `keyword, semantic-lite, test-coverage`
- Category: `amm-invariant`

Evidence:
- `src/ToyHybridMarket.sol:9` in `getReserves`: Solidity function shape matches this readiness finding. Snippet: `getReserves`
- `src/ToyHybridMarket.sol:13` in `quote`: Solidity function shape matches this readiness finding. Snippet: `quote`
- `src/ToyHybridMarket.sol:17` in `swap`: Solidity function shape matches this readiness finding. Snippet: `kLast = reserve0 * reserve1;`
- `test/documentation coverage`: No semantic-lite amm test coverage terms were detected.
- `src/ToyHybridMarket.sol:1`: Keyword signal matched this readiness finding. Snippet: `amountIn, amountOut, getReserves, kLast, pool, quote, reserve0, reserve1`

Detected signals:
- `amountIn`
- `amountOut`
- `getReserves`
- `kLast`
- `pool`
- `quote`
- `reserve0`
- `reserve1`
- `swap`

Affected files:
- `src/ToyHybridMarket.sol`
- `test/ToyHybridMarket.t.sol`

What was detected:

AMM reserve, swap, or liquidity signals were detected without visible invariant or reserve-accounting tests.

Why it matters:

AMM correctness depends on reserve accounting, swap bounds, and invariant preservation staying true under fees, rounding, and repeated operations.

Historical pattern similarity:

Maps to historical AMM invariant and pool-price accounting readiness classes. This is defensive test inspiration, not vulnerability confirmation.

Recommended defensive checks:

- swap invariant conservation
- reserve accounting
- add/remove liquidity consistency
- fee and rounding bounds

Related Knowledge:

- Historical patterns: pattern-amm-invariant-steering, pattern-spot-price-manipulation
- Suggested defensive tests: swap-invariant-conservation, reserve-accounting-test, liquidity-proportionality
- Related PoCs: poc-2021-01-saddle, poc-2021-10-indexed-finance, poc-2025-12-yeth
- Docs: docs/AMM_RULE_PACK.md, docs/RULE_PACKS.md, docs/EXPLOIT_TAXONOMY.md

Suggested tests:

- Assert swaps preserve the documented constant-product or stableswap invariant within expected fee and rounding bounds.

Search tags: `amm-invariant, amm-rule-pack, pre-audit-readiness`

### ARK-AMM-003 - Spot-price or reserve-price dependency without manipulation-resistance tests

- Priority: `High readiness gap`
- Confidence: `high`
- Confidence reason: Semantic-lite Solidity evidence was detected and matching test coverage evidence was not found.
- Detection sources: `keyword, semantic-lite, test-coverage`
- Category: `amm-pricing`

Evidence:
- `src/ToyHybridMarket.sol:9` in `getReserves`: Solidity function shape matches this readiness finding. Snippet: `getReserves`
- `src/ToyHybridMarket.sol:13` in `quote`: Solidity function shape matches this readiness finding. Snippet: `quote`
- `src/ToyHybridMarket.sol:17` in `swap`: Solidity function shape matches this readiness finding. Snippet: `kLast = reserve0 * reserve1;`
- `test/documentation coverage`: No semantic-lite oracle test coverage terms were detected.
- `src/ToyHybridMarket.sol:1`: Keyword signal matched this readiness finding. Snippet: `amountIn, amountOut, getReserves, kLast, pool, quote, reserve0, reserve1`

Detected signals:
- `amountIn`
- `amountOut`
- `getReserves`
- `kLast`
- `pool`
- `quote`
- `reserve0`
- `reserve1`
- `swap`

Affected files:
- `src/ToyHybridMarket.sol`
- `test/ToyHybridMarket.t.sol`

What was detected:

Reserve-ratio, quote, getAmountOut, or spot-price signals were detected without visible TWAP, delay, bounds, or manipulation-resistance tests.

Why it matters:

Same-block reserve prices and spot quotes can be poor readiness evidence unless manipulation boundaries are tested or explicitly documented.

Historical pattern similarity:

Maps to spot-price and pool-price accounting readiness classes.

Recommended defensive checks:

- TWAP or delay assumption
- reserve manipulation sanity test
- price movement bounds

Related Knowledge:

- Historical patterns: pattern-spot-price-manipulation, pattern-pool-price-accounting
- Suggested defensive tests: twap-vs-spot-behavior, reserve-manipulation-sanity-test, price-movement-bounds
- Related PoCs: poc-2020-10-harvest, poc-2021-01-saddle, poc-2025-12-yeth
- Docs: docs/AMM_RULE_PACK.md, docs/ORACLE_RULE_PACK.md

Suggested tests:

- Move reserves in a local pool test and assert dependent protocol decisions respect documented price bounds or TWAP assumptions.

Search tags: `amm-pricing, spot-price, oracle-risk, amm-rule-pack`

### ARK-AMM-004 - Fee-on-transfer or non-standard token assumptions not documented

- Priority: `Medium readiness gap`
- Confidence: `high`
- Confidence reason: Semantic-lite Solidity evidence was detected and matching test coverage evidence was not found.
- Detection sources: `keyword, semantic-lite, test-coverage`
- Category: `amm-token-assumptions`

Evidence:
- `src/ToyHybridMarket.sol:9` in `getReserves`: Solidity function shape matches this readiness finding. Snippet: `getReserves`
- `src/ToyHybridMarket.sol:13` in `quote`: Solidity function shape matches this readiness finding. Snippet: `quote`
- `src/ToyHybridMarket.sol:17` in `swap`: Solidity function shape matches this readiness finding. Snippet: `kLast = reserve0 * reserve1;`
- `test/documentation coverage`: No semantic-lite amm test coverage terms were detected.
- `src/ToyHybridMarket.sol:1`: Keyword signal matched this readiness finding. Snippet: `amountIn, amountOut, getReserves, kLast, pool, quote, reserve0, reserve1`

Detected signals:
- `amountIn`
- `amountOut`
- `getReserves`
- `kLast`
- `pool`
- `quote`
- `reserve0`
- `reserve1`
- `swap`

Affected files:
- `src/ToyHybridMarket.sol`
- `test/ToyHybridMarket.t.sol`

What was detected:

Token transfer and amountIn accounting signals were detected without clear received-amount tests or non-standard token assumptions.

Why it matters:

AMM pools that assume amountIn equals tokens received may mis-account non-standard tokens unless explicitly unsupported or handled.

Historical pattern similarity:

Maps to fee-on-transfer and token accounting assumption readiness classes.

Recommended defensive checks:

- actual received amount accounting
- fee-on-transfer simulation
- unsupported token documentation

Related Knowledge:

- Historical patterns: pattern-pool-price-accounting, pattern-precision-rounding-loss
- Suggested defensive tests: balance-before-after-accounting, fee-on-transfer-token-simulation, unsupported-token-documentation
- Related PoCs: poc-2020-06-balancer-deflationary
- Docs: docs/AMM_RULE_PACK.md, docs/REENTRANCY_VALUE_FLOW_RULE_PACK.md

Suggested tests:

- Use a local fee-on-transfer token mock or document that such tokens are unsupported and guarded by configuration.

Search tags: `amm-token-assumptions, fee-on-transfer, amm-rule-pack`

### ARK-AMM-005 - Slippage/min-output constraints missing or unclear

- Priority: `Medium readiness gap`
- Confidence: `high`
- Confidence reason: Semantic-lite Solidity evidence was detected and matching test coverage evidence was not found.
- Detection sources: `keyword, semantic-lite, test-coverage`
- Category: `amm-slippage`

Evidence:
- `src/ToyHybridMarket.sol:9` in `getReserves`: Solidity function shape matches this readiness finding. Snippet: `getReserves`
- `src/ToyHybridMarket.sol:13` in `quote`: Solidity function shape matches this readiness finding. Snippet: `quote`
- `src/ToyHybridMarket.sol:17` in `swap`: Solidity function shape matches this readiness finding. Snippet: `kLast = reserve0 * reserve1;`
- `test/documentation coverage`: No semantic-lite amm test coverage terms were detected.
- `src/ToyHybridMarket.sol:1`: Keyword signal matched this readiness finding. Snippet: `amountIn, amountOut, getReserves, kLast, pool, quote, reserve0, reserve1`

Detected signals:
- `amountIn`
- `amountOut`
- `getReserves`
- `kLast`
- `pool`
- `quote`
- `reserve0`
- `reserve1`
- `swap`

Affected files:
- `src/ToyHybridMarket.sol`
- `test/ToyHybridMarket.t.sol`

What was detected:

Swap path signals were detected without clear minOut, deadline, slippage, or stale-quote constraints.

Why it matters:

Slippage and stale quote controls help users and integrations bound expected outcomes around swaps.

Historical pattern similarity:

Maps to price boundary and quote freshness readiness classes.

Recommended defensive checks:

- minOut enforcement
- deadline behavior
- stale quote handling

Related Knowledge:

- Historical patterns: pattern-spot-price-manipulation, pattern-assumption-not-encoded-in-tests
- Suggested defensive tests: min-out-enforcement, deadline-or-stale-quote-test, slippage-boundary-test
- Related PoCs: poc-2020-10-harvest, poc-2021-01-saddle
- Docs: docs/AMM_RULE_PACK.md, docs/ORACLE_RULE_PACK.md

Suggested tests:

- Assert swaps revert or follow documented policy when amountOut falls below a user-provided bound or quote is stale.

Search tags: `amm-slippage, min-output, amm-rule-pack`

### ARK-LEND-001 - Collateral/debt solvency invariant not covered by tests

- Priority: `Medium readiness gap`
- Confidence: `medium`
- Confidence reason: Semantic-lite Solidity evidence was detected, and related test coverage terms were also found; priority may be reduced.
- Detection sources: `semantic-lite`
- Category: `lending-solvency`

Evidence:
- `src/ToyHybridMarket.sol:37` in `depositCollateral`: Solidity function contains external value-flow call evidence. Snippet: `collateral[msg.sender] += msg.value;`
- `src/ToyHybridMarket.sol:41` in `collateralValue`: Solidity function shape matches this readiness finding. Snippet: `return collateral[user] * price / 1e18;`
- `src/ToyHybridMarket.sol:46` in `healthFactor`: Solidity function shape matches this readiness finding. Snippet: `if (debt[user] == 0) {`
- `src/ToyHybridMarket.sol:53` in `borrow`: Solidity function contains external value-flow call evidence. Snippet: `require(healthFactor(msg.sender) > 1e18, "HEALTH");`
- `src/ToyHybridMarket.sol:61` in `repay`: Solidity function contains external value-flow call evidence. Snippet: `uint256 paid = amount > debt[msg.sender] ? debt[msg.sender] : amount;`

Detected signals:
- `borrow`
- `cash`
- `collateral`
- `debt`
- `healthFactor`
- `liquidate`
- `liquidationThreshold`
- `repay`
- `totalBorrows`

Affected files:
- `src/ToyHybridMarket.sol`
- `test/ToyHybridMarket.t.sol`

What was detected:

Collateral, debt, borrow, repay, or health-factor signals were detected without visible solvency invariant tests.

Why it matters:

Lending systems depend on collateral and debt accounting staying aligned across every user action.

Historical pattern similarity:

Maps to collateral/debt invariant and oracle-dependent lending readiness classes. This is defensive review context, not vulnerability confirmation.

Recommended defensive checks:

- collateral debt invariant
- unsafe withdrawal rejection
- borrow limit boundary
- repay/deposit accounting

Related Knowledge:

- Historical patterns: pattern-collateral-debt-invariant, pattern-oracle-stale-price
- Suggested defensive tests: collateral-debt-invariant, borrow-limit-boundary-test, unsafe-withdrawal-rejection
- Related PoCs: poc-2025-11-moonwell, poc-2020-11-cheese-bank
- Docs: docs/LENDING_RULE_PACK.md, docs/RULE_PACKS.md, docs/READINESS_SCORE.md

Suggested tests:

- Assert debt cannot exceed documented collateral constraints and collateral withdrawals cannot make a position unsafe unless intended and tested.

Search tags: `lending-solvency, lending-rule-pack, pre-audit-readiness`

### ARK-LEND-002 - Liquidation boundary tests missing

- Priority: `Medium readiness gap`
- Confidence: `medium`
- Confidence reason: Semantic-lite Solidity evidence was detected, and related test coverage terms were also found; priority may be reduced.
- Detection sources: `semantic-lite`
- Category: `lending-liquidation`

Evidence:
- `src/ToyHybridMarket.sol:37` in `depositCollateral`: Solidity function contains external value-flow call evidence. Snippet: `collateral[msg.sender] += msg.value;`
- `src/ToyHybridMarket.sol:41` in `collateralValue`: Solidity function shape matches this readiness finding. Snippet: `return collateral[user] * price / 1e18;`
- `src/ToyHybridMarket.sol:46` in `healthFactor`: Solidity function shape matches this readiness finding. Snippet: `if (debt[user] == 0) {`
- `src/ToyHybridMarket.sol:53` in `borrow`: Solidity function contains external value-flow call evidence. Snippet: `require(healthFactor(msg.sender) > 1e18, "HEALTH");`
- `src/ToyHybridMarket.sol:61` in `repay`: Solidity function contains external value-flow call evidence. Snippet: `uint256 paid = amount > debt[msg.sender] ? debt[msg.sender] : amount;`

Detected signals:
- `borrow`
- `cash`
- `collateral`
- `debt`
- `healthFactor`
- `liquidate`
- `liquidationThreshold`
- `repay`
- `totalBorrows`

Affected files:
- `src/ToyHybridMarket.sol`
- `test/ToyHybridMarket.t.sol`

What was detected:

Liquidation, threshold, bonus, close factor, or seize signals were detected without visible just-above/just-below boundary tests.

Why it matters:

Liquidation boundary errors can reject valid liquidations, liquidate solvent positions, or distort seized collateral accounting.

Historical pattern similarity:

Maps to liquidation boundary and collateral accounting readiness classes.

Recommended defensive checks:

- just-above threshold
- just-below threshold
- bonus bounds
- partial liquidation math

Related Knowledge:

- Historical patterns: pattern-collateral-debt-invariant, pattern-oracle-stale-price
- Suggested defensive tests: just-above-threshold-test, just-below-threshold-test, partial-liquidation-math
- Related PoCs: poc-2025-11-moonwell, poc-2020-11-cheese-bank
- Docs: docs/LENDING_RULE_PACK.md, docs/ORACLE_RULE_PACK.md

Suggested tests:

- Test a position just above threshold cannot be liquidated and a position just below threshold can be liquidated within documented bonus bounds.

Search tags: `lending-liquidation, liquidation-boundary, lending-rule-pack`

### ARK-LEND-004 - Oracle-dependent borrowing/liquidation without stale-price tests

- Priority: `Low readiness gap`
- Confidence: `low`
- Confidence reason: Keyword-only signal detected without Solidity function-level evidence; manual review is recommended before remediation.
- Detection sources: `keyword, test-coverage`
- Category: `lending-oracle`

Evidence:
- `test/documentation coverage`: No semantic-lite oracle test coverage terms were detected.
- `src/ToyHybridMarket.sol:1`: Keyword signal matched this readiness finding. Snippet: `borrow, cash, collateral, debt, getReserves, healthFactor, liquidate, liquidationThreshold`
- `test/ToyHybridMarket.t.sol:1`: Keyword signal matched this readiness finding. Snippet: `borrow, cash, collateral, debt, getReserves, healthFactor, liquidate, liquidationThreshold`

False-positive notes:

Keyword-only signal without Solidity function-level evidence. Review manually before creating remediation tasks.

Detected signals:
- `borrow`
- `cash`
- `collateral`
- `debt`
- `getReserves`
- `healthFactor`
- `liquidate`
- `liquidationThreshold`
- `pool`
- `repay`
- `reserve0`
- `reserve1`
- `totalBorrows`

Affected files:
- `src/ToyHybridMarket.sol`
- `test/ToyHybridMarket.t.sol`

What was detected:

Borrowing, collateral valuation, health-factor, or liquidation logic appears oracle-dependent without visible stale-price or price-shock tests.

Why it matters:

Lending solvency can be distorted when collateral values depend on stale, invalid, or mis-normalized prices.

Historical pattern similarity:

Maps to oracle-dependent liquidation and collateral valuation readiness classes.

Recommended defensive checks:

- stale oracle rejection
- decimals normalization
- price shock boundary
- borrow blocked on invalid price

Related Knowledge:

- Historical patterns: pattern-oracle-stale-price, pattern-collateral-debt-invariant
- Suggested defensive tests: stale-oracle-rejection, decimals-normalization-test, price-shock-boundary-test
- Related PoCs: poc-2025-11-moonwell, poc-2020-10-harvest
- Docs: docs/LENDING_RULE_PACK.md, docs/ORACLE_RULE_PACK.md

Suggested tests:

- Mock stale, invalid, and sharply moved prices and assert borrow/liquidation behavior follows documented policy.

Search tags: `lending-oracle, oracle-risk, lending-rule-pack`

### ARK-LEND-005 - Reserve/cash accounting assumptions not covered

- Priority: `Medium readiness gap`
- Confidence: `high`
- Confidence reason: Semantic-lite Solidity evidence was detected and matching test coverage evidence was not found.
- Detection sources: `semantic-lite`
- Category: `lending-liquidity`

Evidence:
- `src/ToyHybridMarket.sol:37` in `depositCollateral`: Solidity function contains external value-flow call evidence. Snippet: `collateral[msg.sender] += msg.value;`
- `src/ToyHybridMarket.sol:41` in `collateralValue`: Solidity function shape matches this readiness finding. Snippet: `return collateral[user] * price / 1e18;`
- `src/ToyHybridMarket.sol:46` in `healthFactor`: Solidity function shape matches this readiness finding. Snippet: `if (debt[user] == 0) {`
- `src/ToyHybridMarket.sol:53` in `borrow`: Solidity function contains external value-flow call evidence. Snippet: `require(healthFactor(msg.sender) > 1e18, "HEALTH");`
- `src/ToyHybridMarket.sol:61` in `repay`: Solidity function contains external value-flow call evidence. Snippet: `uint256 paid = amount > debt[msg.sender] ? debt[msg.sender] : amount;`

Detected signals:
- `borrow`
- `cash`
- `collateral`
- `debt`
- `healthFactor`
- `liquidate`
- `liquidationThreshold`
- `repay`
- `totalBorrows`

Affected files:
- `src/ToyHybridMarket.sol`
- `test/ToyHybridMarket.t.sol`

What was detected:

Cash, reserves, total borrows, utilization, or available-liquidity signals were detected without visible cash/debt consistency tests.

Why it matters:

Reserve and cash accounting define whether borrowers can draw liquidity and whether repayments restore accounting state.

Historical pattern similarity:

Maps to cash/debt mismatch and liquidity accounting readiness classes.

Recommended defensive checks:

- available liquidity bound
- repay updates cash/debt
- reserve withdrawal constraints
- utilization bounds

Related Knowledge:

- Historical patterns: pattern-collateral-debt-invariant, pattern-accounting-index-drift
- Suggested defensive tests: available-liquidity-bound, repay-cash-debt-consistency, reserve-withdrawal-constraints
- Related PoCs: poc-2020-11-cheese-bank
- Docs: docs/LENDING_RULE_PACK.md, docs/RULE_PACKS.md

Suggested tests:

- Assert borrow reverts above available liquidity and repay updates cash, debt, reserves, and utilization consistently.

Search tags: `lending-liquidity, reserve-accounting, lending-rule-pack`


## Suppressed Readiness Gaps

No readiness gaps were suppressed in this run.

## Suggested Foundry Invariant Skeletons

- Skeleton not generated in this run.
- To generate: `python3 scripts/pre_audit_scan.py --root . --generate-invariant-skeletons`

- **stale price rejection** (`oracle`): Stale oracle rounds should be rejected or handled according to documented policy.
- **decimals normalization** (`oracle`): Price decimals should be normalized consistently before accounting decisions.
- **price bounds** (`oracle`): Outlier prices should hit documented bounds or review paths.
- **TWAP or sanity check** (`oracle`): Spot price dependence should be bounded by TWAP, sanity checks, or explicit assumptions.
- **oracle update access control** (`oracle`): Only authorized roles should change oracle configuration.
- **invariant conservation** (`amm`): Swaps should preserve the AMM invariant within fee and rounding expectations.
- **swap does not create value** (`amm`): No swap sequence should create value outside documented fee mechanics.
- **liquidity add/remove proportionality** (`amm`): Liquidity mint/burn should be proportional to reserves within expected rounding.
- **fee growth consistency** (`amm`): Fee growth should be monotonic and attributable to swaps or configured fee paths.
- **collateralization invariant** (`lending`): Borrower positions should respect collateralization requirements after every user action.
- **liquidation solvency** (`lending`): Liquidations should improve solvency and preserve accounting assumptions.
- **interest index monotonicity** (`lending`): Interest indexes should move monotonically according to configured rate logic.
- **oracle manipulation resistance** (`lending`): Borrow and liquidation paths should resist transient price manipulation.
- **borrow/repay accounting consistency** (`lending`): Debt and collateral balances should reconcile after borrow and repay sequences.

## Audit Readiness Checklist

- [ ] Core user flows have deterministic unit tests.
- [ ] Accounting, oracle, reward, and role assumptions are documented.
- [ ] Foundry invariant tests cover value conservation and access boundaries.
- [ ] Fuzz tests cover edge cases, rounding, and unexpected user sequences.
- [ ] Privileged roles, upgrade controls, and emergency controls are documented and tested.
- [ ] Known limitations are written down for auditors.
- [ ] A formal audit scope names contracts, commit hash, deployment assumptions, and out-of-scope areas.

## Generated Issue Checklist

- No issue checklist file was requested in this run.
- To generate one: `python3 scripts/pre_audit_scan.py --root . --issue-checklist-output ARKHEIONX_ISSUE_CHECKLIST.md`
- Generated issue plan: `examples/reports/amm-lending-hybrid-fixture-issue-plan.json`
- Issue plan JSON can be used with `scripts/create_github_issues.py` in dry-run, create, or update mode.

## GitHub Action Outputs

- Markdown Report: `examples/reports/amm-lending-hybrid-fixture-pre-audit-report.md`
- Json Report: `examples/reports/amm-lending-hybrid-fixture-pre-audit-report.json`
- Sarif Report: `examples/reports/amm-lending-hybrid-fixture.sarif.json`
- Issue Plan: `examples/reports/amm-lending-hybrid-fixture-issue-plan.json`

## Search Tags

`access-control-review`, `arkheionx`, `audit-preparation`, `defi-security`, `foundry`, `historical-exploit-pattern`, `indie-defi`, `invariant-testing`, `oracle-risk`, `pre-audit-readiness`, `reentrancy-review`, `root-cause-analysis`, `smart-contract-security`, `solidity-security`, `vault-accounting`

## Recommended Next Steps

1. Add Foundry invariant tests for accounting, roles, and value-flow boundaries.
2. Document and test oracle freshness, decimals normalization, bounds, and fallback behavior.
3. Write a formal audit scope with contracts, roles, assumptions, known limitations, and test commands.
4. Run a formal smart contract audit before mainnet launch or before handling real user funds.

## What This Report Does Not Prove

- It does not prove protocol safety.
- It does not confirm exploitability.
- It does not replace manual review.
- It does not replace a formal audit.

## Formal Audit Recommendation

Run a formal smart contract audit before mainnet deployment, before material TVL, or before handling real user funds.


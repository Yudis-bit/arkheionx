# Semantic-Lite Analysis

Arkheionx v0.6.0 adds semantic-lite Solidity extraction. It is a local,
dependency-free parser that extracts enough structure to make readiness
findings more evidence-based without pretending to be a full compiler or
formal analyzer.

Semantic-lite is enabled by default.

## What It Extracts

- Solidity contracts, interfaces, and libraries.
- Inheritance names.
- State variable names.
- Function names, visibility, modifiers, payable status, and line ranges.
- Selected call evidence such as token transfers, low-level calls, oracle
  reads, and setter-like admin functions.
- Test functions, invariant functions, fuzz-like tests, and rule-pack coverage
  terms.

## Why It Exists

Earlier Arkheionx versions could surface useful readiness gaps from keyword
signals, but keyword-only detection can be noisy. Semantic-lite helps
distinguish between:

- a README that casually mentions oracle risk; and
- Solidity code that actually calls `latestRoundData()`, `getReserves()`, or a
  price helper.

That distinction lets Arkheionx attach evidence, improve SARIF locations, and
downgrade weak keyword-only findings.

## Evidence Example

```json
{
  "type": "semantic-lite",
  "file": "src/OracleRewardFixture.sol",
  "function": "getPrice",
  "line": 61,
  "snippet": "priceFeed.latestRoundData()",
  "reason": "Solidity function contains oracle or price-feed call evidence."
}
```

Findings can also include test-coverage evidence:

```json
{
  "type": "test-coverage",
  "reason": "No semantic-lite oracle test coverage terms were detected."
}
```

They can also include negative evidence when coverage terms appear in missing
or TODO context:

```json
{
  "type": "negative-test-coverage",
  "file": "test/FakeGlobalVault.t.sol",
  "line": 6,
  "term": "stale oracle tests",
  "reason": "Coverage term appears in negative context."
}
```

Negative evidence is not counted as coverage. It is retained as remediation
context and can influence confidence reasons and score calibration.

Generated Arkheionx artifacts are filtered before semantic-lite extraction.
Old reports, issue plans, SARIF, baselines, and delivery artifacts should not
create semantic evidence, test coverage evidence, or negative evidence.

v1.4.0 extends semantic-lite coverage mapping for AMM and lending shapes:

- AMM: reserve, liquidity, invariant, LP share, slippage, TWAP, actual received
  amount, and non-standard token assumptions.
- Lending: collateral/debt, health factor, liquidation, interest/borrow index,
  reserve/cash accounting, and oracle-dependent borrowing/liquidation terms.

These mappings are heuristic. They improve affected function reporting and
confidence calibration, but manual review remains required.

## Confidence Effects

- Semantic evidence plus missing matching tests can raise confidence.
- Semantic evidence plus matching tests can reduce priority.
- Keyword-only evidence is downgraded when `downgrade_keyword_only` is enabled.
- Low-confidence findings are still visible, but issue plans can exclude them
  by default so teams do not create noisy remediation issues.

## Limits

Semantic-lite is heuristic. It does not build a complete Solidity AST, resolve
imports, execute compilation, compute data flow, or prove exploitability. It is
a pre-audit readiness aid for authorized repositories, not a formal audit or a
security guarantee.

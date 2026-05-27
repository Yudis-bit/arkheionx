# Value Flow Workbench

Arkheionx is repositioning as a local-first DeFi value-flow workbench.

Core promise:

```text
Map the money flow. Find the missing tests.
```

Developer line:

```text
Foundry tells you if your tests pass.
Arkheionx shows where value moves - and what you forgot to test.
```

## What Value Flow Means

In DeFi, value flow is the path by which assets, balances, shares, debt,
collateral, rewards, prices, or privileged parameters change who can receive,
hold, claim, borrow, repay, withdraw, or liquidate value.

Value flow is broader than token transfers. It includes accounting state,
price assumptions, share math, debt indexes, reward accumulators, role-gated
parameters, and any state transition that changes economic rights.

Common examples:

- User asset -> vault balance -> share mint.
- Oracle price -> borrow limit -> debt.
- Collateral -> liquidation payout.
- Reward funding -> user claim.
- Admin parameter -> value impact.

## Why Builders Use It

Builders often know their happy-path tests pass, but still need a clear map of
where value can move and what assumptions make that movement safe.

Arkheionx helps builders review:

- where deposits, withdrawals, borrows, repayments, claims, swaps, and
  liquidations affect accounting;
- whether tests cover critical value-flow paths;
- which assumptions need explicit defensive tests;
- which review areas deserve attention before AI-agent work, CI hardening,
  contests, bounty review, or formal audit prep.

## Why Researchers Use It

Researchers need fast orientation inside unfamiliar repositories. A value-flow
view helps turn local code signals into a review map:

- which functions move or account for value;
- which rules, evidence, and historical patterns are nearby;
- which missing tests or weak assumptions might deserve manual review;
- which issue candidates are grounded in evidence rather than broad claims.

Arkheionx outputs remain review prompts. They do not confirm vulnerabilities,
prove exploitability, or replace human analysis.

## Current Arkheionx Support

v2.0.1 is a repositioning hotfix, not a new flow engine release. Existing
interfaces remain the current functional foundation:

- `arkheionx scan` maps local/static repository signals to findings, evidence,
  Fix First priority, SARIF, JSON, and Markdown reports.
- `arkheionx test-plan` turns findings into defensive test plans and Foundry
  skeleton starters.
- `arkheionx search` connects findings to local security memory and historical
  pattern context.
- `arkheionx validate-config`, `arkheionx doctor`, and `arkheionx version`
  keep local setup and safety posture checkable.

Advanced workflows built on this foundation include pre-audit readiness
reports, SARIF, issue plans, CI artifacts, baseline/diff outputs, delivery
reports, and ecosystem summaries.

## Future Flow Direction

The future `arkheionx flow` command is planned, not implemented in v2.0.1.

Planned directions include:

- `arkheionx flow` for a local value-flow map;
- `arkheionx flow --test-gaps` for missing value-flow tests;
- `arkheionx flow explain` for plain-language flow explanations;
- `arkheionx flow test-template` for flow-based Foundry starter tests;
- `arkheionx flow review-map` for researcher-oriented review areas;
- `arkheionx flow verify` for before/after checks.

These are roadmap items. Use the current `scan`, `test-plan`, and `search`
commands for v2.0.1.

## Safety Boundaries

Arkheionx remains local-first, static, CLI-first, and defensive:

- no RPC or live-chain calls;
- no deployed-contract scanning;
- no transaction execution;
- no private key, mnemonic, token, or secret handling;
- no exploit payload generation or attack automation;
- no formal audit or security guarantee claims.

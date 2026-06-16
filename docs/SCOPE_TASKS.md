# Scope Tasks (V7)

`arkheionx scope-tasks <repo> --scope-file <scope.md>` turns scope-aware lanes into
precise, bounded, evidence-oriented tasks for a human reviewer or a model-agnostic
AI agent. Tasks are research instructions, not findings and not exploit
instructions. Human review required.

## Lanes first

`arkheionx scope-lanes` selects generic review lanes only when a repository surface
or the scope note makes them relevant. Lane types include: Mint/Redeem/Value Flow,
Vault/Share Accounting, Rewards/Vesting, Withdrawal Queue/Claim NFT,
Oracle/Pricing/Decimals, Authorization/Signatures/Replay,
Compliance/Freeze/Sanctions, Cross-Chain/Adapter/Compose, External
Integration/Adapter, Admin/Emergency/Upgrade, Periphery/Callback/Batch,
Gas/Unbounded Loop/Griefing, ERC Standard Compliance, and Token Integration /
Non-standard ERC20. Each lane carries priority (review order, never severity),
targets, why it matters, what can be valid, what is likely invalid, known/accepted
filters, first hypotheses, required evidence, and a stop condition.

## Task fields

Each task is concrete and bound to a target, with: `task_id`, `lane_id`, `title`,
target contract/function, source reference, `hypothesis`, `counterfactual`, why it
might matter, validity filter, known-issue filter, setup, action, required
assertions, required evidence, likely-invalid conditions, stop condition, and a
report-candidate threshold. Every task is `human_review_required`.

## Task categories

authorization bypass; replay / nonce / deadline; signature purpose binding; oracle
stale/deviation/decimals; share price inflation/deflation; virtual accounting
desync; rewards/vesting mismatch; withdrawal amount mismatch; transferable claim
ownership edge; compliance bypass; cross-chain stuck/refund/quarantine edge;
adapter amount mismatch; external call ordering; unbounded loop griefing; admin
role boundary exceedance; ERC standard compliance (Medium/High impact only);
fee/slippage mismatch with user loss; preview vs actual execution mismatch;
burn-to-claim mismatch; capacity/debt accounting mismatch; blocklist/freeze timing
interaction.

## Output

`scope-tasks.md` (Boundary, Task Summary, Tasks) and `scope-tasks.json` (validated
by `schemas/scope-tasks.schema.json`), with `tasks`, `lanes`, `report_filters`, and
`safety`. Each task is ready to hand to a model-agnostic AI agent or a human
reviewer.

```bash
arkheionx scope-tasks examples/scope-fixture --scope-file examples/scope-fixture/scope-note.md
```

See [`SCOPE_ORCHESTRATION.md`](SCOPE_ORCHESTRATION.md),
[`EVIDENCE_JUDGE.md`](EVIDENCE_JUDGE.md), and [`V7_WORKFLOW.md`](archive/versions/V7_WORKFLOW.md).

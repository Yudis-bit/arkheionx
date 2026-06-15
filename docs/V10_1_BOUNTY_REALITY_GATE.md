# V10.1 Bounty Reality Gate

## What Changed

V10.1 separates technical bug shape from submission relevance. The bounty
reality gate receives candidate, severity, memory, scope, proof, cap, profit,
victim-loss, opt-in, reviewer-outcome, and policy-carveout facts, then returns a
submission recommendation.

Blocking verdicts remove submit labels from candidates before artifact output.
The quality gate `NO_SUBMIT_IF_BOUNTY_REALITY_BLOCKED` verifies that blocked
candidates cannot remain `SUBMIT_*`.

## How To Run

```bash
arkheionx war-run tests/fixtures/repos/rejected_rounding_reconciliation_benchmark \
  --memory artifacts/smoke-memory \
  --out artifacts/smoke-rejected-rounding \
  --max-candidates 10 \
  --json
```

Relevant artifacts:

- `17-bounty-reality.json`
- `17-bounty-reality.md`
- `quality-gates.json`
- `quality-gates.md`

## Verdict Interpretation

- `SUBMITTABLE`: proof and economic path are strong, with no known blocker.
- `NEEDS_MORE_PROOF`: no hard blocker, but current proof is insufficient.
- `VALID_CODE_BUG_BUT_NOT_BOUNTY_WORTHY`: code issue may be real, but the
  reviewer-reality gate blocks submission.
- `DO_NOT_SUBMIT_*`: a specific blocker applies, such as duplicate,
  previously rejected, dust, precision-only, no-profit, victim opt-in,
  trusted-role, off-chain validation, key reuse, forced-transfer-only, gas-only,
  or policy carveout.

## Generic Examples

- `rejected_rounding_reconciliation_benchmark`: blocked as previously rejected,
  dust/precision capped, and no attacker profit.
- `lender_consent_route_buffer_benchmark`: blocked or downgraded unless
  realistic capture and large loss are proven.
- `key_reuse_replay_carveout_benchmark`: blocked or routed to human review when
  replay depends only on reused signing authority.
- `forced_value_transfer_no_logic_flaw_benchmark`: blocked when balance changes
  are not connected to exploitable contract logic.
- `generic_signature_binding_bug`: remains promotable when an executed value or
  control field is not signed and no blocker applies.

## Limitations

The gate is a conservative local triage layer. It does not guarantee payout,
acceptance, impact, or final severity. Missing economic evidence should become
`NEEDS_MORE_PROOF` or `HUMAN_REVIEW_REQUIRED`, not a manufactured submit label.

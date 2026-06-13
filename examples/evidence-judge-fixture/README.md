# evidence-judge-fixture

A small, local/static fixture for the V7 Test Evidence Judge. It contains a tiny
share vault plus deliberately strong, weak, invalid, and out-of-scope local tests
so `arkheionx evidence-judge` and `arkheionx judge-report` have something to
grade. **This fixture has no planted vulnerability** — it exists to exercise the
orchestration and evidence-quality workflow, not to demonstrate a bug.

Local/static only. Nothing here is a finding. Evidence quality is not
vulnerability validity. Human review is required.

## Contracts (`src/`)

- `MockToken.sol` — a minimal local test token.
- `Vault.sol` — in-scope vault: `deposit` (value entry), `withdraw` (value exit),
  and `setFeeRecipient` (owner-gated admin setter).
- `AdminConfig.sol` — in-scope, owner-gated configuration (authorization lane).
- `ExperimentalVault.sol` — a HEAD-only experiment marked **out of scope** in
  `scope.json`.

## Tests (`test/`)

- `VaultWithdrawStrong.t.sol` — **strong** evidence: pre/post balances, a
  `totalShares` state delta, attacker/victim separation, a dust boundary, and a
  must-revert negative path on `Vault.withdraw`.
- `VaultDepositWeak.t.sol` — **weak** evidence: calls `Vault.deposit` but makes
  only a shallow assertion, with no pre/post delta and no negative path.
- `InvalidNoTarget.t.sol` — **invalid**: references no in-scope target and makes
  no assertion, so it proves nothing.
- `ExperimentalOutOfScope.t.sol` — targets the **out-of-scope**
  `ExperimentalVault`, so the judge flags it rather than trusting it.

## Scope and evidence

- `scope.json` — local scope hints: `Vault`/`AdminConfig` in scope,
  `ExperimentalVault` out of scope. (`arkheionx` also reads
  `.arkheionx/scope.json` when present.)
- `evidence-submissions/vault-withdraw.json` — a recorded evidence submission for
  the strong withdraw test (`result: pass`).

## Try it

```bash
arkheionx review-lanes examples/evidence-judge-fixture
arkheionx agent-tasks examples/evidence-judge-fixture
arkheionx evidence-judge examples/evidence-judge-fixture
arkheionx judge-report examples/evidence-judge-fixture
```

The output is real engine output, not hardcoded. A human makes every final call.

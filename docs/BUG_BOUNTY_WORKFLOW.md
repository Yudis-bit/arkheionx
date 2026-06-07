# Bug bounty workflow (triage and hypothesis)

ArkheionX is a **triage and hypothesis workbench** for bug bounty work on
DeFi smart-contract repositories. It helps you decide *where to look first* and
*what to test by hand*. It is **not** an exploit finder, a severity oracle, or a
submission tool, and it does **not** confirm vulnerabilities.

Use it to answer five questions before you start manual review:

1. Where is value moving?
2. Which value paths are least tested?
3. Which assumptions are protecting those paths?
4. What should I manually review first?
5. What proof direction should I try by hand?

## What ArkheionX does and does not do here

ArkheionX **does**:

- Map contracts, value paths, assumptions, and test gaps locally and statically.
- Rank value-sensitive functions in review order (not severity order).
- Point each test gap at a `Source: <file>:<line>` so you can open the code.
- Suggest a local Foundry proof scaffold direction you fill in yourself.

ArkheionX **does not**:

- It does not confirm vulnerabilities or prove a bug exists.
- It does not assign severity, impact, or exploitability.
- It does not run exploits, attacks, or transaction broadcasting.
- It does not call RPC endpoints or read deployed/live-chain contracts.
- It does not submit reports or interact with any bounty platform.
- It does not handle private keys, seed phrases, or production credentials.

A HIGH review priority is a prompt for human attention, never a finding.

## Authorization first

Only run ArkheionX on code you own or are explicitly authorized to review under
a published bounty scope or program rules. Do not point any workflow at live
systems, third-party infrastructure, or out-of-scope targets. ArkheionX never
performs network or live-chain actions, but *you* are still responsible for
staying inside the program's authorized scope.

## Safe command flow

Run from a local checkout of the in-scope repository:

```sh
arkheionx doctor
arkheionx review-map .
arkheionx value-paths .
arkheionx assumptions .
arkheionx test-gap-map .
arkheionx proof-plan .
```

Then work the output by hand:

1. **Start with `review-map`.** Read the **Inspect first** list. It is your
   review order, not a ranking of severity.
2. **Prioritize money-moving, externally dependent, and untested paths.** In
   `value-paths`, look for value exits with `coverage none`. Those are where an
   accounting or access-control mistake would matter most.
3. **Use `assumptions` to choose your review angle.** Each assumption (oracle
   freshness, access control, share proportionality, no-reentrancy, standard
   ERC20) is a question to answer in the code: *is this actually enforced?*
4. **Use `test-gap-map` to write local tests.** Open the `Source: <file>:<line>`
   for each gap and write a targeted Foundry test that exercises the path under
   adversarial inputs.
5. **Use `proof-plan` as a starting outline.** It gives an objective, setup,
   action, and assertions to fill in. It is a scaffold, never a result.
6. **Validate manually.** Run your own tests, read the code, and reach your own
   conclusion. ArkheionX output is review context only.

## Turning a test gap into a manual proof idea

For each gap, ask the questions the category implies, then write the test:

| Gap category | Manual review question | Local test idea |
|---|---|---|
| Value exit (`withdraw`, `divest`) | Can value leave beyond the caller's entitlement? | Deposit, then attempt an oversized or repeated exit; assert accounting holds. |
| Admin setter (`setOracle`, `setPrice`) | Is the privileged action bounded and validated? | Call as non-owner (expect revert); set adversarial values; assert downstream behavior. |
| Oracle-dependent (`harvest`) | Does stale or manipulated price corrupt accounting? | Drive a stale/extreme price through a mock; assert the guard rejects it. |

These are **hypotheses to test**, not confirmed issues.

## What good ArkheionX bounty output looks like

This is **demo/heuristic** output from the bundled
[`vault-strategy-oracle-fixture`](../examples/vault-strategy-oracle-fixture/README.md),
not a real finding:

```text
Top Test Gaps
  1. PriceOracle.setPrice [high; medium; admin]
     Source: src/PriceOracle.sol:27
     Proof suggestion: yes (proof-priceoracle-setprice)
  2. Strategy.divest [high; medium; exit]
     Source: src/Strategy.sol:44
     Proof suggestion: yes (proof-strategy-divest)
  3. Vault.emergencyWithdraw [high; medium; exit]
     Source: src/Vault.sol:72
     Proof suggestion: yes (proof-vault-emergencywithdraw)
```

Read this as: "the value exits and the admin setters are untested; open those
files, confirm the assumptions, and write tests." The covered `deposit` path is
deliberately **not** listed — the map tracks observed coverage, not guesses.

## Before you submit

- Independently confirm impact with your own analysis and tests.
- Do **not** submit ArkheionX output as a vulnerability by itself; a test gap or
  a HIGH review priority is not evidence of a bug.
- Follow the program's responsible-disclosure rules.
- Keep the security judgment yours; ArkheionX organizes context, it does not
  decide.

## Related

- [`INTERPRET_RESULTS.md`](INTERPRET_RESULTS.md) — what each output section means.
- [`WHAT_ARKHEIONX_IS_NOT.md`](WHAT_ARKHEIONX_IS_NOT.md) — the boundaries.
- [`SECURITY.md`](../SECURITY.md) — reporting issues in ArkheionX itself.
- [`ETHICS.md`](ETHICS.md) — authorized-use expectations.

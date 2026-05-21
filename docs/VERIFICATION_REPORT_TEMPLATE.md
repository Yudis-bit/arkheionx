# Verification Report Template

Every PoC promoted to `reproducibility: deterministic-confirmed` must
have a corresponding report at `reports/verification/<id>.md` produced
from this template (or by `scripts/generate_verification_report.py` and
then filled in).

The report is the artifact that earns the status. Without it, the
status stays `deterministic-likely-but-unverified`.

---

## Template

```markdown
# Verification Report — <id>

- **Entry id:** `<id>`
- **Protocol:** <protocol>
- **Date of incident:** <YYYY-MM>
- **Chain:** <chain>
- **Fork block:** <block_number>
- **RPC alias:** <alias>

## Environment

- **Repository commit:** `<git rev-parse HEAD>`
- **Foundry version:** `<forge --version>`
- **OS / shell:** <runtime info>
- **RPC provider tier:** <archival tier and provider>

## Command run

\```sh
cd EVM
forge test --match-path "test/<YYYY-MM>/*.t.sol" -vvv
\```

## Result

- **Exit status:** <0 / nonzero>
- **Tests:** `<n>` passed, `<n>` failed, `<n>` skipped
- **Duration:** `<seconds>`

\```
<paste the relevant `forge test` summary block>
\```

## Assertion outcomes

For each assertion family required by the entry's category in
[../docs/ASSERTION_STANDARD.md](../../docs/ASSERTION_STANDARD.md), record
"pass" or "n/a" with a one-line note.

| Family | Required | Observed | Notes |
| ------ | -------- | -------- | ----- |
| F1. Attacker profit              | yes/no | pass/fail/n/a | <note> |
| F2. Victim loss                  | yes/no | pass/fail/n/a | <note> |
| F3. Invariant break              | yes/no | pass/fail/n/a | <note> |
| F4. Unauthorized state           | yes/no | pass/fail/n/a | <note> |
| F5. Oracle deviation             | yes/no | pass/fail/n/a | <note> |
| F6. Accounting mismatch          | yes/no | pass/fail/n/a | <note> |
| F7. Ownership / control          | yes/no | pass/fail/n/a | <note> |
| F8. Liquidation result           | yes/no | pass/fail/n/a | <note> |
| F9. Share price manipulation     | yes/no | pass/fail/n/a | <note> |

## Attacker path summary

One short paragraph reconstructing the on-fork sequence the test
performed. Reviewer should be able to compare this against the public
post-mortem and notice any divergence.

## Invariant broken

Restate the violated invariant from the entry's metadata. Confirm or
correct based on what the run actually demonstrated.

## Victim impact

What the test asserted about the victim's state, in concrete numbers
where possible.

## Root cause confirmed

Confirm the entry's root cause section is consistent with what the run
demonstrated, or note refinements.

## References checked

- [<title>](<url>)

## Missing verification steps

If anything below the "deterministic-confirmed" bar remains, list it:

- [ ] All required assertions pass against current commit.
- [ ] Verification report stored under `reports/verification/<id>.md`.
- [ ] Metadata `verification_status` updated to `verified`.
- [ ] Metadata `reproducibility` set to `deterministic-confirmed`.

## Verifier

- **Handle:** <github / arkheionx handle>
- **Date:** <YYYY-MM-DD>
```

---

## Notes for use

- Generate the skeleton with the script, then fill in the dynamic
  fields by hand. Do not commit a placeholder report — either it has
  real run output or it is not yet a verification report.
- A failed run is still worth a report. Mark `Exit status: nonzero`
  and explain the failure class
  ([FORK_VERIFICATION.md](FORK_VERIFICATION.md)). This is more useful
  than silent absence.
- The "Missing verification steps" section should be empty for a
  fully-verified entry. If anything is checked off, the entry should
  not be at `deterministic-confirmed`.

---

## Re-verification

Re-run reports replace the previous file. Keep one current report per
entry. Historical runs can be referenced via git history.

Re-verify when:

- Solidity / forge-std / OpenZeppelin / submodule versions change in a
  way that touches the test.
- The fork RPC provider or tier changes.
- A category-required assertion is added to the standard.
- Quarterly cadence as described in [EXPANSION_PLAN.md](EXPANSION_PLAN.md).

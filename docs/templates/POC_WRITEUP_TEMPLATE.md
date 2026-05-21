# PoC Writeup Template

Copy this template into a writeup file alongside the PoC, or paste the
content into the PR description. The headings match the metadata fields
so the registry entry can be filled out from the same source.

---

## Header

- **Entry id:** `<YYYY-MM-protocol-slug>`
- **Protocol:** <name>
- **Date of incident:** YYYY-MM
- **Chain:** <chain> (alias `<rpc_alias>`)
- **Fork block:** `<block_number>`
- **Attack transaction:** `<0x...>`
- **Category (primary):** `<from docs/EXPLOIT_TAXONOMY.md>`
- **Tags (secondary):** `<comma-separated>`
- **Severity:** `<critical | high | medium | low | informational>`

## TL;DR

One paragraph. What happened, what was lost, what was the broken
assumption. Reader should be able to stop here and still know what
the PoC is about.

## Background

Briefly: what the protocol does, what the relevant subsystem is, what
the design assumption was that turned out to be wrong. Link to the
protocol's own docs where useful.

Two paragraphs at most.

## Root cause

Use the seven slots from
[`ROOT_CAUSE_PLAYBOOK.md`](../ROOT_CAUSE_PLAYBOOK.md):

1. **Vulnerable assumption.** "Assumed that ..."
2. **Violated invariant.** "Should have held: ..."
3. **Attacker-controlled variable.** ...
4. **Missing validation.** ...
5. **Economic dependency.** ...
6. **Trust boundary failure.** ...
7. **Patch lesson.** ...

## Attacker path

Numbered list. Each item is a single concrete step the attacker took
on chain. Refer to addresses, function names, and amounts where they
matter. Do not paraphrase to the point of losing detail.

```
1. Take flash loan of <amount> <token> from <source>.
2. Swap <amount> on <pool> to push <quoted ratio> to <ratio>.
3. Call <function> on <victim contract> at the manipulated price.
4. Reverse the swap.
5. Repay loan.
```

## Reproduction

- **Fork:** `<chain>` at block `<block_number>` (alias `<rpc_alias>`).
- **PoC file:** `EVM/test/<YYYY-MM>/Exploit_<YYYY-MM>.t.sol`.
- **Run command:**

  ```sh
  cd EVM
  forge test --match-path "test/<YYYY-MM>/*.t.sol" -vvv
  ```

- **Required env vars:** `<*_RPC_URL>` (archival).
- **What setup does:** brief.
- **What the exploit body does:** brief.

## Assertions

List the assertion families used (see
[`ASSERTION_STANDARD.md`](../ASSERTION_STANDARD.md)). For each, paste
the actual `assert*` line from the PoC and a one-line explanation.

```solidity
assertGt(token.balanceOf(attacker) - balBefore, EXPECTED_PROFIT, "F1: profit");
assertLt(token.balanceOf(victim), victimBefore - EXPECTED_LOSS, "F2: loss");
```

## Verification status

- **Reproducibility:** `<from docs/REPRODUCIBILITY_STANDARD.md>`.
- **Verification status:** `<from schema enum>`.
- **Verification report:** `reports/verification/<id>.md` (link).
- **Local run evidence:** paste exit summary from `forge test`, or
  state explicitly that no local run was performed and why.

## Patch and disclosure

- **Patch reference:** commit / PR / advisory URL.
- **Disclosure timeline:** if public.
- **Mitigations now in place:** brief.

## What an auditor should remember

One or two sentences answering: "If I see this pattern again, what
should I check?". This is the value the entry leaves behind beyond
its specific incident.

Cross-reference the relevant section of
[`AUDITOR_CHECKLIST.md`](../AUDITOR_CHECKLIST.md).

## Similar incidents

Bullet list of registry ids that share the primary category, similar
exploit primitive, or shared protocol family.

## References

- [<title>](<url>) — type (post-mortem, contest, writeup, trace).

## Notes

Caveats, gaps, things that did not reproduce, things the public record
does not say. Honest is better than confident.

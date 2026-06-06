# Research Standard

What qualifies as a PoC in Arkheionx Vault, and what each entry must contain
before it can be merged.

## Inclusion criteria

A submission qualifies as a PoC if it:

1. Targets a **historical** incident or a **patched** vulnerability with public
   post-mortem evidence.
2. Reproduces the failure mode **deterministically** under documented conditions
   (pinned fork block, specific runtime, fixed inputs).
3. Terminates with **hard assertions** that prove the vulnerability triggered.
4. Cites at least one **external reference** (post-mortem, advisory, contest
   report, original PoC author).
5. Carries complete **metadata** in `metadata/registry.json` per
   [METADATA_SCHEMA.md](METADATA_SCHEMA.md).

Submissions that target unpatched live systems are out of scope. See
[ETHICS.md](ETHICS.md).

## Determinism

A PoC is **deterministic** when:

- The fork is pinned to a specific block number for EVM.
- Token deals (`vm.deal`, `deal()`) and pranks are explicit.
- Test outcome depends only on documented inputs, not on local state, time of
  day, or external availability beyond the configured archival RPC.

The metadata registry uses the values defined in
[METADATA_SCHEMA.md](METADATA_SCHEMA.md):

| Value | Meaning |
|---|---|
| `deterministic` | Runs to completion with pinned fork and hard assertions. |
| `partially-deterministic` | Pinned fork, but some state is recreated rather than forked. |
| `requires-archival-rpc` | Depends on archive-node history beyond standard RPC retention. |
| `local-only` | Runs against a local validator with deployed bytecode. |
| `template-only` | Stub for future work. Does not reproduce. |
| `unverified` | Code present, reproducibility not yet confirmed. |

## Required assertions

Every EVM PoC must include at least one assertion that proves the exploit
state. Acceptable patterns:

- `assertEq(targetContract.balance, 0)` after a drain.
- `assertGt(IERC20(token).balanceOf(attacker), preBalance)` for theft.
- `assertTrue(victim.isOwner(attacker))` for unauthorized takeover.
- `vm.expectRevert(...)` followed by the call that should now succeed (or vice
  versa) to demonstrate a state change.

A PoC that compiles, forks, and runs without assertions is rejected.

## Severity

Severity values: `critical`, `high`, `medium`, `low`, `informational`.

| Severity | Meaning |
|---|---|
| critical | Unconditional fund loss or full protocol takeover. |
| high | Conditional fund loss, or permanent denial of service of core flow. |
| medium | Fund risk under specific conditions, governance manipulation, or reversible DoS. |
| low | Bounded value impact or significant griefing without direct loss. |
| informational | Defensive note; not exploitable in isolation. |

Severity is recorded in metadata. It is not asserted by the test code.

## Status

| Status | Meaning |
|---|---|
| `historical` | Real-world incident, post-mortem available, no longer exploitable as written. |
| `patched` | Vulnerability fixed; PoC reproduces the pre-patch state via fork. |
| `educational` | Synthetic example illustrating a vulnerability class. |
| `template` | Skeleton, not yet a working PoC. |
| `embargoed` | Under disclosure embargo; metadata only, no code. |
| `incomplete` | Code present, missing assertions or references. |
| `needs-verification` | Listed but the maintainer has not re-run it locally on this branch. |

`needs-verification` is the honest default for ported PoCs whose assertions
have not been re-run since porting.

## Prohibited

- Live-target instructions, scanners, or autonomous attack runners.
- Code that requires private RPC keys, API keys, or paid services not
  documented in [REPRODUCIBILITY.md](REPRODUCIBILITY.md).
- PoCs whose only assertion is "the call succeeded" with no resulting state
  check.
- PoCs that depend on undocumented local mutations to a checked-in repo
  fixture.
- PoCs that target unpatched production code.
- PoCs imported from another repository without preserving original attribution.

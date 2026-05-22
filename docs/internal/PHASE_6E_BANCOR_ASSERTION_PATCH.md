# Phase 6E: Bancor Assertion Patch (One-PoC-Only)

**Phase:** 6E — Additive Assertion Patch, single PoC
**Branch:** `arkheionx/research-grade-rebuild`
**Maintainer:** Yudistira Putra (arkheionx)
**Date:** 2026-05-22

This phase patches **one** PoC with additive-only assertions and ships
no other code or metadata changes beyond what that patch requires.
Phase 6C (2017-11 Parity) and Phase 6D (2018-04 BEC) preceded it; this
phase targets the third PoC in the Phase 6B priority list.

---

## 1. Identity reminder (load-bearing)

Per Phase 6A, the registry `id` and file path remain
`2020-06-balancer-deflationary` for cross-reference stability, but the
code-observed protocol is **Bancor** — specifically, the public
`safeTransferFrom` exposed on a newly deployed Bancor contract that
already held outstanding user approvals. This phase treats the PoC as
Bancor for all assertion-design purposes; the slug is a stable handle,
not a semantic claim.

---

## 2. File modified

- `EVM/test/2020-06/Exploit_2020-06.t.sol` — test file only.

No changes to:

- `EVM/src/**`
- Any other `EVM/test/**` file
- `web/**`, `SVM/**`, `MoveVM/**`

The exploit flow, attacker actions, victim/token addresses, and call
order are unchanged. The transfer amount switched from inline
`XBPToken.balanceOf(victim)` to a snapshotted local `victimBefore`,
which is mathematically identical at the same block (single
`balanceOf` read, no state change between the two reads in the
original code) and is required to make exact-equality post-conditions
provable.

---

## 3. Assertions added (additive-only)

Pre-state snapshots before the existing `cheats.prank(address(this))`:

```solidity
uint256 victimBefore   = XBPToken.balanceOf(victim);
uint256 attackerBefore = XBPToken.balanceOf(attacker);
uint256 allowanceBefore = XBPToken.allowance(victim, bancorAddress);
assertGe(allowanceBefore, victimBefore,
    "victim allowance to Bancor must cover full balance pre-attack");
```

Post-state snapshots and assertions after the existing
`bancorContract.safeTransferFrom(...)`:

```solidity
uint256 victimAfter   = XBPToken.balanceOf(victim);
uint256 attackerAfter = XBPToken.balanceOf(attacker);

assertEq(victimAfter, 0,
    "victim XBPToken balance must be drained to zero");
assertEq(attackerAfter - attackerBefore, victimBefore,
    "attacker must gain exactly the victim's pre-attack balance");
```

Proof targets:

- **F4** (unauthorized state transition) — the public helper consumed
  an allowance the caller had no business spending.
- **F1** (value moved, exact equality) — attacker gain equals victim's
  pre-attack balance; victim balance ends at zero.

The `assertGe(allowanceBefore, victimBefore, ...)` precondition is the
explicit F4 guard: if the victim had not actually approved the Bancor
contract for at least their full balance, the public-helper abuse
would not be the operative root cause and the test should not claim it
is.

---

## 4. Commands run

From repository root unless noted.

```sh
git status --short
python3 scripts/validate_metadata.py
python3 scripts/generate_registry.py --check
python3 scripts/score_pocs.py --check
python3 scripts/generate_verification_report.py --check
cd EVM && forge build
cd EVM && forge fmt --check
cd EVM && forge fmt test/2020-06/Exploit_2020-06.t.sol
cd EVM && forge test --match-path test/2020-06/Exploit_2020-06.t.sol -vvv
python3 scripts/validate_metadata.py
python3 scripts/score_pocs.py
python3 scripts/generate_verification_report.py
cd EVM && forge fmt --check
cd EVM && forge build
```

All `validate_metadata`, `generate_registry --check`,
`generate_verification_report --check` (post-regen), `score_pocs`,
`forge fmt --check`, and `forge build` invocations succeed.
`generate_verification_report` (without `--check`) regenerates the
report's BEGIN/END block to reflect the new
`assertion_quality: strong` and the updated Phase 6A notes; manual
sections (Phase 6B plan, Phase 6A reclassification, Phase 6E patch)
are preserved outside the generated markers.

---

## 5. Fork test result

```
forge test --match-path test/2020-06/Exploit_2020-06.t.sol -vvv
```

Outcome: **fail at `setUp()`** with

```
vm.createSelectFork: failed to get account for
0x1804c8AB1F12E6bbf3894d4083f33e07309d1f38: server returned an error
response: error code -32000: historical state ... is not available
```

Was the failure RPC-related? **Yes — fully RPC-related.** The error
originates from the public mainnet RPC's inability to serve archival
state at block `10307563`. The test never reached `testsafeTransfer`,
so the new assertions did not execute. The patch itself compiles
under `forge build` and is `forge fmt`-clean.

This matches the Phase 6B plan classification: "additive-only but
requires archival verification". It is **not** a PoC defect and not a
patch defect.

Per the rules of this phase:

- The PoC is **not** marked failed.
- The PoC is **not** promoted to `deterministic-confirmed`.
- The PoC is **not** marked `verified`.
- `verification_status` stays `not-run-no-rpc`.
- `reproducibility` stays `deterministic-likely-but-unverified`.

---

## 6. Metadata and report changes

### `metadata/registry.json` (entry `2020-06-balancer-deflationary`)

- `assertion_quality`: `none` → `strong`
  - Justification: the patch encodes both the F4 precondition guard
    (`allowanceBefore >= victimBefore`) and the F1 exact-equality
    post-conditions (`victimAfter == 0`,
    `attackerAfter - attackerBefore == victimBefore`). Static
    assertion strength is high; the only unresolved factor is fork
    execution, which is captured separately by `verification_status`.
- `notes`: appended a Phase 6E sentence describing the additive
  assertions, that the patch compiles and is fmt-clean, that
  execution was blocked by archival-state-not-available on the public
  RPC, and that `verification_status` stays `not-run-no-rpc`.
- `tags`: added `phase-6e-assertion-patch` (alongside the existing
  `phase-6a-reclassified`).
- `verification_status`: **unchanged** (`not-run-no-rpc`).
- `reproducibility`: **unchanged**
  (`deterministic-likely-but-unverified`).
- Phase 6A identity correction (Bancor public-safeTransferFrom, slug
  retained for stability) is preserved verbatim.

### `reports/verification/2020-06-balancer-deflationary.md`

- Generated header now reflects `assertion_quality: strong` (regen
  from registry).
- Manual `## Phase 6E Assertion Patch` section added below the
  `## Phase 6A Reclassification` section, recording: identity
  reminder, file modified, assertions added, proof targets,
  behavioral-change disclosure, command run, RPC-limited fork
  failure, and the explicit decision **not** to promote to
  `verified` / `deterministic-confirmed`.
- Phase 6B plan section preserved.
- Phase 6A reclassification section preserved.

### `reports/poc_quality_matrix.md`

- Regenerated by `scripts/score_pocs.py` to reflect the new
  `assertion_quality: strong` row for `2020-06-balancer-deflationary`.
  The script reported "updated: reports/poc_quality_matrix.md (18
  entries)" once and "ok: matrix unchanged (18 entries)" on re-check.

---

## 7. Current verified count

- **EVM PoCs total:** 18.
- **Verified deterministic (`reproducibility = deterministic-confirmed`
  AND `verification_status = verified`):** **0**.
- **Phase 6E impact on the verified count:** none. This phase did not
  promote any PoC; it strengthened static proof quality on a single
  PoC whose execution remains blocked by the archival-RPC
  precondition.

The verified count cannot rise on this PoC without an archival
mainnet RPC that serves block `10307563`.

---

## 8. Recommendation for next one-PoC patch

Per the Phase 6B priority ordering, the remaining un-patched PoCs in
the planned set are:

1. `2020-09-bzx-ifusdc` — accounting-mismatch (iETH self-transfer
   doubling). Archival fork at block 10_810_804.
2. `2020-12-warp-finance` — accounting-mismatch (Cover-as-collateral
   manipulation). Archival fork at block 11_473_900.

**Recommended next target: `2020-09-bzx-ifusdc`.**

Reasoning:

- The PoC's invariant — internal token transfer must preserve
  `balance(src) + balance(dst)` when `src == dst` — has a clean,
  exact post-condition target: attacker iETH balance after the buggy
  `transfer` doubles relative to the pre-state, and the redeemed ETH
  exceeds the flash-loan principal by a measurable amount. Both are
  expressible with `assertEq` / `assertGt` against snapshotted
  pre-state, with no oracle-style approximations.
- The fork-block / RPC limitation is the **same** class of constraint
  that blocked Phase 6E here, so the patch can be designed and shipped
  with eyes-open expectations: additive-only, compiles, fmt-clean,
  execution likely blocked by public-RPC archival state. That keeps
  the next phase's risk profile identical to this one.
- `2020-12-warp-finance` involves multi-leg flash-loan + Curve LP
  share-price arithmetic; the assertion targets are messier
  (delta-around-pool-state) and the proof writeup is materially
  longer. It should follow `2020-09`, not precede it.

Do **not** start the next PoC in this session — that is Phase 6F's
mandate. This document closes Phase 6E.

---

## 9. Phase 6E close-out checklist

- [x] Single PoC patched (`EVM/test/2020-06/Exploit_2020-06.t.sol`).
- [x] No `EVM/src/**` changes.
- [x] No other `EVM/test/**` file changed.
- [x] No `web/**`, `SVM/**`, `MoveVM/**` changes.
- [x] Exploit flow, addresses, prank, and call order unchanged.
- [x] Assertions are additive-only; transfer amount switch is
      mathematically identical (`balanceOf(victim)` snapshot).
- [x] `forge build` clean.
- [x] `forge fmt --check` clean.
- [x] `forge test --match-path test/2020-06/Exploit_2020-06.t.sol`
      executed; failure classified as RPC limitation, not PoC defect.
- [x] Report `reports/verification/2020-06-balancer-deflationary.md`
      updated with Phase 6E section.
- [x] `metadata/registry.json` updated conservatively
      (`assertion_quality: none → strong`; verification status and
      reproducibility unchanged; identity correction preserved).
- [x] `reports/poc_quality_matrix.md` regenerated.
- [x] `scripts/validate_metadata.py`, `generate_registry.py --check`,
      `generate_verification_report.py --check`,
      `score_pocs.py --check` all pass after final regen.
- [x] Verified count unchanged at **0**.
- [x] No live exploitation tooling added.
- [x] No deterministic-confirmed promotion.

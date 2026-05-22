# Phase 6D: BEC `batchTransfer` Assertion Patch

**Phase:** 6D — Apply additive assertion patch to one PoC
**Branch:** `arkheionx/research-grade-rebuild`
**Latest commit at start:** `46b25d3 test(evm): assert Parity library code removal`
**Maintainer:** Yudistira Putra (arkheionx)
**Date:** 2026-05-22
**Target PoC:** `2018-04-bec-token`

This phase executes the Phase 6B Plan section 4.2 patch on a single PoC.
Only one Solidity test file was modified. No `EVM/src/`, `web/`, `SVM/`,
or `MoveVM/` files were touched. The exploit flow (token address,
attacker addresses, transfer amount, call order) is unchanged.

---

## 1. File modified

- `EVM/test/2018-04/Exploit_2018-04.t.sol` (only)

The local `BECToken` interface was extended with `totalSupply()` so the
test can read the token's pre-attack supply without pulling in
`src/interface.sol::IERC20`. No new imports were added.

---

## 2. Assertions added

Three new assertions wrap the existing `bec.batchTransfer(...)` call.
All values are captured into local variables; no additional external
state is mutated.

```solidity
uint256 mintedPerReceiver = type(uint256).max / 2 + 1;

uint256 a1Before = bec.balanceOf(attacker1);
uint256 a2Before = bec.balanceOf(attacker2);

// existing batchTransfer call (unchanged)
bec.batchTransfer(receivers, mintedPerReceiver);

uint256 a1After = bec.balanceOf(attacker1);
uint256 a2After = bec.balanceOf(attacker2);

// F1 — both attackers received exactly the wrapped-around mint amount
assertEq(a1After - a1Before, mintedPerReceiver, "attacker1 mint delta");
assertEq(a2After - a2Before, mintedPerReceiver, "attacker2 mint delta");

// F3 — sum of attacker holdings alone exceeds totalSupply (overflow fingerprint)
assertGt(a1After + a2After, bec.totalSupply(), "supply invariant broken");
```

**Proof targets:**
- **F1 (attacker profit):** exact equality of both attacker balance
  deltas against the literal `_value` argument passed to
  `batchTransfer`. Because the bug is a `count*value` wraparound that
  leaves the unchecked `_value` untouched, each receiver's balance must
  rise by exactly `_value` if and only if the bug fires.
- **F3 (invariant break):** `a1After + a2After > bec.totalSupply()` is
  the canonical overflow fingerprint — two account balances cannot sum
  above `totalSupply()` under correct token accounting. A passing
  inequality therefore cannot be produced by a no-op or a normal
  transfer.

**Exploit flow:** unchanged.
- Receivers: `[attacker1, attacker2]` — same as before.
- Transfer value: `type(uint256).max / 2 + 1` — same as before, now
  hoisted into `mintedPerReceiver` for reuse in the equality assertions.
- Call order: setUp → log pre-balances → snapshot balances → batchTransfer
  → snapshot post-balances → assertions → log post-balances.

---

## 3. Commands run

```sh
git status --short
python3 scripts/validate_metadata.py             # ok: 18 entries valid
python3 scripts/generate_registry.py --check     # ok: 18 entries
python3 scripts/score_pocs.py --check            # ok: matrix unchanged (18 entries) — pre-patch
python3 scripts/generate_verification_report.py --check  # ok: 18 entries processed, 0 changed — pre-patch
cd EVM && forge build                            # compiles, no errors
cd EVM && forge fmt --check                      # clean
cd EVM && forge test --match-path test/2018-04/Exploit_2018-04.t.sol -vvv
```

After the patch landed, the regenerator scripts were re-run:

```sh
python3 scripts/validate_metadata.py             # ok: 18 entries valid
python3 scripts/generate_verification_report.py  # updated: reports/verification/2018-04-bec-token.md (1 changed)
python3 scripts/score_pocs.py                    # updated: reports/poc_quality_matrix.md (18 entries)
python3 scripts/score_pocs.py --check            # ok: matrix unchanged
python3 scripts/generate_verification_report.py --check  # ok: 0 changed
python3 scripts/generate_registry.py --check     # ok: 18 entries
cd EVM && forge fmt --check                      # clean
cd EVM && forge build                            # compiles
```

---

## 4. Fork test result

**Result:** failed in `setUp()`, before any assertion executed.

**Output (truncated):**

```
ERROR sharedbackend: Failed to send/recv `basic`
  err=failed to get account for 0x1804c8AB1F12E6bbf3894d4083f33e07309d1f38:
  server returned an error response:
  error code -32000: historical state 7606478cdd... is not available
  address=0x1804c8AB1F12E6bbf3894d4083f33e07309d1f38

[FAIL: vm.createSelectFork: ... historical state ... is not available] setUp() (gas: 0)
```

The failure is in `cheats.createSelectFork("mainnet", 5_483_642)` — the
public RPC behind the `mainnet` alias has pruned state at block
5483642. No part of `testExploit` ran, so the assertions were neither
exercised nor falsified.

---

## 5. Whether failure was RPC-related

**Yes.** This is an archival-RPC limitation, not a PoC defect:

- The patched test file compiles under `forge build` with zero errors.
- `forge fmt --check` passes.
- The error originates in `vm.createSelectFork`, before `testExploit`
  executes, so neither the exploit call nor the assertions ran.
- The error message identifies the missing entity as historical state
  for a specific account at a pre-pruning block.
- This matches the pattern recorded for the Parity test in Phase 6C
  (`reports/verification/2017-11-parity-suicide.md`) and the broader
  RPC posture in `docs/PUBLIC_RPC_SMOKE_TEST_READINESS.md`.

Per the rules of this phase, the patch is retained because it
**compiles** and is **logically correct**. No verification-status
upgrade is claimed.

---

## 6. Metadata and report changes

### `metadata/registry.json` (entry `2018-04-bec-token`)

| Field                | Before          | After           |
|----------------------|-----------------|-----------------|
| `assertion_quality`  | `none`          | `strong`        |
| `verification_status`| `not-run-no-rpc`| `not-run-no-rpc` (unchanged) |
| `reproducibility`    | `deterministic-likely-but-unverified` | `deterministic-likely-but-unverified` (unchanged) |
| `notes`              | Phase 5 review note | Phase 6D patch summary referencing the three assertions and the RPC limitation |

`assertion_quality` advances to `strong` because both required families
(F1 attacker profit, F3 invariant break) now have exact assertions, and
F1 is asserted by **exact equality** against the literal exploit
argument — the strongest static proof shape available. No execution
happened, so `verification_status` and `reproducibility` are
**not** promoted.

### `reports/verification/2018-04-bec-token.md`

- Generated section regenerated by
  `scripts/generate_verification_report.py` (reflects the new
  `assertion_quality: strong`).
- Manual section `## Phase 6D Assertion Patch` appended outside the
  generated markers, recording: assertions added, proof target,
  command run, RPC failure mode, that no assertion executed, and the
  remaining archival requirement.

### `reports/poc_quality_matrix.md`

- Re-scored by `scripts/score_pocs.py`. The BEC entry now reflects the
  `assertion_quality: strong` upgrade.

### `docs/internal/PHASE_6D_BEC_ASSERTION_PATCH.md`

- This file (new).

No other files were modified.

---

## 7. Current verified count

**Deterministic-confirmed PoCs: 0** — unchanged.

No PoC has been executed against an archival fork in this phase. The
Phase 6C / 6D patches both compile and are logically correct, but
neither has been runtime-verified. The repository's verification
posture is identical to Phase 6C in this respect.

Phase 6D produces:
- 1 PoC at `assertion_quality: strong` (this PoC, BEC), up from `none`.
- 1 PoC at `assertion_quality: medium` (2017-11 Parity, from Phase 6C).
- 16 PoCs unchanged.

---

## 8. Recommendation for the next one-PoC patch

Per the Phase 6B priority order (sec. 5), the next target is:

**`2020-06-balancer-deflationary` — Bancor public `safeTransferFrom` drain.**

Justification:
- Plan 4.3 specifies exact equality assertions: attacker delta equals
  captured victim pre-balance, and victim post balance equals zero.
- Only `balanceOf` and `allowance` reads are added; no new pranks, no
  changes to the call order, no changes to receivers.
- The transfer amount in the test is already `XBPToken.balanceOf(victim)`
  — the patch only snapshots that value first and reuses it in the
  assertion. Mathematically identical input to the existing call.
- Same archival-RPC limitation applies (block 10307563), so the patch
  will land without runtime execution; a future archival-RPC pass can
  promote it to `verified` in one transcript-only commit.

Phase 6D stops here, per the one-PoC rule. The 6E commit should:
1. Patch only `EVM/test/2020-06/Exploit_2020-06.t.sol`.
2. Update only that PoC's metadata entry and verification report.
3. Run the same validation suite documented in section 3.
4. Record the RPC failure mode if the test cannot execute.

---

## 9. Out of scope for this phase

- Editing any PoC other than `2018-04-bec-token`.
- Editing `EVM/src/`, `EVM/templates/`, `web/`, `SVM/`, `MoveVM/`.
- Marking any PoC `verified`.
- Promoting `reproducibility` to `deterministic-confirmed`.
- Adding live exploitation tooling.
- Configuring or claiming archival RPC.

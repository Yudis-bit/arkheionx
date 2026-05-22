# Phase 6B Plan: Assertion Patch Planning

**Phase:** 6B — Assertion Patch Planning (planning only)
**Branch:** `arkheionx/research-grade-rebuild`
**Latest commit at start:** `d486608 fix(metadata): resolve PoC identity mismatches`
**Maintainer:** Yudistira Putra (arkheionx)
**Date:** 2026-05-22

This phase produces an **assertion-patch design** for the highest-priority
PoCs identified by Phase 5's static review and Phase 6A's metadata-vs-code
reclassification. **No Solidity is edited in this phase.** No tests are
patched. No exploit logic is changed. Nothing is marked verified. The
output is a plan a future Phase 6C can execute one PoC at a time.

---

## 1. Summary

- 5 PoCs were selected for assertion-hardening planning, drawn from the P0
  static-review list and the Phase 6A reclassifications.
- Each plan adds **read-only assertions** (Foundry `assertEq` / `assertGt`
  / `assertGe`) around the existing exploit flow. No `vm.prank`, no extra
  external calls beyond `balanceOf` / `code.length` / `totalSupply` /
  `allowance`, no state mutation.
- Every proposed patch is **additive-only**: it captures pre-state into
  local variables before the attack and asserts the expected delta after.
  None of the proposed patches alters the attack path itself.
- 4 of 5 plans are classified `additive-only but requires archival
  verification` — the assertions themselves cannot produce false negatives,
  but the test cannot **execute** without an archival fork RPC for the
  declared block.
- 1 plan (`2017-11-parity-suicide`) is classified `additive-only and low
  risk` and is the recommended Phase 6C target because the pre-Cancun
  SELFDESTRUCT semantics give a deterministic, exact assertion target with
  zero false-positive surface.
- Deterministic-confirmed count remains **0**. This phase produces no
  verification claims.

---

## 2. Repository State

| Item                                  | Value                                          |
|---------------------------------------|------------------------------------------------|
| Total EVM PoCs                        | 18                                             |
| Verified deterministic                | 0                                              |
| PoCs reviewed in this phase           | 5                                              |
| Solidity files modified in this phase | 0                                              |
| Test files modified in this phase     | 0                                              |
| Metadata mutations in this phase      | 0 (notes-only edits deferred to 6C)            |
| Archival RPC available                | No                                             |
| Phase scope                           | Planning + report-only docs                    |

---

## 3. Selected PoCs

Priority ordering reflects the lowest-risk, highest-signal patch first.

| Rank | id                              | Static quality | Category                       | Patch class                                        |
|------|---------------------------------|----------------|--------------------------------|----------------------------------------------------|
| 1    | 2017-11-parity-suicide          | weak           | access-control-failure         | additive-only and low risk                         |
| 2    | 2018-04-bec-token               | none           | arithmetic-precision-rounding  | additive-only but requires archival verification   |
| 3    | 2020-06-balancer-deflationary   | none           | access-control-failure (Bancor)| additive-only but requires archival verification   |
| 4    | 2020-09-bzx-ifusdc              | weak           | accounting-mismatch (iETH)     | additive-only but requires archival verification   |
| 5    | 2020-12-warp-finance            | weak           | accounting-mismatch (Cover)    | additive-only but requires archival verification   |

Required assertion families per PoC are taken from
`docs/ASSERTION_STANDARD.md` and the per-entry verification report.

---

## 4. Per-PoC Patch Plan

### 4.1 `2017-11-parity-suicide` — Parity WalletLibrary self-destruct

- **File:** `EVM/test/2017-11/Exploit_2017-11.t.sol`
- **Fork block:** `4501735` (mainnet, well pre-Cancun)
- **Family target:** F4 (unauthorized state transition) and F7 (ownership).
- **Current proof weakness:** the only assertion is
  `assertTrue(isowner)` after `initWallet`. The actual destructive step
  (`kill`) has **no** assertion. The test passes even if `kill` reverted
  silently or if `selfdestruct` was a no-op at the fork block.
- **Missing assertion target:** the WalletLibrary **bytecode is cleared**
  by the `kill` call. Pre-Cancun, `SELFDESTRUCT` immediately clears
  `address(...).code` within the transaction; at fork block 4501735 this
  semantics is in force (Cancun activates at block 19426587 on mainnet,
  long after).
- **Proposed assertions (future code, not applied):**

  ```solidity
  // F4 / F7 — proof that the destructive call landed
  uint256 codeLenBefore = address(WalletLibrary).code.length;
  assertGt(codeLenBefore, 0, "WalletLibrary must have code pre-attack");

  WalletLibrary.kill(address(this));

  uint256 codeLenAfter = address(WalletLibrary).code.length;
  assertEq(codeLenAfter, 0, "WalletLibrary bytecode must be cleared");
  ```

- **Where to insert:** wrap the existing `WalletLibrary.kill(...)` call.
  `codeLenBefore` is captured **after** ownership hijack but **before**
  `kill`; `codeLenAfter` is captured immediately after `kill`. The
  existing `assertTrue(isowner)` is preserved.
- **Values compared:** `address(WalletLibrary).code.length` against `0`.
  Both reads are pure observers; neither requires the attacker to hold a
  specific balance, so the assertion is **independent of attacker funds**.
- **Safe without archival RPC?** Assertion is safe in the abstract, but
  the test cannot run at all without an archival mainnet RPC at block
  4501735 (genesis is 8.5 years stale). Public RPC providers prune state
  this old.
- **Requires fork execution?** Yes — historical fork is mandatory.
- **False-positive risk:** zero. A passing assertion proves bytecode was
  cleared, which is a 1:1 fingerprint of `SELFDESTRUCT` executing.
- **Risk of changing exploit behavior:** zero. Two pure reads of
  `code.length` and one extra `assertEq` cannot affect `kill` semantics.
- **Recommended commit message (for Phase 6C):**
  `test(2017-11): assert WalletLibrary bytecode cleared after kill`

---

### 4.2 `2018-04-bec-token` — BEC `batchTransfer` overflow

- **File:** `EVM/test/2018-04/Exploit_2018-04.t.sol`
- **Fork block:** `5483642` (mainnet, pre-0.8 wraparound semantics on
  the deployed BEC contract)
- **Family target:** F1 (attacker profit) and F3 (invariant break).
- **Current proof weakness:** zero assertions. Only `emit
  log_named_decimal_uint` of pre/post balances. The test passes even if
  `batchTransfer` reverted silently or transferred a normal amount.
- **Missing assertion target:** the canonical overflow signature is
  `count * value` wrapping below `2**256`, leaving each receiver with a
  balance equal to the supplied `_value` (`type(uint256).max/2 + 1`).
  The protocol invariant `sum(holders.balanceOf) <= totalSupply` is
  broken because the two attacker balances alone exceed `totalSupply`.
- **Proposed assertions (future code, not applied):**

  ```solidity
  uint256 mintedPerReceiver = type(uint256).max / 2 + 1;

  uint256 a1Before = bec.balanceOf(attacker1);
  uint256 a2Before = bec.balanceOf(attacker2);

  // existing batchTransfer call here (unchanged)

  uint256 a1After = bec.balanceOf(attacker1);
  uint256 a2After = bec.balanceOf(attacker2);

  // F1 — both attackers received the overflowed amount
  assertEq(a1After - a1Before, mintedPerReceiver, "attacker1 mint");
  assertEq(a2After - a2Before, mintedPerReceiver, "attacker2 mint");

  // F3 — sum of attacker holdings alone exceeds totalSupply
  // (canonical overflow fingerprint)
  assertGt(a1After + a2After, IERC20(address(bec)).totalSupply(),
      "supply invariant must be broken");
  ```

  Note: the existing `BECToken` interface in the test does not declare
  `totalSupply`; the patch will add `function totalSupply() external
  view returns (uint256);` to the local interface or reuse `IERC20`
  from `src/interface.sol`.
- **Where to insert:** capture `a1Before` / `a2Before` immediately
  before the existing `bec.batchTransfer(receivers, ...)` line; capture
  `a1After` / `a2After` immediately after. The two `emit log_*` lines
  may be retained.
- **Values compared:** balance deltas vs `type(uint256).max / 2 + 1`;
  combined attacker balance vs `totalSupply()`.
- **Safe without archival RPC?** Test cannot run without archival
  mainnet at block 5483642. The assertions themselves are safe.
- **Requires fork execution?** Yes.
- **False-positive risk:** zero. Equalities against the literal value
  passed to `batchTransfer` are exact.
- **Risk of changing exploit behavior:** zero. Only `balanceOf` reads
  and one `totalSupply` read are added.
- **Recommended commit message (for Phase 6C):**
  `test(2018-04): assert BEC batchTransfer overflow fingerprint`

---

### 4.3 `2020-06-balancer-deflationary` — Bancor public `safeTransferFrom`

- **File:** `EVM/test/2020-06/Exploit_2020-06.t.sol`
- **Fork block:** `10307563` (mainnet)
- **Family target:** F4 (unauthorized state transition) plus F1 (value
  moved). The PoC drains a third-party victim, so attacker profit and
  victim loss are both observable.
- **Current proof weakness:** zero assertions. Only four
  `emit log_named_uint` lines. The test passes even if `safeTransferFrom`
  reverted, transferred zero, or transferred to a different address.
- **Missing assertion target:** the **entirety** of the victim's XBP
  balance must move to the attacker. The only call argument is
  `XBPToken.balanceOf(victim)`, so the post-condition is exact:
  attacker delta equals the captured pre-call victim balance, and the
  victim's post balance is zero.
- **Proposed assertions (future code, not applied):**

  ```solidity
  uint256 victimBefore = XBPToken.balanceOf(victim);
  uint256 attackerBefore = XBPToken.balanceOf(attacker);
  uint256 allowanceBefore = XBPToken.allowance(victim, bancorAddress);

  // F4 precondition: the bug only fires if the public helper has live
  // allowance from the victim. Asserting the precondition makes the
  // exploit fingerprint unambiguous.
  assertGe(allowanceBefore, victimBefore,
      "victim must have approved bancor for at least their balance");

  cheats.prank(address(this));
  bancorContract.safeTransferFrom(
      IERC20(address(XBPToken)), victim, attacker, victimBefore
  );

  uint256 victimAfter = XBPToken.balanceOf(victim);
  uint256 attackerAfter = XBPToken.balanceOf(attacker);

  // F1 — attacker received exactly the victim's pre-attack balance
  assertEq(attackerAfter - attackerBefore, victimBefore,
      "attacker delta must equal victim pre-balance");
  // F2 / loss check — victim drained
  assertEq(victimAfter, 0, "victim XBP must be fully drained");
  ```

- **Where to insert:** snapshot `victimBefore` / `attackerBefore` /
  `allowanceBefore` before the existing `cheats.prank(...)` /
  `bancorContract.safeTransferFrom(...)` lines. Use `victimBefore` as
  the transfer amount instead of re-reading `XBPToken.balanceOf(victim)`
  inline (this also removes a redundant chain read). Existing
  `emit log_named_uint` lines may be retained or replaced.
- **Values compared:** attacker delta vs `victimBefore`; victim post vs
  `0`; allowance vs `victimBefore` (precondition guard).
- **Safe without archival RPC?** Yes for the assertions; no for the
  test as a whole — block 10307563 is archival-only.
- **Requires fork execution?** Yes.
- **False-positive risk:** zero. Each comparison is an exact equality
  against a captured pre-state value.
- **Risk of changing exploit behavior:** zero. The transfer amount
  (`victimBefore`) is mathematically identical to the current inline
  expression `XBPToken.balanceOf(victim)`, just snapshotted first.
- **Recommended commit message (for Phase 6C):**
  `test(2020-06): assert Bancor safeTransferFrom drains victim XBP`

---

### 4.4 `2020-09-bzx-ifusdc` — bZx iETH self-transfer double-write

- **File:** `EVM/test/2020-09/Exploit_2020-09.t.sol`
- **Fork block:** `10852715` (mainnet, one block before the historical
  attack tx at 10852716)
- **Family target:** F6 (accounting mismatch) plus F1 (value moved).
- **Current proof weakness:** the only signal is the inherited
  `balanceLog` modifier emitting an attacker ETH balance line. There is
  no assertion that the attacker's iETH balance actually doubled, and
  no assertion that `burnToEther` returned more ETH than was deposited
  via `mintWithEther`. The test passes if `transfer(self, balance)`
  is silently a no-op, which is the exact case the bug is supposed to
  exploit.
- **Missing assertion target:** after each `transfer(self, balance)`
  iteration, the attacker's iETH balance should have **doubled**
  (canonical fingerprint of the double-write bug). After 4 iterations,
  the iETH balance is `mintAmount * 2**4 = 16 * mintAmount`. The final
  ETH-redeemed amount must exceed the initial `200 ether` deposit by an
  attack-profit margin.
- **Proposed assertions (future code, not applied):**

  ```solidity
  uint256 ethBefore = address(this).balance;
  uint256 mintAmount = loanToken.mintWithEther{value: 200 ether}(address(this));

  uint256 expected = mintAmount;
  for (int256 i = 0; i < 4; i++) {
      uint256 balance = loanToken.balanceOf(address(this));
      assertEq(balance, expected,
          "iETH balance must equal expected pre-doubling value");
      loanToken.transfer(address(this), balance);
      expected = expected * 2; // F6 — double-write fingerprint
  }
  uint256 finalIETH = loanToken.balanceOf(address(this));
  assertEq(finalIETH, mintAmount * 16,
      "final iETH must equal 2**4 * mintAmount");

  uint256 redeemed = loanToken.burnToEther(address(this), finalIETH);

  // F1 — attacker redeemed strictly more than the simulated flash-loan
  // principal (200 ether). The exact margin depends on iETH NAV at the
  // fork block; only a strict inequality is safe to assert.
  assertGt(redeemed, 200 ether,
      "burnToEther must return more than the 200 ether principal");
  ```

  Note: the existing PoC ends with `payable(address(0x0)).transfer(200
  ether)` to simulate flash-loan repayment, then the `balanceLog`
  modifier prints the attacker's after-balance. The assertion above
  uses `redeemed` (the return value of `burnToEther`) rather than the
  attacker's net ETH balance, because the existing flow burns 200 ETH
  to address(0); using the function return value avoids any dependence
  on whether the burn-to-zero step is preserved.
- **Where to insert:** replace the existing standalone
  `loanToken.mintWithEther{value: 200 ether}(address(this));` call with
  one that captures `mintAmount`. Wrap the existing 4-iteration loop
  with the `expected` invariant. Capture `redeemed` from the existing
  `burnToEther` call (currently discards return value).
- **Values compared:** per-iteration `balanceOf` against doubling
  `expected`; final `balanceOf` against `mintAmount * 16`; `redeemed`
  against `200 ether`.
- **Safe without archival RPC?** Yes for the assertions; no for the
  test as a whole.
- **Requires fork execution?** Yes.
- **False-positive risk:** the per-iteration doubling check is exact
  and zero-FP. The final `assertGt(redeemed, 200 ether)` could pass
  with margin smaller than the historical loss but cannot pass without
  the double-write bug occurring; it is therefore a correct lower
  bound, not a quantitative claim.
- **Risk of changing exploit behavior:** very low. Capturing return
  values from `mintWithEther` and `burnToEther` does not change call
  semantics; the four `transfer` calls are unchanged.
- **Recommended commit message (for Phase 6C):**
  `test(2020-09): assert iETH balance doubles per self-transfer`

---

### 4.5 `2020-12-warp-finance` — Cover Protocol Blacksmith infinite mint

- **File:** `EVM/test/2020-12/Exploit_2020-12.t.sol`
- **Fork block:** `11542309` (mainnet)
- **Family target:** F6 (accounting mismatch) plus F1 (value moved).
- **Current proof weakness:** the only signal is one
  `emit log_named_uint("After claimRewards, Cover Balance", ...)`. The
  test passes if `claimRewards` is a no-op, if it reverted silently, or
  if Cover balance went up by a normal staking-yield amount (which
  would not constitute exploitation).
- **Missing assertion target:** the bug mints **dramatically more**
  COVER than the protocol's per-block emission schedule allows for a
  single-block deposit. The defendable assertion is a strict ordering:
  attacker's COVER balance after `claimRewards` is **non-trivial** and
  **larger than any plausible single-block normal yield** (a hard upper
  bound on normal claim is far below 1 COVER for a one-block stake).
  The exact historical figure (≈ 40M COVER pre-reversal) is an
  archival-fork observation, not a static constant.
- **Proposed assertions (future code, not applied):**

  ```solidity
  address depositor = 0x00007569643bc1709561ec2E86F385Df3759e5DD;
  uint256 coverBefore = Cover.balanceOf(depositor);
  uint256 coverTotalSupplyBefore = Cover.totalSupply();

  cheat.prank(depositor);
  bs.deposit(address(bpt), 15_255_552_810_089_260_015_361);

  cheat.prank(depositor);
  bs.claimRewards(address(bpt));

  uint256 coverAfter = Cover.balanceOf(depositor);
  uint256 coverTotalSupplyAfter = Cover.totalSupply();

  // F1 — depositor received non-trivial COVER from a single-block stake
  // 1e18 = 1 COVER. A normal single-block claim would be far below this.
  assertGt(coverAfter - coverBefore, 1e18,
      "claimRewards must mint > 1 COVER (sanity floor)");

  // F6 — totalSupply rose by exactly the depositor's delta (no other
  // recipient), confirming the mint went through the pool path.
  assertEq(
      coverTotalSupplyAfter - coverTotalSupplyBefore,
      coverAfter - coverBefore,
      "COVER totalSupply delta must equal depositor delta"
  );
  ```

  The `1e18` floor is intentionally conservative; the historical mint
  was many orders of magnitude larger. Any number ≥ 1 COVER is enough
  to disprove "no-op" while remaining safely below any plausible
  legitimate single-block claim.
- **Where to insert:** snapshot `coverBefore` /
  `coverTotalSupplyBefore` immediately before the existing `prank` /
  `deposit` lines; snapshot `coverAfter` / `coverTotalSupplyAfter`
  immediately after the existing `claimRewards` call. The existing
  `emit log_named_uint(...)` lines may be retained.
- **Values compared:** depositor delta vs `1e18`; totalSupply delta vs
  depositor delta.
- **Safe without archival RPC?** Yes for the assertions; no for the
  test as a whole — block 11542309 is archival.
- **Requires fork execution?** Yes.
- **False-positive risk:** low. The `1e18` floor is conservative and
  does not encode a precise loss claim; the totalSupply equality is
  exact and zero-FP.
- **Risk of changing exploit behavior:** zero. Only `balanceOf` and
  `totalSupply` reads are added.
- **Recommended commit message (for Phase 6C):**
  `test(2020-12): assert Cover Blacksmith claimRewards mints non-trivial COVER`

---

## 5. Priority Order for Phase 6C

| Order | id                              | Why this order                                                       |
|-------|---------------------------------|----------------------------------------------------------------------|
| 1st   | 2017-11-parity-suicide          | Smallest patch, exact `code.length == 0` fingerprint, zero false-positive surface, zero behavior risk. |
| 2nd   | 2018-04-bec-token               | Exact equality assertions against literal exploit input; obvious overflow signature. |
| 3rd   | 2020-06-balancer-deflationary   | Exact equality drain assertions; only victim/attacker balance reads added. |
| 4th   | 2020-09-bzx-ifusdc              | Iterative invariant requires capturing return values; slightly more refactor. |
| 5th   | 2020-12-warp-finance            | Conservative threshold rather than exact value; least quantitative claim. |

Phase 6C is recommended to apply **only the first** PoC's patch and run
its full validation suite before proceeding to the next.

---

## 6. Risks

- **Archival RPC dependency.** All five PoCs target archival fork
  blocks. Phase 4A confirmed that public mainnet endpoints prune state
  this old. None of these tests can be executed end-to-end until an
  archival mainnet RPC is configured. **No assertion here is
  independently runnable from public infrastructure.**
- **Identity confidence varies.** 2020-06, 2020-09, and 2020-12 were
  reclassified in Phase 6A. Their root-cause and protocol identity are
  high-confidence, but specific historical figures (loss_usd, attack_tx
  for 2020-12) are intentionally absent from metadata. The proposed
  assertions deliberately do not encode such figures.
- **Drift between proposed snippets and current source.** The snippets
  in section 4 are designed against current `EVM/test/.../*.t.sol`
  contents at commit `d486608`. If exploit logic is later modified
  before Phase 6C runs, snippets must be re-validated against the
  updated test file before patching.
- **No exploit-flow modification.** Every snippet adds only `balanceOf`,
  `code.length`, `totalSupply`, and `allowance` reads, plus
  `assertEq` / `assertGt` / `assertGe` calls. None of them prank a
  different actor, change a transfer amount, change the fork block, or
  reorder external calls.
- **False-positive surface.** Where exact equalities are used, the FP
  surface is zero. Where strict inequalities are used (2020-09
  `redeemed > 200 ether`, 2020-12 `delta > 1e18`), the threshold is
  chosen so the assertion can only pass if the exploit fingerprint is
  present, never as a side effect of an unrelated transaction.

---

## 7. Validation Commands for Phase 6C

After each patch is applied, the following commands must pass before
proceeding to the next PoC:

```sh
git status --short
python3 scripts/validate_metadata.py
python3 scripts/generate_registry.py --check
python3 scripts/score_pocs.py --check
python3 scripts/generate_verification_report.py --check
cd EVM && forge fmt --check
cd EVM && forge build
# Per-PoC test invocation (requires archival RPC):
cd EVM && forge test --match-path "test/<MM-YY>/Exploit_<MM-YY>.t.sol" -vvv
```

Validation policy for Phase 6C:
- A patch is accepted only if `forge build` succeeds and the test file
  in question still compiles on the existing IERC20/ILoanTokenLogicWeth
  interface declarations in `src/interface.sol`.
- A test run is **not required** for the patch to be accepted into the
  branch — the assertions can land before archival RPC is available —
  but `verification_status` and `reproducibility` MUST stay
  `not-run-no-rpc` / `deterministic-likely-but-unverified` until the
  test actually executes against an archival fork.

---

## 8. Recommended Next Phase

**Phase 6C — Apply additive assertion patch to exactly one PoC.**

Recommended target: `2017-11-parity-suicide`. Justification:

- Lowest blast radius — two `code.length` reads and one `assertEq`.
- Pre-Cancun fork block guarantees `SELFDESTRUCT` clears bytecode in
  the same transaction, making the assertion deterministic and exact.
- Existing test already has one `assertTrue(isowner)` line, so the
  shape of an asserting test is familiar to readers.
- Failure of the patch (compile error, test won't build) is contained
  to a single 36-line file and can be reverted cleanly.

Phase 6C should land its patch, run the validation suite in section 7,
and stop. Subsequent PoCs (rank 2 through 5 in section 5) are deferred
to later sub-phases (6D, 6E, ...), one per phase, so each lands as a
small, reviewable, independently revertible commit.

After all five priority PoCs are patched, Phase 7 should re-run the
Phase 5 static review on the patched files to confirm
`assertion_quality` advances from `none` / `weak` to `strong` for the
patched entries.

---

## 9. Out of Scope for This Phase

- Editing any file under `EVM/src/`, `EVM/test/`, or `EVM/templates/`.
- Editing `web/`, `SVM/`, or `MoveVM/`.
- Modifying `metadata/registry.json` (notes-field updates that describe
  the planned patches are deferred to Phase 6C, where they ship in the
  same commit as each patch).
- Marking any PoC `verified` or upgrading any `reproducibility` field.
- Running any test (no archival RPC is configured).

---

## 10. Sign-off

This plan is read-only with respect to the exploit corpus. Applying any
snippet from section 4 belongs to a future Phase 6C/6D/6E commit and
must follow the validation policy in section 7. The repository's
deterministic-confirmed count remains **0** at the end of this phase.

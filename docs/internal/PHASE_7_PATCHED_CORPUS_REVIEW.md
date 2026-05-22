# Phase 7: Patched Corpus Re-Review and Next-Tier Prioritization

**Phase:** 7 — Patched corpus re-review (planning only)
**Branch:** `arkheionx/research-grade-rebuild`
**Latest commit at start:** `a4e6e9b test(evm): assert Cover Blacksmith mint impact`
**Maintainer:** Yudistira Putra (arkheionx)
**Date:** 2026-05-22

This phase is **review and planning only**. No Solidity is edited, no
tests are patched, no PoC is added or removed, nothing is marked
verified. The output is a written re-review of the corpus after the
Phase 6C–6G assertion-patch batch and a prioritized queue for the next
single-PoC patch phase (Phase 7B, not started here).

---

## 1. Summary

- The Phase 6C–6G batch landed five additive-only assertion patches
  without changing any exploit flow. All 18 PoCs still build and
  `forge fmt --check` is clean.
- Static `assertion_quality` distribution moved from `weak`-dominant to
  a more balanced split: **5 strong / 3 medium / 10 weak / 0 none /
  0 unknown** (was, at end of Phase 5: 1 strong / 3 medium / 11 weak /
  3 none, before any reclassification).
- Deterministic-confirmed PoCs remains **0**. No Phase 6 patch was
  executed end-to-end because the public RPC is not archival; assertion
  hardening was justified for static-review value only.
- Five next-tier candidates were selected for Phase 7B onward, ordered
  by patch risk (lowest first). One of them (`2025-11-moonwell`) is the
  only PoC currently runnable end-to-end on public infrastructure.
- Six PoCs are explicitly deferred (no-patch-yet queue) for documented
  reasons such as unresolved identity mismatch, exploit-flow rebase
  helpers that mask balance changes, or large external-interface
  surface area that exceeds Phase-7B's "single-PoC, low-risk" bar.

---

## 2. Repository State at Start of Phase 7

| Item                                       | Value                                          |
|--------------------------------------------|------------------------------------------------|
| Total EVM PoCs                             | 18                                             |
| Verified deterministic                     | 0                                              |
| Files modified in this phase               | docs/internal/PHASE_7_PATCHED_CORPUS_REVIEW.md only |
| Solidity changed                           | None                                           |
| Test files changed                         | None                                           |
| Metadata changed                           | None                                           |
| Web changed                                | None (out of scope)                            |
| Archival mainnet RPC available             | No                                             |
| Public Base RPC archival enough for 2025-11| Yes (Phase 4A confirmed)                       |

Pre-flight commands at start of phase:

```text
git status --short                                  : clean
git log --oneline -14                               : 14 commits, latest a4e6e9b
python3 scripts/validate_metadata.py                : ok: 18 entries valid
python3 scripts/generate_registry.py --check        : ok: 18 entries
python3 scripts/score_pocs.py --check               : ok: matrix unchanged (18 entries)
python3 scripts/generate_verification_report.py --check : ok: 18 entries processed, 0 changed
forge build                                         : success (lint warnings only)
forge fmt --check                                   : clean
```

`forge build` reports two pre-existing `erc20-unchecked-transfer` lint
warnings on `EVM/test/2020-09/Exploit_2020-09.t.sol:42` and
`EVM/test/2022-02/Exploit_2022-02.t.sol:45`. These are warnings, not
errors; they pre-date Phase 7 and are noted for future polish only.

---

## 3. Assertion-Quality Distribution

### 3.1 Current distribution (post-Phase 6G)

| assertion_quality | Count | PoCs |
|-------------------|-------|------|
| strong            | 5     | 2017-07-parity-multisig, 2018-04-bec-token, 2020-06-balancer-deflationary, 2020-09-bzx-ifusdc, 2020-12-warp-finance |
| medium            | 3     | 2017-11-parity-suicide, 2021-02-yearn-v1-dai, 2025-11-moonwell |
| weak              | 10    | 2018-10-spankchain, 2020-04-uniswap-imbtc, 2020-08-opyn, 2020-10-harvest, 2020-11-cheese-bank, 2021-01-saddle, 2021-03-dodo-crowdpool, 2021-10-indexed-finance, 2022-02-dexible, 2025-12-yeth |
| none              | 0     | —    |
| unknown           | 0     | —    |

### 3.2 Phase 5 baseline vs. now

| assertion_quality | Phase 5 baseline | Post-Phase 6G | Delta |
|-------------------|------------------|---------------|-------|
| strong            | 1                | 5             | +4    |
| medium            | 3                | 3             | 0     |
| weak              | 11               | 10            | -1    |
| none              | 3                | 0             | -3    |
| unknown           | 0                | 0             | 0     |

Per-PoC movement during Phase 6:

| PoC                            | Phase 5 | Post-Phase 6 | Phase that moved it          |
|--------------------------------|---------|--------------|------------------------------|
| 2017-11-parity-suicide         | weak    | medium*      | 6C (code.length fingerprint) |
| 2018-04-bec-token              | none    | strong       | 6D (overflow fingerprint)    |
| 2020-06-balancer-deflationary  | none    | strong       | 6E (drain equality)          |
| 2020-09-bzx-ifusdc             | weak    | strong       | 6F (per-iteration doubling)  |
| 2020-12-warp-finance           | weak    | strong       | 6G (mint floor + supply eq.) |

*`2017-11-parity-suicide` is recorded as `medium` in
`metadata/registry.json` even though the assertions added in Phase 6C
(`assertGt(codeLenBefore, 0)` plus `assertEq(codeLenAfter, 0)`) are an
exact 1:1 fingerprint of the destructive state transition. The
`scripts/score_pocs.py` matrix already credits it 20/20 in the
`Assert` column. Phase 7 leaves this label at `medium` to stay
conservative — see §6.4 for the documented rationale and recommended
sync direction.

### 3.3 PoCs that improved during Phase 6

5 of 18 PoCs hardened: 2017-11, 2018-04, 2020-06, 2020-09, 2020-12.

### 3.4 PoCs that remain weak (10)

Detailed in §4. None are `none` anymore — every PoC now has either an
inherited balance log only (still scored as weak) or substantive
assertion structure.

### 3.5 PoCs that still only log values

The following PoCs still rely on `console.log` or `emit
log_named_uint` for proof. They are scored `weak`:

- 2018-10-spankchain
- 2020-04-uniswap-imbtc (also identity-mismatch — see §6.1)
- 2020-08-opyn
- 2020-10-harvest
- 2020-11-cheese-bank (Pickle, post-reclassification)
- 2021-01-saddle (SushiMaker, post-reclassification)
- 2021-03-dodo-crowdpool
- 2021-10-indexed-finance
- 2022-02-dexible (BUILD, post-reclassification)
- 2025-12-yeth

### 3.6 PoCs with assertions but lacking victim/invariant proof

- 2025-11-moonwell — single `assertGt(wethAfter, wethBefore)`. Missing
  F2 (victim Moonwell market reserves) and F5 (Chainlink oracle
  staleness vs. heartbeat).
- 2021-02-yearn-v1-dai — two `require(...)` lines on DAI/USDC parity
  give partial F1, but no `assertGt` on `crv3` / `usdt` profit and no
  F2 against yvDAI total assets.

---

## 4. Full Corpus Re-Review Table

For each PoC: current `assertion_quality`, what proof is already
present in the test, the remaining proof gap, a Phase 7B priority
band, and the recommended next action. This table is the source of
truth for the next-tier selection in §5.

Priority bands:
- **P0** — selected for Phase 7B (next-tier patch queue, §5)
- **P1** — defer until P0 batch lands; clear proof target, low risk
- **P2** — defer; identity, root cause, or interface complexity blocks
  a small additive patch right now (no-patch-yet queue, §6)
- **REF** — strong-template reference; no further patching needed

| PoC                            | Current quality | Proof already present                                               | Remaining proof gap                                                                                          | Priority | Recommended next action                                                  |
|--------------------------------|-----------------|---------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------|----------|--------------------------------------------------------------------------|
| 2017-07-parity-multisig        | strong          | 4 assertions covering F1, F2, F4, F7                                | None static; archival fork run still pending                                                                 | REF      | Hold as canonical template; archival fork verification only              |
| 2017-11-parity-suicide         | medium          | F4/F7 fingerprint via `code.length` pre/post `kill`                 | None static; metadata `assertion_quality` undersells current state                                           | REF      | Phase 7C: bump `assertion_quality` to strong on metadata-only commit     |
| 2018-04-bec-token              | strong          | F1 deltas equal `type(uint256).max/2+1`; F3 `sum > totalSupply`     | None static; archival fork run still pending                                                                 | REF      | No further static patch; archival fork verification only                 |
| 2018-10-spankchain             | weak            | Inherited `balanceLog` modifier only                                | F1 attacker pre-burn ETH delta; F2 hub balance drop; the `transfer(0,5 ether)` post-burn hides true profit   | P1       | Phase 7C: assert hub balance fell, attacker net (pre-burn) > 5 ether     |
| 2020-04-uniswap-imbtc          | weak            | `emit log_named_uint` only                                          | Identity mismatch — PoC targets Lendf.Me, not Uniswap V1 imBTC; defer until reclassification or rename       | P2       | Hold; needs identity decision before any assertion patch                 |
| 2020-06-balancer-deflationary  | strong          | Allowance precondition; victim==0 and attacker delta==victim_before | None static; archival fork run still pending                                                                 | REF      | No further static patch; archival fork verification only                 |
| 2020-08-opyn                   | weak            | `console.log` only                                                  | F1 attacker USDC delta; F2 second vault collateral drop; clean equality if only the two cited vaults change  | P0 #4    | Phase 7B candidate — see §5.4                                            |
| 2020-09-bzx-ifusdc             | strong          | Per-iteration doubling; final `mintAmount * 16`; redeemed > 200 ether | None static; archival fork run still pending                                                                | REF      | No further static patch; archival fork verification only                 |
| 2020-10-harvest                | weak            | `emit log_named_uint` only                                          | F1 attacker stable delta; F2 fUSDC vault underlying drop; large external interface (Curve Y-pool, Harvest)   | P2       | Hold; interface surface area exceeds Phase-7B "small additive" bar       |
| 2020-11-cheese-bank            | weak            | `emit log_named_decimal_uint`, `console.log`                        | F1 `tx.origin` cDAI delta; F2 pDAI strategy DAI/cDAI drop; PoC drains to `tx.origin`, not `address(this)`    | P0 #5    | Phase 7B candidate — see §5.5                                            |
| 2020-12-warp-finance           | strong          | F1 `> 1e18` floor; F6 `totalSupply` delta == depositor delta        | None static; archival fork run still pending                                                                 | REF      | No further static patch; archival fork verification only                 |
| 2021-01-saddle                 | weak            | `console.log` only                                                  | F1 attacker WETH delta vs `0.001 ether` seed; F2 SushiMaker WBTC fee balance drop                            | P0 #3    | Phase 7B candidate — see §5.3                                            |
| 2021-02-yearn-v1-dai           | medium          | Two `require()` on DAI/USDC parity (partial F1)                     | `assertGt(crv3 / usdt)` for profit; F2 yvDAI underlying drop                                                 | P1       | Phase 7C: tighten existing requires + add yvDAI snapshot                 |
| 2021-03-dodo-crowdpool         | weak            | `emit log_named_uint` only                                          | F4 DVM `_BASE_TOKEN_` / `_QUOTE_TOKEN_` flipped to attacker tokens; F1 wCRES + USDT > 0                      | P0 #2    | Phase 7B candidate — see §5.2                                            |
| 2021-10-indexed-finance        | weak            | `console.log` only                                                  | F1 strict `assertGt` on at least one borrowed-token balance vs pre; F2 DEFI5 pool reserves drop              | P2       | Hold; pool-internal `getBalance` reads exist but multi-token assertion surface large |
| 2022-02-dexible                | weak            | `emit log_named_uint` only                                          | F4 BUILD allowance from BuildGovernance to attacker == max post-execute; F1/F2 BuildGovernance balance == 0  | P0 #1    | Phase 7B candidate — see §5.1                                            |
| 2025-11-moonwell               | medium          | F1 `assertGt(wethAfter, wethBefore)`                                | F2 Moonwell `mwstEth` cash drop; F5 Chainlink staleness vs heartbeat                                         | P1       | Phase 7C: easy to land because public Base RPC works (Phase 4A pass)     |
| 2025-12-yeth                   | weak            | `console.log(vb_prod_sum)` + inherited `balanceLog`                 | F2 pool asset reserves ≈ dust post-drain; F1 attacker holdings > pre, captured **before** the `_takeInitialsBack` rebase | P2       | Hold; `_takeInitialsBack` rebases via `deal()` which can mask profit     |

---

## 5. Next-Tier Patch Queue (Phase 7B onward)

Five P0 candidates, ordered lowest patch risk first. The intent is the
same one-PoC-per-phase cadence used in 6C–6G: Phase 7B applies only
the first candidate's patch and runs the full validation suite before
the next sub-phase.

For each candidate the snippet below is **planning, not code to apply
in this phase**. Snippets are designed against the current
`EVM/test/<MM-YY>/Exploit_<MM-YY>.t.sol` contents at commit
`a4e6e9b`; if exploit logic changes before Phase 7B runs, the snippet
must be re-validated against the updated test file.

### 5.1 P0 #1 — `2022-02-dexible` (BUILD Finance governance takeover)

- **Why selected:** post-Phase 6A reclassification the protocol identity
  is high-confidence (BuildGovernance + BUILD token). The exploit's
  proof target is exact: after `execute(8, ...)` the BUILD token's
  allowance from BuildGovernance to attacker EOA must equal `max`
  (`type(uint256).max`), and after the final `transferFrom` the
  governance contract's BUILD balance must be zero.
- **Exact proof target:**
  - F4: `BUILD.allowance(address(BuildGovernance), 0xb4c79dab8f...)`
    equals `type(uint256).max` immediately after `execute(...)`.
  - F1/F2: `BUILD.balanceOf(address(BuildGovernance))` equals zero
    immediately after `transferFrom(...)`.
- **Likely assertion type:** two `assertEq` (max allowance, zero
  victim balance), one `assertGt` for attacker delta floor.
- **Additive-only?** Yes. Captures three pre-state values into locals
  (`govBalanceBefore`, `attackerBefore`, `proposalCountBefore`) and
  asserts post-state equalities. No `prank`, no `warp`, no extra
  external calls beyond `balanceOf` and `allowance`.
- **Risk level:** low. The attacker EOA is a hex literal in the
  existing call, so the allowance read is unambiguous.
- **Archival RPC required?** Yes (mainnet block 14235712). Public
  mainnet RPC is not archival; assertions still land in branch as
  static-quality improvement.
- **Recommended phase name:** Phase 7B
- **Suggested commit message:**
  `test(2022-02): assert BUILD governance treasury fully drained`

### 5.2 P0 #2 — `2021-03-dodo-crowdpool` (DVM re-init)

- **Why selected:** the bug fingerprint is exact and observable through
  two read-only DVM accessors (`_BASE_TOKEN_()` and `_QUOTE_TOKEN_()`).
  The current PoC re-inits with attacker-controlled `token1`/`token2`
  addresses already declared as constants at the top of the file, so
  pre/post equality assertions are direct comparisons against those
  literals.
- **Exact proof target:**
  - F4: `dvm._BASE_TOKEN_()` equals `token1` after `dvm.init(...)`.
  - F4: `dvm._QUOTE_TOKEN_()` equals `token2` after `dvm.init(...)`.
  - F1: `wCRES_token.balanceOf(mywallet) > 0` and
    `usdt_token.balanceOf(mywallet) > 0` after the two transfers.
- **Likely assertion type:** two `assertEq` for token-rebind
  fingerprint, two `assertGt` for attacker holdings.
- **Additive-only?** Yes. The DVM accessor reads do not exist in the
  current PoC's `DVM` interface — Phase 7B must add `function
  _BASE_TOKEN_() external view returns (address);` and `function
  _QUOTE_TOKEN_() external view returns (address);` to the local
  interface declaration. This is interface-only (no state mutation).
- **Risk level:** low. Adding two `view` accessors to the existing
  `DVM` interface declaration is mechanical; if the deployed DVM does
  not expose those names at this fork block (they may be storage-slot
  reads), Phase 7B must verify naming against the deployed contract
  before patching.
- **Archival RPC required?** Yes (mainnet block 12000000).
- **Recommended phase name:** Phase 7C
- **Suggested commit message:**
  `test(2021-03): assert DVM re-initialized with attacker tokens`

### 5.3 P0 #3 — `2021-01-saddle` (SushiMaker missing-bridge convert)

- **Why selected:** post-Phase 6A reclassification the protocol identity
  is SushiMaker, not Saddle Finance. The PoC seeds with `0.001 ether`
  WETH and ends with `IERC20(WETH).balanceOf(address(this))` shown via
  `console.log`. F1 reduces to a strict inequality against the seed.
- **Exact proof target:**
  - F1: `WETH.balanceOf(address(this))` after `rugPull()` strictly
    greater than the `0.001 ether` seed.
  - F2: `wbtc.balanceOf(address(sushiMaker))` for the DIGG/WBTC pair
    after `convert(...)` strictly less than its pre-convert value.
- **Likely assertion type:** one `assertGt` (attacker WETH > seed),
  one `assertLt` (SushiMaker WBTC fee balance fell).
- **Additive-only?** Yes. Pre-state snapshot is one `WBTC.balanceOf`
  read before `convert(...)`; post-state is two reads after
  `rugPull()`. No flow change.
- **Risk level:** low. WBTC is already declared as
  `wethBridgeToken = 0x2260FAC5...`. The only addition is a
  `WBTC.balanceOf(sushiMaker)` snapshot before/after the convert call.
- **Archival RPC required?** Yes (mainnet block 11720049).
- **Recommended phase name:** Phase 7D
- **Suggested commit message:**
  `test(2021-01): assert SushiMaker WBTC fee drained via fake bridge`

### 5.4 P0 #4 — `2020-08-opyn` (duplicate ETH option exercise)

- **Why selected:** the exploit calls `opyn.exercise{value: 30 ether}`
  with two vaults — the attacker's own vault plus a third party's
  (`0x01BDb7Ada61C82E951b9eD9F0d312DC9Af0ba0f2`). The second vault's
  collateral fall is a clean F2 victim signal, and attacker USDC
  delta is already computed via `balAfter - balBefore` (currently only
  printed).
- **Exact proof target:**
  - F1: attacker USDC delta from `balAfter - balBefore` is strictly
    positive.
  - F2: USDC collateral attributable to vault
    `0x01BDb7Ada61C82E951b9eD9F0d312DC9Af0ba0f2` falls between
    pre-`exercise` and post-`exercise`.
- **Likely assertion type:** one `assertGt` for attacker delta,
  one `assertLt` for second-vault collateral.
- **Additive-only?** Yes if the second-vault collateral is readable
  through a public Opyn view function (e.g., `getVault(...)` or
  `vaults(...)`). Phase 7C must confirm the accessor name from the
  deployed Opyn v1 oToken before adding it to the local `IOpyn`
  interface.
- **Risk level:** low-to-medium. F1 (`assertGt(balAfter, balBefore)`)
  is trivially additive. F2 depends on resolving the Opyn vault
  accessor — if the accessor is non-trivial, Phase 7C may land F1
  alone and defer F2 to a later sub-phase.
- **Archival RPC required?** Yes (mainnet block 10592516).
- **Recommended phase name:** Phase 7E
- **Suggested commit message:**
  `test(2020-08): assert Opyn duplicate-exercise drains second vault`

### 5.5 P0 #5 — `2020-11-cheese-bank` (Pickle ControllerV4 swapExactJarForJar)

- **Why selected:** post-Phase 6A the identity is Pickle Finance, not
  Cheese Bank. The PoC's emit statements show attacker `cDAI` balance
  on `address(msg.sender)` (i.e., `tx.origin`) before and after the
  exploit. Phase 7B can lock the F1 invariant down to one `assertGt`
  on the same expression.
- **Exact proof target:**
  - F1: `CDAI.balanceOf(msg.sender)` after `swapExactJarForJar`
    strictly greater than the same value before.
  - F2: `DAI.balanceOf(address(PDAI))` and/or
    `CDAI.balanceOf(STRAT)` strictly less than pre-attack value.
- **Likely assertion type:** one `assertGt` for attacker delta,
  one or two `assertLt` for victim drains.
- **Additive-only?** Yes. The PoC already reads
  `CDAI.balanceOf(address(msg.sender))` and
  `DAI.balanceOf(address(PDAI))` for logging; Phase 7B captures
  these into locals and asserts the inequalities.
- **Risk level:** low. The only nuance is that profit lands on
  `tx.origin`, not `address(this)` — assertions must match.
- **Archival RPC required?** Yes (mainnet block 11303122).
- **Recommended phase name:** Phase 7F
- **Suggested commit message:**
  `test(2020-11): assert Pickle ControllerV4 drains pDAI cDAI position`

---

## 6. No-Patch-Yet Queue

PoCs explicitly deferred from Phase 7B. Each entry names the blocker
that prevents a small, low-risk additive patch right now and the
condition that must change before it can move into a P0 slot.

### 6.1 `2020-04-uniswap-imbtc` — identity mismatch unresolved

- **Blocker:** the PoC source forks block 9899725 and calls
  `IMoneyMarket(0x0eEe3E3828A45f7601D5F54bF49bB01d1A9dF5ea)` —
  Lendf.Me on the historical Uniswap V1 imBTC + Lendf.Me joint
  PeckShield writeup, not Uniswap V1's pool. The id slug, title, and
  metadata still describe the Uniswap V1 imBTC reentrancy path,
  which the test does not exercise.
- **Why this blocks Phase 7B:** any assertion added now would be a
  Lendf.Me-shaped F1/F2, but the registry's `victim_loss_check`,
  `attacker_path`, and `summary` describe a Uniswap-shaped one. A
  patch under those conditions would lock the metadata-vs-code
  mismatch into stronger assertion phrasing.
- **Unblock condition:** decide between rename to `2020-04-lendfme`
  and full reclassification under the existing slug (Phase 6A-style
  metadata-only fix). Either path can land before any assertion patch
  is attempted.

### 6.2 `2020-10-harvest` — large external interface surface

- **Blocker:** the PoC drives the Curve Y-pool (`0x45F783CC...`),
  Harvest fUSDC vault (`0xf0358e8c...`), USDT/USDC, and two Uniswap
  V2 pairs, all through interfaces declared in `src/interface.sol`.
  Adding F2 (fUSDC vault underlying drop) is small in isolation but
  F5 (Curve spot deviation) requires extending the local
  `IcurveYSwap` declaration with a `get_dy_underlying` or balance-
  reading accessor.
- **Why this blocks Phase 7B:** Phase 7B's bar is "single-PoC, low
  risk, additive-only." Reading multiple Curve pool internals to
  prove F5 oracle-deviation is non-trivial; F2 alone is an
  acceptable later phase target but does not cover the price-feed
  half of the exploit.
- **Unblock condition:** scope a future phase to only F1 + F2 (drop
  F5) so the patch fits the additive-only bar.

### 6.3 `2021-10-indexed-finance` — multi-token assertion surface

- **Blocker:** the PoC borrows 6 tokens (UNI, AAVE, COMP, CRV, MKR,
  SNX) via Uniswap V2 / Sushi pairs, drives DEFI5 reweighting, and
  redeems via Sushi. F1 strictly requires asserting at least one of
  the six post-redeem balances exceeds its pre-loan margin; F2
  requires reading DEFI5 internal token reserves. The assertion
  surface is correct but wide (6+ snapshot variables).
- **Why this blocks Phase 7B:** the patch is not technically risky
  but exceeds the "small reviewable diff" budget for the next
  one-PoC phase.
- **Unblock condition:** scope a future phase to a single-token F1
  assertion (e.g., MKR or SUSHI delta) plus one DEFI5 reserve drop
  rather than the full basket.

### 6.4 `2017-11-parity-suicide` — metadata undersells current quality

- **Blocker:** Phase 6C added an exact `code.length` fingerprint
  pre/post `kill`. `scripts/score_pocs.py` already credits the test
  20/20 in the assertion column, but `metadata/registry.json` still
  records `assertion_quality: medium`.
- **Why this blocks Phase 7B:** there is **no Solidity work** to do
  on this PoC right now. The mismatch is a metadata-only correction
  and was deliberately left in `medium` during Phase 6C to avoid
  shipping a quality bump in the same commit as the assertion patch.
- **Unblock condition:** a one-line `assertion_quality: medium →
  strong` metadata bump in a future Phase 7C, with a notes-field
  edit explaining the basis.

### 6.5 `2025-12-yeth` — exploit flow rebases attacker balances

- **Blocker:** the PoC ends with `_takeInitialsBack()`, which uses
  Foundry's `deal()` cheat to rewrite each pool asset balance to
  `current - INITIAL_BALANCE`. This is a bookkeeping subtraction,
  not a real transfer. Any F1 assertion captured **after**
  `_takeInitialsBack` runs will compare a `deal()`-clamped balance,
  not the true post-exploit holding.
- **Why this blocks Phase 7B:** moving the assertion to **before**
  `_takeInitialsBack` is, in principle, a flow change (it must
  break the existing `balanceLog` modifier ordering). The "no
  exploit-flow change" bar Phase 6 enforced does not cleanly cover
  this case.
- **Unblock condition:** explicit user approval to relocate the
  assertion inside `testExploit`, or an alternative invariant —
  e.g., assert each pool asset's `balanceOf(POOL)` is dust **after
  `_executeFinalDrain`** but **before `_takeInitialsBack`** — that
  observes pool state instead of attacker state.

### 6.6 PoCs whose only blocker is archival RPC

Five Phase-6-patched PoCs (2017-11, 2018-04, 2020-06, 2020-09,
2020-12) are statically complete but cannot be executed against
mainnet today because the public RPC pruned state. These do **not**
go in the no-patch-yet queue — they are REF rows in the §4 table —
and are blocked only on archival RPC procurement, which is outside
Phase 7's scope.

---

## 7. Risk Table

| Risk                                                            | Affected items                                  | Severity | Mitigation                                                                                          |
|-----------------------------------------------------------------|-------------------------------------------------|----------|-----------------------------------------------------------------------------------------------------|
| Archival RPC required for end-to-end run                        | All 17 EVM mainnet PoCs                         | High     | Procure archival mainnet RPC; defer verification flag until passing fork run                        |
| Static patch passes statically but exploit logic regressed      | All Phase-6-patched PoCs                        | Medium   | Phase 7B/onward must always re-validate snippet against current test file before applying           |
| Identity mismatch hardened by stronger assertions               | 2020-04-uniswap-imbtc                           | Medium   | Hold in §6.1 until rename or full reclassification lands                                            |
| Metadata `assertion_quality` undersells static state            | 2017-11-parity-suicide                          | Low      | Phase 7C metadata-only correction (§6.4)                                                            |
| Exploit-flow rebase masks profit                                | 2025-12-yeth                                    | Medium   | Hold in §6.5 until invariant target is decided with user                                            |
| Wide multi-token assertion surface exceeds "small diff" budget  | 2020-10-harvest, 2021-10-indexed-finance        | Low      | Scope future phases to single-token F1 + single-pool F2; defer F5                                   |
| Pre-existing `erc20-unchecked-transfer` lint warnings           | 2020-09, 2022-02                                | Low      | Note only; not in Phase 7 scope                                                                     |
| Public RPC drift between phases                                 | 2025-11-moonwell                                | Low      | Re-run smoke test before Phase 7C touches it; current Phase 4A pass may have aged                   |

---

## 8. Validation Policy for Phase 7B and Beyond

After every assertion patch landed in Phase 7B/7C/7D/...:

```sh
git status --short
python3 scripts/validate_metadata.py
python3 scripts/generate_registry.py --check
python3 scripts/score_pocs.py --check
python3 scripts/generate_verification_report.py --check
forge fmt --check
forge build
# Per-PoC test invocation (requires archival RPC for mainnet PoCs):
forge test --match-path "test/<MM-YY>/Exploit_<MM-YY>.t.sol" -vvv
```

Acceptance bar (unchanged from Phase 6C):

- A patch lands only if `forge build` succeeds and `forge fmt --check`
  is clean.
- A test run is **not required** for the patch to be accepted into
  the branch — the assertions can land before archival RPC is
  available — but `verification_status` and `reproducibility` MUST
  stay `not-run-no-rpc` / `deterministic-likely-but-unverified`
  until the test actually executes against an archival fork.
- One PoC per phase. The Phase 6 cadence is the contract.

---

## 9. Recommended Phase 7B

**Phase 7B — Apply additive assertion patch to exactly one selected
next-tier PoC.**

Recommended target: **`2022-02-dexible`** (BUILD Finance governance
takeover).

Justification (in priority order):

1. **Lowest patch risk.** All three assertion targets are reads of
   ERC-20 state (`balanceOf`, `allowance`) on tokens already
   declared in the test file (`build`, `BuildGovernance`). No new
   interface is required.
2. **Exact equality fingerprints.** F4
   (`allowance == type(uint256).max`) and F1/F2
   (`balanceOf(BuildGovernance) == 0`) are equality assertions
   against literal post-conditions, not bounds against unknown
   values. Zero false-positive surface.
3. **Identity is settled.** Phase 6A reclassified this entry from
   "Dexible" to BUILD Finance with high confidence; the protocol,
   victim, and attacker addresses are all hex literals in the
   current test source.
4. **Diff size minimal.** Three locals captured before propose/vote/
   execute, three `assertEq` / `assertGt` after, no flow change.
5. **Symmetric to Phase 6C precedent.** Phase 6C applied the
   smallest, exactness-driven assertion in the batch first; Phase 7B
   applies the same pattern to the next batch.

Expected file diff for Phase 7B:

- `EVM/test/2022-02/Exploit_2022-02.t.sol`: ~10 added lines (3 locals
  before, 3 asserts after, plus optional cleanup of the existing
  `emit log_named_uint` lines).
- `metadata/registry.json` (`2022-02-dexible` entry):
  `assertion_quality: weak → strong`, `notes` extended with Phase 7B
  marker, `tags` extended with `phase-7b-asserted`.
- No other files changed.

Phase 7B should land its patch, run §8 validation suite, and stop.
Subsequent P0 candidates (§5.2 through §5.5) ship as 7C, 7D, 7E, 7F
respectively, one per phase.

---

## 10. Out of Scope for Phase 7

- Editing any file under `EVM/src/`, `EVM/test/`, or `EVM/templates/`.
- Editing `web/`, `SVM/`, or `MoveVM/`.
- Marking any PoC `verified` or upgrading any `reproducibility` field.
- Running any test (no archival RPC is configured).
- Adding new PoCs to the corpus.
- `metadata/registry.json` mutations beyond conservative
  `assertion_quality` / notes corrections justified by already-applied
  Phase 6 patches. (None were required in Phase 7 itself; the
  underselling of `2017-11-parity-suicide` is documented in §6.4 as
  a Phase 7C target.)

---

## 11. Sign-off

This phase produced a written re-review of the patched corpus and a
prioritized queue for the next-tier assertion-hardening batch. No
Solidity, no test code, no metadata, no web file was modified. The
deterministic-confirmed count remains **0**.

The recommended next phase is **Phase 7B** with target
`2022-02-dexible`, per §9.





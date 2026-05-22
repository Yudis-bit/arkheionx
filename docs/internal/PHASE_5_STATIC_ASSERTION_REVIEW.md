# Phase 5 Report: Static Assertion and Root-Cause Hardening

**Phase:** 5 — Static Assertion and Root-Cause Hardening
**Branch:** `arkheionx/research-grade-rebuild`
**Latest commit at start:** `e31da3c docs(verification): add public RPC smoke-test readiness`
**Maintainer:** Yudistira Putra (arkheionx)
**Date:** 2026-05-21

This phase performs a static, line-by-line review of every existing EVM PoC.
No exploit logic is modified; no archival fork tests are run; no web changes
are made. Findings drive metadata hardening, verification-report enrichment,
and a per-PoC action plan for a future Phase 6.

---

## 1. Summary

- 18 EVM PoCs reviewed line-by-line.
- `assertion_quality` is no longer `unknown` for any reviewed PoC.
- 1 PoC has **strong** assertions (`2017-07-parity-multisig`).
- 2 PoCs have **medium** assertions (`2021-02-yearn-v1-dai`, `2025-11-moonwell`).
- 14 PoCs have **weak** assertions (mostly `console.log` / `emit log_*`).
- 1 PoC has **none** (`2018-04-bec-token`).
- 5 PoCs show a **metadata-vs-code mismatch** that must be reconciled before
  any further claim about the entry: 2020-06, 2020-11, 2020-12, 2021-01, 2022-02.
- 1 PoC has a misleading id (`2020-09-bzx-ifusdc` — code targets iETH).
- Repository remains honest: deterministic-confirmed count is **0**.
  Phase 4A's single public-RPC pass (Moonwell) is **not** promoted.

---

## 2. Repository State

| Item                              | Value                                                |
|-----------------------------------|------------------------------------------------------|
| Total EVM PoCs                    | 18                                                   |
| Verified deterministic            | 0                                                    |
| Public-RPC pass (smoke only)      | 1 (`2025-11-moonwell`)                               |
| Public-RPC failed-not-archival    | 2 (`2020-04-uniswap-imbtc`, `2025-12-yeth`)          |
| Archival RPC available            | No                                                   |
| Web stack                         | Out of scope (per Phase 5 brief)                     |
| Static review coverage            | 18 / 18 (100%)                                       |

---

## 3. Commands Run

```sh
git status --short
git log --oneline -5
python3 scripts/validate_metadata.py
python3 scripts/generate_registry.py --check
python3 scripts/score_pocs.py --check
python3 scripts/generate_verification_report.py --check
forge fmt --check     # in EVM/
forge build           # in EVM/
```

All checks passed at start. `generate_registry.py --check` reports
`would update: web/public/metadata.json` — this is a pre-existing artifact
of an older registry → web export and is documented (see Phase 4A report);
it is **not** a Phase 5 regression and is not addressed here because web is
out of scope.

No fork tests were executed. No web commands were executed.

---

## 4. PoC Review Queue

| # | Entry id                       | Category                              | Status      |
|---|--------------------------------|---------------------------------------|-------------|
| 1 | 2017-07-parity-multisig        | access-control-failure                | historical  |
| 2 | 2017-11-parity-suicide         | access-control-failure                | historical  |
| 3 | 2018-04-bec-token              | arithmetic-precision-rounding         | historical  |
| 4 | 2018-10-spankchain             | reentrancy                            | historical  |
| 5 | 2020-04-uniswap-imbtc          | reentrancy                            | historical  |
| 6 | 2020-06-balancer-deflationary  | fee-on-transfer-rebasing-assumption   | historical  |
| 7 | 2020-08-opyn                   | invariant-bypass                      | historical  |
| 8 | 2020-09-bzx-ifusdc             | accounting-mismatch                   | historical  |
| 9 | 2020-10-harvest                | flash-loan-price-manipulation         | historical  |
| 10| 2020-11-cheese-bank            | flash-loan-price-manipulation         | historical  |
| 11| 2020-12-warp-finance           | flash-loan-price-manipulation         | historical  |
| 12| 2021-01-saddle                 | arithmetic-precision-rounding         | incomplete  |
| 13| 2021-02-yearn-v1-dai           | flash-loan-price-manipulation         | historical  |
| 14| 2021-03-dodo-crowdpool         | initialization-bug                    | historical  |
| 15| 2021-10-indexed-finance        | amm-invariant-manipulation            | historical  |
| 16| 2022-02-dexible                | unsafe-external-call                  | historical  |
| 17| 2025-11-moonwell               | oracle-manipulation                   | historical  |
| 18| 2025-12-yeth                   | amm-invariant-manipulation            | historical  |

---

## 5. Static Review — Per PoC

Each entry below summarizes what the PoC actually does in code, the
assertion shape it uses, and the proof gap that prevents promoting it
beyond static review. Severity of recommendation reflects gap size, not
exploit severity.

### 5.1 `2017-07-parity-multisig` — STRONG

- **What it does:** Forks at block 4,043,799. Asserts pre-state balance
  and `isOwner(ATTACKER) == false`. Pranks attacker, calls `initWallet`
  with attacker as sole owner, asserts `isOwner == true`. Calls
  `execute` to move stolen ETH. Asserts post-state wallet balance == 0
  and attacker delta == `STOLEN_AMOUNT`.
- **Assertions present:** `assertEq` pre/post wallet balance,
  `assertFalse`/`assertTrue` ownership transition, `assertEq` attacker
  delta. **All four assertion families (F1, F2, F4, F7) implicitly proven.**
- **Proof strength:** The test would actively fail if any step regressed.
- **Proof gap:** None at static-review level. Final promotion still
  requires archival fork verification.
- **Recommendation:** Keep as the canonical reference template for
  access-control-failure PoCs.

### 5.2 `2017-11-parity-suicide` — WEAK

- **What it does:** Forks at 4,501,735. Calls `initWallet` to claim
  ownership of the shared library, asserts `isOwner == true`, then
  calls `kill`. After `kill`, calls `isOwner` again with no assertion.
- **Assertions present:** Single `assertTrue(isowner)` for the ownership
  hijack (F4/F7).
- **Proof gap:** No assertion that the library is actually destroyed.
  The final `WalletLibrary.isOwner(address(this))` is a discarded read,
  so the test passes even if `kill` reverts silently or the SELFDESTRUCT
  is a no-op.
- **Recommendation:** Capture `address(WalletLibrary).code.length`
  before the kill and assert it > 0; capture again after and assert it
  == 0. (Cancun semantics: SELFDESTRUCT only clears code if the contract
  was created in the same transaction. At the historical fork block
  this was pre-Cancun and code-clearing was the contemporary behavior;
  the assertion is therefore valid for the fork but the comment should
  say so.)

### 5.3 `2018-04-bec-token` — NONE

- **What it does:** Forks at 5,483,642. Logs balances of two attacker
  EOAs, calls `batchTransfer(receivers, type(uint256).max / 2 + 1)`,
  logs balances again. No assertions.
- **Assertions present:** None — only `emit log_named_decimal_uint`.
- **Proof gap:** Test will pass even if `batchTransfer` reverts on the
  fork (catch is silent for `Test`-style logs only when paired with
  expected reverts; here it would actually fail, but more importantly
  there is no positive proof that overflow occurred). No check that the
  resulting balance is mathematically larger than `totalSupply` could
  legitimately allow.
- **Recommendation:** Snapshot `bec.balanceOf(attacker1)` before; assert
  post-balance > pre-balance + `type(uint256).max / 2 + 1` for each
  receiver; assert `bec.totalSupply()` is now smaller than the sum of
  the two receivers' balances (the canonical overflow proof).

### 5.4 `2018-10-spankchain` — WEAK

- **What it does:** Forks at 6,467,247. Funds attacker with 5 ETH (flash
  loan simulation), deploys `SpankChainExploitHelper` whose `transfer`
  function recursively reenters `LCOpenTimeout` 32 times, then sends 5
  ETH to address(0) "to simulate flash loan repayment".
- **Assertions present:** None directly. Only the inherited
  `balanceLog` modifier emits a Before/After log of attacker ETH.
- **Proof gap:** "Send 5 ETH to address(0)" is a *burn*, not a flash
  loan repayment, so the After log understates real attacker balance by
  5 ETH and is misleading. No assertion of victim hub balance delta.
- **Recommendation:** Snapshot SpankChain LedgerChannel ETH balance
  before; assert it strictly decreases by exactly 32 × per-channel
  amount after. Keep, do not burn, the simulated flash-loan ETH; assert
  attacker net = (drained − loan principal − fees) > 0.

### 5.5 `2020-04-uniswap-imbtc` — WEAK

- **What it does:** Forks at 9,899,725. Hijacks the imBTC sender hook,
  pranks attacker to transfer their imBTC to `address(this)`, supplies
  to Lendf.Me, then calls `withdraw(type(uint256).max)` once at top
  level — and inside the `tokensToSend` hook (when `amount == 1`)
  recursively calls `withdraw` again before state updates.
  **Note:** the on-chain incident is universally cited as **Lendf.Me**,
  not Uniswap V1; the PoC's URL header (peckshield "uniswap-lendf-me")
  and the use of an `IMoneyMarket` interface confirm this. The registry
  title is wrong.
- **Assertions present:** None — only `emit log_named_uint` of
  victim/attacker balances.
- **Proof gap:** Test passes even if reentrancy never fires.
- **Recommendation:** Snapshot victim imBTC balance and attacker imBTC
  balance before; assert attacker delta > legitimate single withdraw,
  and victim delta < −(single withdraw); fix metadata title and root
  cause to reflect Lendf.Me.

### 5.6 `2020-06-balancer-deflationary` — WEAK / METADATA MISMATCH (P0)

- **What it does:** Forks at 10,307,563. Pranks `address(this)`, calls
  `Bancor.safeTransferFrom(XBPToken, victim, attacker, victim_balance)`.
  This is the **Bancor public-`safeTransferFrom`** incident from June
  2020 (CVE-class access-control bug in a Bancor router upgrade), not
  Balancer's STA / deflationary-token incident.
- **Assertions present:** None — only logs.
- **Metadata mismatch:** Registry classifies this as
  `fee-on-transfer-rebasing-assumption` ("Balancer deflationary"). The
  code is a totally different incident with different category, root
  cause, and protocol.
- **Recommendation:** Either (a) re-author the test to actually
  demonstrate Balancer's STA drain, or (b) re-classify the entry to
  the Bancor public-`safeTransferFrom` incident with category
  `unsafe-external-call` (router used the public `safeTransferFrom`
  helper that any caller could invoke against active token approvals).
  Phase 5 records this as a P0 blocker.

### 5.7 `2020-08-opyn` — WEAK

- **What it does:** Forks at 10,592,516, pranks the historical attacker
  EOA, mints a put option, then calls `exercise{value: 30 ether}` with
  an array of two vault addresses (the attacker's plus a real victim's),
  followed by `removeUnderlying`. Logs `balBefore`, `balAfter`, profit.
- **Assertions present:** None.
- **Proof gap:** No assertion that profit > 0 or that USDC was actually
  drained from a vault belonging to another user.
- **Recommendation:** Capture victim vault collateral pre/post; assert
  collateral strictly decreases by the duplicated payment amount;
  assert attacker USDC delta > 0.

### 5.8 `2020-09-bzx-ifusdc` (ACTUALLY iETH) — WEAK / ID MISLEADING

- **What it does:** Forks at 10,852,715. Funds attacker with 200 ETH
  (flash loan sim), `mintWithEther` on `loanToken =
  0xB983E01458529665007fF7E0CDdeCDB74B967Eb6` (which is
  `iETH_v2`, not iUSDC), self-transfers 4 times to inflate balance,
  redeems via `burnToEther`, then sends 200 ETH to address(0).
- **Assertions present:** None.
- **Proof gap:** The id and registry root cause say **iUSDC** and
  **219,200 LINK**; the actual code targets **iETH** and the
  contemporary on-chain attack with this exact pattern stole ~4,503 ETH.
  This is a P0 metadata mismatch.
- **Recommendation:** Rename the entry id concept (keep on-disk path,
  but fix `title`, `protocol`, `summary`, `impact`, `attack_tx`,
  `loss_usd`, references); add assertions that attacker ETH net of the
  200 ETH "loan" is strictly positive and that loanToken vault
  underlying decreased.


### 5.9 `2020-10-harvest` — WEAK

- **What it does:** Forks at 11,129,473. Approves Curve Y / Harvest /
  Uniswap pairs; takes a Uniswap V2 USDC flash loan, then nests a USDT
  flash loan; in the inner callback runs 6 rounds of
  `curveYSwap.exchange_underlying(USDT→USDC)` + `harvest.deposit` +
  reverse swap + `harvest.withdraw`. Logs balances; repays both loans.
- **Assertions present:** None. Only `emit log_named_uint` of attacker
  USDC/USDT balances.
- **Proof gap:** No assertion that attacker net (after repay) is
  strictly positive, no assertion against fUSDC vault underlying drift.
- **Recommendation:** Snapshot `fusdc` total backing pre/post; assert
  attacker USDC delta > flash-loan fees; assert fUSDC backing dropped.
  Required families: F1, F2, F5.

### 5.10 `2020-11-cheese-bank` — WEAK / METADATA MISMATCH (P0)

- **What it does:** Forks at **11,303,122** — not 11,205,646 as the
  registry claims. Constructs an exploit that calls
  `Pickle ControllerV4.swapExactJarForJar` (`0x6847259b...`) with fake
  Jar / fake underlying contracts that bypass the controller's
  arbitrary-call-builder logic to drain `pickleJar` (pDAI,
  `0x6949Bb...`) into `cDAI` for `tx.origin`. This is the **Pickle
  Finance cDAI exploit (Nov 21 2020, ~$19.7M)**, not Cheese Bank.
- **Assertions present:** None (just two `emit log_named_decimal_uint`
  on attacker cDAI balance).
- **Metadata mismatch:** Title, protocol, attack tx, root cause, all
  three category-relevant fields, fork block, and loss USD all describe
  Cheese Bank. Code targets Pickle.
- **Recommendation:** Re-classify as `2020-11-pickle-controller`
  (`unsafe-external-call` / `accounting-mismatch`). Assertion plan:
  snapshot pDAI's cDAI holdings pre and assert post == 0; assert
  attacker `tx.origin` cDAI delta > 0.

### 5.11 `2020-12-warp-finance` — WEAK / METADATA MISMATCH (P0)

- **What it does:** Forks at 11,542,309. Pranks
  `0x00007569...` (the on-chain Cover claim attacker) and calls
  `Blacksmith.deposit` with 15.25 BPT, then `claimRewards(BPT)`. Logs
  COVER balance.
- **Assertions present:** None.
- **Metadata mismatch:** Registry calls this Warp Finance LP-oracle
  manipulation. Code is the **Cover Protocol infinite-mint /
  Blacksmith claimRewards** incident (Dec 28 2020). Different protocol,
  category (`vault-strategy-accounting-flaw` /
  `arithmetic-precision-rounding`), attacker, and root cause.
- **Recommendation:** Re-classify entirely. Assertion plan: snapshot
  COVER total supply and attacker COVER balance pre; assert post-claim
  attacker COVER balance is many orders of magnitude higher than the
  reward schedule could justify.

### 5.12 `2021-01-saddle` — WEAK / METADATA MISMATCH (P0)

- **What it does:** Forks at 11,720,049. Creates a fake Sushi DIGG/WETH
  pair, calls `SushiMaker.convert(WBTC, DIGG)` so the maker's bridge
  logic drains its WBTC fee balance via the fake pair, then redeems LP
  for WETH. Logs `WETH.balanceOf / 1e18` as "Attacker's profit".
  This is the **SushiSwap SushiMaker bridge exploit (Jan 26 2021)**.
- **Assertions present:** None.
- **Metadata mismatch:** Registry says Saddle Finance early-deposit
  rounding; code is unrelated to Saddle.
- **Recommendation:** Re-classify as
  `2021-01-sushiswap-sushimaker-bridge` with category
  `unsafe-external-call`. Assertion plan: snapshot SushiMaker WETH
  balance pre, assert it is non-trivial; assert attacker WETH delta > 0
  and equals SushiMaker's pre-balance minus dust.

### 5.13 `2021-02-yearn-v1-dai` — MEDIUM

- **What it does:** Forks at 11,792,183. Pre-funds attacker with DAI +
  USDC; calls Curve `add_liquidity` to imbalance the 3pool, then 5
  rounds of `remove_liquidity_imbalance` + `yvdai.deposit` +
  `yvdai.earn` + `add_liquidity` + `yvdai.withdrawAll`. Closes with
  one `remove_liquidity_imbalance` to restore DAI/USDC and uses two
  hard `require` checks: post-DAI == pre-DAI + 1 and post-USDC ==
  pre-USDC + 1. `writeTokenBalance` rebases attacker so logged 3CRV +
  USDT balances are pure profit.
- **Assertions present:** Two `require` lines that *do* fail the test
  if exploit math drifts. Profit logged but not asserted.
- **Proof gap:** No `assertGt(crv3.balanceOf(...), 0)` or USDT analog;
  no victim-side assertion against `yvdai` underlying.
- **Recommendation:** Add `assertGt(crv3.balanceOf(this), 0)` and
  `assertGt(usdt.balanceOf(this), 0)`; snapshot yvDAI total assets pre
  and assert post < pre.

### 5.14 `2021-03-dodo-crowdpool` — WEAK

- **What it does:** Forks at 12,000,000. Calls `dvm.flashLoan(wCRES,
  USDT, ...)` and in `DVMFlashLoanCall` calls `dvm.init(...)` to
  re-initialize the pool with attacker-controlled tokens, then transfers
  the borrowed wCRES + USDT to `mywallet` (`msg.sender`). Logs balances.
- **Assertions present:** None.
- **Proof gap:** Flash-loan repayment is implicit in DVM — if it
  silently succeeds with stolen state, the test passes even if no
  exploit. No assertion that re-init actually changed reserves to
  attacker-controlled tokens.
- **Recommendation:** Snapshot DVM `_BASE_TOKEN_` and `_QUOTE_TOKEN_`
  pre/post; assert they changed to attacker tokens; assert mywallet
  wCRES + USDT delta > 0.

### 5.15 `2021-10-indexed-finance` — WEAK

- **What it does:** Forks at 13,417,948. Recursively flash-loans 6
  basket tokens from Uni/Sushi pairs; once all 6 are stacked, calls
  `controller.reindexPool(DEFI5)`, swaps token-in for token-out using
  `swapExactAmountIn` until the index is rebalanced into the cheap
  asset, then `controller.updateMinimumBalance` and
  `joinswapExternAmountIn` mint outsized DEFI5; takes a Sushi flash
  loan, calls `gulp(SUSHI)`, exits the index pool, repays. Logs final
  balances.
- **Assertions present:** None.
- **Proof gap:** Test passes if flash-loan repay succeeds, even when
  exploit margin is zero or negative.
- **Recommendation:** Snapshot pre-balances of all 8 tokens; after
  `start()`, assert at least one of (WETH, UNI, AAVE, COMP, CRV, MKR,
  SNX, SUSHI) post-balance > 0 with strict `assertGt` ratio; assert
  DEFI5 underlying basket value dropped vs pre.

### 5.16 `2022-02-dexible` — WEAK / METADATA MISMATCH (P0)

- **What it does:** Forks at 14,235,712. Pranks
  `0x562680a4...` to push 101.5 BUILD into `address(this)`, calls
  `BuildGovernance.propose(BUILD, 0, approve(spender, max))` with a
  hand-crafted approve calldata, votes from a third wallet, warps
  `block.timestamp` to 1655436437 (≈ Jun 17 2022), executes the
  malicious proposal granting attacker `transferFrom` on the
  governance treasury, then drains. This is the **BUILD Finance
  governance takeover (Feb 2022, ~$470k)** — *not* Dexible.
- **Assertions present:** None.
- **Metadata mismatch:** Title, protocol, root cause, attack tx, and
  category all reference Dexible's `selfSwap`. Code is BUILD's
  governance attack.
- **Recommendation:** Re-classify as
  `2022-02-build-finance-governance` with category
  `governance-attack`. Assertion plan: snapshot governance BUILD
  balance pre; assert == 0 post; assert attacker BUILD delta equals
  pre-balance.

### 5.17 `2025-11-moonwell` — MEDIUM

- **What it does:** Forks Base at 37,722,881 (one before attack). Stands
  up an `AttackContract` that takes a wrsETH flash loan from
  `wstETH/wrsETH` Aerodrome CL pool, mints `mwrsETH` against the stale
  collateral price, enters market, borrows wstETH, swaps wstETH→WETH and
  WETH→wrsETH to repay flash loan, then dumps the residual wrsETH. Top-
  level `testExploit()` asserts `assertGt(wethAfter, wethBefore)`.
- **Assertions present:** Single `assertGt` on attacker WETH delta (F1).
- **Proof gap:** No oracle deviation assertion (F5) — the test does not
  capture stale `updatedAt` vs `block.timestamp`. No victim-side
  assertion (F2) against Moonwell market reserves.
- **Recommendation:** Read Chainlink price feed `latestRoundData` pre
  and assert `updatedAt < block.timestamp - heartbeat`; snapshot
  Moonwell `mwstETH` cash pre and assert post < pre by `BORROW_AMOUNT`.

### 5.18 `2025-12-yeth` — WEAK

- **What it does:** Forks at 23,914,085. Uses Foundry `deal` to
  pre-fund attacker with 20,000e18 of each of 8 yETH pool assets (this
  is the "flashloan" simulation). Runs `_initialRateUpdate` on assets
  0–5, then phases 1–8 of `add_liquidity`/`remove_liquidity` with
  carefully tuned amounts plus an `OETH.rebase()` to perturb
  `vb_prod_sum`, ending with `remove_liquidity(POOL.supply())` to
  fully drain. Then `_takeInitialsBack()` rebases attacker back so the
  After log shows pure profit.
- **Assertions present:** None — only `console.log` of vb_prod / vb_sum
  and a `balanceLog` modifier.
- **Proof gap:** No assertion that pool reserves are zero after final
  drain. The "take initials back" step uses `deal` to *adjust* attacker
  balance which can mask whether the exploit actually netted anything.
- **Recommendation:** After final drain, for each of 8 assets assert
  `IERC20(POOL.assets(i)).balanceOf(POOL) <= dust`. Also assert post-
  drain attacker balance > pre-balance for at least one underlying
  asset before the bookkeeping rebase.


---

## 6. Assertion Quality Distribution

| assertion_quality | Count | Entries                                                                 |
|-------------------|-------|-------------------------------------------------------------------------|
| strong            | 1     | 2017-07-parity-multisig                                                 |
| medium            | 2     | 2021-02-yearn-v1-dai, 2025-11-moonwell                                  |
| weak              | 14    | 2017-11, 2018-10, 2020-04, 2020-06, 2020-08, 2020-09, 2020-10, 2020-11, 2020-12, 2021-01, 2021-03, 2021-10, 2022-02, 2025-12 |
| none              | 1     | 2018-04-bec-token                                                       |
| unknown           | 0     | —                                                                       |

## 7. Root-Cause Quality Distribution

Static review compared each `root_cause` field against the actual
exploit logic in the PoC.

| root_cause_quality | Count | Entries                                                                |
|--------------------|-------|------------------------------------------------------------------------|
| strong             | 5     | 2017-07, 2017-11, 2018-04, 2020-04, 2025-11                            |
| medium             | 4     | 2018-10, 2020-08, 2021-02, 2025-12                                     |
| weak               | 4     | 2020-09 (id mismatch), 2020-10, 2021-03, 2021-10                       |
| mismatched         | 5     | 2020-06, 2020-11, 2020-12, 2021-01, 2022-02 (P0 — code != metadata)    |

## 8. Strongest PoCs

1. **2017-07-parity-multisig** — pre/post equality assertions on the
   exact stolen amount; ownership transition checked both directions;
   structurally sound and the cleanest reference template in the repo.
2. **2025-11-moonwell** — single F1 `assertGt`, but the assertion
   actually traces attacker WETH profit through the full exploit path.

## 9. Weakest PoCs

1. **2018-04-bec-token** — zero assertions on a textbook overflow.
2. **2020-06 / 2020-11 / 2020-12 / 2021-01 / 2022-02** — code does not
   match metadata. These cannot be trusted at the static-review stage
   regardless of whether their assertions are weak or strong, because
   the verification report would describe an entirely different attack
   than the test exercises.
3. **2021-03-dodo-crowdpool** — drains via flash-loan callback with no
   assertion that the attacker actually kept funds.
4. **2025-12-yeth** — multi-phase manipulation with `console.log` only
   and a bookkeeping `deal()` that obscures whether profit was real.


---

## 10. Proof Target Matrix

For each PoC the table records which assertion families a research-grade
verification should ultimately include. Filled cells = required; empty =
not applicable. Family keys per `docs/ASSERTION_STANDARD.md`.

| Entry id                       | F1 profit | F2 victim | F3 invariant | F4 unauth | F5 oracle | F6 acct | F7 control | F8 liq | F9 share | callback |
|--------------------------------|:--------:|:---------:|:-----------:|:--------:|:---------:|:-------:|:----------:|:------:|:--------:|:--------:|
| 2017-07-parity-multisig        |    ✔     |     ✔     |             |    ✔     |           |         |     ✔      |        |          |          |
| 2017-11-parity-suicide         |          |     ✔     |             |    ✔     |           |         |     ✔      |        |          |          |
| 2018-04-bec-token              |    ✔     |     ✔     |     ✔       |          |           |    ✔    |            |        |          |          |
| 2018-10-spankchain             |    ✔     |     ✔     |             |          |           |         |            |        |          |    ✔     |
| 2020-04-uniswap-imbtc          |    ✔     |     ✔     |             |          |           |         |            |        |          |    ✔     |
| 2020-06 (Bancor reclassify)    |    ✔     |     ✔     |             |    ✔     |           |         |            |        |          |          |
| 2020-08-opyn                   |    ✔     |     ✔     |     ✔       |          |           |    ✔    |            |        |          |          |
| 2020-09 (iETH retitle)         |    ✔     |     ✔     |             |          |           |    ✔    |            |        |          |          |
| 2020-10-harvest                |    ✔     |     ✔     |             |          |     ✔     |         |            |        |    ✔     |          |
| 2020-11 (Pickle reclassify)    |    ✔     |     ✔     |             |    ✔     |           |    ✔    |            |        |          |          |
| 2020-12 (Cover reclassify)     |    ✔     |     ✔     |     ✔       |          |           |    ✔    |            |        |          |          |
| 2021-01 (Sushi reclassify)     |    ✔     |     ✔     |             |    ✔     |           |         |            |        |          |          |
| 2021-02-yearn-v1-dai           |    ✔     |     ✔     |             |          |     ✔     |         |            |        |    ✔     |          |
| 2021-03-dodo-crowdpool         |    ✔     |     ✔     |             |    ✔     |           |         |            |        |          |          |
| 2021-10-indexed-finance        |    ✔     |     ✔     |     ✔       |          |           |         |            |        |          |          |
| 2022-02 (BUILD reclassify)     |    ✔     |     ✔     |             |          |           |         |     ✔      |        |          |          |
| 2025-11-moonwell               |    ✔     |     ✔     |             |          |     ✔     |         |            |        |          |          |
| 2025-12-yeth                   |    ✔     |     ✔     |     ✔       |          |           |    ✔    |            |        |          |          |


---

## 11. Per-PoC Action Plan (P0 / P1 / P2 / P3)

Priority key:
- **P0** — misleading or likely broken; cannot be promoted at all until reconciled.
- **P1** — compiles, but proof is weak enough that test could pass without proving exploit.
- **P2** — adequate but missing a victim/invariant assertion.
- **P3** — acceptable static quality; only archival fork verification remains.

| # | Entry id                       | Now (assert / RC) | Missing proof                               | Future code change             | RPC required | Risk  | Priority |
|---|--------------------------------|-------------------|---------------------------------------------|--------------------------------|--------------|-------|----------|
| 1 | 2017-07-parity-multisig        | strong / strong   | none (template)                             | none                           | yes (final)  | low   | P3       |
| 2 | 2017-11-parity-suicide         | weak / strong     | code-length collapse post-suicide           | add F2 / F4 assertions         | yes (final)  | low   | P1       |
| 3 | 2018-04-bec-token              | none / strong     | balance > MAX_INT/2; supply invariant       | add F1 / F3 assertions         | yes (final)  | low   | P0       |
| 4 | 2018-10-spankchain             | weak / medium     | victim hub balance delta                    | add F2; remove `transfer(0)`   | yes (final)  | low   | P1       |
| 5 | 2020-04-uniswap-imbtc          | weak / strong     | F1, F2; metadata title (Lendf.Me)           | add F1 / F2; fix metadata      | yes (final)  | low   | P1       |
| 6 | 2020-06-balancer-deflationary  | weak / mismatched | category, root cause, summary               | reclassify entry               | n/a yet      | med   | P0       |
| 7 | 2020-08-opyn                   | weak / medium     | F1, F2 against vault                        | add F1 / F2                    | yes (final)  | low   | P1       |
| 8 | 2020-09-bzx-ifusdc             | weak / weak       | id is wrong (iETH not iUSDC); F1, F2        | rename / fix metadata; F1 / F2 | yes (final)  | med   | P0       |
| 9 | 2020-10-harvest                | weak / weak       | F1 strict, F2 fUSDC backing, F5 oracle      | add F1 / F2 / F5               | yes (final)  | low   | P1       |
| 10| 2020-11-cheese-bank            | weak / mismatched | code is Pickle Controller, not Cheese Bank  | reclassify entry               | n/a yet      | high  | P0       |
| 11| 2020-12-warp-finance           | weak / mismatched | code is Cover, not Warp                     | reclassify entry               | n/a yet      | high  | P0       |
| 12| 2021-01-saddle                 | weak / mismatched | code is SushiMaker, not Saddle              | reclassify entry               | n/a yet      | high  | P0       |
| 13| 2021-02-yearn-v1-dai           | medium / medium   | F1 strict assertion; F2 vault delta         | add F1 / F2                    | yes (final)  | low   | P2       |
| 14| 2021-03-dodo-crowdpool         | weak / weak       | F1, F4 token rebind                         | add F1 / F4                    | yes (final)  | low   | P1       |
| 15| 2021-10-indexed-finance        | weak / weak       | F1 strict, F3 basket valuation              | add F1 / F3                    | yes (final)  | low   | P1       |
| 16| 2022-02-dexible                | weak / mismatched | code is BUILD governance, not Dexible       | reclassify entry               | n/a yet      | high  | P0       |
| 17| 2025-11-moonwell               | medium / strong   | F2 vs market; F5 oracle deviation           | add F2 / F5                    | yes (final)  | low   | P2       |
| 18| 2025-12-yeth                   | weak / medium     | F2 pool drain assertion; F1 strict          | add F1 / F2 / F3               | yes (final)  | med   | P1       |

---

## 12. Metadata Updates Applied This Phase

Conservative, code-supported metadata updates:

- **All 18 entries:** `assertion_quality` set from `unknown` to one of
  `strong | medium | weak | none` based on the static review above.
- **2017-07-parity-multisig:** add `audit_lesson` and `tags` reinforcing
  template status.
- **2017-11-parity-suicide:** tighten `notes` to record missing
  code-length post-suicide check.
- **2018-04-bec-token:** tighten `notes` to record missing supply
  invariant assertion.
- **2018-10-spankchain:** `notes` to record misleading
  `transfer(address(0))` flash-loan simulation.
- **2020-04-uniswap-imbtc:** `notes` flag the title-vs-incident
  ambiguity (PoC targets Lendf.Me; Uniswap V1 imBTC was a separate
  earlier incident at the same fork era — title kept for now to avoid
  cascading id rename, but `notes` records the static-review finding).
- **2020-06 / 2020-11 / 2020-12 / 2021-01 / 2022-02:** `notes` flag
  metadata-vs-code mismatch as a P0 blocker; do NOT rewrite the
  category fields automatically — that requires user approval since
  reclassification is structural, not cosmetic.
- **2020-09-bzx-ifusdc:** `notes` flag the iUSDC-vs-iETH id mismatch.
- **2020-10 / 2021-03 / 2021-10:** `notes` record missing strict
  attacker-profit assertion.
- **2021-02-yearn-v1-dai:** `notes` record that two `require` lines
  exist but no `assertGt` for crv3/USDT profit and no F2 victim check.
- **2025-11-moonwell:** `notes` record that the single `assertGt`
  passes the smoke test but F5 oracle-deviation assertion is missing.
- **2025-12-yeth:** `notes` record that no pool-drain assertion exists.

No `verification_status`, no `reproducibility`, no `loss_usd`, no
`block_number`, and no `references` fields were modified. Metadata
schema validation continues to pass.

---

## 13. Verification Reports Updated

For each entry in `reports/verification/<id>.md`, the generator now
emits a "Static Assertion Review" subsection inside the generated
block. The subsection records:
- assertion quality at end of Phase 5
- assertions currently present in the test
- proof gaps identified by static review
- recommended future assertions
- root-cause confidence
- whether archival RPC is required for final proof

The generator continues to preserve any out-of-band manual blocks
written outside the BEGIN/END markers.

---

## 14. Quality Matrix Changes

After updating `assertion_quality` for all 18 entries, the matrix in
`reports/poc_quality_matrix.md` was regenerated. Public-RPC
limitations are not allowed to depress static quality grades — the
scorer reads `assertion_quality` independently of `verification_status`.

---

## 15. Commands Run (Final)

```sh
python3 scripts/validate_metadata.py
python3 scripts/generate_registry.py --check
python3 scripts/score_pocs.py
python3 scripts/score_pocs.py --check
python3 scripts/generate_verification_report.py
python3 scripts/generate_verification_report.py --check
forge fmt --check     # in EVM/
forge build           # in EVM/
```

## 16. Skipped Commands and Why

- Fork tests (`forge test`) — Phase 5 is static review; the brief
  forbids fork execution this phase, and archival RPC is not yet
  available.
- Web build / tests — out of scope per Phase 5 brief.
- `python3 scripts/generate_registry.py` (write mode) — would update
  `web/public/metadata.json`, which is a web artifact and out of scope.

---

## 17. Current Verification Truth

- `deterministic-confirmed` count: **0**. No archival fork tests have
  been run. Static review improves research readiness; it does **not**
  prove execution.
- Phase 4A's single public-RPC pass on Moonwell remains a smoke
  signal only and is **not** promoted to verified.
- 5 entries cannot be honestly verified at all until their
  metadata-vs-code mismatch is resolved.

## 18. Recommended Phase 6

**Phase 6 — Assertion Patch Planning and Safe Test Enhancement.**

Phase 6 should:
- pick 3 to 5 highest-priority PoCs (start with `2017-11-parity-suicide`,
  `2018-04-bec-token`, `2025-11-moonwell`, `2021-02-yearn-v1-dai`,
  `2025-12-yeth` — each targets a strong or medium root cause and only
  needs additive assertions);
- propose exact Solidity assertion patches without changing exploit
  flow (no edits to swap math, callback ordering, or amounts);
- keep each PoC in its own commit with the assertion diff and the
  Phase 5 row it closes;
- defer final verification until archival RPC is available;
- explicitly leave the 5 P0 metadata-mismatch entries to a separate
  reclassification track where the user approves the new category /
  protocol / id before any test edit.


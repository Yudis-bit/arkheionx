# Phase 6A — P0 Metadata-vs-Code Reclassification

Date: 2026-05-21
Branch: `arkheionx/research-grade-rebuild`
Scope: Resolve Phase 5's flagged P0 metadata-vs-code mismatches without touching exploit logic.

## Summary

Phase 5 surfaced six entries whose `metadata/registry.json` records named one
protocol while the corresponding Solidity test file targeted a different
protocol (or, in one case, a different market of the same protocol). Phase 6A
reclassified those six entries strictly to match what the code does, kept the
historical `id` slugs (and therefore file paths and prior cross-references)
intact, and downgraded the affected entries to
`status: needs-verification` until an archival fork run can confirm them.

No code under `EVM/src/**` or `EVM/test/**/*.t.sol` was modified. No new PoCs
were added. No exploit logic was changed. No entry was promoted to verified.

| # | id (retained) | Previous label | Code-observed label | Decision |
|---|---|---|---|---|
| 1 | `2020-06-balancer-deflationary` | Balancer — deflationary token rounding | Bancor — public `safeTransferFrom` on newly deployed contract | Reclassified |
| 2 | `2020-09-bzx-ifusdc` | bZx — iToken duplicate transfer (iUSDC/LINK framing) | bZx — iETH self-transfer double-write | Refined to iETH market |
| 3 | `2020-11-cheese-bank` | Cheese Bank — Uniswap LP price oracle manipulation | Pickle Finance — `swapExactJarForJar` arbitrary-call drains cDAI strategy | Reclassified |
| 4 | `2020-12-warp-finance` | Warp Finance — LP token oracle manipulation | Cover Protocol — Blacksmith `claimRewards` infinite mint | Reclassified |
| 5 | `2021-01-saddle` | Saddle Finance — early swap rounding | SushiSwap SushiMaker — DIGG/WBTC missing-bridge convert exploit | Reclassified |
| 6 | `2022-02-dexible` | Dexible — preApproved selfSwap drain | BUILD Finance — governance takeover via low-quorum proposal | Reclassified |

All six entries had `assertion_quality: weak` (or `none`) before Phase 6A and
still do — Phase 6A intentionally does not patch assertions; that is Phase 6B.

## Rules followed

- Did not modify `EVM/src/**`, `EVM/test/**/*.t.sol`, or any exploit logic.
- Did not modify the web app.
- Did not add new PoCs.
- Did not invent incident details (`loss_usd`, `attack_tx`, `block_number`,
  references) where the code did not pin them. Where a previous entry had a
  loss/tx that belonged to the *previously labelled* incident and not to the
  *code-observed* one, the field was removed rather than re-attributed.
- Did not claim verification.
- Did not mark anything `deterministic-confirmed`.
- Retained `id` slugs as opaque identifiers. Renaming the slugs would have
  changed `poc_path` semantics, broken existing links from
  `reports/verification/<id>.md`, and forced churn in the web export.


## Entries reviewed

### 1. `2020-06-balancer-deflationary`

**Source-of-truth file:** `EVM/test/2020-06/Exploit_2020-06.t.sol`

**Evidence:**
- Source comment header: `Bancor Protocol Access Control Exploit PoC`.
- `bancorAddress = 0x5f58058C0eC971492166763c8C22632B583F667f`.
- `victim = 0xfd0B4DAa7bA535741E6B5Ba28Cba24F9a816E67E`,
  `XBPToken = 0x28dee01D53FED0Edf5f6E310BF8Ef9311513Ae40`.
- `cheats.createSelectFork("mainnet", 10_307_563)`.
- Single mutating call:
  `bancorContract.safeTransferFrom(XBPToken, victim, attacker, victim_balance)`.
- Source comment links example tx
  `0x4643b63dcbfc385b8ab8c86cbc46da18c2e43d277de3e5bc3b4516d3c0fdeb9f`.

**Decision:** reclassify metadata to Bancor public-safeTransferFrom incident.

**Fields changed:**
- `title`: → `"Bancor — public safeTransferFrom on newly deployed contract"`
- `protocol`: `"Balancer"` → `"Bancor"`
- `category`: `"fee-on-transfer-rebasing-assumption"` → `"access-control-failure"`
- `status`: `"historical"` → `"needs-verification"`
- `summary`, `root_cause`, `impact`, `references`,
  `exploit_primitive`, `attacker_path`, `invariant_broken`,
  `protocol_assumption_failure`, `attacker_profit_check`,
  `victim_loss_check`: replaced to describe the Bancor flow.
- `assertion_quality`: `"weak"` → `"none"` (no assertions in PoC).
- `notes`: replaced with Phase 6A reclassification block.
- `tags`: `["phase-6a-reclassified"]`.

**Remaining uncertainty:** aggregate USD loss across all victims of the
Bancor public-safeTransferFrom incident is not authoritatively confirmed
from PoC alone; only the single-victim drain is exercised.

### 2. `2020-09-bzx-ifusdc`

**Source-of-truth file:** `EVM/test/2020-09/Exploit_2020-09.t.sol`

**Evidence:**
- `loanToken = ILoanTokenLogicWeth(0xB983E01458529665007fF7E0CDdeCDB74B967Eb6)`
  — bZx iETH market.
- `vm.createSelectFork("mainnet", 10_852_716 - 1)` (i.e. 10852715).
- Flow: `vm.deal(this, 200 ether)` →
  `loanToken.mintWithEther{value: 200 ether}` →
  4× `loanToken.transfer(this, balance)` →
  `loanToken.burnToEther(this, balance)` →
  `payable(0).transfer(200 ether)`.
- Source comment links
  `attack_tx 0x85dc2a433fd9eaadaf56fd8156c956da23fc17e5ef83955c7e2c4c37efa20bb5`
  and attacker `0xd1c0f1316140D6bF1a9e2Eea8a227dAD151F69b7`.

**Decision:** same root cause as the cited iUSDC/LINK incident, but the PoC
exercises the iETH market specifically. Refined metadata to that market;
retained `attack_tx` and the cited PeckShield URL because the PoC source
comment block names them; removed `loss_usd: 8000000` because that figure
aggregated multiple markets the PoC does not exercise.

**Fields changed:**
- `title`: → `"bZx — iETH self-transfer double-write"`
- `category`: unchanged (`"accounting-mismatch"`).
- `status`: `"historical"` → `"needs-verification"`.
- `summary`, `root_cause`, `impact`, `exploit_primitive`,
  `attacker_path`, `attacker_profit_check`, `victim_loss_check`:
  rewritten to describe the iETH path.
- `loss_usd`: removed.
- `notes`: replaced with Phase 6A reclassification block.
- `tags`: `["phase-6a-reclassified"]`.

**Remaining uncertainty:** whether the cited `attack_tx` is the iETH
transaction or an iUSDC/LINK sibling — manual confirmation against
Etherscan call-trace required before any loss claim.

### 3. `2020-11-cheese-bank`

**Source-of-truth file:** `EVM/test/2020-11/Exploit_2020-11.t.sol`

**Evidence:**
- `cheat.createSelectFork("mainnet", 11_303_122)` — Pickle exploit block,
  not Cheese Bank's 11205646.
- `ControllerLike CONTROLLER = 0x6847259b2B3A4c17e7c43C54409810aF48bA5210`
  (Pickle ControllerV4).
- `JarLike PDAI = 0x6949Bb624E8e8A90F87cD2058139fcd77D2F3F87`,
  `STRAT = 0xCd892a97951d46615484359355e3Ed88131f829D`,
  `CurveLogicLike CURVE_LOGIC = 0x6186E99D9CFb05E1Fdf1b442178806E81da21dD8`.
- `FakeJar`/`FakeUnderlying` mocks deployed by the test.
- `CONTROLLER.swapExactJarForJar(fakeJar, fakeJar, 0, 0, targets[], datas[])`
  invokes `STRAT.withdrawAll()`, repeated `PDAI.earn()`, and finally
  `STRAT.withdraw(address(CDAI))`, sending cDAI to `tx.origin`.
- Source comment links samczsun reference:
  `https://github.com/banteg/evil-jar/blob/master/reference/samczsun.sol`.

**Decision:** reclassify metadata to Pickle Finance ControllerV4 exploit.

**Fields changed:**
- `title`: → `"Pickle Finance — swapExactJarForJar arbitrary-call drains cDAI strategy"`.
- `protocol`: `"Cheese Bank"` → `"Pickle Finance"`.
- `category`: `"flash-loan-price-manipulation"` → `"unsafe-external-call"`.
- `status`: `"historical"` → `"needs-verification"`.
- `block_number`: `11205646` → `11303122` (matches `createSelectFork`).
- `attack_tx`: replaced with the samczsun-cited Pickle exploit tx
  `0xe72d4e7ba9b5af0cf2a8cfb1e30fd9f388df0ab3da79790be842bfbed11087b0`
  (this same tx hash had been incorrectly attached to the Cheese Bank
  framing previously).
- `loss_usd`: `3300000` → removed.
- `references`: replaced (Cheese Bank PeckShield URL → samczsun sample).
- `summary`, `root_cause`, `impact`, `exploit_primitive`,
  `attacker_path`, `invariant_broken`, `protocol_assumption_failure`,
  `attacker_profit_check`, `victim_loss_check`: rewritten.
- `notes`: replaced.
- `tags`: `["phase-6a-reclassified"]`.

**Remaining uncertainty:** aggregate Pickle Finance cDAI exploit loss
(commonly cited around $19.7M) not authoritatively reconfirmed from PoC
alone; left absent.


### 4. `2020-12-warp-finance`

**Source-of-truth file:** `EVM/test/2020-12/Exploit_2020-12.t.sol`

**Evidence:**
- `cheat.createSelectFork("mainnet", 11_542_309)` (Cover incident block).
- `Blacksmith bs = 0xE0B94a7BB45dD905c79bB1992C9879f40F1CAeD5`
  — Cover Protocol Blacksmith staking contract.
- `IERC20 bpt = 0x59686E01Aa841f622a43688153062C2f24F8fDed`,
  `IERC20 Cover = 0x5D8d9F5b96f4438195BE9b99eee6118Ed4304286` (COVER token).
- Flow: `cheat.prank(0x00007569643bc1709561ec2E86F385Df3759e5DD)` →
  `bs.deposit(bpt, 15_255_552_810_089_260_015_361)` →
  `bs.claimRewards(bpt)` → log `Cover.balanceOf(0x00007569...)`.

**Decision:** reclassify metadata to Cover Protocol Blacksmith infinite-mint.

**Fields changed:**
- `title`: → `"Cover Protocol — Blacksmith claimRewards infinite mint"`.
- `protocol`: `"Warp Finance"` → `"Cover Protocol"`.
- `category`: `"flash-loan-price-manipulation"` → `"accounting-mismatch"`.
- `status`: `"historical"` → `"needs-verification"`.
- `loss_usd`: `7700000` → removed (Warp Finance figure).
- `references`: replaced (Warp post-mortem → Blacksmith contract on Etherscan).
- `summary`, `root_cause`, `impact`, `exploit_primitive`,
  `attacker_path`, `invariant_broken`, `protocol_assumption_failure`,
  `attacker_profit_check`, `victim_loss_check`: rewritten.
- `notes`: replaced.
- `tags`: `["phase-6a-reclassified"]`.

**Remaining uncertainty:** aggregate USD impact of the Cover incident
(and the white-hat reversal that followed) not authoritatively
reconfirmed from PoC alone; `attack_tx` left unset.

### 5. `2021-01-saddle`

**Source-of-truth file:** `EVM/test/2021-01/Exploit_2021-01.t.sol`

**Evidence:**
- `vm.createSelectFork("mainnet", 11_720_049)` — Sushi/DIGG incident block.
- `sushiMaker = 0xE11fc0B43ab98Eb91e9836129d1ee7c3Bc95df50`,
  `sushiFactory = 0xC0AEe478e3658e2610c5F7A4A2E1777cE9e4f2Ac`.
- `wethBridgeToken = 0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599` (WBTC),
  `nonWethBridgeToken = 0x798D1bE841a82a273720CE31c822C61a67a601C3` (DIGG).
- Flow: wrap 0.001 ETH → swap WETH→WBTC→DIGG →
  `sushiFactory.createPair(DIGG, WETH)` → `addLiquidity` →
  `sushiMaker.convert(WBTC, DIGG)` → `removeLiquidity` →
  swap DIGG→WBTC→WETH; logs `Attacker's profit: %s WETH`.
- Source comment block cites `SushiMaker.sol L192` and links
  cmichel/slowmist/rekt postmortems.

**Decision:** reclassify metadata to SushiSwap SushiMaker missing-bridge
exploit. Removed Saddle disclosure URL since the code does not target
Saddle. Cleared the prior `incomplete` status (the PoC author's "incomplete"
note was about hardhat-vs-foundry porting frustration, not a missing
exploit step — the foundry test exercises the full convert+rugPull flow).

**Fields changed:**
- `title`: → `"SushiSwap SushiMaker — DIGG/WBTC missing-bridge convert exploit"`.
- `protocol`: `"Saddle Finance"` → `"SushiSwap (SushiMaker)"`.
- `severity`: `"medium"` → `"high"`.
- `category`: `"arithmetic-precision-rounding"` → `"amm-invariant-manipulation"`.
- `status`: `"incomplete"` → `"needs-verification"`.
- `summary`, `root_cause`, `impact`, `exploit_primitive`,
  `attacker_path`, `invariant_broken`, `protocol_assumption_failure`,
  `attacker_profit_check`, `victim_loss_check`: rewritten.
- `references`: replaced (Saddle disclosure → cmichel + rekt URLs already
  cited in the PoC source comment).
- `notes`: replaced.
- `tags`: `["phase-6a-reclassified"]`.

**Remaining uncertainty:** aggregate USD captured in the historical incident
not authoritatively re-confirmed from PoC alone; left absent.

### 6. `2022-02-dexible`

**Source-of-truth file:** `EVM/test/2022-02/Exploit_2022-02.t.sol`

**Evidence:**
- `cheat.createSelectFork("mainnet", 14_235_712)` (BUILD incident block).
- `IBuildFinance BuildGovernance = 0x5A6eBeB61A80B2a2a5e0B4D893D731358d888583`.
- `IERC20 build = 0x6e36556B3ee5Aa28Def2a8EC3DAe30eC2B208739` (BUILD token).
- Flow: `cheat.prank(0x562680a4dC50ed2f14d75BF31f494cfE0b8D10a1)` →
  `build.transfer(this, 101_529_401_443_281_484_977)` →
  `BuildGovernance.propose(BUILD, 0, approve(0xb4c79dab8f259c7aee6e5b2aa729821864227e84, max))` →
  vote via prank `0xf41c13f4E2f750408fC6eb5cF0E34225D52E7002` →
  `cheat.warp(1_655_436_437)` → `BuildGovernance.execute(8, ...)` →
  `build.transferFrom(BuildGovernance, this, balance)`.

**Decision:** reclassify metadata to BUILD Finance governance takeover.
Replaced Dexible post-mortem URL with the BuildGovernance contract address
on Etherscan as a verifiable on-chain reference (the PoC source itself does
not link a postmortem).

**Fields changed:**
- `title`: → `"BUILD Finance — governance takeover via low-quorum proposal"`.
- `protocol`: `"Dexible"` → `"BUILD Finance"`.
- `category`: `"unsafe-external-call"` → `"governance-attack"`.
- `status`: `"historical"` → `"needs-verification"`.
- `summary`, `root_cause`, `impact`, `exploit_primitive`,
  `attacker_path`, `invariant_broken`, `protocol_assumption_failure`,
  `attacker_profit_check`, `victim_loss_check`: rewritten.
- `references`: replaced (Dexible post-mortem → BuildGovernance contract).
- `notes`: replaced.
- `tags`: `["phase-6a-reclassified"]`.

**Remaining uncertainty:** aggregate USD value of the BuildGovernance treasury
at fork block (commonly cited around $470k) not authoritatively re-confirmed
from PoC alone; left absent.


## Metadata fields changed (cross-cutting summary)

For all six entries:
- `id`: unchanged.
- `poc_path`: unchanged.
- `block_number`: unchanged for 5/6 entries; corrected on
  `2020-11-cheese-bank` (`11205646` → `11303122`) to match
  `createSelectFork`.
- `chain`: unchanged.
- `vm`: unchanged.
- `rpc_alias`: unchanged.
- `verification_status`: unchanged (`not-run-no-rpc`).
- `reproducibility`: unchanged (`deterministic-likely-but-unverified`).
- `status`: `historical` (or `incomplete` for `2021-01-saddle`) →
  `needs-verification`.

`loss_usd` and `attack_tx` were removed where the previous values came
from a different incident than the one the code exercises:
- `2020-09-bzx-ifusdc`: `loss_usd` removed; `attack_tx` retained
  (PoC source comment names it; manual confirmation pending).
- `2020-11-cheese-bank`: `loss_usd` removed; `attack_tx` retained
  but pointing at the Pickle ControllerV4 tx referenced in the
  samczsun sample linked from the PoC source.
- `2020-12-warp-finance`: `loss_usd` removed; `attack_tx` left unset.
- `2022-02-dexible`: no prior `loss_usd`/`attack_tx`; added none.

## Reports changed

- `reports/verification/2020-06-balancer-deflationary.md`
- `reports/verification/2020-09-bzx-ifusdc.md`
- `reports/verification/2020-11-cheese-bank.md`
- `reports/verification/2020-12-warp-finance.md`
- `reports/verification/2021-01-saddle.md`
- `reports/verification/2022-02-dexible.md`

Each report's BEGIN/END GENERATED block was regenerated from the new
metadata via `scripts/generate_verification_report.py`. A manual
"Phase 6A Reclassification" block was appended *outside* the
generated markers and contains:
- previous label
- code-observed label
- decision
- evidence from code
- remaining uncertainty
- verification status (unchanged)

`reports/poc_quality_matrix.md` was regenerated by
`scripts/score_pocs.py`. `README.md` and `web/public/metadata.json`
were regenerated by `scripts/generate_registry.py` (titles, protocols,
categories, and statuses for the six entries are now consistent across
the registry, the web export, and the README index).

## Unresolved uncertainties

1. Whether the `attack_tx` cited in the PoC source comments for
   `2020-09-bzx-ifusdc` is actually the iETH transaction or one of the
   iUSDC/LINK siblings — needs Etherscan call-trace inspection.
2. Aggregate USD figures for all six reclassified entries are
   intentionally absent. Per Phase 6A rules, `loss_usd` was not
   re-introduced from external sources.
3. The previous `2020-11-cheese-bank` and `2020-12-warp-finance`
   labels referred to real, distinct incidents that this repo no
   longer represents in code. They are not lost — they remain as
   gaps that a future Phase 6+ track could fill with new PoC code
   under fresh `id` slugs.
4. `2020-06-balancer-deflationary` previously implied a Balancer-
   specific assertion family (`F6` accounting mismatch on a pool).
   The Bancor reclassification still requires `F6` (accounting
   mismatch on user approvals) plus `F1` (attacker profit), which
   the PoC currently asserts at quality `none`. Phase 6B is the
   place to add those.

## Current verified count

`reports/poc_quality_matrix.md` summary, post-Phase-6A:

- Total PoCs: 18
- Verified (`verification_status: verified`): 0
- All entries remain `not-run-no-rpc`. Phase 6A did not run any forks.

`scripts/validate_metadata.py`, `scripts/generate_registry.py --check`,
`scripts/score_pocs.py --check`, and `scripts/generate_verification_report.py --check`
all report clean. `cd EVM && forge build` exits 0 (lint warnings only,
unchanged from baseline).

## Next recommended phase

**Phase 6B — Assertion Patch Planning for 3–5 highest-priority PoCs.**

Priority candidates, from `assertion_quality` plus historical impact:

1. `2018-04-bec-token` (`assertion_quality: none`, batchTransfer
   overflow). Canonical zero-assertion PoC; small surface to patch.
2. `2020-06-balancer-deflationary` (now Bancor;
   `assertion_quality: none`). Single mutating call; F6 + F1 assertions
   are mechanical to add.
3. `2020-09-bzx-ifusdc` (now iETH;
   `assertion_quality: weak`). Simple pre/post ETH balance assertion
   plus loanToken contract underlying balance check.
4. `2020-12-warp-finance` (now Cover Protocol;
   `assertion_quality: weak`). One assertion against
   `Cover.totalSupply()` pre/post would prove the infinite-mint
   directly.
5. `2017-11-parity-suicide` (`assertion_quality: weak`).
   Code-length pre/post assertion is already documented in Phase 5
   notes and is trivially mechanical.

Phase 6B should *not* start until requested.

# Phase 7C — DODO Crowdpool Assertion Patch

- **Date:** 2026-05-22
- **Target PoC:** `2021-03-dodo-crowdpool`
- **Scope:** one-PoC-only assertion strengthening; no flow / address / call-order
  changes; no edits outside the test file (and metadata + reports).

## File modified

- `EVM/test/2021-03/Exploit_2021-03.t.sol`

No edits to `EVM/src/**`, no edits to other test files, no edits to `web/**`,
`SVM/**`, or `MoveVM/**`.

## Accessor / precondition result

- Required accessors on the deployed DVM
  (`0x051EBD717311350f1684f89335bed4ABd083a2b6`):
  - `_BASE_TOKEN_()`
  - `_QUOTE_TOKEN_()`
- The shared `DVM` interface in `EVM/src/interface.sol` (line 1515) already
  declares both. They were declared non-`view`, but on-chain they are public
  state-variable getters and are safe to call as `view`.
- Per the patch rules (no edits to `EVM/src/**`), a minimal local interface
  was added inside the test file:

  ```solidity
  interface IDVMView {
      function _BASE_TOKEN_() external view returns (address);
      function _QUOTE_TOKEN_() external view returns (address);
  }
  ```

  No fallback proof target was needed; the planned base/quote flip assertion
  is supported.

## Assertions added

Pre-state (before the unchanged `dvm.flashLoan(...)` call):

- `assertEq(dvmView._BASE_TOKEN_(),  address(wCRES_token), "pre: DVM base != wCRES")`
- `assertEq(dvmView._QUOTE_TOKEN_(), address(usdt_token), "pre: DVM quote != USDT")`

Post-state (after the unchanged exploit flow returns):

- `assertEq(dvmView._BASE_TOKEN_(),  token1, "post: DVM base not flipped to attacker token1")`
- `assertEq(dvmView._QUOTE_TOKEN_(), token2, "post: DVM quote not flipped to attacker token2")`
- `assertTrue(baseAfter  != baseBefore, "post: DVM base unchanged")`
- `assertTrue(quoteAfter != quoteBefore, "post: DVM quote unchanged")`

Two `log_named_address` lines are emitted for pre and post observability;
they are diagnostic only.

## Proof target

Exact reconfiguration of the DVM crowdpool's base/quote token bindings —
from the legitimate `(wCRES, USDT)` pair to attacker-chosen `(token1, token2)`
addresses — caused by re-`init` invoked from inside the flash-loan callback.

This satisfies the `initialization-bug` category's required assertion
families:

- **F4** — unauthorized state transition assertion
- **F7** — ownership / control assertion (attacker now controls which tokens
  the pool is bound to)

The exploit body (`DVMFlashLoanCall`) was not modified. Attacker addresses,
token addresses, balances, and the `dvm.init(...)` call ordering are
preserved.

## Commands run

| Command | Result |
| --- | --- |
| `git status --short` | clean |
| `python3 scripts/validate_metadata.py` | ok: 18 entries valid |
| `python3 scripts/generate_registry.py --check` | ok: 18 entries |
| `python3 scripts/score_pocs.py --check` (pre-patch) | ok: matrix unchanged |
| `python3 scripts/generate_verification_report.py --check` (pre-patch) | ok: 18 entries processed, 0 changed |
| `cd EVM && forge fmt --check` | clean |
| `cd EVM && forge build` | compiles (warnings unrelated to this PoC) |
| `cd EVM && forge test --match-path test/2021-03/Exploit_2021-03.t.sol -vvv` | RPC failure in `setUp()` (see below) |
| `python3 scripts/validate_metadata.py` (post-patch) | ok: 18 entries valid |
| `python3 scripts/score_pocs.py` (post-patch) | updated: matrix |
| `python3 scripts/generate_verification_report.py` (post-patch) | updated: report |
| `python3 scripts/generate_registry.py --check` (post-patch) | ok: 18 entries |
| `cd EVM && forge fmt --check` (post-patch) | clean |

## Fork test result

`forge test` failed in `setUp()` before the test body executed:

```
vm.createSelectFork: failed to get account for 0x1804c8AB1F12E6bbf3894d4083f33e07309d1f38:
server returned an error response: error code -32000:
historical state ... is not available
```

Therefore the new pre/post assertions did not actually run.

### Was this an RPC limitation?

**Yes.** The configured public `mainnet` RPC does not retain archival state
at block `12000000`. This is classified as a verification limitation, not a
PoC failure. The patch compiles cleanly under `forge build` and is
formatted-correct under `forge fmt --check`; the assertions themselves are
logically consistent with the registry's `attacker_path`, `invariant_broken`,
and `protocol_assumption_failure` fields.

## Metadata / report changes

- `metadata/registry.json` — entry `2021-03-dodo-crowdpool`:
  - `assertion_quality`: `weak` → `strong`
  - `notes`: replaced with a Phase 7C summary (assertions added, accessor
    rationale, RPC limitation classification).
  - `reproducibility`: **unchanged** (`deterministic-likely-but-unverified`).
  - `verification_status`: **unchanged** (`not-run-no-rpc`).
- `reports/verification/2021-03-dodo-crowdpool.md` — appended a new
  `## Phase 7C Assertion Patch` section after the generated marker;
  the generated section was regenerated and now reflects
  `Assertion quality (static): strong`.
- `reports/poc_quality_matrix.md` — regenerated. The PoC's score moved
  from **69 / D** to **89 / B**, driven by the assertion-section delta
  (0 → 20).

## Verified count

`verification_status: verified` count is **unchanged at 0** in the registry.
Phase 7C did not promote anything to verified — the public RPC could not
serve historical state at block 12,000,000, so the new exact-state
assertions did not execute. Promotion to `deterministic-confirmed` /
`verified` requires a future archival-RPC run.

## Recommendation for next one-PoC patch

Per `docs/internal/PHASE_7_PATCHED_CORPUS_REVIEW.md`, the remaining
weak-assertion D-grade entries before this patch were:

- `2020-04-uniswap-imbtc` (callback-misuse / reentrancy primitive)
- `2020-08-opyn` (signature-permit-misuse-style replay)
- `2020-10-harvest` (oracle / share-price)

Of these, `2020-08-opyn` is the smallest blast-radius candidate: it is a
self-contained replay PoC where the natural proof target is an exact
attacker token-balance delta against a known invariant, and it does not
require introducing new external read accessors. Recommend Phase 7D target:
**`2020-08-opyn`**, contingent on confirming the relevant getters (e.g.
collateral / payout token) are already exposed in `interface.sol` before
committing to the assertion shape.

Do not start the next PoC in this phase.

# Phase 4A — Public RPC Smoke Test and Archive-RPC Readiness

Internal log. Not a verification artifact.

This phase classifies endpoint capability against the existing PoC archive. It
does NOT verify any PoC as `deterministic-confirmed`. A public RPC failing on
historical state is not evidence of a broken PoC.

---

## Run context

- **Phase:** 4A — Public RPC Smoke Test and Archive-RPC Readiness
- **Date:** 2026-05-21
- **Branch:** `arkheionx/research-grade-rebuild`
- **Latest commit (pre-phase):** `d9ea970` — `feat(research): add DeFi PoC verification framework`

## Pre-flight commands run

| Command                                              | Result                                 |
| ---------------------------------------------------- | -------------------------------------- |
| `git status --short`                                 | clean (one untracked stub `git`)        |
| `git log --oneline -5`                               | ok                                     |
| `python3 scripts/validate_metadata.py`               | `ok: 18 entries valid`                 |
| `python3 scripts/generate_registry.py --check`       | drift on `web/public/metadata.json` (web excluded by phase scope) |
| `python3 scripts/score_pocs.py --check`              | `ok: matrix unchanged (18 entries)`    |
| `python3 scripts/generate_verification_report.py --check` | `ok: 18 entries processed, 0 changed` |
| `forge fmt --check`                                  | clean                                  |
| `forge build`                                        | succeeds with pre-existing lint warnings on `test/2025-11/Exploit_2025-11.t.sol` (ERC20-unchecked-transfer, unsafe-typecast). Not phase blockers. |

## RPC environment availability

Reported as present/missing only. No values printed.

| Env var             | Status   |
| ------------------- | -------- |
| `ETH_RPC_URL`       | present  |
| `BASE_RPC_URL`      | present  |
| `ARBITRUM_RPC_URL`  | missing  |
| `OPTIMISM_RPC_URL`  | missing  |
| `POLYGON_RPC_URL`   | missing  |
| `BSC_RPC_URL`       | missing  |
| `AVALANCHE_RPC_URL` | missing  |

The presence of an env var alone does not imply archival capability. Public
endpoints are common defaults and often non-archival.

## Public RPC limitation summary

Public RPC endpoints are useful for cheap smoke testing of compile / link /
fork-setup paths but typically cannot serve historical state for old DeFi
incidents. For pre-2023 mainnet PoCs, archival access is effectively required.

Common failures observed in this class of work:

- `historical state is not available`
- `missing trie node`
- `header not found`
- 429 / project-id-rate-exceeded
- timeout / 502 / 504

These are RPC-side failures and are classified as endpoint capability issues,
not PoC defects.

---

## Known smoke-test result (Task 2)

The following result was observed prior to Phase 4A and is the seed evidence
for this phase. It is also recorded in
`reports/verification/2020-04-uniswap-imbtc.md` (manual section, preserved
across regeneration via the new `<!-- BEGIN MANUAL: ... -->` marker).

| Field                              | Value                                                              |
| ---------------------------------- | ------------------------------------------------------------------ |
| PoC                                | `EVM/test/2020-04/Exploit_2020-04.t.sol`                           |
| Command                            | `forge test --match-path test/2020-04/Exploit_2020-04.t.sol -vvv`  |
| Endpoint type                      | public Ethereum RPC                                                |
| Failure stage                      | fork setup (`vm.createSelectFork` inside `setUp()`)                |
| RPC error class                    | `historical state is not available`                                |
| Classification                     | `public-rpc-not-archival`                                          |
| Exploit execution started          | no                                                                 |
| Assertions ran                     | no                                                                 |
| PoC considered broken              | no — RPC limitation, not PoC defect                                |
| Final verification possible here   | no — requires archival Ethereum RPC                                |

This entry's `metadata/registry.json` row was updated with:

- `latest_public_rpc_status: public-rpc-not-archival`
- `latest_public_rpc_notes`: short description of the failure (no URLs).

`verification_status` and `reproducibility` remain unchanged.

---

## Public RPC compatibility matrix (Task 3)

For every PoC currently in `metadata/registry.json`. Compatibility is a
prediction, not a measurement. "Likely" means the block is recent enough that
some public endpoints may serve it; it does not mean a public RPC will work.

| ID                              | Protocol             | Chain    | Block      | Age    | Public-RPC compat | Reason                                                       |
| ------------------------------- | -------------------- | -------- | ---------- | ------ | ----------------- | ------------------------------------------------------------ |
| `2017-07-parity-multisig`       | Parity Multisig      | ethereum |  4,043,799 | old    | unlikely          | 2017 mainnet; archival required for state at this depth       |
| `2017-11-parity-suicide`        | Parity Library       | ethereum |  4,501,735 | old    | unlikely          | 2017 mainnet; archival required                               |
| `2018-04-bec-token`             | BEC Token            | ethereum |  5,483,642 | old    | unlikely          | 2018 mainnet; archival required                               |
| `2018-10-spankchain`            | SpankChain           | ethereum |  6,605,501 | old    | unlikely          | 2018 mainnet; archival required                               |
| `2020-04-uniswap-imbtc`         | Uniswap V1 / imBTC   | ethereum |  9,899,725 | old    | unlikely (confirmed) | Already failed with `historical state is not available`    |
| `2020-06-balancer-deflationary` | Balancer             | ethereum | 10,307,563 | old    | unlikely          | 2020 mainnet; archival required                               |
| `2020-08-opyn`                  | Opyn v1              | ethereum | 10,592,516 | old    | unlikely          | 2020 mainnet; archival required                               |
| `2020-09-bzx-ifusdc`            | bZx                  | ethereum | 10,852,715 | old    | unlikely          | 2020 mainnet; archival required                               |
| `2020-10-harvest`               | Harvest Finance      | ethereum | 11,129,473 | old    | unlikely          | 2020 mainnet; archival required                               |
| `2020-11-cheese-bank`           | Cheese Bank          | ethereum | 11,205,646 | old    | unlikely          | 2020 mainnet; archival required                               |
| `2020-12-warp-finance`          | Warp Finance         | ethereum | 11,542,309 | old    | unlikely          | 2020 mainnet; archival required                               |
| `2021-01-saddle`                | Saddle Finance       | ethereum | 11,720,049 | old    | unlikely          | 2021 mainnet; archival required                               |
| `2021-02-yearn-v1-dai`          | Yearn v1 yDAI        | ethereum | 11,792,183 | old    | unlikely          | 2021 mainnet; archival required                               |
| `2021-03-dodo-crowdpool`        | DODO V2 CrowdPooling | ethereum | 12,000,000 | old    | unlikely          | 2021 mainnet; archival required                               |
| `2021-10-indexed-finance`       | Indexed Finance      | ethereum | 13,417,326 | old    | unlikely          | 2021 mainnet; archival required                               |
| `2022-02-dexible`               | Dexible              | ethereum | 14,235,712 | old    | unlikely          | 2022 mainnet; archival required                               |
| `2025-11-moonwell`              | Moonwell             | base     | 37,722,881 | recent | possible          | Late-2025 Base; some public Base endpoints may serve this    |
| `2025-12-yeth`                  | yETH                 | ethereum | 23,914,085 | recent | possible          | Late-2025 mainnet; some public ETH endpoints may serve this  |

Conclusions:

- 16 of 18 entries should be assumed `requires-archival-rpc` for any
  meaningful verification attempt.
- 2 of 18 entries (`2025-11-moonwell`, `2025-12-yeth`) may be reachable from
  a sufficiently recent public endpoint, but compatibility is not guaranteed.
- Public RPC smoke testing is appropriate for these 2 entries; the remaining
  16 should not be smoke-tested against public RPCs in this phase.

---

## Additional smoke tests (Task 4)

Two limited smoke tests were executed under the rule "at most 2 additional".
Both ran against the Foundry profile defaults using whatever endpoint
`ETH_RPC_URL` / `BASE_RPC_URL` resolves to in this environment.

### Smoke test A — `2025-11-moonwell`

| Field                              | Value                                                              |
| ---------------------------------- | ------------------------------------------------------------------ |
| Command                            | `forge test --match-path test/2025-11/Exploit_2025-11.t.sol -vvv`  |
| Endpoint type                      | public Base RPC (env-resolved)                                     |
| Outcome                            | test PASS, suite ok                                                |
| Classification                     | `public-rpc-pass`                                                  |
| Setup succeeded                    | yes                                                                |
| Exploit executed                   | yes                                                                |
| Logged result                      | `WETH profit: 24917534577559974182` (~24.92 WETH)                  |
| Assertion family check             | F5 oracle deviation, F2 victim loss expected per category but not yet reviewed for strength |
| Promotion to `deterministic-confirmed` | NOT performed in this phase. A `public-rpc-pass` does not auto-promote; assertion-quality review and verification report writing belong to a later phase |

### Smoke test B — `2025-12-yeth`

| Field                              | Value                                                              |
| ---------------------------------- | ------------------------------------------------------------------ |
| Command                            | `forge test --match-path test/2025-12/Exploit_2025-12.t.sol -vvv`  |
| Endpoint type                      | public Ethereum RPC (env-resolved)                                 |
| Outcome                            | suite FAILED in `setUp()` before exploit logic                     |
| RPC error                          | `error code -32000: historical state ... is not available`         |
| Failure stage                      | `vm.createSelectFork` while reading account state at fork block    |
| Classification                     | `public-rpc-not-archival`                                          |
| Setup succeeded                    | no                                                                 |
| Exploit executed                   | no                                                                 |
| Assertions ran                     | no                                                                 |
| PoC considered broken              | no — RPC limitation, not PoC defect                                |

Conclusion of additional smoke tests: even the most recent Ethereum mainnet
PoC in the archive (block 23,914,085, December 2025) cannot be served by the
currently configured public Ethereum RPC. Final verification of any
Ethereum-mainnet entry in this archive should be planned for an archival
endpoint.

---

## Smoke-test result table (summary)

| Entry                       | Endpoint  | Stage reached    | Classification               |
| --------------------------- | --------- | ---------------- | ---------------------------- |
| `2020-04-uniswap-imbtc`     | public ETH | fork-setup fail | `public-rpc-not-archival`    |
| `2025-11-moonwell`          | public Base | exploit pass   | `public-rpc-pass`            |
| `2025-12-yeth`              | public ETH | fork-setup fail | `public-rpc-not-archival`    |

The other 15 entries were not smoke-tested in this phase because public RPC
attempts against pre-2024 mainnet blocks are not informative; they would
predictably classify as `public-rpc-not-archival`.

## Final classification

- 2 entries: `public-rpc-not-archival` recorded.
- 1 entry: `public-rpc-pass` (recent Base PoC) — NOT promoted to verified.
- 15 entries: not smoke-tested this phase; remain unchanged in metadata for
  the public-RPC dimension. Their `latest_public_rpc_status` defaults to
  `not-tested` (field is optional; absence means not-tested).

## Next action

- Phase 4A: complete.
- Phase 5 (proposed): Static Assertion and Root-Cause Hardening — line-by-line
  PoC review, classify assertion quality, propose tightenings, prepare
  archival verification candidates.

---

# Phase 4A Report: Public RPC Smoke Test and Archive-RPC Readiness

## 1. Summary

- Phase 4A did NOT verify any PoC as deterministic-confirmed.
- Public RPC smoke testing was used only to classify endpoint capability.
- Two of three observed smoke tests failed during fork setup with
  "historical state is not available". One smoke test passed on a recent
  Base PoC, but is not auto-promoted.
- Verified PoC count remains accurate and honest at 0.
- The repo now records public-RPC results separately from final verification
  status, so the two cannot be confused.

## 2. Repository state

- Branch: `arkheionx/research-grade-rebuild`
- Latest commit (pre-phase): `d9ea970`
- Working tree before phase: clean except untracked stub `git`
- Web: untouched
- Exploit logic: untouched
- EVM helpers: untouched

## 3. RPC environment

| Env var             | Status   |
| ------------------- | -------- |
| `ETH_RPC_URL`       | present  |
| `BASE_RPC_URL`      | present  |
| `ARBITRUM_RPC_URL`  | missing  |
| `OPTIMISM_RPC_URL`  | missing  |
| `POLYGON_RPC_URL`   | missing  |
| `BSC_RPC_URL`       | missing  |
| `AVALANCHE_RPC_URL` | missing  |

Presence does not imply archival capability.

## 4. Known smoke test result

- PoC: `EVM/test/2020-04/Exploit_2020-04.t.sol`
- Command: `forge test --match-path test/2020-04/Exploit_2020-04.t.sol -vvv`
- Failure stage: `vm.createSelectFork` inside `setUp()`
- Failure class: `public-rpc-not-archival`
- Conclusion: PoC was neither verified nor disproven; archival RPC required.

## 5. Additional smoke tests

| Entry              | Command                                                            | Endpoint   | Result                                       | Classification              |
| ------------------ | ------------------------------------------------------------------ | ---------- | -------------------------------------------- | --------------------------- |
| `2025-11-moonwell` | `forge test --match-path test/2025-11/Exploit_2025-11.t.sol -vvv`  | public Base| 1 passed; logged WETH profit ~24.92          | `public-rpc-pass`           |
| `2025-12-yeth`     | `forge test --match-path test/2025-12/Exploit_2025-12.t.sol -vvv`  | public ETH | failed in `setUp()`: historical state n/a    | `public-rpc-not-archival`   |

`2025-11-moonwell` was NOT promoted to verified. A passing run on public RPC
is a positive smoke signal but does not establish assertion strength or
fork-block correctness; that review belongs to a later phase.

## 6. Public RPC compatibility matrix

- 16 of 18: `unlikely` (pre-2024 mainnet); archival RPC required.
- 2 of 18 (recent): `possible` (2025-11 Base, 2025-12 ETH).
- Empirically observed: 2025-11 passed on public Base, 2025-12 failed on
  public ETH.

Full matrix is in this document above.

## 7. Metadata changes

- Schema (`metadata/schema.json`):
  - Added optional field `latest_public_rpc_status` with enum
    `not-tested | public-rpc-pass | public-rpc-not-archival |
    public-rpc-rate-limited | public-rpc-unstable | public-rpc-failed-unknown`.
  - Added optional field `latest_public_rpc_notes` (string).
  - Existing enums for `verification_status` and `reproducibility` left intact.
- Registry (`metadata/registry.json`):
  - `2020-04-uniswap-imbtc`: `latest_public_rpc_status: public-rpc-not-archival`
    + notes.
  - `2025-11-moonwell`: `latest_public_rpc_status: public-rpc-pass` + notes.
  - No `verification_status` was promoted to `verified`.

## 8. Verification reports updated

- `reports/verification/2020-04-uniswap-imbtc.md` — added manual section
  "Public RPC Smoke Test" between BEGIN/END MANUAL markers, preserved across
  regeneration.
- All 18 reports rewritten to include the BEGIN/END GENERATED VERIFICATION
  SUMMARY markers. Manual sections (when present) are preserved on subsequent
  regeneration runs.

## 9. Documentation changes

- `docs/FORK_VERIFICATION.md`: added "Public RPC vs Archival RPC" section
  covering public vs archival, common failure messages, classification rules,
  required env vars, example commands, and the deterministic-confirmed bar.
- `docs/REPRODUCIBILITY_STANDARD.md`: added a section that distinguishes
  reproducibility status, verification status, RPC capability, and assertion
  quality, and a decision table mapping observations to status fields.
- `docs/internal/PHASE_4A_PUBLIC_RPC_SMOKE_TEST.md`: this file.

## 10. Validation commands

| Command                                                  | Result                              |
| -------------------------------------------------------- | ----------------------------------- |
| `python3 scripts/validate_metadata.py`                   | `ok: 18 entries valid`              |
| `python3 scripts/score_pocs.py`                          | `updated: reports/poc_quality_matrix.md (18 entries)` |
| `python3 scripts/score_pocs.py --check`                  | `ok: matrix unchanged (18 entries)` |
| `python3 scripts/generate_verification_report.py`        | 18 entries processed                |
| `python3 scripts/generate_verification_report.py --check`| `ok: 18 entries processed, 0 changed` |
| `forge fmt --check`                                      | clean                               |
| `forge build`                                            | succeeds (pre-existing lint warnings on `test/2025-11/Exploit_2025-11.t.sol`; not phase blockers) |

Web commands were not run. Web files were not modified.

## 11. Current verification truth

- Total PoCs: **18**
- `verification_status: verified` (deterministic-confirmed): **0**
- `latest_public_rpc_status: public-rpc-pass`: **1** (`2025-11-moonwell`,
  not promoted to verified)
- `latest_public_rpc_status: public-rpc-not-archival`: **2**
  (`2020-04-uniswap-imbtc`, `2025-12-yeth`)
- `reproducibility: requires-archival-rpc`: **2** (existing classifications
  for `2025-11-moonwell` and `2025-12-yeth`, set in earlier phases)
- Unverified (anything other than `verification_status: verified`): **18**

The verified count remains zero. Phase 4A did not falsify or inflate this
number.

## 12. What this means

- The repository is now more honest about the difference between
  "the public RPC could not serve historical state" and "the PoC failed".
  Previously these would have been visually indistinguishable.
- Anyone with a paid archival RPC now has a clear, scoped path to verify
  PoCs: the env-var matrix, the classification table, and the per-entry
  verification reports tell them exactly what command to run and what to
  record.
- Public RPC is acceptable for cheap smoke tests but should not be relied
  upon for final verification of pre-2024 mainnet incidents.
- The `2025-11-moonwell` `public-rpc-pass` is a useful signal that the PoC
  is at least functional end-to-end; it is not yet a research-grade
  verification claim.

## 13. Recommended Phase 5

Phase 5 — Static Assertion and Root-Cause Hardening — should:

- Read every PoC line by line.
- Classify `assertion_quality` per entry (`strong | medium | weak | none`).
- Identify weak or missing assertions and propose exact tightenings.
- Add missing root-cause / invariant detail to metadata where appropriate.
- Avoid changing exploit logic unless separately approved.
- Prepare a prioritized list of candidates for archival verification in a
  later phase.

Phase 5 is not started in Phase 4A.

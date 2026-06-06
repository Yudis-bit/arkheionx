# Fork Verification

How EVM PoCs in this archive are verified against pinned chain state.

---

## Required environment

The Foundry profile in `EVM/foundry.toml` declares chain aliases. Each
alias is resolved from an environment variable. The minimum set:

| Alias       | Env var          | Notes                                  |
| ----------- | ---------------- | -------------------------------------- |
| `mainnet`   | `ETH_RPC_URL`    | Ethereum mainnet, archival required.   |
| `base`      | `BASE_RPC_URL`   | Base, archival required.               |
| `arbitrum`  | `ARBITRUM_RPC_URL` | Arbitrum One, archival required.    |
| `optimism`  | `OPTIMISM_RPC_URL` | Optimism, archival required.        |
| `polygon`   | `POLYGON_RPC_URL`  | Polygon PoS, archival required.     |
| `bsc`       | `BSC_RPC_URL`      | BNB Smart Chain, archival required. |
| `avalanche` | `AVALANCHE_RPC_URL` | Avalanche C-Chain, archival required. |

Add new aliases by editing `EVM/foundry.toml` (additive only — do not
remove or rename existing aliases without a registry sweep).

## Archival requirement

Most consumer RPC endpoints prune historical state past 128 blocks.
Replaying an exploit at its original block requires:

- An archival node (full historical state), or
- An archival-tier endpoint from a provider (Alchemy, Infura, QuickNode,
  Ankr, etc.) — confirm the plan you have actually serves archival.

A non-archival RPC will produce errors like "missing trie node",
"header not found", or silent zero balances. Treat any of these as a
hard fail and stop — do not "patch" the test to work around them.

## Block pinning

Every PoC pins its fork block in the test file:

```solidity
uint256 constant FORK_BLOCK = 4_043_799;
```

The block must:

- Match the value in `metadata/registry.json` for the same entry.
- Be at or one block before the actual attack transaction.
- Use underscores for readability.

Drift between the test file and metadata is a CI-level failure once
the metadata validator is extended; for now treat it as a review-blocker.

## Verification command

The canonical command for one PoC:

```sh
cd EVM
forge test --match-path "test/<YYYY-MM>/*.t.sol" -vvv
```

Verbosity `-vvv` shows assertion failures and trace summaries; use
`-vvvv` for full traces while debugging.

For all PoCs (only realistic with full RPC coverage):

```sh
cd EVM
forge test -vvv
```

## Recording results

Verification records go to `reports/verification/<id>.md` using
[VERIFICATION_REPORT_TEMPLATE.md](VERIFICATION_REPORT_TEMPLATE.md).
The report should include:

- The exact command run.
- The local commit SHA.
- The fork block and chain alias used.
- The full pass / fail summary line from `forge test`.
- The output of each required assertion (or that it implicitly passed).
- Any environmental notes (RPC provider, archival tier).

The report is the primary evidence for promoting the entry's
`reproducibility` to `deterministic-confirmed`. Without a report, the
status stays at `deterministic-likely-but-unverified` regardless of
how confident the contributor is.

## Failure interpretation

When `forge test` fails on a PoC, classify the failure:

1. **Setup failure** — fork creation failed, addresses returned 0,
   token contracts return wrong values. Almost always RPC-level.
   Action: try a known-good archival endpoint; do not change the test.
2. **Compile failure** — Solidity / forge-std version drift. Action:
   record in `notes`, mark `compile-only` until fixed.
3. **Assertion failure** — exploit ran but post-state did not match
   expected. Possibilities: (a) genuine bug in the PoC, (b) public
   loss figures were rounded and the lower bound is too tight,
   (c) library behavior change. Investigate before relaxing assertions.
4. **Revert during exploit** — the attack path no longer reaches the
   profit step. Possible reasons: contract self-destructed since the
   incident, dependency redeployed, or fork block off-by-one. Investigate
   before patching.

Do not respond to failure by deleting assertions or weakening bounds
without a recorded justification.

## Verification cadence

- New PoC: full verification before merge.
- Library update (forge-std, foundry-rs, OpenZeppelin): re-run all
  affected tests; any drop from `deterministic-confirmed` is reported
  in the next PR.
- Quarterly: full re-run of all confirmed PoCs against the same fork
  blocks, with a fresh quality matrix and a new verification report
  set.

## What CI does and does not do

CI runs:

- `forge fmt --check`
- `forge build`
- `python3 scripts/validate_metadata.py`
- `python3 scripts/generate_registry.py --check`

CI runs fork tests only when the relevant RPC secrets are configured.
RPC URLs are not committed. Maintainers can also run fork tests locally
with their own RPC, attach the verification report to the PR, and CI
verifies that the metadata matches.

Any CI workflow that runs fork tests must:

- Use repository secrets, never embed URLs.
- Skip safely when the relevant secret is absent.
- Publish or reference a verification artifact before metadata is promoted.

Until an archival run transcript is committed, the verification report remains
the artifact of record.

---

## Public RPC vs Archival RPC

The distinction between public and archival RPC endpoints determines whether a
PoC can be reproduced at all, and whether a passing run constitutes final
verification.

### 1. Public RPC

- Useful for cheap smoke testing (does the test compile, link, and reach setup).
- May work for very recent fork blocks within the endpoint's prune window.
- Almost always rate-limited; bursty fork-test traffic frequently 429s.
- Typically does **not** serve historical state for old DeFi incidents.
- Cannot be relied upon for final verification of pre-2023 mainnet exploits.

### 2. Archival RPC

- Required for historical state access at arbitrary block numbers.
- Needed for almost every old mainnet exploit PoC in this archive.
- Required to reproduce fork state at the original attack block.
- Final deterministic verification should use an archival endpoint.

### 3. Common public-RPC failure messages

When a public endpoint cannot serve the requested historical state, the failure
typically presents as one of:

- `historical state is not available`
- `missing trie node`
- `header not found`
- `state unavailable`
- `project ID request rate exceeded`
- `timeout` / gateway / `502` / `504`
- Inconsistent or zero token balances at fork (silent archival failure)

### 4. Failure interpretation

| Symptom                                | Likely class                  |
| -------------------------------------- | ----------------------------- |
| Historical state / trie node errors    | `public-rpc-not-archival`     |
| 429 / rate limit / project ID exceeded | `public-rpc-rate-limited`     |
| Timeout / 502 / 504 / inconsistent     | `public-rpc-unstable`         |
| Setup revert before exploit logic      | possible code/config issue    |
| Exploit reverts mid-flow               | possible PoC logic issue      |
| Assertion fails post-execution         | possible PoC or bound issue   |
| Solidity / forge-std error             | repository issue              |

A historical-state failure is **not** evidence the PoC is broken. Classify it
as an RPC limitation; do not downgrade the PoC's reproducibility.

### 5. Required env vars

Public RPC smoke tests and final archival verification both read these env vars:

- `ETH_RPC_URL`
- `BASE_RPC_URL`
- `ARBITRUM_RPC_URL`
- `OPTIMISM_RPC_URL`
- `POLYGON_RPC_URL`
- `BSC_RPC_URL`
- `AVALANCHE_RPC_URL`

Never paste RPC URLs into code, tests, or reports. Endpoint family (e.g.
"public Ethereum RPC", "Alchemy archival") may be mentioned generically.

### 6. Example commands

```sh
export ETH_RPC_URL="..."        # archival recommended for old mainnet PoCs
export BASE_RPC_URL="..."

cd EVM
forge test --match-path test/2020-04/Exploit_2020-04.t.sol -vvv
```

### 7. Verification rule

A PoC may only be promoted to `deterministic-confirmed` when **all** of:

- The correct RPC alias is configured for the target chain.
- The fork block is pinned and matches `metadata/registry.json`.
- `setUp()` succeeds against that fork.
- The exploit path executes (no reverts mid-flow).
- All required assertion families pass with meaningful bounds.
- The verification report is updated with the command, transcript, and result.
- `metadata/registry.json` is updated honestly in the same change.

A `public-rpc-pass` result is a positive signal but does **not** automatically
constitute research-grade verification — assertion quality and fork-block
correctness still need human review. See
[`REPRODUCIBILITY_STANDARD.md`](REPRODUCIBILITY_STANDARD.md) for the full bar.

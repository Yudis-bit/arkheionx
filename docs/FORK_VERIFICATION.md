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
| `arbitrum`  | `ARB_RPC_URL`    | Arbitrum One, archival required.       |
| `optimism`  | `OP_RPC_URL`     | Optimism, archival required.           |
| `polygon`   | `POLYGON_RPC_URL`| Polygon PoS, archival required.        |
| `bnb`       | `BNB_RPC_URL`    | BNB Smart Chain, archival required.    |
| `avalanche` | `AVAX_RPC_URL`   | Avalanche C-Chain, archival required.  |

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
- `python scripts/validate_metadata.py`
- `python scripts/generate_registry.py --check`

CI does **not** run fork tests by default. RPC URLs are not committed.
Maintainers run fork tests locally with their own RPC, attach the
verification report to the PR, and CI verifies that the metadata
matches.

If a future workflow runs fork tests, it must:

- Use repository secrets, never embed URLs.
- Run on a schedule, not on every PR (cost).
- Publish a verification artifact.

Until then, the verification report is the artifact.

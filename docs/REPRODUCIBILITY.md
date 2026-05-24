# Reproducibility

What you need to run the PoCs in this repository, and what "reproduced" means.

## Environments

| VM | Runtime | Required for |
|---|---|---|
| EVM | [Foundry](https://book.getfoundry.sh/) | All EVM PoCs under `EVM/test/`. |
| SVM | [Anchor](https://www.anchor-lang.com/) + Solana CLI | Currently template only. |
| MoveVM | [Aptos CLI](https://aptos.dev/tools/aptos-cli/) | Currently template only. |

See [VM_SUPPORT.md](VM_SUPPORT.md) for the honest current state of each VM.

## EVM environment

### Required tooling

- `foundry` (`forge`, `cast`, `anvil`) — install via:

  ```sh
  curl -L https://foundry.paradigm.xyz | bash
  foundryup
  ```

- `git` (for cloning the repository and optional local reference data;
  `forge-std` is vendored under `EVM/lib/forge-std`)

### Required environment variables

EVM PoCs run against pinned forks. You need archival RPC endpoints for the
chains you want to exercise.

```sh
# .env (do not commit)
ETH_RPC_URL=https://your-ethereum-archive-node-endpoint
BASE_RPC_URL=https://your-base-archive-node-endpoint
```

Aliases declared in `EVM/foundry.toml`:

| Alias | Env var | Required for |
|---|---|---|
| `mainnet` | `ETH_RPC_URL` | Ethereum PoCs (17 currently merged). |
| `base` | `BASE_RPC_URL` | Base PoCs (currently `2025-11-moonwell`). |
| `arbitrum` | `ARBITRUM_RPC_URL` | Arbitrum-specific PoCs (none merged yet). |
| `optimism` | `OPTIMISM_RPC_URL` | Optimism-specific PoCs (none merged yet). |
| `polygon` | `POLYGON_RPC_URL` | Polygon-specific PoCs (none merged yet). |
| `bsc` | `BSC_RPC_URL` | BNB Chain PoCs (none merged yet). |
| `avalanche` | `AVALANCHE_RPC_URL` | Avalanche PoCs (none merged yet). |

If a chain alias is not configured, tests for that chain are expected to fail
fast with a clear message rather than silently pass. Aliases without merged
PoCs are present so future submissions can use them without a `foundry.toml`
edit.

### Archival requirement

Most PoCs reference state from blocks older than 128 blocks (the default
non-archival window for Erigon and Geth). Use a provider that exposes
archival history (Alchemy, QuickNode, Ankr archival, your own archival node).

If you only have a non-archival RPC, fork tests will fail with errors like
`missing trie node` or `state not available at block N`.

## Running a PoC

From the `EVM/` directory:

```sh
# Build only.
forge build

# Run a single PoC, with full traces.
forge test --match-path "test/2017-07/*.t.sol" -vvvv

# Run all PoCs.
forge test -vvv
```

`forge test` reads the relevant `*_RPC_URL` from the environment via the
alias declared in `foundry.toml` (`mainnet`, `base`, etc.). The fork block is
pinned inside each PoC file and must match `metadata/registry.json`.

## What counts as "reproduced"

A PoC is **reproduced** on your environment when:

1. `forge test` for that specific PoC exits with code 0.
2. Foundry traces show the expected calls (the post-mortem references match
   what you see).
3. The asserted post-state holds (drained balance, ownership change, etc.).

A PoC is **not reproduced** if:

- The fork failed to load due to RPC errors. Fix the RPC; the PoC's status is
  unknown.
- Assertions failed because the fork block produced unexpected state. This is
  a real failure and should be filed via the **Reproducibility issue** template.
- The test was skipped.

`metadata/registry.json` records the maintainer's last known reproduction
status per PoC. If you reproduce one and the metadata is stale, please open
a PR updating `reproducibility` and `status`.

## Common failure modes

| Symptom | Likely cause |
|---|---|
| `Error: invalid value for '--fork-url <URL>'` | `ETH_RPC_URL` empty or malformed. |
| `failed to get block N` | RPC is non-archival. |
| `EvmError: Revert` with no message | Your RPC returned different state than the pinned block expects (provider-side caching / pruning). |
| Tests pass without forking | Fork URL silently empty; some Foundry versions skip fork creation rather than fail. Verify the alias resolves. |

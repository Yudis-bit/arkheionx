# EVM (Foundry)

Foundry project for the EVM PoCs in [Arkheionx Vault](../README.md).

## Layout

```
EVM/
├── foundry.toml         Profile, remappings, RPC aliases
├── lib/forge-std        Submodule
├── src/                 Shared helpers (basetest.sol, interface.sol, tokenhelper.sol)
└── test/<YYYY-MM>/      One PoC per folder; one .t.sol per folder
```

## Setup

```sh
# From EVM/
forge install
```

The `forge-std` submodule is the only direct dependency. PoC-specific
interfaces live inline in the test files.

## RPC configuration

EVM PoCs run against pinned forks. Set the env vars for the chains you want
to exercise:

```sh
export ETH_RPC_URL=https://your-archive-node-endpoint   # mainnet alias
export BASE_RPC_URL=https://your-base-archive-endpoint  # base alias
```

The full alias table is in [foundry.toml](foundry.toml). Most PoCs need an
**archival** RPC; see [../docs/REPRODUCIBILITY.md](../docs/REPRODUCIBILITY.md).

## Running

```sh
# Single PoC, full traces.
forge test --match-path "test/2017-07/*.t.sol" -vvvv

# All PoCs.
forge test -vvv

# Format check (no RPC required).
forge fmt --check

# Build only (no RPC required).
forge build
```

## Adding a PoC

See [../docs/CONTRIBUTING.md](../docs/CONTRIBUTING.md) and
[../docs/RESEARCH_STANDARD.md](../docs/RESEARCH_STANDARD.md). Every PoC
must:

- Live in `test/<YYYY-MM>/Exploit_<YYYY-MM>.t.sol` (or the protocol-named
  pattern for new entries).
- Pin a `FORK_BLOCK` constant.
- Use a chain alias declared in `foundry.toml`.
- Assert post-exploit state.
- Have a matching entry in `../metadata/registry.json`.

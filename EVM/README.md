# EVM Verification Fixtures

This directory contains Foundry-based historical vulnerable-case fixtures used
for regression, taxonomy, and local review validation.

The legacy file names use `Exploit_*` because this repository originally grew
from historical incident reproduction work. In the current ArkheionX public
surface, treat these files as verification fixtures, not live exploit tooling.

ArkheionX does not automate exploitation, confirm severity automatically, or
replace human review. Run these fixtures only in authorized local environments
and with archival RPC access when a historical fork requires it.

## Layout

```
EVM/
├── foundry.toml         Profile, remappings, RPC aliases
├── lib/forge-std        Vendored Foundry standard library
├── src/                 Shared helpers (basetest.sol, interface.sol, tokenhelper.sol)
├── templates/           Legacy validation fixture template
└── test/<YYYY-MM>/      One historical vulnerable-case fixture per folder
```

## Setup

No install step is required for a normal checkout because `forge-std` is
vendored under `EVM/lib/forge-std`.

```sh
# From EVM/
forge build
```

`forge-std` is the only direct dependency. Fixture-specific interfaces live
inline in the test files.

## RPC configuration

EVM fixtures run against pinned forks. Set the env vars for the chains you want
to exercise:

```sh
export ETH_RPC_URL=https://your-archive-node-endpoint   # mainnet alias
export BASE_RPC_URL=https://your-base-archive-endpoint  # base alias
```

The full alias table is in [foundry.toml](foundry.toml). Most historical
fixtures need an **archival** RPC; see
[../docs/REPRODUCIBILITY.md](../docs/REPRODUCIBILITY.md).

## Running

```sh
# Single fixture, full traces.
forge test --match-path "test/2017-07/*.t.sol" -vvvv

# All fixtures.
forge test -vvv

# Format check (no RPC required).
forge fmt --check

# Build only (no RPC required).
forge build
```

## Adding a validation fixture

See [../docs/CONTRIBUTING.md](../docs/CONTRIBUTING.md) and
[../docs/RESEARCH_STANDARD.md](../docs/RESEARCH_STANDARD.md). Every fixture
must:

- Live in `test/<YYYY-MM>/Exploit_<YYYY-MM>.t.sol` (or the protocol-named
  pattern for new entries). The legacy `Exploit_` prefix is path compatibility,
  not a public product claim.
- Pin a `FORK_BLOCK` constant.
- Use a chain alias declared in `foundry.toml`.
- Assert the relevant post-condition or accounting/state transition.
- Have a matching entry in `../metadata/registry.json`.

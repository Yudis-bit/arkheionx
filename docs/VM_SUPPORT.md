# VM Support

Honest, current state of each VM family.

## Status table

| VM | Runtime | Status | Test command | CI | Notes |
|---|---|---|---|---|---|
| EVM | Foundry | Supported | `forge test` (from `EVM/`) | `evm.yml` | All currently merged PoCs are EVM. |
| SVM | Anchor / Solana CLI | Template | `anchor test` (from `SVM/`) | not wired | Single empty test stub. No real PoC yet. |
| MoveVM | Aptos CLI | Template | `aptos move test` (from `MoveVM/`) | not wired | Single empty entry function. No real PoC yet. |

Status values:

- **Supported**: real PoCs exist; CI builds and (where RPC is available) runs
  tests; reproducibility documented.
- **Experimental**: at least one real PoC; not yet covered by CI or
  reproducibility docs.
- **Template**: scaffolding only; no real PoCs.
- **Planned**: not in the repository yet.

## EVM

- Source of truth: `EVM/`
- Configuration: `EVM/foundry.toml`
- Tests: `EVM/test/<YYYY-MM>/<file>.t.sol`
- Helpers: `EVM/src/{basetest.sol,interface.sol,tokenhelper.sol}`
- Submodule: `EVM/lib/forge-std`
- CI: `.github/workflows/evm.yml`

EVM is the only VM that ships real, runnable PoCs today.

## SVM

- Source of truth: `SVM/`
- Configuration: `SVM/Anchor.toml`
- Test stub: `SVM/tests/exploit.ts` (empty; no `expect` calls)
- No on-chain program, no real exploit logic.

The directory exists so future PoCs have a place to land. **Do not interpret
the directory's existence as a claim that SVM PoCs are available.**

If you want to contribute the first real SVM PoC, start by reading
[CONTRIBUTING.md](CONTRIBUTING.md) and [RESEARCH_STANDARD.md](RESEARCH_STANDARD.md).

## MoveVM

- Source of truth: `MoveVM/`
- Configuration: `MoveVM/Move.toml` (Aptos framework, mainnet branch)
- Source stub: `MoveVM/sources/exploit.move` (empty entry function)
- No real exploit logic.

Same caveat as SVM: the directory is scaffolding, not a claim of coverage.

## Roadmap

See [ROADMAP.md](ROADMAP.md) for the plan to bring SVM and MoveVM out of
template state.

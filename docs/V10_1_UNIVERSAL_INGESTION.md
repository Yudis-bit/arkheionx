# V10.1 Universal Ingestion

## What Changed

V10.1 adds a repository ingestion layer that detects common Solidity layouts,
discovers source files outside a single default directory, counts contracts,
records artifact mode, and warns loudly when no contracts are indexed.

The war-run console and artifacts now include:

- framework detected
- Solidity files indexed
- contracts indexed
- artifact mode
- excluded dependency files
- zero-contract warnings

## How To Run

```bash
arkheionx war-run tests/fixtures/repos/hardhat_style_multisig_safe \
  --out artifacts/smoke-hardhat-style-multisig \
  --max-candidates 10 \
  --json
```

Useful options:

- `--include-tests`
- `--include-scripts`
- `--include-deps`
- `--framework auto|foundry|hardhat|truffle|brownie|generic`
- `--build-artifacts <path>`
- `--solidity-root <path>`

Relevant artifacts:

- `ingest-summary.json`
- `ingest-summary.md`

## Interpretation

- `framework` is one of the generic layout labels such as `foundry_style`,
  `hardhat_style`, `truffle_style`, `brownie_style`, `generic_solidity`, or
  `unknown`.
- `solidity_files_indexed` counts source files accepted after filters.
- `contracts_indexed` comes from semantic parsing after source discovery.
- `artifact_mode` shows whether compiler artifacts enriched fallback parsing.
- `ZERO_CONTRACTS_INDEXED` means the run did not analyze Solidity contracts and
  should not be treated as a clean result.

## Generic Fixtures

- `foundry_style_basic`
- `hardhat_style_basic`
- `truffle_style_basic`
- `brownie_style_basic`
- `generic_solidity_basic`
- `hardhat_style_multisig_safe`
- `truffle_style_legacy_multisig_replay`
- `generic_signature_binding_bug`

## Limitations

Discovery intentionally excludes dependency, generated, build, test, and script
paths unless explicitly included. Artifact ingestion enriches confidence but is
not mandatory; fallback source parsing still runs without artifacts.

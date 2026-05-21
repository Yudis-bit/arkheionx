# Scripts

Internal tooling for Arkheionx Vault. All scripts are pure-stdlib Python 3.11+
and run from the repository root unless noted.

## `validate_metadata.py`

Validates `metadata/registry.json` against `metadata/schema.json` plus the
repository-level rules in `docs/METADATA_SCHEMA.md` (unique IDs, existing
PoC paths, required references, embargoed-entry constraints).

```sh
python scripts/validate_metadata.py
```

Exits 0 on success, 1 on any error. CI runs this on every PR that touches
`metadata/`.

## `generate_registry.py`

Generates downstream artifacts from the canonical registry:

- The vulnerability registry table embedded in `README.md` (between the
  `<!-- BEGIN: registry -->` / `<!-- END: registry -->` markers).
- `web/public/metadata.json`, consumed by the Next.js app under `web/`.

```sh
# Write outputs.
python scripts/generate_registry.py

# CI / pre-commit mode: exit 1 if outputs would change.
python scripts/generate_registry.py --check
```

## `poc_factory.py`

Assist porting upstream PoCs (default source:
[SunWeb3Sec/DeFiHackLabs](https://github.com/SunWeb3Sec/DeFiHackLabs)) into
the EVM test tree. **Safe by default** — never writes without `--apply`,
never commits, never pushes.

### Workflow

```sh
# 1. Clone the reference data once (manual; the factory does not auto-clone).
git clone https://github.com/SunWeb3Sec/DeFiHackLabs.git .reference_data

# 2. List candidates not yet imported.
python scripts/poc_factory.py --report

# 3. Inspect the import plan for one candidate. No writes.
python scripts/poc_factory.py --target 2023-03-EulerFinance --dry-run

# 4. Import. Writes EVM/test/<target>/ but does not commit.
python scripts/poc_factory.py --target 2023-03-EulerFinance --apply
```

After `--apply`, the human is responsible for:

1. Reviewing the diff.
2. Running `forge build` and `forge test --match-path "test/<target>/*.t.sol"`.
3. Adding the metadata entry to `metadata/registry.json`.
4. Running `python scripts/validate_metadata.py` and `generate_registry.py`.
5. Committing.

### What the factory does not do

- No automatic `git clone`. The reference repository must be cloned by hand
  with provenance you trust.
- No `git add`, `git commit`, `git push`. Ever.
- No silent edits to exploit logic. The transformer rewrites pragma, contract
  name, and import paths; everything else is preserved verbatim.
- No live-target adaptation. PoCs are imported as-is for historical record.

### Provenance

When `--apply` writes a file, it injects a header with the upstream
repository URL and the upstream commit SHA (resolved from
`.reference_data/.git/HEAD`). Do not delete those lines from imported
files.

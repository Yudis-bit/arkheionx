# Scripts

Internal tooling for Arkheionx. The repository includes the historical
Arkheionx Vault archive plus local/static value-flow review, pre-audit
readiness, security memory, reporting, and feedback calibration tooling. All
scripts are pure-stdlib Python 3.11+ and run from the repository root unless
noted.

## Pre-v2 Module CLI Candidate

v1.9.0 defines a local module CLI candidate. v2.0.0 adds the installable
`arkheionx` console command. v2.0.1 keeps those interfaces as the current
functional foundation for the value-flow workbench direction. Shared helpers live under
`arkheionx/`, but the scripts in this directory remain supported entrypoints
for scans, generated reports, indexes, dashboards, and validation checks.

```sh
python3 -m pip install -e .
arkheionx version
arkheionx doctor
arkheionx scan .
python3 -m arkheionx.cli.main version
python3 -m arkheionx.cli.main doctor
python3 -m arkheionx.cli.main scan .
python3 -m arkheionx.cli.main validate-config --config .arkheionx.json
python3 -m arkheionx.cli.main test-plan --report reports/arkheionx-report.json
python3 -m arkheionx.cli.main search "oracle stale price"
```

The console and module CLIs wrap existing scripts/modules. They do not replace
`scripts/pre_audit_scan.py`.

Planned future commands such as `arkheionx flow`,
`arkheionx flow --test-gaps`, `arkheionx flow explain`,
`arkheionx flow test-template`, `arkheionx flow review-map`, and
`arkheionx flow verify` are roadmap items and are not available in v2.0.1.

## `validate_config.py`

Validates safe local Arkheionx config files and rejects dangerous keys such as
RPC URLs, private keys, live targets, remote clone targets, or attack modes.

```sh
python3 scripts/validate_config.py --config examples/arkheionx.config.example.json
python3 scripts/validate_config.py --config examples/configs/minimal.config.json --json
```

v1.8.0 report UX uses the same config surface for output profiles:

```sh
python3 scripts/pre_audit_scan.py \
  --root examples/amm-lending-hybrid-fixture \
  --config examples/configs/ci.config.json \
  --output examples/reports/ci-profile-report.md \
  --json-output examples/reports/ci-profile-report.json
```

## `pre_audit_scan.py`

Runs the GitHub-native pre-audit readiness scanner. It inspects local
repository files only and writes a Markdown report plus optional JSON output.
It does not call RPC endpoints, submit transactions, inspect deployed
contracts, or collect secrets.

```sh
python3 scripts/pre_audit_scan.py \
  --root . \
  --protocol-type auto \
  --output ARKHEIONX_PRE_AUDIT_REPORT.md \
  --json-output arkheionx-report.json \
  --summary-output ARKHEIONX_ACTION_SUMMARY.md \
  --comment-output ARKHEIONX_PR_COMMENT.md \
  --issue-checklist-output ARKHEIONX_ISSUE_CHECKLIST.md
```

Generate safe Foundry invariant skeletons:

```sh
python3 scripts/pre_audit_scan.py --root . --generate-invariant-skeletons
```

Run the v0.2.0 Vault Rule Pack explicitly:

```sh
python3 scripts/pre_audit_scan.py \
  --root . \
  --protocol-type vault \
  --output ARKHEIONX_VAULT_READINESS_REPORT.md \
  --json-output arkheionx-vault-report.json
```

v0.3.0 adds stable finding IDs, optional `.arkheionx.json` config,
documented suppression, Actions summary output, PR comment body generation,
and generated issue checklist output.

v0.4.0 adds SARIF output, compact baseline snapshots, report diff mode,
stable finding fingerprints, and optional CI readiness thresholds.

```sh
python3 scripts/pre_audit_scan.py \
  --root . \
  --protocol-type auto \
  --output ARKHEIONX_PRE_AUDIT_REPORT.md \
  --json-output arkheionx-report.json \
  --sarif-output arkheionx.sarif.json \
  --baseline-output arkheionx.baseline.json

python3 scripts/pre_audit_scan.py \
  --root . \
  --protocol-type auto \
  --compare-baseline arkheionx.baseline.json \
  --diff-output ARKHEIONX_DIFF.md \
  --diff-json-output arkheionx-diff.json
```

## `post_pr_comment.py`

Posts or updates the optional Arkheionx pull request comment when a GitHub
workflow explicitly provides a token and `pr-comment: "true"`.

```sh
python3 scripts/post_pr_comment.py \
  --comment-file ARKHEIONX_PR_COMMENT.md \
  --mode update
```

It expects `GITHUB_TOKEN`, `GITHUB_REPOSITORY`, and `GITHUB_EVENT_PATH` from
GitHub Actions. Missing context is skipped gracefully.

## `generate_search_index.py`

Generates [`reports/search_index.md`](../reports/search_index.md) from
`metadata/registry.json`, `metadata/search_terms.json`, and the product
surface map.

```sh
python3 scripts/generate_search_index.py
python3 scripts/generate_search_index.py --check
```

## `validate_metadata.py`

Validates `metadata/registry.json` against `metadata/schema.json` plus the
repository-level rules in `docs/METADATA_SCHEMA.md` (unique IDs, existing
PoC paths, required references, embargoed-entry constraints).

```sh
python3 scripts/validate_metadata.py
```

Exits 0 on success, 1 on any error. CI runs this on every PR that touches
`metadata/`.

## `generate_registry.py`

Generates downstream artifacts from the canonical registry:

- The vulnerability registry table embedded in `README.md` (between the
  `<!-- BEGIN: registry -->` / `<!-- END: registry -->` markers).

```sh
# Write outputs.
python3 scripts/generate_registry.py

# CI / pre-commit mode: exit 1 if outputs would change.
python3 scripts/generate_registry.py --check
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
python3 scripts/poc_factory.py --report

# 3. Inspect the import plan for one candidate. No writes.
python3 scripts/poc_factory.py --target 2023-03-EulerFinance --dry-run

# 4. Import. Writes EVM/test/<target>/ but does not commit.
python3 scripts/poc_factory.py --target 2023-03-EulerFinance --apply
```

After `--apply`, the human is responsible for:

1. Reviewing the diff.
2. Running `forge build` and `forge test --match-path "test/<target>/*.t.sol"`.
3. Adding the metadata entry to `metadata/registry.json`.
4. Running `python3 scripts/validate_metadata.py` and `python3 scripts/generate_registry.py`.
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

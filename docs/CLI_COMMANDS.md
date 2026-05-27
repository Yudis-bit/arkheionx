# CLI Commands

Arkheionx v1.9.0 exposes a pre-v2 local module CLI candidate.

## version

```sh
python3 -m arkheionx.cli.main version
```

Prints package version metadata, latest stable release, current milestone, and
next milestone.

## doctor

```sh
python3 -m arkheionx.cli.main doctor
```

Checks Python/package import health, lists rule packs, and prints the local
static safety posture.

## scan

```sh
python3 -m arkheionx.cli.main scan examples/amm-fixture \
  --protocol-type amm \
  --output examples/reports/cli-amm-report.md \
  --json-output examples/reports/cli-amm-report.json \
  --sarif-output examples/reports/cli-amm.sarif.json \
  --issue-plan-output examples/reports/cli-amm-issue-plan.json
```

The `scan` command wraps `scripts/pre_audit_scan.py`. Supported candidate
options include:

- `--protocol-type`
- `--config`
- `--output`
- `--json-output`
- `--sarif-output`
- `--issue-plan-output`
- `--summary-output`
- `--comment-output`
- `--baseline-output`
- `--compare-baseline`
- `--diff-output`
- `--diff-json-output`
- `--fail-under-score`
- `--min-confidence`
- `--output-profile`
- `--generate-invariant-skeletons`

CLI flags override config where applicable.

## validate-config

```sh
python3 -m arkheionx.cli.main validate-config \
  --config examples/arkheionx.config.example.json
```

Wraps `scripts/validate_config.py`.

## test-plan

```sh
python3 -m arkheionx.cli.main test-plan \
  --report examples/reports/cli-amm-report.json \
  --output examples/reports/cli-test-plan.md \
  --json-output examples/reports/cli-test-plan.json \
  --foundry-output examples/reports/ArkheionxCLIInvariants.t.sol
```

Wraps `scripts/generate_test_plan.py`.

## search

```sh
python3 -m arkheionx.cli.main search "oracle stale price"
python3 -m arkheionx.cli.main search "oracle stale price" --json
```

Wraps the local security-memory search helper. It reads committed metadata only
and does not call external services.

## Exit Codes

- `0`: success.
- `1`: runtime/check failed.
- `2`: invalid arguments/config.
- `3`: safety/config rejection.


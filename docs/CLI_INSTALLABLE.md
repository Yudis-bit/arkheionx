# Installable CLI

Arkheionx v2.0.0 adds the `arkheionx` console command for local editable
installs.

```sh
python3 -m pip install -e .
arkheionx --help
arkheionx version
arkheionx doctor
```

## Commands

```sh
arkheionx scan examples/amm-fixture --protocol-type amm
arkheionx validate-config --config examples/arkheionx.config.example.json
arkheionx test-plan --report examples/reports/amm-fixture-pre-audit-report.json
arkheionx search "oracle stale price"
```

The console command uses the same implementation as:

```sh
python3 -m arkheionx.cli.main ...
```

Existing scripts remain supported.

## Not Published

v2.0.0 does not publish a PyPI package. Install from this source checkout for
local development and validation.

## Safety

The CLI is for authorized local repositories only. It does not require secrets
or RPC keys and does not add live-chain behavior or exploit automation.


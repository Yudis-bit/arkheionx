# Pre-v2 CLI Candidate

Arkheionx v1.9.0 introduces a local module CLI candidate:

```sh
python3 -m arkheionx.cli.main version
python3 -m arkheionx.cli.main doctor
python3 -m arkheionx.cli.main scan .
python3 -m arkheionx.cli.main validate-config --config .arkheionx.json
python3 -m arkheionx.cli.main test-plan --report reports/arkheionx-report.json
python3 -m arkheionx.cli.main search "oracle stale price"
```

This is not the final v2 installable package. Existing scripts remain
supported and first-class until v2.0.0.

## Safety

The module CLI is local/static only. It does not perform RPC calls, live-chain
calls, transaction execution, deployed-contract scanning, remote cloning, or
exploit automation. Use it only on repositories you own or are authorized to
review.

## Status

- v1.9.0 defines and tests the future command surface.
- v2.0.0 is reserved for the installable CLI/package release.
- Script entrypoints remain documented and supported during the transition.


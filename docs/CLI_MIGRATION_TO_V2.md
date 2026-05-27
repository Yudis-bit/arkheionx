# CLI Migration To v2

Arkheionx v1.9.0 is a pre-v2 CLI candidate. It defines the command shape that
will become the installable v2 CLI, but it does not publish a package.

## What Stays Supported

These script entrypoints remain supported:

- `scripts/pre_audit_scan.py`
- `scripts/validate_config.py`
- `scripts/generate_test_plan.py`
- `scripts/search_knowledge.py`
- `scripts/generate_search_index.py`
- `scripts/generate_knowledge_graph.py`
- `scripts/generate_feedback_dashboard.py`
- `scripts/generate_paid_offer_index.py`
- `scripts/generate_ecosystem_report.py`

## Candidate Module Commands

The module CLI mirrors the most common workflows:

```sh
python3 -m arkheionx.cli.main scan .
python3 -m arkheionx.cli.main validate-config --config .arkheionx.json
python3 -m arkheionx.cli.main test-plan --report reports/arkheionx-report.json
python3 -m arkheionx.cli.main search "oracle stale price"
```

## v2 Expectations

v2.0.0 is expected to make the CLI installable while preserving the local/static
safety model. The v1.9.0 candidate exists so users can test command names,
options, exit codes, and docs before package publishing.

## Boundaries

The CLI migration does not add RPC, live-chain scanning, remote cloning,
transaction execution, secrets handling, or exploit automation. It is still a
pre-audit readiness workflow for authorized local repositories.


# CLI Migration To v2

Arkheionx v2.0.0 adds local editable installation and the `arkheionx` console
command. It does not publish a package to PyPI.

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

The module CLI remains available:

```sh
python3 -m arkheionx.cli.main scan .
python3 -m arkheionx.cli.main validate-config --config .arkheionx.json
python3 -m arkheionx.cli.main test-plan --report reports/arkheionx-report.json
python3 -m arkheionx.cli.main search "oracle stale price"
```

## v2 Expectations

Use the console command after editable install:

```sh
python3 -m pip install -e .
arkheionx scan .
arkheionx validate-config --config .arkheionx.json
arkheionx test-plan --report reports/arkheionx-report.json
arkheionx search "oracle stale price"
```

The script and module command paths remain supported during v2.0.0.

## Boundaries

The CLI migration does not add RPC, live-chain scanning, remote cloning,
transaction execution, secrets handling, or exploit automation. It is still a
pre-audit readiness workflow for authorized local repositories.

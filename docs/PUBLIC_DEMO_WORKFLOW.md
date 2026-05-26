# Public Demo Workflow

The public demo workflow gives new users a reproducible way to evaluate
Arkheionx without connecting wallets, RPC endpoints, private repositories, or
external services.

## Why This Exists

Arkheionx is easiest to trust when people can run it locally, inspect the
artifacts, and understand the limits. The demo workflow shows the full
GitHub-native loop:

scan -> report -> SARIF -> baseline -> issue plan -> Launch Report -> sprint
plan -> Contest Readiness report.

## Demo Fixtures

| Fixture | What It Shows |
|---|---|
| `examples/mini-vault` | Small vault-like shape and basic readiness output. |
| `examples/vault-risk-fixture` | Vault Rule Pack signals and missing invariants. |
| `examples/oracle-staking-fixture` | Oracle, reward accounting, access-control, and value-flow gaps. |
| `examples/oracle-staking-fixture-fixed` | Toy improved fixture for before/after calibration. |
| `examples/semantic-lite-fixture` | False-positive reduction and evidence-backed findings. |

All fixtures are toy examples. They are not production systems.

## Run Locally

Use the five-minute guide:

```sh
python3 scripts/pre_audit_scan.py \
  --root examples/oracle-staking-fixture \
  --protocol-type auto \
  --output examples/reports/demo-pre-audit-report.md \
  --json-output examples/reports/demo-report.json \
  --issue-plan-output examples/reports/demo-issue-plan.json \
  --launch-report-output examples/reports/demo-launch-report.md \
  --contest-readiness-output examples/reports/demo-contest-readiness.md
```

## Run With GitHub Actions

Use the manual workflow:

```yaml
name: Arkheionx Demo

on:
  workflow_dispatch:

permissions:
  contents: read

jobs:
  demo:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/pre-audit
        with:
          root: examples/oracle-staking-fixture
          protocol-type: auto
          output: examples/reports/demo-pre-audit-report.md
          json-output: examples/reports/demo-report.json
          issue-plan-output: examples/reports/demo-issue-plan.json
          launch-report-output: examples/reports/demo-launch-report.md
          sprint-plan-output: examples/reports/demo-sprint-plan.md
          contest-readiness-output: examples/reports/demo-contest-readiness.md
```

The repository includes `.github/workflows/arkheionx-demo.yml` for a fuller
manual demo artifact workflow.

## Outputs To Inspect

- `demo-executive-summary.md` for the short overview.
- `demo-pre-audit-report.md` for evidence-backed readiness findings.
- `demo-issue-plan.json` for remediation task structure.
- `demo-launch-report.md` for client-facing readiness delivery.
- `demo-contest-readiness.md` for scope and researcher onboarding prompts.
- `demo-remediation-roadmap.md` for phased remediation.

## Baseline And Diff

Create a baseline from the original fixture, then scan the fixed fixture to
compare score, evidence, and remaining gaps. Treat improvements as demo
signals, not proof of safety.

## Interpreting Readiness Gaps

Arkheionx uses readiness language:

- readiness gap;
- risk signal;
- review recommended;
- evidence-backed finding;
- historical pattern similarity;
- suggested defensive check.

It does not confirm vulnerabilities.

## Limitations

- Demo fixtures are internal toy examples.
- Scanner output is heuristic.
- Semantic-lite extraction is not a full Solidity compiler.
- Formal audit remains recommended before mainnet, material TVL, or user funds.

## Safety Boundaries

- No live-chain calls.
- No RPC required.
- No deployed-contract scanning.
- No exploit payload generation.
- No GitHub issues created by default.

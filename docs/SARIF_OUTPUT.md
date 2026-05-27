# SARIF Output

Arkheionx v0.4.0 can write SARIF v2.1.0 so readiness findings can be uploaded
to GitHub Code Scanning-compatible workflows.

SARIF output is a GitHub-native artifact. It is not a formal audit result and
does not confirm exploitable vulnerabilities.

## How Arkheionx Uses SARIF

- SARIF rules map to stable Arkheionx finding IDs such as `ARK-VLT-001`.
- SARIF results represent readiness gaps and review prompts.
- Result levels are mapped from readiness priority:
  - critical readiness gap: `error`
  - high readiness gap: `warning`
  - medium readiness gap: `warning`
  - low or informational: `note`
- Result properties include defensive metadata:
  - `readiness_gap: true`
  - `not_a_vulnerability_confirmation: true`
  - `not_formal_audit: true`
  - `category`
  - `confidence`
  - `historical_pattern_similarity`
  - `suggested_tests`
  - `confidence_reason`
  - `detection_sources`
  - `evidence_count`
  - `affected_functions`

Suppressed findings are not emitted as normal SARIF results. Suppression counts
and suppressed IDs appear in run properties.

v0.6.0 and later locations prefer semantic-lite evidence first, optional Slither evidence
second, affected files third, and README fallback only when no code evidence is
available.

## Local Command

```sh
python3 scripts/pre_audit_scan.py \
  --root examples/vault-risk-fixture \
  --protocol-type vault \
  --output examples/reports/vault-risk-fixture-pre-audit-report.md \
  --json-output examples/reports/vault-risk-fixture-pre-audit-report.json \
  --sarif-output examples/reports/vault-risk-fixture.sarif.json
```

## GitHub Code Scanning Workflow

Use a separate `upload-sarif` step in your workflow:

```yaml
name: Arkheionx Code Scanning

on:
  workflow_dispatch:
  pull_request:
    branches: [main]

permissions:
  contents: read
  security-events: write

jobs:
  arkheionx:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: Yudis-bit/DeFi-Exploit-PoCs/.github/actions/pre-audit@v1.2.0
        with:
          protocol-type: auto
          output: ARKHEIONX_PRE_AUDIT_REPORT.md
          json-output: arkheionx-report.json
          sarif-output: arkheionx.sarif.json
      - uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: arkheionx.sarif.json
```

Use `@main` only for development testing of changes after the latest stable
release.

## Limitations

- Locations prefer semantic-lite or optional Slither evidence when available,
  then fall back to affected files.
- Arkheionx does not perform a full semantic Solidity call graph.
- GitHub Code Scanning display language may look security-oriented, but
  Arkheionx SARIF results remain pre-audit readiness findings.
- Upload requires `security-events: write`.

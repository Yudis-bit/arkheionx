# GitHub Action Usage

The Arkheionx pre-audit action runs the local scanner inside GitHub Actions and
writes a Markdown report into the workflow workspace.

It requires no secrets, no RPC endpoint, and no network access from the
scanner itself.

## Basic Workflow

```yaml
name: Arkheionx Pre-Audit Scan

on:
  workflow_dispatch:
  pull_request:
    branches: [main]

jobs:
  pre-audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: Yudis-bit/DeFi-Exploit-PoCs/.github/actions/pre-audit@main
        with:
          root: "."
          protocol-type: "auto"
          output: "ARKHEIONX_PRE_AUDIT_REPORT.md"
          json-output: "arkheionx-report.json"
          generate-invariant-skeletons: "false"
          fail-on-critical-readiness-gap: "false"
          summary: "true"
```

## Vault Builder Workflow

For ERC4626-like vaults, strategy vaults, and share/accounting systems, pin the
protocol type to `vault` so the v0.2.0 Vault Rule Pack is used:

```yaml
name: Arkheionx Vault Readiness

on:
  workflow_dispatch:
  pull_request:
    branches: [main]

jobs:
  vault-readiness:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: Yudis-bit/DeFi-Exploit-PoCs/.github/actions/pre-audit@main
        with:
          root: "."
          protocol-type: "vault"
          output: "ARKHEIONX_VAULT_READINESS_REPORT.md"
          json-output: "arkheionx-vault-report.json"
          generate-invariant-skeletons: "true"
          fail-on-critical-readiness-gap: "false"
          summary: "true"
```

The vault report includes a Vault Rule Pack coverage section and a
`vault_rule_pack` object in JSON output.

## Pull Request Workflow

Use pull request scans to surface readiness gaps before code reaches `main`.
The default is non-blocking. To make critical readiness gaps block a PR, set:

```yaml
fail-on-critical-readiness-gap: "true"
```

This should be used carefully. Early-stage repositories may prefer reports
first and enforcement later.

## Manual Workflow

The `workflow_dispatch` trigger lets maintainers run readiness scans on demand,
for example before audit intake or before publishing a launch update.

## Local CLI Equivalent

```sh
python3 scripts/pre_audit_scan.py \
  --root . \
  --protocol-type auto \
  --output ARKHEIONX_PRE_AUDIT_REPORT.md \
  --json-output arkheionx-report.json
```

## JSON Output

Set `json-output` to write a machine-readable report:

```yaml
json-output: "arkheionx-report.json"
```

The JSON includes:

- protocol type and confidence;
- score and score band;
- score breakdown;
- scanned files;
- risk signals;
- historical pattern similarity;
- readiness gaps;
- suggested invariants;
- next steps;
- disclaimer.

## Invariant Skeleton Generation

To generate a safe Foundry skeleton:

```yaml
generate-invariant-skeletons: "true"
```

The action writes:

```text
test/invariant/ArkheionxReadinessInvariants.t.sol
```

The skeleton contains placeholders only. It has no live addresses, no RPC
calls, and no exploit logic.

## Inputs

| Input | Default | Purpose |
|---|---|---|
| `root` | `.` | Repository path to scan. |
| `protocol-type` | `auto` | `auto`, `vault`, `amm`, `lending`, `staking`, `oracle`, or `generic`. |
| `output` | `ARKHEIONX_PRE_AUDIT_REPORT.md` | Markdown report path. |
| `json-output` | empty | Optional JSON report path. |
| `generate-invariant-skeletons` | `false` | Create safe Foundry invariant skeletons. |
| `fail-on-critical-readiness-gap` | `false` | Fail only when explicitly enabled. |
| `create-issues` | `false` | Reserved for future local issue suggestions. No remote issues are created. |
| `summary` | `true` | Write a short report excerpt to the GitHub Actions job summary. |

## Troubleshooting

If no Solidity files are found:

- check the `root` input;
- confirm contracts are committed;
- confirm files are not only inside ignored build/cache folders.

If the protocol type looks wrong:

- set `protocol-type` manually;
- open a `False Positive Report` issue with the scanned signals.

If the score looks too high or too low:

- read the score breakdown before relying on the total;
- remember that this is a readiness heuristic, not a formal audit result.

## Limitations

The action does not:

- call RPC endpoints;
- inspect deployed contracts;
- submit transactions;
- create remote GitHub issues;
- prove that a repository is secure.

Use it as a pre-audit preparation step, then seek formal review before user
funds are at risk.

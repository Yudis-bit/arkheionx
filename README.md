# Arkheionx

GitHub-native DeFi Security Memory and Pre-Audit Readiness OS for indie
builders.

> Find exploit-pattern risks, missing invariants, and audit blockers before
> paying for a formal smart contract audit.

> Not an audit. A way to prepare for one.

Arkheionx is not a formal audit and not a security guarantee. It is a
defensive readiness layer for authorized repositories.

Arkheionx turns historical DeFi failures into practical GitHub-native readiness
checks for the next generation of indie protocols. The repository remains an
independent assertion-driven exploit PoC research archive, and now also acts as
a local scanner, GitHub Action, Markdown reporting system, searchable security
knowledge base, and service surface for authorized defensive work.

Maintained by **Yudistira Putra**, creator of Arkheionx - `arkheionx` /
[@Yudis-bit](https://github.com/Yudis-bit).

## Start Here

### If You Are An Indie DeFi Builder

1. Add the GitHub Action to an authorized repository.
2. Run a pre-audit readiness scan.
3. Read the generated Markdown report.
4. Review SARIF, PR comment, or issue-checklist output if enabled.
5. Fix readiness gaps and missing invariants.
6. Request a Launch Report or Pre-Audit Sprint only if you want manual
   readiness support.

### If You Are A Security Researcher

1. Explore the historical exploit archive.
2. Review assertion standards and root-cause docs.
3. Check maturity and verification status before making claims.
4. Contribute defensive case improvements, metadata, or scanner calibration.

## Latest Release

Latest stable release: **v0.4.0 - SARIF Output and Baseline Diff Mode**.

v0.4.0 adds:

- SARIF 2.1.0 output for GitHub Code Scanning-compatible workflows;
- compact baseline snapshots;
- report diff mode for new, resolved, unchanged, changed, and suppressed
  readiness gaps;
- stable finding fingerprints;
- optional CI thresholds that are disabled by default.

| Release | Focus | Status |
|---|---|---|
| v0.1.0 | Pre-Audit Readiness OS MVP | Released |
| v0.2.0 | Vault Rule Pack | Released |
| v0.3.0 | GitHub Action UX + PR Comment Mode | Released |
| v0.4.0 | SARIF Output + Baseline Diff Mode | Released |
| v0.4.1 | Public polish and release consistency | In preparation |

## The Five Pillars

1. **Arkheionx Memory** - historical DeFi exploit research, root-cause
   taxonomy, exploit primitives, broken invariants, failed assumptions,
   assertion families, reproducibility status, and case references.
2. **Arkheionx Readiness** - a GitHub-native pre-audit scanner for authorized
   repositories that generates practical Markdown and JSON reports.
3. **Arkheionx Tests** - suggested invariant tests, Foundry skeletons,
   readiness checklists, test coverage guidance, and audit preparation
   templates.
4. **Arkheionx Search** - searchable security knowledge base with tags,
   indexes, category maps, metadata, reports, and GitHub search terms.
5. **Arkheionx Market** - GitHub Sponsors, Launch Reports, Pre-Audit Sprints,
   Ecosystem Packs, training, and research sponsorship.

## What Arkheionx Is

- Historical DeFi exploit memory.
- Assertion-driven research archive.
- Pre-audit readiness scanner.
- GitHub Action.
- Markdown report generator.
- JSON report generator.
- Safe Foundry invariant skeleton generator.
- Searchable root-cause knowledge base.
- Indie-builder support and services surface.

## What Arkheionx Is Not

- Not a formal audit.
- Not a security guarantee.
- Not live-target abuse tooling.
- Not a bounty guarantee.
- Not an attack framework.
- Not a replacement for professional review.
- Not affiliated with any audit firm, contest platform, bounty program, or
  protocol unless a relationship is explicitly documented in committed public
  artifacts.

## Current Status

Honest snapshot from the current branch. Numeric values are regenerated from
[`metadata/registry.json`](metadata/registry.json) by
[`scripts/research_dashboard.py`](scripts/research_dashboard.py) and
[`scripts/poc_maturity_index.py`](scripts/poc_maturity_index.py).

| Metric | Value |
|---|---:|
| Total structured PoCs | 18 |
| Deterministic-confirmed L4+ entries | 0 |
| Assertion-hardened entries (medium / strong) | 11 |
| Strong static assertions | 7 |
| Medium static assertions | 4 |
| Weak static assertions | 7 |
| Public-RPC smoke attempted | 2 |
| Needs verification | 18 |
| EVM / Foundry | active |
| SVM / Anchor | scaffold only |
| MoveVM / Aptos | scaffold only |

`deterministic-confirmed` is reserved for entries that have been re-run on a
pinned archival fork on this branch and have a verification report under
[`reports/verification/`](reports/verification/). Static assertion quality is
measured separately and is not a substitute for archival fork verification.

Current dashboards:

- [`reports/research_dashboard.md`](reports/research_dashboard.md)
- [`reports/poc_maturity_index.md`](reports/poc_maturity_index.md)
- [`reports/poc_quality_matrix.md`](reports/poc_quality_matrix.md)

## Quick Start: GitHub Action

Use `@v0.4.0` for stable usage:

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
      - uses: Yudis-bit/DeFi-Exploit-PoCs/.github/actions/pre-audit@v0.4.0
        with:
          root: "."
          protocol-type: "auto"
          output: "ARKHEIONX_PRE_AUDIT_REPORT.md"
          json-output: "arkheionx-report.json"
          generate-invariant-skeletons: "false"
          fail-on-critical-readiness-gap: "false"
          summary: "true"
```

The action requires no secrets and no RPC endpoint. It scans local repository
files only.

Use `@main` only when you intentionally want the latest development changes.

## Pull Request Comment Mode

PR comment mode is opt-in. It posts or updates a concise readiness comment on
the pull request running the workflow.

Stable example:

```yaml
permissions:
  contents: read
  pull-requests: write
  issues: write

jobs:
  pre-audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: Yudis-bit/DeFi-Exploit-PoCs/.github/actions/pre-audit@v0.4.0
        with:
          protocol-type: "auto"
          json-output: "arkheionx-report.json"
          pr-comment: "true"
          github-token: ${{ secrets.GITHUB_TOKEN }}
          create-issue-checklist: "true"
```

Config-enabled scan:

```yaml
with:
  config: ".arkheionx.json"
```

Read:

- [`docs/GITHUB_ACTION_USAGE.md`](docs/GITHUB_ACTION_USAGE.md)
- [`docs/PR_COMMENT_MODE.md`](docs/PR_COMMENT_MODE.md)
- [`docs/GENERATED_ISSUE_CHECKLIST.md`](docs/GENERATED_ISSUE_CHECKLIST.md)
- [`docs/ARKHEIONX_CONFIG.md`](docs/ARKHEIONX_CONFIG.md)

## SARIF And Baseline Diff

SARIF results are readiness gaps, not confirmed vulnerabilities. Generate the
SARIF file with Arkheionx, then upload it with GitHub's SARIF action:

```yaml
- uses: Yudis-bit/DeFi-Exploit-PoCs/.github/actions/pre-audit@v0.4.0
  with:
    protocol-type: "auto"
    output: "ARKHEIONX_PRE_AUDIT_REPORT.md"
    json-output: "arkheionx-report.json"
    sarif-output: "arkheionx.sarif.json"

- uses: github/codeql-action/upload-sarif@v3
  if: always()
  with:
    sarif_file: arkheionx.sarif.json
```

Read:

- [`docs/SARIF_OUTPUT.md`](docs/SARIF_OUTPUT.md)
- [`docs/BASELINE_DIFF_MODE.md`](docs/BASELINE_DIFF_MODE.md)
- [`docs/CI_GATING.md`](docs/CI_GATING.md)

Create a readiness baseline:

```yaml
with:
  baseline-output: "arkheionx.baseline.json"
```

Compare a later scan against that baseline:

```yaml
with:
  compare-baseline: "arkheionx.baseline.json"
  diff-output: "ARKHEIONX_DIFF.md"
  diff-json-output: "arkheionx-diff.json"
```

## Quick Start: Local CLI

```sh
python3 scripts/pre_audit_scan.py \
  --root . \
  --protocol-type auto \
  --output ARKHEIONX_PRE_AUDIT_REPORT.md \
  --json-output arkheionx-report.json \
  --sarif-output arkheionx.sarif.json \
  --baseline-output arkheionx.baseline.json \
  --summary-output ARKHEIONX_ACTION_SUMMARY.md \
  --comment-output ARKHEIONX_PR_COMMENT.md \
  --issue-checklist-output ARKHEIONX_ISSUE_CHECKLIST.md
```

Vault builders can force the v0.2.0 Vault Rule Pack:

```sh
python3 scripts/pre_audit_scan.py \
  --root . \
  --protocol-type vault \
  --output ARKHEIONX_VAULT_READINESS_REPORT.md \
  --json-output arkheionx-vault-report.json \
  --generate-invariant-skeletons
```

Generate a safe Foundry invariant skeleton:

```sh
python3 scripts/pre_audit_scan.py \
  --root . \
  --protocol-type auto \
  --output ARKHEIONX_PRE_AUDIT_REPORT.md \
  --json-output arkheionx-report.json \
  --generate-invariant-skeletons
```

## Sample Report Excerpt

See the committed examples:

- Markdown: [`examples/reports/mini-vault-pre-audit-report.md`](examples/reports/mini-vault-pre-audit-report.md)
- JSON: [`examples/reports/mini-vault-pre-audit-report.json`](examples/reports/mini-vault-pre-audit-report.json)
- Actions summary: [`examples/reports/mini-vault-action-summary.md`](examples/reports/mini-vault-action-summary.md)
- PR comment body: [`examples/reports/mini-vault-pr-comment.md`](examples/reports/mini-vault-pr-comment.md)
- Issue checklist: [`examples/reports/mini-vault-issue-checklist.md`](examples/reports/mini-vault-issue-checklist.md)
- SARIF: [`examples/reports/mini-vault.sarif.json`](examples/reports/mini-vault.sarif.json)
- Baseline: [`examples/reports/mini-vault.baseline.json`](examples/reports/mini-vault.baseline.json)
- Diff report: [`examples/reports/mini-vault-diff.md`](examples/reports/mini-vault-diff.md)
- Fixture: [`examples/mini-vault/`](examples/mini-vault/)
- Vault Rule Pack Markdown: [`examples/reports/vault-risk-fixture-pre-audit-report.md`](examples/reports/vault-risk-fixture-pre-audit-report.md)
- Vault Rule Pack JSON: [`examples/reports/vault-risk-fixture-pre-audit-report.json`](examples/reports/vault-risk-fixture-pre-audit-report.json)
- Vault Rule Pack fixture: [`examples/vault-risk-fixture/`](examples/vault-risk-fixture/)

Excerpt:

```text
Readiness score: 73/100
Score band: Improving
Detected protocol type: vault
Historical pattern similarity:
- Vault accounting invariant readiness gap
- Reentrancy-sensitive value flow review recommended
- Privileged control and operational risk review recommended

Recommended next steps:
1. Add Foundry invariant tests for accounting, roles, and value-flow boundaries.
2. Add deposit/withdraw roundtrip, totalAssets consistency, and donation/inflation-resistance tests.
3. Review state update order and add malicious local receiver tests for callback-capable flows.
```

The report is a readiness artifact. It does not prove safety or confirm
exploitability.

## v0.2.0 Vault Rule Pack

Arkheionx v0.2.0 adds a vault-focused rule pack for indie builders working on
ERC4626-like vaults, strategy vaults, yield vaults, staking vaults, and
share/accounting systems.

It checks for readiness gaps around:

- ERC4626 preview/action consistency;
- shares/assets conversion and rounding;
- totalAssets external dependencies;
- donation and low-supply sensitivity;
- fee accounting;
- strategy gain/loss/debt lifecycle;
- withdrawal queue and cooldown lifecycle;
- oracle and pool-pricing assumptions;
- admin setters, pause, emergency, and upgrade boundaries.

Read [`docs/VAULT_RULE_PACK.md`](docs/VAULT_RULE_PACK.md).

## What The Scanner Checks

- Vault accounting and ERC4626-like share conversion.
- Vault strategies, fees, withdrawal queues, and totalAssets assumptions.
- Oracle assumptions.
- Reentrancy-sensitive value flows.
- Access control.
- Upgradeability.
- Reward accounting.
- AMM invariants.
- Lending and liquidation signals.
- Cross-chain message validation signals.
- Tests, assertions, invariant/fuzz coverage.
- Documentation readiness.
- CI readiness.
- Operational and admin readiness.

Output language is intentionally defensive: risk signal, readiness gap,
historical pattern similarity, missing invariant, review recommended, audit
blocker, and defensive check.

## Output Artifacts

| Artifact | Purpose |
|---|---|
| Markdown report | Human-readable readiness report and audit-prep checklist. |
| JSON report | Machine-readable score, findings, signals, outputs, and metadata. |
| SARIF report | GitHub Code Scanning-compatible readiness findings. |
| Baseline JSON | Compact readiness snapshot for future comparison. |
| Diff report | New, resolved, unchanged, changed, and suppressed readiness gaps. |
| Actions summary | Short CI summary for GitHub Actions runs. |
| PR comment body | Optional pull request feedback with top readiness gaps. |
| Issue checklist | Copyable remediation checklist for GitHub Issues. |

## Search Arkheionx

Start here:

- [`docs/SEARCH_GUIDE.md`](docs/SEARCH_GUIDE.md)
- [`reports/search_index.md`](reports/search_index.md)
- [`metadata/search_terms.json`](metadata/search_terms.json)
- [`metadata/registry.json`](metadata/registry.json)

Search examples:

```text
vault accounting
ERC4626
convertToShares
withdrawal queue
strategy accounting
share price manipulation
oracle manipulation
reentrancy-review
access-control-review
missing invariant
pre-audit readiness
root-cause analysis
Foundry invariant testing
```

Recommended GitHub topics:

```text
defi-security
smart-contract-security
solidity-security
foundry
pre-audit
audit-readiness
invariant-testing
exploit-research
root-cause-analysis
web3-security
indie-defi
security-tools
github-action
```

## Research Standard

Every mature PoC in the archive aims to carry:

- pinned fork block and explicit chain alias;
- protocol identity, attack transaction, and incident date;
- exploit primitive and attacker path;
- broken invariant;
- failed protocol assumption;
- hard post-state assertions;
- documented reproducibility status;
- external reference;
- verification report once runtime confirmation is achieved.

Core standards:

- [`docs/RESEARCH_STANDARD.md`](docs/RESEARCH_STANDARD.md)
- [`docs/POC_STANDARD.md`](docs/POC_STANDARD.md)
- [`docs/ASSERTION_STANDARD.md`](docs/ASSERTION_STANDARD.md)
- [`docs/REPRODUCIBILITY_STANDARD.md`](docs/REPRODUCIBILITY_STANDARD.md)
- [`docs/POC_MATURITY_MODEL.md`](docs/POC_MATURITY_MODEL.md)
- [`docs/EXPLOIT_TAXONOMY.md`](docs/EXPLOIT_TAXONOMY.md)
- [`docs/ROOT_CAUSE_PLAYBOOK.md`](docs/ROOT_CAUSE_PLAYBOOK.md)

## Documentation Map

| Need | Document |
|---|---|
| Understand the system | [`docs/PRE_AUDIT_READINESS_OS.md`](docs/PRE_AUDIT_READINESS_OS.md) |
| Install the GitHub Action | [`docs/GITHUB_ACTION_USAGE.md`](docs/GITHUB_ACTION_USAGE.md) |
| Use PR comments | [`docs/PR_COMMENT_MODE.md`](docs/PR_COMMENT_MODE.md) |
| Generate issue checklists | [`docs/GENERATED_ISSUE_CHECKLIST.md`](docs/GENERATED_ISSUE_CHECKLIST.md) |
| Use SARIF / Code Scanning | [`docs/SARIF_OUTPUT.md`](docs/SARIF_OUTPUT.md) |
| Track baseline diff | [`docs/BASELINE_DIFF_MODE.md`](docs/BASELINE_DIFF_MODE.md) |
| Configure suppressions | [`docs/ARKHEIONX_CONFIG.md`](docs/ARKHEIONX_CONFIG.md) |
| Understand scoring | [`docs/READINESS_SCORE.md`](docs/READINESS_SCORE.md) |
| Run vault-specific checks | [`docs/VAULT_RULE_PACK.md`](docs/VAULT_RULE_PACK.md) |
| Find builder support paths | [`docs/INDIE_BUILDER_OFFER.md`](docs/INDIE_BUILDER_OFFER.md) |
| Request paid support | [`SERVICES.md`](SERVICES.md) |
| Review monetization boundaries | [`docs/MONETIZATION.md`](docs/MONETIZATION.md) |
| Sponsor public work | [`docs/SPONSORSHIP.md`](docs/SPONSORSHIP.md) |
| Check roadmap | [`docs/ROADMAP.md`](docs/ROADMAP.md) |

## Monetization And Support

| Offer | Price | Purpose |
|---|---:|---|
| Free GitHub Action | Free | Basic readiness scan, Markdown report, optional SARIF, and baseline diff artifacts. |
| Indie Builder Sponsor | USD 29/month | Support public tooling, early previews, priority Q&A. |
| Protocol Pro Sponsor | USD 99/month | Deeper templates and priority issue support. |
| Launch Report | USD 299-499 | Manual review of generated report and prioritized fix checklist. |
| Pre-Audit Sprint | USD 1,000-2,000 | Manual readiness review, missing invariant plan, GitHub issue checklist. |
| Vault Launch Report | USD 299-499 | Vault Rule Pack review and prioritized vault fix checklist. |
| Vault Pre-Audit Sprint | USD 1,000-2,000 | Vault-focused invariant, strategy, oracle, and withdrawal lifecycle plan. |
| Ecosystem Pack | USD 5,000-20,000/month | Bulk readiness reports and builder security clinic. |
| Ecosystem Vault Readiness Pack | Custom | Bulk vault readiness reports and portfolio-level Markdown dashboard. |
| Research Sponsorship | Flexible | Fund public exploit-memory and readiness-rule work. |

Use [`SERVICES.md`](SERVICES.md) for requests and
[`docs/SPONSORSHIP.md`](docs/SPONSORSHIP.md) for sponsor boundaries.

## Ethics

Arkheionx is defensive only.

- Use only on repositories you own or are authorized to review.
- No live-target testing without authorization.
- No chain calls or RPC in the scanner.
- No transaction submission.
- No private key or mnemonic handling.
- No adapting historical PoCs to active systems.
- Formal audit recommended before mainnet, material TVL, or user funds.

Read [`docs/ETHICS.md`](docs/ETHICS.md).

## Repository Layout

```text
.
├── .github/actions/pre-audit/   GitHub Action wrapper
├── .github/workflows/           CI and validation workflows
├── EVM/                         Active Foundry exploit-memory project
├── SVM/                         Anchor scaffold only
├── MoveVM/                      Aptos Move scaffold only
├── docs/                        Research, readiness, ethics, growth docs
├── examples/                    Mini fixtures and generated sample reports
├── metadata/                    Registry, schema, search terms
├── reports/                     Dashboards, search index, verification reports
├── scripts/                     Registry and readiness tooling
├── templates/                   Report and invariant templates
├── README.md
└── SERVICES.md
```

## Roadmap

- **v0.1.0: scanner MVP.** Local scanner, GitHub Action, Markdown/JSON reports,
  mini-vault demo.
- **v0.2.0: vault rule pack.** Stronger vault accounting and ERC4626-specific
  readiness rules, vault-risk fixture, vault-specific scoring, report coverage,
  and scanner tests.
- **v0.3.0: GitHub Action UX.** Actions summary, optional PR comment mode,
  generated issue checklist, stable finding IDs, and local config suppression.
- **v0.4.0: SARIF and baseline diff mode.** SARIF output, readiness
  baselines, new/resolved/unchanged gap tracking, and explicit CI thresholds.
- **v0.4.1: public polish and release consistency.** README onboarding,
  stable `@v0.4.0` examples, and docs cleanup. In preparation.
- **v0.5.0: generated GitHub issue workflow and rule-pack expansion.**
  Opt-in issue creation workflow proposal plus staking/reward and oracle rule
  packs.
- **v1.0: stable GitHub-native pre-audit kit.** Documented interfaces,
  calibrated rules, release artifacts, contribution workflow.

Archive milestones remain honest:

- keep hardening weak PoCs;
- do not claim L4 or L5 without committed verification evidence;
- graduate SVM and MoveVM only when real entries exist.

## Contribution Path

Good contributions:

- improve scanner rules defensively;
- report false positives;
- add safe example fixtures;
- improve invariant skeletons;
- improve metadata and search terms;
- harden existing historical PoCs with better assertions;
- improve docs without inflating claims.

Start with:

- [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md)
- `Rule Request` issue template
- `False Positive Report` issue template
- `Research candidate` issue template
- `Assertion hardening` issue template

## Maintainer

Built by the creator of Arkheionx, a defensive research project focused on:

- DeFi exploit reproduction;
- assertion-driven security research;
- pre-audit readiness tooling;
- root-cause intelligence;
- indie-builder security support.

Clarity, standards, and honest verification are the brand.

## License And Disclaimer

All content is provided for defensive research, education, and authorized
pre-audit readiness use. Reproductions target historical, patched, or otherwise
resolved incidents. Nothing in this repository is investment, legal, or
security advice. The maintainer assumes no liability for downstream use.

## Vulnerability Registry

The table below is generated from `metadata/registry.json`. Do not hand-edit.
Run `python3 scripts/generate_registry.py` to regenerate.

<!-- BEGIN: registry -->

_Generated from `metadata/registry.json`. Run `python3 scripts/generate_registry.py` to regenerate. Total entries: 18._

| Date | Protocol | Chain | Severity | Category | Status | PoC |
|------|----------|-------|----------|----------|--------|-----|
| 2017-07 | Parity Multisig — initWallet hijack | ethereum | critical | access-control-failure | historical | [`EVM/test/2017-07/Exploit_2017-07.t.sol`](EVM/test/2017-07/Exploit_2017-07.t.sol) |
| 2017-11 | Parity Wallet Library — suicide | ethereum | critical | access-control-failure | historical | [`EVM/test/2017-11/Exploit_2017-11.t.sol`](EVM/test/2017-11/Exploit_2017-11.t.sol) |
| 2018-04 | BeautyChain (BEC) — batchTransfer overflow | ethereum | critical | arithmetic-precision-rounding | historical | [`EVM/test/2018-04/Exploit_2018-04.t.sol`](EVM/test/2018-04/Exploit_2018-04.t.sol) |
| 2018-10 | SpankChain — payment channel reentrancy | ethereum | high | reentrancy | historical | [`EVM/test/2018-10/Exploit_2018-10.t.sol`](EVM/test/2018-10/Exploit_2018-10.t.sol) |
| 2020-04 | Uniswap V1 — imBTC reentrancy | ethereum | high | reentrancy | historical | [`EVM/test/2020-04/Exploit_2020-04.t.sol`](EVM/test/2020-04/Exploit_2020-04.t.sol) |
| 2020-06 | Bancor — public safeTransferFrom on newly deployed contract | ethereum | high | access-control-failure | needs-verification | [`EVM/test/2020-06/Exploit_2020-06.t.sol`](EVM/test/2020-06/Exploit_2020-06.t.sol) |
| 2020-08 | Opyn — duplicate ETH option exercise | ethereum | high | invariant-bypass | historical | [`EVM/test/2020-08/Exploit_2020-08.t.sol`](EVM/test/2020-08/Exploit_2020-08.t.sol) |
| 2020-09 | bZx — iETH self-transfer double-write | ethereum | critical | accounting-mismatch | needs-verification | [`EVM/test/2020-09/Exploit_2020-09.t.sol`](EVM/test/2020-09/Exploit_2020-09.t.sol) |
| 2020-10 | Harvest Finance — fUSDT/fUSDC oracle manipulation | ethereum | critical | flash-loan-price-manipulation | historical | [`EVM/test/2020-10/Exploit_2020-10.t.sol`](EVM/test/2020-10/Exploit_2020-10.t.sol) |
| 2020-11 | Pickle Finance — swapExactJarForJar arbitrary-call cDAI strategy asset loss | ethereum | critical | unsafe-external-call | needs-verification | [`EVM/test/2020-11/Exploit_2020-11.t.sol`](EVM/test/2020-11/Exploit_2020-11.t.sol) |
| 2020-12 | Cover Protocol — Blacksmith claimRewards infinite mint | ethereum | critical | accounting-mismatch | needs-verification | [`EVM/test/2020-12/Exploit_2020-12.t.sol`](EVM/test/2020-12/Exploit_2020-12.t.sol) |
| 2021-01 | SushiSwap SushiMaker — DIGG/WBTC missing-bridge convert exploit | ethereum | high | amm-invariant-manipulation | needs-verification | [`EVM/test/2021-01/Exploit_2021-01.t.sol`](EVM/test/2021-01/Exploit_2021-01.t.sol) |
| 2021-02 | Yearn v1 DAI vault — Curve 3pool oracle manipulation | ethereum | critical | flash-loan-price-manipulation | historical | [`EVM/test/2021-02/Exploit_2021-02.t.sol`](EVM/test/2021-02/Exploit_2021-02.t.sol) |
| 2021-03 | DODO — CrowdPooling init reentrancy | ethereum | high | initialization-bug | historical | [`EVM/test/2021-03/Exploit_2021-03.t.sol`](EVM/test/2021-03/Exploit_2021-03.t.sol) |
| 2021-10 | Indexed Finance — DEFI5/CC10 reweight manipulation | ethereum | critical | amm-invariant-manipulation | historical | [`EVM/test/2021-10/Exploit_2021-10.t.sol`](EVM/test/2021-10/Exploit_2021-10.t.sol) |
| 2022-02 | BUILD Finance — governance takeover via low-quorum proposal | ethereum | high | governance-attack | needs-verification | [`EVM/test/2022-02/Exploit_2022-02.t.sol`](EVM/test/2022-02/Exploit_2022-02.t.sol) |
| 2025-11 | Moonwell — Chainlink oracle staleness on Base | base | high | oracle-manipulation | historical | [`EVM/test/2025-11/Exploit_2025-11.t.sol`](EVM/test/2025-11/Exploit_2025-11.t.sol) |
| 2025-12 | yETH — pool invariant manipulation | ethereum | critical | amm-invariant-manipulation | historical | [`EVM/test/2025-12/Exploit_2025-12.t.sol`](EVM/test/2025-12/Exploit_2025-12.t.sol) |

<!-- END: registry -->

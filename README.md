# Arkheionx

GitHub-native DeFi Security Memory and Pre-Audit Readiness OS for indie
builders.

Find exploit-pattern risks, missing invariants, and audit blockers before
paying for a formal smart contract audit.

> Not an audit. A way to prepare for one.

Arkheionx turns historical DeFi failures into practical GitHub-native readiness
checks for the next generation of indie protocols. The repository remains an
independent assertion-driven exploit PoC research archive, and now also acts as
a local scanner, GitHub Action, Markdown reporting system, searchable security
knowledge base, and service surface for authorized defensive work.

Maintained by **Yudistira Putra**, creator of Arkheionx - `arkheionx` /
[@Yudis-bit](https://github.com/Yudis-bit).

## Two Audiences, One System

For indie builders:

- run the pre-audit scanner locally or in GitHub Actions;
- get a Markdown readiness report and optional JSON output;
- identify missing invariants and audit blockers;
- generate safe Foundry invariant skeletons;
- prepare a cleaner formal audit scope.

For security researchers:

- study historical exploit root causes;
- improve PoC assertion quality;
- contribute case metadata and taxonomy;
- help grow the security memory layer;
- keep verification claims honest.

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
- Not live exploitation tooling.
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

Add this to an authorized repository:

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
```

The action requires no secrets and no RPC endpoint. It scans local repository
files only.

## Quick Start: Local CLI

```sh
python3 scripts/pre_audit_scan.py \
  --root . \
  --protocol-type auto \
  --output ARKHEIONX_PRE_AUDIT_REPORT.md \
  --json-output arkheionx-report.json
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

See the committed example:

- Markdown: [`examples/reports/mini-vault-pre-audit-report.md`](examples/reports/mini-vault-pre-audit-report.md)
- JSON: [`examples/reports/mini-vault-pre-audit-report.json`](examples/reports/mini-vault-pre-audit-report.json)
- Fixture: [`examples/mini-vault/`](examples/mini-vault/)

Excerpt:

```text
Readiness score: 70/100
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

## What The Scanner Checks

- Vault accounting.
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

## Search Arkheionx

Start here:

- [`docs/SEARCH_GUIDE.md`](docs/SEARCH_GUIDE.md)
- [`reports/search_index.md`](reports/search_index.md)
- [`metadata/search_terms.json`](metadata/search_terms.json)
- [`metadata/registry.json`](metadata/registry.json)

Search examples:

```text
vault accounting
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

## Product Docs

- [`docs/PRE_AUDIT_READINESS_OS.md`](docs/PRE_AUDIT_READINESS_OS.md)
- [`docs/GITHUB_ACTION_USAGE.md`](docs/GITHUB_ACTION_USAGE.md)
- [`docs/READINESS_SCORE.md`](docs/READINESS_SCORE.md)
- [`docs/INDIE_BUILDER_OFFER.md`](docs/INDIE_BUILDER_OFFER.md)
- [`docs/MONETIZATION.md`](docs/MONETIZATION.md)
- [`docs/SPONSORSHIP.md`](docs/SPONSORSHIP.md)
- [`docs/MARKETING_ENGINE.md`](docs/MARKETING_ENGINE.md)
- [`docs/ROADMAP.md`](docs/ROADMAP.md)
- [`SERVICES.md`](SERVICES.md)

## Monetization And Support

| Offer | Price | Purpose |
|---|---:|---|
| Free GitHub Action | Free | Basic readiness scan and Markdown report. |
| Indie Builder Sponsor | USD 29/month | Support public tooling, early previews, priority Q&A. |
| Protocol Pro Sponsor | USD 99/month | Deeper templates and priority issue support. |
| Launch Report | USD 299-499 | Manual review of generated report and prioritized fix checklist. |
| Pre-Audit Sprint | USD 1,000-2,000 | Manual readiness review, missing invariant plan, GitHub issue checklist. |
| Ecosystem Pack | USD 5,000-20,000/month | Bulk readiness reports and builder security clinic. |
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

- **v0.1: scanner MVP.** Local scanner, GitHub Action, Markdown/JSON reports,
  mini-vault demo.
- **v0.2: vault rule pack.** Stronger vault accounting and ERC4626-specific
  readiness rules.
- **v0.3: invariant skeleton generator.** Better protocol-specific skeletons
  and handler guidance.
- **v0.4: historical pattern mapping.** More precise mappings from registry
  categories to readiness checks.
- **v0.5: searchable memory layer.** Better generated search index and
  metadata tags.
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
| 2020-11 | Pickle Finance — swapExactJarForJar arbitrary-call drains cDAI strategy | ethereum | critical | unsafe-external-call | needs-verification | [`EVM/test/2020-11/Exploit_2020-11.t.sol`](EVM/test/2020-11/Exploit_2020-11.t.sol) |
| 2020-12 | Cover Protocol — Blacksmith claimRewards infinite mint | ethereum | critical | accounting-mismatch | needs-verification | [`EVM/test/2020-12/Exploit_2020-12.t.sol`](EVM/test/2020-12/Exploit_2020-12.t.sol) |
| 2021-01 | SushiSwap SushiMaker — DIGG/WBTC missing-bridge convert exploit | ethereum | high | amm-invariant-manipulation | needs-verification | [`EVM/test/2021-01/Exploit_2021-01.t.sol`](EVM/test/2021-01/Exploit_2021-01.t.sol) |
| 2021-02 | Yearn v1 DAI vault — Curve 3pool oracle manipulation | ethereum | critical | flash-loan-price-manipulation | historical | [`EVM/test/2021-02/Exploit_2021-02.t.sol`](EVM/test/2021-02/Exploit_2021-02.t.sol) |
| 2021-03 | DODO — CrowdPooling init reentrancy | ethereum | high | initialization-bug | historical | [`EVM/test/2021-03/Exploit_2021-03.t.sol`](EVM/test/2021-03/Exploit_2021-03.t.sol) |
| 2021-10 | Indexed Finance — DEFI5/CC10 reweight manipulation | ethereum | critical | amm-invariant-manipulation | historical | [`EVM/test/2021-10/Exploit_2021-10.t.sol`](EVM/test/2021-10/Exploit_2021-10.t.sol) |
| 2022-02 | BUILD Finance — governance takeover via low-quorum proposal | ethereum | high | governance-attack | needs-verification | [`EVM/test/2022-02/Exploit_2022-02.t.sol`](EVM/test/2022-02/Exploit_2022-02.t.sol) |
| 2025-11 | Moonwell — Chainlink oracle staleness on Base | base | high | oracle-manipulation | historical | [`EVM/test/2025-11/Exploit_2025-11.t.sol`](EVM/test/2025-11/Exploit_2025-11.t.sol) |
| 2025-12 | yETH — pool invariant manipulation | ethereum | critical | amm-invariant-manipulation | historical | [`EVM/test/2025-12/Exploit_2025-12.t.sol`](EVM/test/2025-12/Exploit_2025-12.t.sol) |

<!-- END: registry -->

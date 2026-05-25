# Arkheionx Search Index

GitHub-searchable index for Arkheionx Memory, Readiness, Tests, Search, and Market.

Use this page with GitHub search or local `rg` to find exploit primitives,
broken invariants, failed assumptions, readiness gaps, services, templates,
examples, and reports.

Current truth: 18 structured PoCs, 0 deterministic-confirmed L4+ entries,
EVM/Foundry active, SVM/Anchor and MoveVM/Aptos scaffold only.

## Product Surface Index

| Surface | Path | Search tags |
|---|---|---|
| README landing page | [`README.md`](../README.md) | arkheionx, pre-audit-readiness, security-memory |
| Changelog | [`CHANGELOG.md`](../CHANGELOG.md) | v0.4.1, v0.4.0 released, SARIF, baseline diff, release notes |
| Services | [`SERVICES.md`](../SERVICES.md) | Launch Report, Pre-Audit Sprint, Ecosystem Pack |
| Pre-Audit Readiness OS | [`docs/PRE_AUDIT_READINESS_OS.md`](../docs/PRE_AUDIT_READINESS_OS.md) | scanner, readiness gap, historical pattern similarity |
| GitHub Action usage | [`docs/GITHUB_ACTION_USAGE.md`](../docs/GITHUB_ACTION_USAGE.md) | github-action, SARIF, baseline diff, PR comment |
| PR comment mode | [`docs/PR_COMMENT_MODE.md`](../docs/PR_COMMENT_MODE.md) | pull-request, comment marker, GitHub token |
| Generated issue checklist | [`docs/GENERATED_ISSUE_CHECKLIST.md`](../docs/GENERATED_ISSUE_CHECKLIST.md) | issue checklist, remediation, finding IDs |
| Arkheionx config | [`docs/ARKHEIONX_CONFIG.md`](../docs/ARKHEIONX_CONFIG.md) | config, suppression, ignore paths |
| SARIF output | [`docs/SARIF_OUTPUT.md`](../docs/SARIF_OUTPUT.md) | SARIF, GitHub Code Scanning, readiness gap |
| Baseline diff mode | [`docs/BASELINE_DIFF_MODE.md`](../docs/BASELINE_DIFF_MODE.md) | baseline, diff mode, new resolved unchanged |
| CI gating | [`docs/CI_GATING.md`](../docs/CI_GATING.md) | fail threshold, fail-score-below, CI readiness gate |
| Readiness score | [`docs/READINESS_SCORE.md`](../docs/READINESS_SCORE.md) | score bands, audit blockers, invariant testing |
| Vault Rule Pack | [`docs/VAULT_RULE_PACK.md`](../docs/VAULT_RULE_PACK.md) | ERC4626, vault accounting, share accounting |
| Indie builder offer | [`docs/INDIE_BUILDER_OFFER.md`](../docs/INDIE_BUILDER_OFFER.md) | indie-defi, launch preparation, paid path |
| Search guide | [`docs/SEARCH_GUIDE.md`](../docs/SEARCH_GUIDE.md) | search tags, root-cause analysis, broken invariant |
| Marketing engine | [`docs/MARKETING_ENGINE.md`](../docs/MARKETING_ENGINE.md) | growth, positioning, GitHub-only funnel |
| Monetization | [`docs/MONETIZATION.md`](../docs/MONETIZATION.md) | sponsors, revenue ladder, services |
| Sponsorship | [`docs/SPONSORSHIP.md`](../docs/SPONSORSHIP.md) | funding, research sponsorship, public work |
| Ethics | [`docs/ETHICS.md`](../docs/ETHICS.md) | defensive-only, authorized review, no live targeting |
| Roadmap | [`docs/ROADMAP.md`](../docs/ROADMAP.md) | release roadmap, rule packs, GitHub-native |
| Mini-vault fixture | [`examples/mini-vault/README.md`](../examples/mini-vault/README.md) | vault, fixture, scanner demo |
| Vault-risk fixture | [`examples/vault-risk-fixture/README.md`](../examples/vault-risk-fixture/README.md) | ERC4626, strategy vault, Vault Rule Pack |
| Sample Markdown report | [`examples/reports/mini-vault-pre-audit-report.md`](../examples/reports/mini-vault-pre-audit-report.md) | readiness report, vault, example |
| Vault-risk Markdown report | [`examples/reports/vault-risk-fixture-pre-audit-report.md`](../examples/reports/vault-risk-fixture-pre-audit-report.md) | vault readiness, ERC4626, readiness gaps |
| Sample JSON report | [`examples/reports/mini-vault-pre-audit-report.json`](../examples/reports/mini-vault-pre-audit-report.json) | json-output, automation, example |
| Vault-risk JSON report | [`examples/reports/vault-risk-fixture-pre-audit-report.json`](../examples/reports/vault-risk-fixture-pre-audit-report.json) | vault_rule_pack, json-output, example |
| Mini-vault action summary | [`examples/reports/mini-vault-action-summary.md`](../examples/reports/mini-vault-action-summary.md) | GitHub Actions summary, score, top gaps |
| Vault-risk PR comment | [`examples/reports/vault-risk-fixture-pr-comment.md`](../examples/reports/vault-risk-fixture-pr-comment.md) | PR comment, marker, top gaps |
| Vault-risk issue checklist | [`examples/reports/vault-risk-fixture-issue-checklist.md`](../examples/reports/vault-risk-fixture-issue-checklist.md) | issue checklist, readiness remediation, finding IDs |
| Vault-risk SARIF report | [`examples/reports/vault-risk-fixture.sarif.json`](../examples/reports/vault-risk-fixture.sarif.json) | SARIF, Code Scanning, readiness result |
| Vault-risk baseline | [`examples/reports/vault-risk-fixture.baseline.json`](../examples/reports/vault-risk-fixture.baseline.json) | baseline, finding fingerprint, readiness snapshot |
| Vault-risk diff report | [`examples/reports/vault-risk-fixture-diff.md`](../examples/reports/vault-risk-fixture-diff.md) | baseline diff, new resolved unchanged, remediation tracking |
| Arkheionx config example | [`examples/arkheionx.config.example.json`](../examples/arkheionx.config.example.json) | config, suppression, ignore paths |
| Pre-audit scanner | [`scripts/pre_audit_scan.py`](../scripts/pre_audit_scan.py) | cli, scanner, standard-library |
| PR comment poster | [`scripts/post_pr_comment.py`](../scripts/post_pr_comment.py) | GitHub API, PR comment, marker update |
| Report template | [`templates/pre_audit_report.md`](../templates/pre_audit_report.md) | template, Markdown report, disclaimer |
| Invariant skeleton template | [`templates/invariant_skeletons/ArkheionxReadinessInvariants.t.sol`](../templates/invariant_skeletons/ArkheionxReadinessInvariants.t.sol) | Foundry, invariant, skeleton |

## Search Term Index

| Term | Aliases | Category | Related checks | Tags |
|---|---|---|---|---|
| `Arkheionx` | Arkheionx Security Memory, Arkheionx Readiness, pre-audit readiness OS, GitHub-native security memory | product | GitHub Action, Markdown report, SARIF output, baseline diff | arkheionx, security-memory, pre-audit-readiness, indie-defi |
| `GitHub Action` | pre-audit action, Arkheionx action, GitHub-native scanner, Actions summary | GitHub-native workflow | Markdown report, JSON report, PR comment, issue checklist, SARIF | github-action, ci, pre-audit-readiness |
| `security memory` | DeFi security memory, historical exploit memory, root-cause knowledge base, security knowledge base | research archive | registry, search index, research dashboard, PoC maturity index | security-memory, root-cause-analysis, exploit-research |
| `readiness gap` | audit blocker, risk signal, review recommended, missing invariant | pre-audit readiness | finding ID, finding fingerprint, issue checklist, baseline diff | readiness-gap, audit-readiness, defensive-review |
| `historical exploit pattern` | historical pattern similarity, exploit primitive, broken invariant, failed assumption | research archive | registry metadata, search guide, scanner historical patterns | historical-exploit-pattern, root-cause-analysis, defi-security |
| `indie DeFi` | indie builder, solo DeFi founder, grant-funded builder, small DAO | audience | Launch Report, Pre-Audit Sprint, GitHub Action | indie-defi, builder-security, pre-audit |
| `vault accounting` | share accounting, totalAssets, pricePerShare, convertToShares, convertToAssets | pre-audit readiness | totalAssets consistency, deposit-withdraw roundtrip, share price manipulation resistance | vault-security, invariant-testing, audit-readiness |
| `oracle manipulation` | price manipulation, stale oracle, TWAP, latestRoundData, spot price | historical exploit pattern | stale price rejection, decimals normalization, price bounds, TWAP or sanity check | oracle-risk, price-assumptions, defi-security |
| `reentrancy` | callback, external call, value flow, nonReentrant, checks effects interactions | historical exploit pattern | malicious local receiver test, state update order, callback boundary review | reentrancy-review, value-flow, smart-contract-security |
| `access control` | onlyOwner, AccessControl, admin, role, privileged setter | pre-audit readiness | unauthorized role rejection, privileged setter tests, pause behavior | access-control-review, admin-risk, operational-security |
| `upgradeability` | initializer, reinitializer, proxy, UUPS, implementation, storage gap | pre-audit readiness | initializer runs once, upgrade authorization, storage layout documentation | upgradeability, initialization-bug, proxy-review |
| `reward accounting` | rewardPerToken, accumulator, index, claim, emission | pre-audit readiness | reward conservation, no overclaim, index monotonicity, precision tests | reward-accounting, staking, precision |
| `AMM invariant` | reserve manipulation, liquidity, swap invariant, kLast, sqrtPriceX96 | historical exploit pattern | invariant conservation, swap does not create value, liquidity proportionality | amm-invariant, liquidity, reserve-manipulation |
| `lending liquidation` | collateral, debt, healthFactor, liquidate, loanToValue | pre-audit readiness | collateralization invariant, liquidation solvency, interest index monotonicity | lending, liquidation, collateral, oracle-risk |
| `cross-chain validation` | bridge, endpoint, relayer, message, LayerZero, CCIP, Hyperlane, Wormhole | pre-audit readiness | source validation, sender validation, replay rejection, trusted endpoint documentation | cross-chain, bridge-validation, message-authentication |
| `pre-audit readiness` | audit preparation, readiness score, audit blocker, missing invariant, launch report | product | readiness report, GitHub Action, Markdown report, JSON report | pre-audit, audit-readiness, indie-defi, github-action |
| `ERC4626` | vault standard, previewDeposit, previewWithdraw, maxRedeem, asset() | vault rule pack | preview/action equivalence, convertToShares/convertToAssets consistency, max function boundaries | erc4626, vault-security, share-accounting, pre-audit |
| `share inflation` | donation sensitivity, low supply share accounting, share price manipulation, donation risk class | vault rule pack | donation tests, first deposit tests, rounding direction tests, low supply tests | share-inflation-risk, donation-sensitivity, vault-invariant |
| `strategy accounting` | strategy debt, harvest, gain, loss, totalDebt, withdrawFromStrategy | vault rule pack | mock strategy gain, mock strategy loss, debt update, harvest/report tests | strategy-accounting, gain-loss, vault-lifecycle |
| `withdrawal queue` | requestWithdraw, claimWithdraw, cooldown, pendingWithdraw, liquidityBuffer | vault rule pack | request lifecycle, claim lifecycle, cancel lifecycle, liquidity buffer tests | withdrawal-queue, vault-lifecycle, liquidity-buffer |
| `oracle-dependent vault` | LP token pricing, pool price, Chainlink vault, Yearn-style vault risk, Harvest-style oracle risk | vault rule pack | stale price rejection, pool price bounds, TWAP sanity check, decimals normalization | oracle-risk, vault-pricing, pool-pricing |
| `vault invariant tests` | totalAssets invariant, share accounting invariant, fee accounting invariant, strategy loss invariant | vault rule pack | totalAssets consistency, deposit-withdraw roundtrip, fee accounting conservation, strategy loss handling | vault-invariant, foundry, invariant-testing |
| `PR readiness comment` | pull request comment, GitHub Action comment, Arkheionx PR comment, readiness comment | GitHub Action UX | score summary, top readiness gaps, marker update mode | github-action, pull-request, pre-audit-readiness |
| `generated issue checklist` | issue checklist, remediation checklist, launch checklist, readiness checklist | GitHub Action UX | finding IDs, suggested tests, documentation tasks | issue-checklist, audit-readiness, indie-defi |
| `finding IDs` | ARK-VLT-001, ARK-ORC-001, stable readiness finding, readiness gap ID | report UX | JSON findings, Markdown gap sections, suppression by ID | finding-id, json-schema, report-ux |
| `Arkheionx config` | .arkheionx.json, false positive suppression, ignore paths, suppress findings | configuration | suppressed_findings, ignore_paths, additional_search_tags | config, false-positive, local-static-analysis |
| `SARIF` | SARIF output, sarif-output, GitHub Code Scanning, upload-sarif | GitHub security workflow | readiness_gap properties, not_formal_audit, SARIF rules and results | sarif, code-scanning, github-security-workflow |
| `GitHub Code Scanning` | code scanning, security-events, upload-sarif, CodeQL upload SARIF | GitHub security workflow | security-events: write, github/codeql-action/upload-sarif, readiness result severity | github-code-scanning, sarif, pre-audit-readiness |
| `baseline diff` | readiness baseline, compare baseline, diff mode, pre-audit diff | report UX | new findings, resolved findings, unchanged findings, changed findings | baseline-diff, readiness-tracking, report-diff |
| `finding fingerprint` | stable fingerprint, fingerprint_version, readiness fingerprint, finding hash | report UX | id, category, title, detected signals, affected files | finding-fingerprint, baseline, json-schema |
| `CI gating` | fail threshold, fail-score-below, fail-on-new-high, fail-on-unsuppressed-high | GitHub Action UX | score threshold, new high readiness gaps, unsuppressed high readiness gaps | ci-gating, fail-threshold, audit-readiness |
| `new readiness gaps` | new findings, new gaps, regression readiness, diff new | baseline diff | compare-baseline, diff-output, diff-json-output | new-readiness-gaps, baseline-diff, pre-audit-diff |
| `resolved readiness gaps` | resolved findings, closed gaps, remediated readiness, diff resolved | baseline diff | baseline comparison, remediation tracking, diff report | resolved-readiness-gaps, baseline-diff, remediation |
| `pre-audit diff` | readiness diff, report diff, baseline comparison, diff report | GitHub-native workflow | new/resolved/unchanged counts, PR comment diff, issue checklist diff | pre-audit-diff, readiness-baseline, github-action |
| `GitHub security workflow` | Actions security workflow, Code Scanning workflow, pre-audit CI workflow, security-events | GitHub-native workflow | SARIF upload, Actions summary, PR comment, baseline diff | github-security-workflow, code-scanning, pre-audit-readiness |

## Historical Memory Index

Generated from `metadata/registry.json`.

| ID | Protocol | Category | Severity | Tags | Path |
|---|---|---|---|---|---|
| `2017-07-parity-multisig` | Parity Multisig Wallet | `access-control-failure` | `critical` | template-reference, phase-5-strong | [`EVM/test/2017-07/Exploit_2017-07.t.sol`](../EVM/test/2017-07/Exploit_2017-07.t.sol) |
| `2017-11-parity-suicide` | Parity Multisig Library | `access-control-failure` | `critical` | - | [`EVM/test/2017-11/Exploit_2017-11.t.sol`](../EVM/test/2017-11/Exploit_2017-11.t.sol) |
| `2018-04-bec-token` | BeautyChain Token (BEC) | `arithmetic-precision-rounding` | `critical` | - | [`EVM/test/2018-04/Exploit_2018-04.t.sol`](../EVM/test/2018-04/Exploit_2018-04.t.sol) |
| `2018-10-spankchain` | SpankChain | `reentrancy` | `high` | - | [`EVM/test/2018-10/Exploit_2018-10.t.sol`](../EVM/test/2018-10/Exploit_2018-10.t.sol) |
| `2020-04-uniswap-imbtc` | Uniswap V1 / imBTC | `reentrancy` | `high` | - | [`EVM/test/2020-04/Exploit_2020-04.t.sol`](../EVM/test/2020-04/Exploit_2020-04.t.sol) |
| `2020-06-balancer-deflationary` | Bancor | `access-control-failure` | `high` | phase-6a-reclassified, phase-6e-assertion-patch | [`EVM/test/2020-06/Exploit_2020-06.t.sol`](../EVM/test/2020-06/Exploit_2020-06.t.sol) |
| `2020-08-opyn` | Opyn v1 | `invariant-bypass` | `high` | - | [`EVM/test/2020-08/Exploit_2020-08.t.sol`](../EVM/test/2020-08/Exploit_2020-08.t.sol) |
| `2020-09-bzx-ifusdc` | bZx | `accounting-mismatch` | `critical` | phase-6a-reclassified, phase-6f-asserted | [`EVM/test/2020-09/Exploit_2020-09.t.sol`](../EVM/test/2020-09/Exploit_2020-09.t.sol) |
| `2020-10-harvest` | Harvest Finance | `flash-loan-price-manipulation` | `critical` | - | [`EVM/test/2020-10/Exploit_2020-10.t.sol`](../EVM/test/2020-10/Exploit_2020-10.t.sol) |
| `2020-11-cheese-bank` | Pickle Finance | `unsafe-external-call` | `critical` | phase-6a-reclassified | [`EVM/test/2020-11/Exploit_2020-11.t.sol`](../EVM/test/2020-11/Exploit_2020-11.t.sol) |
| `2020-12-warp-finance` | Cover Protocol | `accounting-mismatch` | `critical` | phase-6a-reclassified, phase-6g-asserted | [`EVM/test/2020-12/Exploit_2020-12.t.sol`](../EVM/test/2020-12/Exploit_2020-12.t.sol) |
| `2021-01-saddle` | SushiSwap (SushiMaker) | `amm-invariant-manipulation` | `high` | phase-6a-reclassified | [`EVM/test/2021-01/Exploit_2021-01.t.sol`](../EVM/test/2021-01/Exploit_2021-01.t.sol) |
| `2021-02-yearn-v1-dai` | Yearn v1 (yDAI vault) | `flash-loan-price-manipulation` | `critical` | - | [`EVM/test/2021-02/Exploit_2021-02.t.sol`](../EVM/test/2021-02/Exploit_2021-02.t.sol) |
| `2021-03-dodo-crowdpool` | DODO V2 CrowdPooling | `initialization-bug` | `high` | - | [`EVM/test/2021-03/Exploit_2021-03.t.sol`](../EVM/test/2021-03/Exploit_2021-03.t.sol) |
| `2021-10-indexed-finance` | Indexed Finance | `amm-invariant-manipulation` | `critical` | - | [`EVM/test/2021-10/Exploit_2021-10.t.sol`](../EVM/test/2021-10/Exploit_2021-10.t.sol) |
| `2022-02-dexible` | BUILD Finance | `governance-attack` | `high` | phase-6a-reclassified, phase-7b-asserted | [`EVM/test/2022-02/Exploit_2022-02.t.sol`](../EVM/test/2022-02/Exploit_2022-02.t.sol) |
| `2025-11-moonwell` | Moonwell | `oracle-manipulation` | `high` | - | [`EVM/test/2025-11/Exploit_2025-11.t.sol`](../EVM/test/2025-11/Exploit_2025-11.t.sol) |
| `2025-12-yeth` | yETH | `amm-invariant-manipulation` | `critical` | - | [`EVM/test/2025-12/Exploit_2025-12.t.sol`](../EVM/test/2025-12/Exploit_2025-12.t.sol) |

## High-Value Searches

```text
vault accounting
ERC4626
totalAssets
convertToShares
convertToAssets
share price manipulation
share inflation
donation risk class
strategy accounting
withdrawal queue
fee accounting
oracle-dependent vault
vault invariant tests
PR readiness comment
generated issue checklist
finding IDs
.arkheionx.json
SARIF
GitHub Code Scanning
baseline diff
readiness baseline
finding fingerprint
CI gating
fail threshold
new readiness gaps
resolved readiness gaps
pre-audit diff
GitHub security workflow
oracle manipulation
flash loan price manipulation
reentrancy
access control
initialization bug
upgradeability
reward accounting
AMM invariant
lending liquidation
bridge validation
historical exploit pattern
pre-audit readiness
indie DeFi
audit blocker
missing invariant
Foundry invariant testing
root-cause analysis
```

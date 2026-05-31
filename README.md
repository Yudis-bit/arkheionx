# Arkheionx

A local-first DeFi value-flow workbench.

**Map the money flow. Find the missing tests.**

Arkheionx helps DeFi builders and security researchers map how value moves
through a protocol, identify critical assumptions, and find missing security
tests.

Foundry tells you if your tests pass.
Arkheionx shows where value moves - and what you forgot to test.

`Stable: v2.0.0` | `Python: 3.x` | `Mode: local/static` | `No RPC required` | `Outputs: SARIF / JSON / Markdown`

It combines:

- local/static DeFi value-flow review;
- evidence-backed findings;
- SARIF output;
- GitHub issue plans;
- Launch / Contest / Sprint reports;
- security memory graph;
- historical exploit-pattern knowledge;
- feedback and rule calibration workflows.

Arkheionx started as an independent DeFi exploit PoC archive and now includes a
local-first value-flow workbench, security memory graph, reports, issue plans,
test-plan generation, and advanced pre-audit readiness workflows. Maintained by
**Yudistira Putra**, creator of Arkheionx -
`arkheionx` / [@Yudis-bit](https://github.com/Yudis-bit).

## What Arkheionx Is For

- Mapping DeFi value flows.
- Finding missing value-flow tests.
- Identifying high-signal review areas.
- Generating reports, test plans, SARIF, issue plans, and review artifacts.
- Preparing repos for developer review, AI-agent work, CI, audit-prep,
  contests, or bounty review.

## What Arkheionx Is Not

- Not a formal audit.
- Not a security guarantee.
- Not exploit automation.
- Not live-chain scanning.
- Not a replacement for Foundry, auditors, or human review.

## Advanced Workflow

Arkheionx can also produce pre-audit readiness reports, SARIF, issue plans,
test plans, and CI artifacts. Those outputs remain supported as advanced
workflows built on the local value-flow direction.

## Start Here

| Goal | Link |
|---|---|
| Try it in 5 minutes | [`docs/TRY_IN_5_MINUTES.md`](docs/TRY_IN_5_MINUTES.md) |
| Install locally | [`docs/INSTALLATION.md`](docs/INSTALLATION.md) |
| Run the CLI | [`docs/CLI_REFERENCE.md`](docs/CLI_REFERENCE.md) |
| Understand the value-flow workbench | [`docs/VALUE_FLOW_WORKBENCH.md`](docs/VALUE_FLOW_WORKBENCH.md) |
| See the value-flow roadmap | [`docs/VALUE_FLOW_ROADMAP.md`](docs/VALUE_FLOW_ROADMAP.md) |
| Developer and researcher workflow | [`docs/DEVELOPER_RESEARCHER_WORKFLOW.md`](docs/DEVELOPER_RESEARCHER_WORKFLOW.md) |
| Use GitHub Action | [`docs/GITHUB_ACTION_USAGE.md`](docs/GITHUB_ACTION_USAGE.md) |
| Understand outputs | [`docs/OUTPUT_ARTIFACTS.md`](docs/OUTPUT_ARTIFACTS.md) |
| Search security memory | [`docs/SEARCH_KNOWLEDGE.md`](docs/SEARCH_KNOWLEDGE.md) |
| Give feedback | [`docs/PUBLIC_FEEDBACK_GUIDE.md`](docs/PUBLIC_FEEDBACK_GUIDE.md) |
| Report false positives | [`.github/ISSUE_TEMPLATE/false_positive.yml`](.github/ISSUE_TEMPLATE/false_positive.yml) |

Quick demo:

```sh
make demo
```

The demo uses toy fixtures only. Dry-run issue workflows make no GitHub API
calls.

## Run On Your Own Repo

Use Arkheionx only on repositories you own or are authorized to review:

```sh
python3 scripts/pre_audit_scan.py \
  --root /path/to/your/repo \
  --protocol-type auto \
  --output reports/ARKHEIONX_PRE_AUDIT_REPORT.md \
  --json-output reports/arkheionx-report.json \
  --sarif-output reports/arkheionx.sarif.json \
  --issue-plan-output reports/ARKHEIONX_ISSUE_PLAN.json
```

Local scans require Python 3. They do not require RPC, private keys,
mnemonics, or a GitHub token.

## Installable CLI

For local development:

```sh
python3 -m pip install -e .
arkheionx doctor
arkheionx scan .
```

The installed console command is local/static only and does not require RPC
keys, private keys, mnemonics, or hosted services. The package is prepared for
local editable installs; this repository does not claim PyPI availability.

## What It Produces

| Output | Purpose |
|---|---|
| Pre-Audit Report | Advanced technical readiness findings with evidence. |
| JSON Report | Machine-readable scan and value-flow review output. |
| SARIF | GitHub Code Scanning-compatible review signals. |
| Issue Plan | GitHub-native remediation and missing-test tasks. |
| Launch Report | Founder/client-facing readiness summary. |
| Sprint Plan | Day-by-day test and remediation workflow. |
| Contest Readiness | Prep for authorized contest or review scope. |
| Remediation Roadmap | Prioritized work plan. |
| Security Memory Search | Finding-to-pattern knowledge lookup. |

## Safety Boundaries

- Use only on repositories you own or are authorized to review.
- Local/static analysis only.
- No RPC, live-chain calls, transaction execution, or deployed-contract
  scanning.
- No private key, mnemonic, token, or secret handling.
- No exploit automation, bounty guarantee, or formal audit claim.

Arkheionx ignores its own generated reports and artifacts by default so
previous outputs do not affect future readiness scores.

## Security Memory Graph

Arkheionx v0.9.0 connects readiness findings to historical exploit patterns,
broken invariants, failed assumptions, suggested defensive tests, and related
docs through a local security memory graph.

Search examples:

```sh
python3 scripts/search_knowledge.py "oracle stale price"
python3 scripts/search_knowledge.py "vault accounting invariant"
python3 scripts/search_knowledge.py "missing invariant"
```

Outputs may include related findings, rule packs, historical patterns,
historical PoC metadata, suggested tests, and docs. This is defensive context,
not vulnerability confirmation.

Read:

- [`docs/SECURITY_MEMORY_GRAPH.md`](docs/SECURITY_MEMORY_GRAPH.md)
- [`docs/SEARCH_KNOWLEDGE.md`](docs/SEARCH_KNOWLEDGE.md)
- [`docs/FINDING_KNOWLEDGE_MAP.md`](docs/FINDING_KNOWLEDGE_MAP.md)
- [`reports/security_memory_graph.md`](reports/security_memory_graph.md)

## Demo Case Study

Start with the internal toy case studies:

- [`docs/case-studies/ORACLE_STAKING_FIXTURE_CASE_STUDY.md`](docs/case-studies/ORACLE_STAKING_FIXTURE_CASE_STUDY.md)
- [`docs/case-studies/ORACLE_STAKING_BEFORE_AFTER.md`](docs/case-studies/ORACLE_STAKING_BEFORE_AFTER.md)

These are reproducible demo case studies, not real protocol validation or
evidence of users.

## Latest Release

Latest stable release: **v2.2.0 - Execution Proof & Trace Workbench**.

v2.2.0 is the current published release. It adds the Foundry-style workbench
(`open`/`map`/`flow`/`hunt`/`prove`/`trace`), execution proof, and trace
summaries on top of the v2.0.0 installable local CLI package.

v2.0.1 is prepared locally as the Packaging + Product Repositioning Hotfix. It
reframes Arkheionx as a local-first DeFi value-flow workbench while preserving
the installable CLI, module CLI, old scripts, reports, SARIF, issue plans, and
test-plan workflows from v2.0.0.

v2.0.0 added editable local installation and the `arkheionx` console command
while preserving every existing script entrypoint:

- `arkheionx scan`;
- `arkheionx validate-config`;
- `arkheionx test-plan`;
- `arkheionx search`;
- `arkheionx version` / `arkheionx doctor`.

| Release | Focus | Status |
|---|---|---|
| v0.1.0 | Pre-Audit Readiness OS MVP | Released |
| v0.2.0 | Vault Rule Pack | Released |
| v0.4.0 | GitHub Action UX + PR Comment Mode | Released |
| v0.4.0 | SARIF Output + Baseline Diff Mode | Released |
| v0.4.1 | Public polish and release consistency | Released |
| v0.5.0 | Generated issue workflow + rule-pack expansion | Released |
| v0.6.0 | Semantic-lite analysis + false-positive reduction | Released |
| v0.7.0 | Launch Report OS + Sprint + Contest Readiness | Released |
| v0.8.0 | External validation + public demos + rule calibration | Released |
| v0.9.0 | Security Memory Graph + search upgrade | Released |
| v0.9.1 | Negative evidence and score calibration | Released |
| v0.9.2 | Generated artifact ignore and self-ingestion guard | Released |
| v1.0.0 | Stable public release + schema freeze | Released |
| v1.0.1 | Docs link validation hotfix | Released |
| v1.1.0 | Feedback Loop + External Calibration | Released |
| v1.1.1 | Public surface polish | Released |
| v1.2.0 | Paid offer refinement | Released |
| v1.3.0 | Ecosystem Pack | Released |
| v1.4.0 | AMM + Lending Protocol Packs | Released |
| v1.5.0 | Invariant/Test Plan Generator Upgrade | Released |
| v1.6.0 | Internal Engine Split | Released |
| v1.7.0 | Config + Rule Pack Stabilization | Released |
| v1.8.0 | Report UX + Noise Reduction | Released |
| v1.9.0 | Pre-v2 CLI Candidate | Released |
| v2.0.0 | Installable Arkheionx CLI / Package | Released |
| v2.0.1 | Packaging + Product Repositioning Hotfix | Unreleased |

## Stable v2.0.0 Surface

Arkheionx v2.0.0 treats these surfaces as stable unless a future changelog
explicitly says otherwise:

- CLI flags documented in [`docs/CLI_REFERENCE.md`](docs/CLI_REFERENCE.md).
- GitHub Action inputs documented in [`docs/GITHUB_ACTION_USAGE.md`](docs/GITHUB_ACTION_USAGE.md).
- Main JSON output shapes documented in [`docs/SCHEMA_REFERENCE.md`](docs/SCHEMA_REFERENCE.md).
- SARIF 2.1.0 readiness output behavior.
- Recommended output names in [`docs/OUTPUT_ARTIFACTS.md`](docs/OUTPUT_ARTIFACTS.md).

Stable GitHub Action examples use `@v2.2.0`. Use `@main` only for development
or testing unreleased changes.

## Configuration

Arkheionx supports safe local configuration through `.arkheionx.json`.

```sh
python3 scripts/validate_config.py --config examples/arkheionx.config.example.json
```

Config can control protocol hints, enabled rule packs, minimum confidence,
suppressions, generated-artifact behavior, output profile, and test-plan
preferences. It cannot enable RPC, live-chain behavior, remote cloning, private
keys, or attack modes.

Read:

- [`docs/CONFIG_REFERENCE.md`](docs/CONFIG_REFERENCE.md)
- [`docs/RULE_PACK_CONFIGURATION.md`](docs/RULE_PACK_CONFIGURATION.md)
- [`docs/SUPPRESSIONS.md`](docs/SUPPRESSIONS.md)
- [`docs/CONFIG_SAFETY.md`](docs/CONFIG_SAFETY.md)

## Report Profiles

Arkheionx supports report profiles for different workflows:

- `concise`
- `standard`
- `full`
- `ci`

Example:

```sh
python3 scripts/pre_audit_scan.py \
  --root . \
  --config examples/configs/ci.config.json \
  --output reports/ARKHEIONX_PRE_AUDIT_REPORT.md \
  --json-output reports/arkheionx-report.json
```

Read:

- [`docs/OUTPUT_PROFILES.md`](docs/OUTPUT_PROFILES.md)
- [`docs/FIX_FIRST.md`](docs/FIX_FIRST.md)
- [`docs/REPORT_UX.md`](docs/REPORT_UX.md)
- [`docs/NOISE_REDUCTION.md`](docs/NOISE_REDUCTION.md)

## Pre-v2 CLI Candidate

v1.9.0 introduced a local module CLI candidate:

```sh
python3 -m arkheionx.cli.main scan .
python3 -m arkheionx.cli.main validate-config --config .arkheionx.json
python3 -m arkheionx.cli.main test-plan --report reports/arkheionx-report.json
python3 -m arkheionx.cli.main search "oracle stale price"
```

Existing scripts remain supported and first-class in v2.0.1.

Read:

- [`docs/CLI_CANDIDATE.md`](docs/CLI_CANDIDATE.md)
- [`docs/CLI_COMMANDS.md`](docs/CLI_COMMANDS.md)
- [`docs/CLI_MIGRATION_TO_V2.md`](docs/CLI_MIGRATION_TO_V2.md)

## Engine and CLI Roadmap

Arkheionx v1.6.0 began the internal engine split toward an installable
CLI/package. v2.0.0 added local editable installation and the `arkheionx`
console command while preserving the module CLI and old scripts. v2.0.1 keeps
that package surface stable and updates the public roadmap toward value-flow
mapping.

```sh
python3 -m arkheionx.cli.main version
python3 -m arkheionx.cli.main doctor
```

Read:

- [`docs/INTERNAL_ENGINE_SPLIT.md`](docs/INTERNAL_ENGINE_SPLIT.md)
- [`docs/PACKAGE_ARCHITECTURE.md`](docs/PACKAGE_ARCHITECTURE.md)
- [`docs/CLI_ROADMAP.md`](docs/CLI_ROADMAP.md)
- [`docs/VALUE_FLOW_ROADMAP.md`](docs/VALUE_FLOW_ROADMAP.md)

## Foundry-Powered Workbench (Preview)

Arkheionx now ships a Foundry-style solo security testing workbench:

```sh
pip install -e .
arkheionx doctor                         # check install + Foundry
arkheionx open .                         # one-command project understanding
arkheionx map .                          # draw the protocol: roles, journeys, money flow
arkheionx flow .                         # money-flow graph (Mermaid + JSON)
arkheionx hunt . --top 5                 # rank bug-hunting surfaces
arkheionx prove . --target Contract.function          # local Foundry proof scaffold
arkheionx prove . --target Contract.function --run    # run targeted Foundry tests
arkheionx trace . --target Contract.function          # summarize the proof/trace
arkheionx evidence . --target Contract.function       # package proof + trace as evidence
arkheionx report . --target Contract.function         # responsible local report draft
```

Full loop: `doctor → open → map → flow → hunt → prove --run → trace → evidence
→ report → manual review`. The `evidence` and `report` commands are local draft
tools: they never auto-submit, never claim a final severity, and include
explicit limitations and a safety notice.

Find the money. Map the protocol. Prove the bug. Every major result carries an
explicit evidence level:

- `HEURISTIC` — static scan only (useful for direction, not proof).
- `COMPILER_CONFIRMED` — `forge build` passed.
- `EXECUTION_CONFIRMED` — a relevant local Foundry test actually executed.

Foundry is an optional precision backend; commands degrade gracefully to
heuristic analysis when it is unavailable. Generated artifacts (JSON, Mermaid,
proof, trace) are written under `.arkheionx/out/`.

Safety boundaries: local analysis only; no RPC by default; no live-chain
transaction; no private keys; no exploit automation; not a formal audit and no
bounty/severity guarantee.

Read:

- [`docs/SOLO_RESEARCH_WORKFLOW.md`](docs/SOLO_RESEARCH_WORKFLOW.md)
- [`docs/PROTOCOL_MAP.md`](docs/PROTOCOL_MAP.md)
- [`docs/EXECUTION_PROOF.md`](docs/EXECUTION_PROOF.md)
- [`docs/TRACE_ENGINE.md`](docs/TRACE_ENGINE.md)
- [`docs/EVIDENCE_PACKAGE.md`](docs/EVIDENCE_PACKAGE.md)
- [`docs/REPORT_DRAFTS.md`](docs/REPORT_DRAFTS.md)
- [`docs/OUTPUT_STANDARD.md`](docs/OUTPUT_STANDARD.md)
- [`docs/FOUNDRY_INTEGRATION.md`](docs/FOUNDRY_INTEGRATION.md)

Advanced flow sub-modes such as `arkheionx flow --test-gaps`,
`arkheionx flow explain`, `arkheionx flow test-template`,
`arkheionx flow review-map`, and `arkheionx flow verify` are roadmap items.
They are not yet available commands.

## Protocol Packs

Arkheionx currently includes readiness checks for:

- Vaults
- Oracles
- Access Control / Upgradeability
- Reentrancy / Value Flow
- Rewards / Staking
- AMMs
- Lending

## Test Plan Generation

Arkheionx can turn readiness findings into suggested defensive test plans and
Foundry invariant skeletons:

```sh
python3 scripts/generate_test_plan.py \
  --report examples/reports/amm-fixture-pre-audit-report.json \
  --output examples/reports/amm-fixture-test-plan.md \
  --foundry-output examples/reports/ArkheionxAMMInvariants.t.sol
```

Generated skeletons are starting points, not formal verification or proof of
safety. Review TODOs, bind local project contracts and mocks, and replace
placeholder assertions with project-specific properties.

## Feedback and Calibration

v1.1.0 adds a structured feedback loop for false positives, false negatives,
report quality, GitHub Action feedback, and rule calibration.

Start here:

- [`docs/FEEDBACK_LOOP.md`](docs/FEEDBACK_LOOP.md)
- [`docs/PUBLIC_FEEDBACK_GUIDE.md`](docs/PUBLIC_FEEDBACK_GUIDE.md)
- [`docs/FEEDBACK_TRIAGE_WORKFLOW.md`](docs/FEEDBACK_TRIAGE_WORKFLOW.md)
- [`reports/feedback_dashboard.md`](reports/feedback_dashboard.md)
- [`reports/rule_calibration_backlog.md`](reports/rule_calibration_backlog.md)

## Paid Readiness Support

Arkheionx is open-source. For teams that want help applying it to an
authorized DeFi repository, paid readiness services are documented in
[`docs/business/PAID_OFFER.md`](docs/business/PAID_OFFER.md).

Available services:

- Readiness Snapshot;
- Pre-Audit Sprint;
- Contest Readiness Pack;
- GitHub Action Setup;
- Ecosystem Readiness Pilot.

Paid support is not a formal audit and does not guarantee security, bounty
outcomes, or findings.

## Ecosystem Readiness

Arkheionx can support ecosystem-level readiness workflows by combining multiple
authorized repo reports into anonymized common-gap summaries.

Start here:

- [`docs/ecosystem/ECOSYSTEM_PACK.md`](docs/ecosystem/ECOSYSTEM_PACK.md)
- [`docs/ecosystem/MULTI_REPO_READINESS_WORKFLOW.md`](docs/ecosystem/MULTI_REPO_READINESS_WORKFLOW.md)
- [`reports/ecosystem_readiness_summary.md`](reports/ecosystem_readiness_summary.md)

The workflow does not clone remote repositories, scan unauthorized repos, or
publish private details. Public summaries use aliases unless explicit
permission exists.

## The Five Pillars

1. **Arkheionx Memory** - historical DeFi exploit research, root-cause
   taxonomy, exploit primitives, broken invariants, failed assumptions,
   assertion families, reproducibility status, and case references.
2. **Arkheionx Flow** - local/static value-flow review for asset movements,
   accounting assumptions, admin-controlled value impact, and missing tests.
3. **Arkheionx Tests** - suggested invariant tests, Foundry skeletons,
   readiness checklists, test coverage guidance, and review preparation
   templates.
4. **Arkheionx Search** - searchable security knowledge base with tags,
   indexes, category maps, metadata, reports, and GitHub search terms.
5. **Arkheionx Advanced Workflows** - GitHub Action usage, Launch Reports,
   Pre-Audit Sprints, Ecosystem Packs, training, and research sponsorship.

## What Arkheionx Is

- Historical DeFi exploit memory.
- Assertion-driven research archive.
- Local-first DeFi value-flow workbench.
- Static repository scanner.
- GitHub Action.
- Markdown report generator.
- JSON report generator.
- Safe Foundry invariant skeleton generator.
- Searchable root-cause knowledge base.
- Builder and researcher support surface.

## What Arkheionx Is Not

- Not a formal audit.
- Not a security guarantee.
- Not live-chain scanning.
- Not exploit automation.
- Not a bounty guarantee.
- Not an attack framework.
- Not a replacement for Foundry, auditors, or human review.
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
| Not-run/no-RPC entries | 18 |
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

Use `@v2.2.0` for stable usage:

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
      - uses: Yudis-bit/DeFi-Exploit-PoCs/.github/actions/pre-audit@v2.2.0
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
      - uses: Yudis-bit/DeFi-Exploit-PoCs/.github/actions/pre-audit@v2.2.0
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
- uses: Yudis-bit/DeFi-Exploit-PoCs/.github/actions/pre-audit@v2.2.0
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
  --issue-checklist-output ARKHEIONX_ISSUE_CHECKLIST.md \
  --issue-plan-output ARKHEIONX_ISSUE_PLAN.json
```

See [`docs/CLI_REFERENCE.md`](docs/CLI_REFERENCE.md) for the current CLI
surface.

Vault builders can force the v0.4.0 Vault Rule Pack:

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
- Issue plan: [`examples/reports/vault-risk-fixture-issue-plan.json`](examples/reports/vault-risk-fixture-issue-plan.json)
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

## v0.4.0 Vault Rule Pack

Arkheionx v0.4.0 adds a vault-focused rule pack for indie builders working on
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

## v0.8.0 Public Demo Workflow

Arkheionx v0.8.0 focuses on external evaluation: five-minute demos,
reproducible toy case studies, rule calibration notes, false-positive review,
and external feedback workflows.

v0.8.0 includes:

- Try Arkheionx in 5 Minutes guide;
- public demo GitHub Actions workflow;
- oracle/staking demo case study;
- before/after readiness case study;
- rule calibration documentation;
- false-positive review workflow;
- external validation feedback templates;
- honest launch and outreach material.

Read:

- [`docs/TRY_IN_5_MINUTES.md`](docs/TRY_IN_5_MINUTES.md)
- [`docs/PUBLIC_DEMO_WORKFLOW.md`](docs/PUBLIC_DEMO_WORKFLOW.md)
- [`docs/RULE_CALIBRATION.md`](docs/RULE_CALIBRATION.md)
- [`docs/FALSE_POSITIVE_REVIEW_WORKFLOW.md`](docs/FALSE_POSITIVE_REVIEW_WORKFLOW.md)
- [`docs/EXTERNAL_VALIDATION.md`](docs/EXTERNAL_VALIDATION.md)

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
| Markdown report | Human-readable value-flow/readiness report and review checklist. |
| JSON report | Machine-readable score, findings, signals, outputs, and metadata. |
| SARIF report | GitHub Code Scanning-compatible review findings. |
| Baseline JSON | Compact readiness snapshot for future comparison. |
| Diff report | New, resolved, unchanged, changed, and suppressed readiness gaps. |
| Actions summary | Short CI summary for GitHub Actions runs. |
| PR comment body | Optional pull request feedback with top readiness gaps. |
| Issue checklist | Copyable remediation and missing-test checklist for GitHub Issues. |
| Issue plan | Structured remediation issue plan for optional dry-run/create/update workflows. |
| Launch Report | Client-facing launch readiness report. |
| Sprint Plan | 3/5/7/10 day Pre-Audit Sprint plan. |
| Contest Readiness | Scope and researcher onboarding preparation report. |
| Executive Summary | Short founder/stakeholder summary. |
| Remediation Roadmap | Phase-based remediation task roadmap. |

Recommended output names and generated-artifact ignore behavior are documented
in [`docs/OUTPUT_ARTIFACTS.md`](docs/OUTPUT_ARTIFACTS.md).

## Search Arkheionx

Start here:

- [`docs/SEARCH_GUIDE.md`](docs/SEARCH_GUIDE.md)
- [`docs/SEARCH_KNOWLEDGE.md`](docs/SEARCH_KNOWLEDGE.md)
- [`reports/search_index.md`](reports/search_index.md)
- [`reports/security_memory_graph.md`](reports/security_memory_graph.md)
- [`metadata/search_terms.json`](metadata/search_terms.json)
- [`metadata/security_memory_graph.json`](metadata/security_memory_graph.json)
- [`metadata/finding_knowledge_map.json`](metadata/finding_knowledge_map.json)
- [`metadata/rule_calibration_matrix.json`](metadata/rule_calibration_matrix.json)
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
value flow
money flow
flow map
missing security tests
map the money flow
pre-audit readiness
root-cause analysis
Foundry invariant testing
```

Recommended GitHub topics:

```text
arkheionx
defi-security
smart-contract-security
foundry
solidity
value-flow
security-testing
audit-readiness
test-coverage
security-research
web3-security
local-first
sarif
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

### Start

- [`docs/TRY_IN_5_MINUTES.md`](docs/TRY_IN_5_MINUTES.md)
- [`docs/INSTALLATION.md`](docs/INSTALLATION.md)
- [`docs/CLI_REFERENCE.md`](docs/CLI_REFERENCE.md)
- [`docs/VALUE_FLOW_WORKBENCH.md`](docs/VALUE_FLOW_WORKBENCH.md)
- [`docs/VALUE_FLOW_ROADMAP.md`](docs/VALUE_FLOW_ROADMAP.md)
- [`docs/DEVELOPER_RESEARCHER_WORKFLOW.md`](docs/DEVELOPER_RESEARCHER_WORKFLOW.md)
- [`docs/CLI_INSTALLABLE.md`](docs/CLI_INSTALLABLE.md)
- [`docs/CLI_CANDIDATE.md`](docs/CLI_CANDIDATE.md)
- [`docs/CLI_COMMANDS.md`](docs/CLI_COMMANDS.md)
- [`docs/CLI_MIGRATION_TO_V2.md`](docs/CLI_MIGRATION_TO_V2.md)
- [`docs/GITHUB_ACTION_USAGE.md`](docs/GITHUB_ACTION_USAGE.md)
- [`docs/PRE_AUDIT_READINESS_OS.md`](docs/PRE_AUDIT_READINESS_OS.md)
- [`docs/CLI_ROADMAP.md`](docs/CLI_ROADMAP.md)

### Outputs

- [`docs/OUTPUT_ARTIFACTS.md`](docs/OUTPUT_ARTIFACTS.md)
- [`docs/SARIF_OUTPUT.md`](docs/SARIF_OUTPUT.md)
- [`docs/BASELINE_DIFF_MODE.md`](docs/BASELINE_DIFF_MODE.md)
- [`docs/GENERATED_ISSUE_CHECKLIST.md`](docs/GENERATED_ISSUE_CHECKLIST.md)
- [`docs/GITHUB_ISSUE_WORKFLOW.md`](docs/GITHUB_ISSUE_WORKFLOW.md)
- [`docs/DELIVERY_ARTIFACTS.md`](docs/DELIVERY_ARTIFACTS.md)
- [`docs/REPORT_UX.md`](docs/REPORT_UX.md)
- [`docs/OUTPUT_PROFILES.md`](docs/OUTPUT_PROFILES.md)
- [`docs/FIX_FIRST.md`](docs/FIX_FIRST.md)
- [`docs/NOISE_REDUCTION.md`](docs/NOISE_REDUCTION.md)
- [`docs/INVARIANT_TEST_PLAN_GENERATOR.md`](docs/INVARIANT_TEST_PLAN_GENERATOR.md)
- [`docs/FOUNDRY_INVARIANT_SKELETONS.md`](docs/FOUNDRY_INVARIANT_SKELETONS.md)

### Analysis

- [`docs/INTERNAL_ENGINE_SPLIT.md`](docs/INTERNAL_ENGINE_SPLIT.md)
- [`docs/PACKAGE_ARCHITECTURE.md`](docs/PACKAGE_ARCHITECTURE.md)
- [`docs/PACKAGING.md`](docs/PACKAGING.md)
- [`docs/PACKAGE_DATA.md`](docs/PACKAGE_DATA.md)
- [`docs/RULE_PACKS.md`](docs/RULE_PACKS.md)
- [`docs/AMM_RULE_PACK.md`](docs/AMM_RULE_PACK.md)
- [`docs/LENDING_RULE_PACK.md`](docs/LENDING_RULE_PACK.md)
- [`docs/SEMANTIC_LITE_ANALYSIS.md`](docs/SEMANTIC_LITE_ANALYSIS.md)
- [`docs/SLITHER_INTEGRATION.md`](docs/SLITHER_INTEGRATION.md)
- [`docs/SECURITY_MEMORY_GRAPH.md`](docs/SECURITY_MEMORY_GRAPH.md)
- [`docs/SEARCH_KNOWLEDGE.md`](docs/SEARCH_KNOWLEDGE.md)
- [`docs/FINDING_KNOWLEDGE_MAP.md`](docs/FINDING_KNOWLEDGE_MAP.md)
- [`docs/INVARIANT_SAFETY_BOUNDARIES.md`](docs/INVARIANT_SAFETY_BOUNDARIES.md)

### Configuration

- [`docs/ARKHEIONX_CONFIG.md`](docs/ARKHEIONX_CONFIG.md)
- [`docs/CONFIG_REFERENCE.md`](docs/CONFIG_REFERENCE.md)
- [`docs/RULE_PACK_CONFIGURATION.md`](docs/RULE_PACK_CONFIGURATION.md)
- [`docs/SUPPRESSIONS.md`](docs/SUPPRESSIONS.md)
- [`docs/CONFIG_SAFETY.md`](docs/CONFIG_SAFETY.md)

### Feedback

- [`docs/FEEDBACK_LOOP.md`](docs/FEEDBACK_LOOP.md)
- [`docs/PUBLIC_FEEDBACK_GUIDE.md`](docs/PUBLIC_FEEDBACK_GUIDE.md)
- [`docs/FEEDBACK_TRIAGE_WORKFLOW.md`](docs/FEEDBACK_TRIAGE_WORKFLOW.md)
- [`docs/VALIDATION_LEVELS.md`](docs/VALIDATION_LEVELS.md)
- [`reports/feedback_dashboard.md`](reports/feedback_dashboard.md)

### Paid Readiness Support

- [`docs/business/PAID_OFFER.md`](docs/business/PAID_OFFER.md)
- [`docs/business/PRICING_LADDER.md`](docs/business/PRICING_LADDER.md)
- [`docs/business/SERVICE_PACKAGES.md`](docs/business/SERVICE_PACKAGES.md)
- [`docs/business/CLIENT_INTAKE.md`](docs/business/CLIENT_INTAKE.md)
- [`docs/business/PAID_WORK_BOUNDARIES.md`](docs/business/PAID_WORK_BOUNDARIES.md)
- [`reports/paid_offer_index.md`](reports/paid_offer_index.md)

### Ecosystem Readiness

- [`docs/ecosystem/ECOSYSTEM_PACK.md`](docs/ecosystem/ECOSYSTEM_PACK.md)
- [`docs/ecosystem/MULTI_REPO_READINESS_WORKFLOW.md`](docs/ecosystem/MULTI_REPO_READINESS_WORKFLOW.md)
- [`docs/ecosystem/ANONYMIZED_REPORTING.md`](docs/ecosystem/ANONYMIZED_REPORTING.md)
- [`docs/ecosystem/ECOSYSTEM_READINESS_PILOT.md`](docs/ecosystem/ECOSYSTEM_READINESS_PILOT.md)
- [`reports/ecosystem_readiness_summary.md`](reports/ecosystem_readiness_summary.md)

### Safety

- [`docs/ETHICS.md`](docs/ETHICS.md)
- [`docs/SECURITY.md`](docs/SECURITY.md)
- [`docs/GENERATED_ARTIFACT_IGNORE.md`](docs/GENERATED_ARTIFACT_IGNORE.md)
- [`docs/FALSE_POSITIVE_REDUCTION.md`](docs/FALSE_POSITIVE_REDUCTION.md)
- [`docs/RULE_CALIBRATION.md`](docs/RULE_CALIBRATION.md)

### Repository Surface

- [`docs/GITHUB_REPO_SURFACE.md`](docs/GITHUB_REPO_SURFACE.md)
- [`docs/ROADMAP.md`](docs/ROADMAP.md)

## Monetization And Support

| Offer | Price | Purpose |
|---|---:|---|
| Free GitHub Action | Free | Basic readiness scan, Markdown report, optional SARIF, baseline diff artifacts, and issue plan output. |
| Indie Builder Sponsor | USD 29/month | Support public tooling, early previews, priority Q&A. |
| Protocol Pro Sponsor | USD 99/month | Deeper templates and priority issue support. |
| Launch Report | USD 299-499 | Manual review of generated report, evidence, issue plan, and prioritized fix checklist. |
| Pre-Audit Sprint | Pilot USD 2,500-5,000; standard USD 5,000-12,000 | Manual readiness review, missing invariant plan, evidence-based GitHub issue plan/checklist. |
| Contest Readiness Pack | USD 1,500-6,000 | Scope checklist, researcher onboarding checklist, and pre-contest remediation priorities. |
| Vault Launch Report | USD 299-499 | Vault Rule Pack review and prioritized vault fix checklist. |
| Vault Pre-Audit Sprint | USD 1,000-2,000 | Vault-focused invariant, strategy, oracle, and withdrawal lifecycle plan. |
| Ecosystem Readiness Pilot | Pilot USD 5,000-15,000; expanded USD 15,000-40,000+ | Multi-repo readiness summaries, anonymized common gaps, and rule-family heatmap for authorized cohorts. |
| Ecosystem Vault Readiness Pack | Custom | Bulk vault readiness reports and portfolio-level Markdown dashboard. |
| Research Sponsorship | Flexible | Fund public exploit-memory and readiness-rule work. |

Use [`SERVICES.md`](SERVICES.md) for requests and
[`docs/business/SPONSORSHIP.md`](docs/business/SPONSORSHIP.md) for sponsor boundaries.

## Ethics

Arkheionx is defensive only.

## Safety Boundaries

Arkheionx performs local/static repository analysis. It does not make RPC
calls, scan deployed contracts, submit transactions, collect secrets, or create
remote GitHub issues unless the separate issue workflow is explicitly enabled
with a token in an authorized repository.

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
- **v0.4.0: GitHub Action UX.** Actions summary, optional PR comment mode,
  generated issue checklist, stable finding IDs, and local config suppression.
- **v0.4.0: SARIF and baseline diff mode.** SARIF output, readiness
  baselines, new/resolved/unchanged gap tracking, and explicit CI thresholds.
- **v0.4.1: public polish and release consistency.** README onboarding,
  stable action examples, and docs cleanup.
- **v0.5.0: generated GitHub issue workflow and rule-pack expansion.**
  Opt-in issue workflow plus oracle, access/upgradeability, reentrancy/value-flow,
  and staking/reward rule packs.
- **v0.6.0: semantic-lite and false-positive reduction.** Evidence-based
  findings, confidence reasons, optional local Slither enrichment, and better
  affected-function/SARIF location mapping.
- **v0.7.0: Launch Report OS and Contest Readiness.** Client-facing delivery
  artifacts, sprint plans, executive summaries, and remediation roadmaps.
- **v0.8.0: external validation and public demos.** Five-minute demo workflow,
  demo case studies, rule calibration notes, feedback templates, and public
  demo artifacts.
- **v0.9.0-v0.9.2: security memory and calibration.** Security memory graph,
  local search, negative evidence calibration, and self-ingestion guard.
- **v1.0.x: stable GitHub-native pre-audit kit.** Documented interfaces,
  schema freeze, calibrated rules, release artifacts, contribution workflow.
- **v1.1.0: feedback loop and external calibration.** Structured templates,
  calibration backlog, feedback dashboard, and validation language.
- **v1.1.1: public surface polish.** README front-page clarity, repository
  About guidance, topics, and onboarding path cleanup.
- **v1.2.0: paid offer refinement.** Productized readiness services, pricing
  ladder, client intake, scope templates, and paid-work boundaries.
- **v1.3.0: ecosystem pack.** Multi-repo readiness workflow, anonymized common
  gap reports, repo-by-repo summary tables, and ecosystem pilot templates.
- **v1.4.0: AMM + Lending Protocol Packs.** Defensive AMM and lending readiness
  findings, fixtures, reports, and knowledge mappings.
- **v1.5.0: Invariant/Test Plan Generator Upgrade.** Finding-to-test-plan map,
  defensive test-plan generator, and Foundry starter skeletons.
- **v1.6.0: Internal Engine Split.** Package scaffold, shared metadata modules,
  generator extraction, and preview internal CLI commands.
- **v1.7.0: Config + Rule Pack Stabilization.** Stable config schema,
  validator, examples, suppression reference, and rule-pack controls.
- **v1.8.0: Report UX + Noise Reduction.** Output profiles, Fix First ranking,
  grouped findings, suppression/config summaries, and CI-oriented reports.
- **v1.9.0: Pre-v2 CLI Candidate.** Local module CLI commands for scan,
  config validation, test-plan generation, and security memory search.
- **v2.0.0: Installable Local CLI Package.** Editable local install,
  `arkheionx` console entrypoint, module CLI, old script compatibility, and
  packaging hygiene.
- **v2.0.1: Packaging + Product Repositioning Hotfix.** Public docs and
  roadmap shift Arkheionx toward a local-first DeFi value-flow workbench.
- **v2.1.0: Value Flow Map MVP.** Planned first value-flow map surface.
- **v3.0.0: DeFi Value Flow Workbench.** Target product shape for value-flow
  maps, test gaps, review maps, templates, verification, and diffs.

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

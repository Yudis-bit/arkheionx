# Services

Arkheionx offers GitHub-native pre-audit readiness support for indie DeFi
builders and defensive research support for the public exploit-memory archive.

This is not a formal audit service. Arkheionx helps builders prepare for one.

Paid offer details introduced in v1.2.0 and expanded for ecosystem pilots in
v1.4.0 are documented in
[`docs/business/PAID_OFFER.md`](docs/business/PAID_OFFER.md),
[`docs/business/PRICING_LADDER.md`](docs/business/PRICING_LADDER.md), and
[`reports/paid_offer_index.md`](reports/paid_offer_index.md).

Core message:

> Find exploit-pattern risks, missing invariants, and audit blockers before
> paying for a formal smart contract audit.

## For Indie Builders

Best fit:

- solo DeFi founders;
- small vault, AMM, lending, staking, and oracle teams;
- hackathon winners preparing for grants or testnet;
- small DAOs preparing an audit scope;
- L2 ecosystem builders who need practical security readiness before formal
  review.

Arkheionx helps turn local repository signals into a Markdown readiness report:

- readiness score;
- GitHub Actions summary;
- optional PR Readiness Comment;
- optional SARIF artifact for GitHub Code Scanning-compatible workflows;
- baseline diff report for tracking readiness changes over time;
- missing invariant plan;
- historical exploit-pattern similarity;
- generated issue checklist;
- generated GitHub issue plan for remediation tracking;
- confidence reasons and evidence summaries for findings;
- optional Launch Report, executive summary, remediation roadmap, sprint plan,
  and contest readiness artifacts when generated in v0.7 workflows;
- prioritized fix checklist after manual review;
- audit preparation notes;
- formal audit recommendation.

Before requesting paid work, builders can inspect the public demo flow:

- [`docs/TRY_IN_5_MINUTES.md`](docs/TRY_IN_5_MINUTES.md);
- [`docs/PUBLIC_DEMO_WORKFLOW.md`](docs/PUBLIC_DEMO_WORKFLOW.md);
- [`docs/case-studies/ORACLE_STAKING_FIXTURE_CASE_STUDY.md`](docs/case-studies/ORACLE_STAKING_FIXTURE_CASE_STUDY.md).

## Free GitHub Action

Price: Free.

Value:

- basic pre-audit scan;
- readiness score;
- Markdown report;
- optional JSON report;
- optional SARIF report;
- optional baseline and diff artifacts;
- GitHub Actions summary;
- optional PR Readiness Comment;
- generated issue checklist;
- generated issue plan and dry-run issue workflow;
- stable finding IDs;
- limited historical pattern mapping;
- basic checklist;
- optional safe Foundry invariant skeleton.

Use it from any authorized repository:

```yaml
- uses: Yudis-bit/DeFi-Exploit-PoCs/.github/actions/pre-audit@v1.4.0
  with:
    root: "."
    protocol-type: "auto"
    output: "ARKHEIONX_PRE_AUDIT_REPORT.md"
    json-output: "arkheionx-report.json"
    create-issue-checklist: "true"
```

## Readiness Snapshot

Price range: pilot USD 500-1,000; standard USD 1,000-2,500.

Best for:

- builders preparing for first audit intake;
- teams close to testnet or public launch;
- grant-funded teams that need a concise readiness artifact.

What you receive:

- automated Arkheionx scan;
- generated Pre-Audit Readiness Report;
- one-page executive summary;
- generated issue plan;
- manual review of the generated report;
- review of semantic-lite evidence and confidence reasons;
- top 5-10 readiness gaps;
- 30-minute walkthrough;
- Markdown report suitable for internal planning;
- clear limitations and formal audit recommendation.

Sample output structure is visible in the oracle/staking demo case study and
the `examples/reports/demo-*` artifact bundle.

This is a launch preparation report, not a formal audit.

## Vault Launch Report

Price range: USD 299-499 one time.

Best for:

- ERC4626-like vault builders;
- strategy vaults preparing for first audit;
- teams with fee, withdrawal, or oracle-dependent share accounting;
- founders who need a concise vault readiness artifact.

What you receive:

- automated Vault Rule Pack scan;
- manual review of vault readiness gaps;
- prioritized vault fix checklist;
- suggested invariant plan;
- Markdown report.

This is vault launch preparation, not a formal audit.

## Pre-Audit Sprint

Price range: pilot USD 2,500-5,000; standard USD 5,000-12,000.

Best for:

- teams preparing for a formal audit;
- protocols with vault accounting, oracle assumptions, reward math,
  upgradeability, liquidation, or admin-role complexity;
- teams that want a missing invariant plan before paying for deeper review.

What you receive:

- automated scan;
- generated Pre-Audit Sprint Plan;
- manual security readiness review;
- historical exploit-pattern mapping;
- missing invariant and test plan;
- baseline/diff review to track remediation progress across scans;
- generated GitHub issue checklist converted into a prioritized remediation plan;
- generated issue plan reviewed and organized into owner-ready tasks;
- evidence-based prioritization using affected files/functions when available;
- daily checklist and sprint exit criteria;
- final readiness summary;
- final Markdown report;
- optional follow-up comments if capacity allows.

The public demo sprint plan shows the structure before any paid engagement is
requested.

This is defensive readiness work. It does not certify protocol safety.

## Contest Readiness Pack

Price range: USD 1,500-6,000 one time.

Best for:

- protocol teams preparing for a bug bounty launch, audit contest, or public
  security review;
- maintainers who need cleaner scope documentation before external researchers
  review the code;
- teams that want researcher onboarding gaps fixed before a competitive review.

What you receive:

- generated Contest Readiness Report;
- scope preparation checklist;
- researcher onboarding checklist;
- pre-contest remediation priorities;
- known limitations documentation prompts;
- optional baseline/diff interpretation if prior scan artifacts exist.

The public demo Contest Readiness report shows the scope and researcher
onboarding checklist structure.

This is defensive contest preparation for authorized maintainers. It is not a
bug bounty guarantee, exploit strategy document, or formal audit.

## GitHub Action Setup

Price range: USD 500-2,500 one time.

Best for:

- teams that want Arkheionx in CI;
- repositories that need SARIF and report artifacts;
- builders who want baseline/diff tracking and config guidance.

What you receive:

- GitHub Action integration;
- SARIF output setup;
- report artifact setup;
- config/suppression setup;
- recommended readiness thresholds;
- short handoff guide.

This does not include secret management, payment integration, CRM integration,
email automation, or remote issue creation unless explicitly scoped.

## Vault Pre-Audit Sprint

Price range: USD 1,000-2,000 one time.

Best for:

- vault teams preparing for formal audit intake;
- protocols with strategy accounting, withdrawal queues, LP pricing, or
  performance/management fee logic;
- teams that need a concrete Foundry invariant plan.

What you receive:

- Vault Rule Pack scan;
- manual readiness review;
- historical vault-pattern mapping;
- strategy/oracle/withdrawal lifecycle checklist;
- GitHub issue checklist;
- optional issue plan review;
- final Markdown report.

This is readiness support only. Formal audit remains recommended before user
funds are at risk.

## Ecosystem Pack

Price range: pilot USD 5,000-15,000; expanded USD 15,000-40,000+.

Best for:

- chain ecosystems;
- accelerators;
- grant programs;
- venture studios;
- audit-prep cohorts;
- ecosystem security teams.

What you receive:

- readiness summary across 3-5 authorized repositories for a pilot, or 5-10
  authorized repositories for an expanded engagement;
- repo-by-repo readiness table;
- anonymized ecosystem-level gap summary;
- common gap report;
- rule-family heatmap;
- GitHub Action setup recommendations;
- feedback and calibration notes;
- 60-90 minute ecosystem walkthrough.

This is not a public endorsement, certification, or adoption claim. Public
summaries use aliases unless explicit naming permission exists.

## Ecosystem Vault Readiness Pack

Price: custom.

Best for:

- L2 ecosystems with many vault builders;
- accelerators supporting yield or ERC4626 projects;
- grant programs that want portfolio-level readiness visibility.

What you receive:

- bulk Vault Rule Pack reports;
- portfolio-level Markdown dashboard;
- vault invariant workshop;
- builder Q&A through GitHub-native channels if configured.

## Research Sponsorship

Price: flexible.

Sponsors can fund public work:

- assertion hardening for weak PoCs;
- archival verification when RPC access is available;
- new historical case metadata;
- root-cause writeups;
- educational examples;
- readiness rule improvements.

Sponsors do not buy influence over severity, taxonomy, verification status, or
inclusion decisions.

## What This Is Not

Arkheionx does not provide:

- formal audit certification;
- security guarantees;
- live-target testing without authorization;
- exploit adaptation for active systems;
- private key, mnemonic, or secret handling;
- bounty outcome promises;
- deployed-contract attack workflows.

## How To Request

Open one of the GitHub issue forms:

- `Pre-Audit Readiness Request` for free guidance or package fit;
- `Launch Report Request` for a one-time paid report;
- `Pre-Audit Sprint Request` for deeper readiness preparation;
- `Rule Request` for new defensive scanner coverage;
- `False Positive Report` for scanner calibration.

Do not include private keys, mnemonics, RPC credentials, undisclosed exploit
details, or confidential production material in public issues.

## Ethical Boundaries

All work is defensive and authorized. Formal audit remains recommended before
mainnet deployment, material TVL, or handling real user funds.

See [`docs/ETHICS.md`](docs/ETHICS.md).

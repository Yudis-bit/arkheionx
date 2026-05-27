# Indie Builder Offer

Arkheionx is built for indie DeFi builders who need to prepare for security
review before they can afford or schedule a formal smart contract audit.

## Who This Is For

- solo DeFi founders;
- hackathon winners;
- grant-funded protocol teams;
- small vault builders;
- early-stage DeFi teams;
- small DAOs;
- indie Solidity developers;
- L2 ecosystem grant recipients;
- protocol engineers preparing for their first audit.

## The Problem

Formal audits are expensive, and audit time is often wasted on fixable
readiness gaps:

- missing invariant tests;
- unclear vault accounting assumptions;
- oracle usage without documented safety checks;
- admin roles not explained;
- upgradeability not tested;
- no report a founder can show to collaborators, communities, or grant teams.

Arkheionx helps turn those gaps into a practical checklist.

## Free Path

Use the GitHub Action or local CLI:

```sh
python3 scripts/pre_audit_scan.py \
  --root . \
  --protocol-type auto \
  --output ARKHEIONX_PRE_AUDIT_REPORT.md \
  --json-output arkheionx-report.json \
  --sarif-output arkheionx.sarif.json \
  --baseline-output arkheionx.baseline.json \
  --issue-plan-output ARKHEIONX_ISSUE_PLAN.json \
  --executive-summary-output ARKHEIONX_EXECUTIVE_SUMMARY.md \
  --remediation-roadmap-output ARKHEIONX_REMEDIATION_ROADMAP.md
```

You receive:

- a readiness score;
- top readiness gaps;
- stable finding IDs;
- stable finding fingerprints for baseline comparison;
- optional SARIF output for GitHub Code Scanning-compatible workflows;
- optional baseline and diff artifacts;
- optional PR Readiness Comment;
- generated issue checklist;
- generated issue plan for owner-ready remediation tasks;
- optional executive summary and remediation roadmap artifacts;
- evidence summaries, confidence reasons, and detection sources;
- historical pattern similarity;
- suggested invariant tests;
- audit preparation checklist;
- Markdown report you can commit or share internally.

Before scanning your own repository, run the public demo:

- [`TRY_IN_5_MINUTES.md`](TRY_IN_5_MINUTES.md);
- [`PUBLIC_DEMO_WORKFLOW.md`](PUBLIC_DEMO_WORKFLOW.md);
- [`case-studies/ORACLE_STAKING_FIXTURE_CASE_STUDY.md`](case-studies/ORACLE_STAKING_FIXTURE_CASE_STUDY.md).

## Paid Path

Paid work is optional and scoped. It is defensive readiness work, not a formal
audit.

Start with [`PAID_OFFER.md`](PAID_OFFER.md), then use
[`../../templates/client_intake.md`](../../templates/client_intake.md) for
scoping.

Core v1.2.0 offers:

- Readiness Snapshot;
- Pre-Audit Sprint;
- Contest Readiness Pack;
- GitHub Action Setup;
- Ecosystem Readiness Pilot.

## Vault Builder Path

For ERC4626-like vaults, strategy vaults, yield vaults, or share/accounting
systems:

1. Run the scanner with `--protocol-type vault`.
2. Review the Vault Rule Pack coverage table.
3. Add invariant tests for totalAssets, share conversion, roundtrip behavior,
   donation/rounding edges, fee accounting, strategy gain/loss, and withdrawal
   lifecycle if relevant.
4. Re-run the report and compare readiness gaps.
5. Save a baseline and use diff mode to track new, resolved, and unchanged
   readiness gaps.
6. Open a Launch Report or Pre-Audit Sprint request if you want manual help
   turning the report into a fix plan.

Local command:

```sh
python3 scripts/pre_audit_scan.py \
  --root . \
  --protocol-type vault \
  --output ARKHEIONX_VAULT_READINESS_REPORT.md \
  --json-output arkheionx-vault-report.json \
  --sarif-output arkheionx-vault.sarif.json \
  --baseline-output arkheionx-vault.baseline.json \
  --issue-plan-output ARKHEIONX_ISSUE_PLAN.json \
  --issue-checklist-output ARKHEIONX_ISSUE_CHECKLIST.md \
  --generate-invariant-skeletons
```

Vault builders should read [`VAULT_RULE_PACK.md`](VAULT_RULE_PACK.md).

### Readiness Snapshot

Price range: pilot USD 500-1,000; standard USD 1,000-2,500.

Best for:

- teams close to testnet or first audit;
- founders who need a concise readiness report;
- builders who want a prioritized fix list.

Output:

- automated scan;
- generated Pre-Audit Readiness Report;
- one-page executive summary;
- generated issue plan;
- manual review of generated report;
- semantic-lite evidence and confidence reasons reviewed for prioritization;
- top 5-10 readiness gaps;
- 30-minute walkthrough;
- Markdown report;
- clear limitations and formal audit recommendation.

You can preview the output shape with the `examples/reports/demo-*` artifacts.

### Vault Launch Report

Price range: USD 299-499 one time.

Best for:

- ERC4626-like vault builders;
- strategy vaults preparing for first audit;
- teams that need share/accounting, fee, withdrawal, and oracle assumptions
  organized before review.

Output:

- automated Vault Rule Pack report;
- manual review of readiness gaps;
- prioritized vault fix checklist;
- suggested invariant plan;
- Markdown report.

### Pre-Audit Sprint

Price range: pilot USD 2,500-5,000; standard USD 5,000-12,000.

Best for:

- teams preparing for formal audit intake;
- protocols with vault, AMM, lending, staking, oracle, or upgradeable flows;
- teams that want missing invariant planning.

Output:

- automated scan;
- generated Pre-Audit Sprint Plan;
- manual security readiness review;
- historical exploit-pattern mapping;
- missing invariant plan;
- diff-mode review to track remediation progress;
- generated GitHub issue checklist reviewed and prioritized;
- generated GitHub issue plan converted into owner-ready tasks;
- evidence-based prioritization using affected files/functions when available;
- remediation roadmap and sprint exit criteria;
- final Markdown report;
- optional follow-up comments if capacity allows.

You can preview the sprint structure in `examples/reports/demo-sprint-plan.md`.

### Contest Readiness Pack

Price range: USD 1,500-6,000 one time.

Best for:

- teams preparing for a bug bounty launch, audit contest, or public security
  review;
- maintainers who need a cleaner scope package before external researchers
  review the repository;
- founders who want known limitations, privileged roles, oracle assumptions,
  and test instructions documented before review begins.

Output:

- generated Contest Readiness Report;
- scope preparation checklist;
- researcher onboarding checklist;
- pre-contest remediation priorities;
- known limitations documentation prompts.

You can preview the contest-readiness structure in
`examples/reports/demo-contest-readiness.md`.

This is defensive preparation for authorized maintainers. It does not promise
contest outcomes or replace a formal audit.

### GitHub Action Setup

Price range: USD 500-2,500 one time.

Best for:

- teams that want Arkheionx in CI;
- repositories that need SARIF/report artifacts;
- builders who want baseline/diff tracking.

Output:

- GitHub Action integration;
- SARIF output setup;
- report artifact setup;
- config/suppression setup;
- recommended thresholds;
- short handoff guide.

### Vault Pre-Audit Sprint

Price range: USD 1,000-2,000 one time.

Best for:

- vault teams preparing for formal audit intake;
- teams with strategy accounting, queued withdrawals, LP pricing, or fee logic;
- teams that want a sharper invariant and test plan.

Output:

- Vault Rule Pack scan;
- manual readiness review;
- strategy/oracle/withdrawal lifecycle checklist;
- suggested Foundry invariant plan;
- GitHub issue checklist;
- issue plan review;
- final Markdown report.

### Ecosystem Pack

Price range: USD 5,000-20,000 per month.

Best for:

- L2 ecosystems;
- accelerators;
- hackathons;
- grant programs;
- builder communities.

Output:

- bulk readiness reports;
- monthly security clinic;
- portfolio-level Markdown dashboard;
- private GitHub Discussion support if configured;
- training session;
- no website required.

## What To Expect

Arkheionx will help you:

- understand your current pre-audit posture;
- identify missing invariants;
- map local code patterns to historical failure classes;
- prepare a cleaner formal audit scope;
- communicate readiness work through GitHub-native artifacts.

## What Not To Expect

Arkheionx will not:

- certify that your protocol is secure;
- replace a formal audit;
- test live deployed targets without authorization;
- adapt historical PoCs to active systems;
- handle private keys, mnemonics, or secrets;
- promise bounty outcomes.

## How To Request

Open one of these GitHub issue templates:

- `Pre-Audit Readiness Request` for free guidance or package fit;
- `Launch Report Request` for a scoped one-time report;
- `Pre-Audit Sprint Request` for deeper preparation.

Built by the creator of Arkheionx, a defensive research project focused on
DeFi exploit reproduction, assertion-driven PoCs, root-cause analysis, and
pre-audit readiness tooling.

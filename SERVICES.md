# Services

Arkheionx offers GitHub-native pre-audit readiness support for indie DeFi
builders and defensive research support for the public exploit-memory archive.

This is not a formal audit service. Arkheionx helps builders prepare for one.

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
- missing invariant plan;
- historical exploit-pattern similarity;
- prioritized fix checklist;
- audit preparation notes;
- formal audit recommendation.

## Free GitHub Action

Price: Free.

Value:

- basic pre-audit scan;
- readiness score;
- Markdown report;
- optional JSON report;
- limited historical pattern mapping;
- basic checklist;
- optional safe Foundry invariant skeleton.

Use it from any authorized repository:

```yaml
- uses: Yudis-bit/DeFi-Exploit-PoCs/.github/actions/pre-audit@main
  with:
    root: "."
    protocol-type: "auto"
    output: "ARKHEIONX_PRE_AUDIT_REPORT.md"
    json-output: "arkheionx-report.json"
```

## Launch Report

Price range: USD 299-499 one time.

Best for:

- builders preparing for first audit intake;
- teams close to testnet or public launch;
- grant-funded teams that need a serious readiness artifact.

What you receive:

- automated Arkheionx scan;
- manual review of the generated report;
- prioritized fix checklist;
- Markdown report suitable for internal planning;
- clear limitations and formal audit recommendation.

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

Price range: USD 1,000-2,000 one time.

Best for:

- teams preparing for a formal audit;
- protocols with vault accounting, oracle assumptions, reward math,
  upgradeability, liquidation, or admin-role complexity;
- teams that want a missing invariant plan before paying for deeper review.

What you receive:

- automated scan;
- manual security readiness review;
- historical exploit-pattern mapping;
- missing invariant and test plan;
- GitHub issue checklist;
- final Markdown report;
- optional follow-up comments if capacity allows.

This is defensive readiness work. It does not certify protocol safety.

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
- final Markdown report.

This is readiness support only. Formal audit remains recommended before user
funds are at risk.

## Ecosystem Pack

Price range: USD 5,000-20,000 per month.

Best for:

- L2 ecosystems;
- accelerators;
- hackathons;
- grant programs;
- builder communities.

What you receive:

- bulk readiness reports for participating repositories;
- monthly security clinic;
- portfolio-level Markdown dashboard;
- private GitHub Discussion support if configured;
- training session for builders;
- no website or SaaS dashboard required.

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

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
  --json-output arkheionx-report.json
```

You receive:

- a readiness score;
- top readiness gaps;
- historical pattern similarity;
- suggested invariant tests;
- audit preparation checklist;
- Markdown report you can commit or share internally.

## Paid Path

Paid work is optional and scoped. It is defensive readiness work, not a formal
audit.

### Launch Report

Price range: USD 299-499 one time.

Best for:

- teams close to testnet or first audit;
- founders who need a concise readiness report;
- builders who want a prioritized fix list.

Output:

- automated scan;
- manual review of generated report;
- prioritized fix checklist;
- Markdown report;
- clear limitations and formal audit recommendation.

### Pre-Audit Sprint

Price range: USD 1,000-2,000 one time.

Best for:

- teams preparing for formal audit intake;
- protocols with vault, AMM, lending, staking, oracle, or upgradeable flows;
- teams that want missing invariant planning.

Output:

- automated scan;
- manual security readiness review;
- historical exploit-pattern mapping;
- missing invariant plan;
- GitHub issue checklist;
- final Markdown report;
- optional follow-up comments if capacity allows.

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

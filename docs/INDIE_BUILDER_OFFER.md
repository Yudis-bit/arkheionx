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
  --issue-plan-output ARKHEIONX_ISSUE_PLAN.json
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
- evidence summaries, confidence reasons, and detection sources;
- historical pattern similarity;
- suggested invariant tests;
- audit preparation checklist;
- Markdown report you can commit or share internally.

## Paid Path

Paid work is optional and scoped. It is defensive readiness work, not a formal
audit.

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

### Launch Report

Price range: USD 299-499 one time.

Best for:

- teams close to testnet or first audit;
- founders who need a concise readiness report;
- builders who want a prioritized fix list.

Output:

- automated scan;
- manual review of generated report;
- baseline/diff interpretation if prior scan output is available;
- generated issue checklist reviewed and turned into a prioritized fix list;
- generated issue plan reviewed for safe remediation tasks;
- semantic-lite evidence and confidence reasons reviewed for prioritization;
- Markdown report;
- clear limitations and formal audit recommendation.

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
- diff-mode review to track remediation progress;
- generated GitHub issue checklist reviewed and prioritized;
- generated GitHub issue plan converted into owner-ready tasks;
- evidence-based prioritization using affected files/functions when available;
- final Markdown report;
- optional follow-up comments if capacity allows.

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

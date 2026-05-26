# GitHub Repository Surface

This page keeps Arkheionx's public GitHub About panel aligned with the current
project identity.

Arkheionx started as an independent DeFi exploit PoC archive and now includes a
GitHub-native pre-audit readiness workflow, security memory graph, reports,
issue plans, and feedback calibration. The repository surface should reflect
that full scope without claiming audits, customers, adoption, or guarantees.

## Recommended GitHub About

Use this as the repository description:

> GitHub-native DeFi pre-audit readiness and security memory OS for finding readiness gaps before audits, contests, and bug bounty launches.

Alternative shorter version:

> DeFi pre-audit readiness, SARIF reports, issue plans, and security memory for authorized smart contract repos.

## Recommended Topics

Recommended final topic set:

- `arkheionx`
- `defi-security`
- `web3-security`
- `smart-contract-security`
- `solidity`
- `foundry`
- `forge`
- `github-actions`
- `sarif`
- `pre-audit`
- `audit-readiness`
- `security-research`
- `root-cause-analysis`
- `exploit-patterns`
- `security-memory`
- `rule-calibration`
- `smart-contract-auditing`
- `open-source-security`
- `ethereum`

The old archive terms `ethereum-archival` and `exploit-poc` can be
de-emphasized in the About topics. The archive identity remains documented in
the README and research docs.

## Recommended Resource

Recommended website/resource field:

```text
https://github.com/Yudis-bit/DeFi-Exploit-PoCs#readme
```

Alternative start-guide URL:

```text
https://github.com/Yudis-bit/DeFi-Exploit-PoCs/blob/main/docs/TRY_IN_5_MINUTES.md
```

## Optional GitHub CLI Commands

Do not run these from automation unless the maintainer explicitly chooses to
update repository metadata. They require authenticated `gh` CLI access.

```sh
gh repo edit Yudis-bit/DeFi-Exploit-PoCs \
  --description "GitHub-native DeFi pre-audit readiness and security memory OS for finding readiness gaps before audits, contests, and bug bounty launches." \
  --homepage "https://github.com/Yudis-bit/DeFi-Exploit-PoCs#readme"

gh repo edit Yudis-bit/DeFi-Exploit-PoCs --add-topic arkheionx
gh repo edit Yudis-bit/DeFi-Exploit-PoCs --add-topic defi-security
gh repo edit Yudis-bit/DeFi-Exploit-PoCs --add-topic web3-security
gh repo edit Yudis-bit/DeFi-Exploit-PoCs --add-topic smart-contract-security
gh repo edit Yudis-bit/DeFi-Exploit-PoCs --add-topic solidity
gh repo edit Yudis-bit/DeFi-Exploit-PoCs --add-topic foundry
gh repo edit Yudis-bit/DeFi-Exploit-PoCs --add-topic forge
gh repo edit Yudis-bit/DeFi-Exploit-PoCs --add-topic github-actions
gh repo edit Yudis-bit/DeFi-Exploit-PoCs --add-topic sarif
gh repo edit Yudis-bit/DeFi-Exploit-PoCs --add-topic pre-audit
gh repo edit Yudis-bit/DeFi-Exploit-PoCs --add-topic audit-readiness
gh repo edit Yudis-bit/DeFi-Exploit-PoCs --add-topic security-research
gh repo edit Yudis-bit/DeFi-Exploit-PoCs --add-topic root-cause-analysis
gh repo edit Yudis-bit/DeFi-Exploit-PoCs --add-topic exploit-patterns
gh repo edit Yudis-bit/DeFi-Exploit-PoCs --add-topic security-memory
gh repo edit Yudis-bit/DeFi-Exploit-PoCs --add-topic rule-calibration
gh repo edit Yudis-bit/DeFi-Exploit-PoCs --add-topic smart-contract-auditing
gh repo edit Yudis-bit/DeFi-Exploit-PoCs --add-topic open-source-security
gh repo edit Yudis-bit/DeFi-Exploit-PoCs --add-topic ethereum
```

`gh repo edit --help` confirms support for `--description`, `--homepage`, and
`--add-topic`.

## Manual GitHub UI Steps

1. Open the repository on GitHub.
2. Go to **Settings -> General -> About**.
3. Update **Description** with the recommended About text.
4. Update **Website** with the recommended resource URL.
5. Update **Topics** with the recommended topic set.

## Safety And Claim Boundaries

Do not add About text or topics that imply:

- formal audit coverage;
- replacing audits;
- security guarantees;
- bug bounty guarantees;
- exploit automation;
- live target scanning;
- customers, adoption, auditor trust, or partnerships without committed public
  evidence.

Use wording around pre-audit readiness, local/static analysis, authorized
repositories, security memory, evidence-backed findings, and defensive security
research.

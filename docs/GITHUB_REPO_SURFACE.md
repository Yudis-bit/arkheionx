# GitHub Repository Surface

This page keeps Arkheionx's public GitHub About panel aligned with the current
project identity.

Arkheionx started as an independent DeFi exploit PoC archive and now includes a
local-first DeFi value-flow workbench, security memory graph, reports, issue
plans, test plans, and advanced pre-audit readiness workflows. The repository
surface should reflect that full scope without claiming audits, customers,
adoption, or guarantees.

## Recommended GitHub About

Use this as the repository description:

> Local-first DeFi value-flow workbench for mapping how assets move through protocols and finding missing security tests.

Alternative shorter version:

> Map DeFi value flows and missing security tests from your local repo.

## Recommended Topics

Recommended final topic set:

- `arkheionx`
- `defi-security`
- `smart-contract-security`
- `foundry`
- `solidity`
- `value-flow`
- `security-testing`
- `audit-readiness`
- `test-coverage`
- `security-research`
- `web3-security`
- `local-first`
- `sarif`

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
  --description "Local-first DeFi value-flow workbench for mapping how assets move through protocols and finding missing security tests." \
  --homepage "https://github.com/Yudis-bit/DeFi-Exploit-PoCs#readme"

gh repo edit Yudis-bit/DeFi-Exploit-PoCs --add-topic arkheionx
gh repo edit Yudis-bit/DeFi-Exploit-PoCs --add-topic defi-security
gh repo edit Yudis-bit/DeFi-Exploit-PoCs --add-topic smart-contract-security
gh repo edit Yudis-bit/DeFi-Exploit-PoCs --add-topic foundry
gh repo edit Yudis-bit/DeFi-Exploit-PoCs --add-topic solidity
gh repo edit Yudis-bit/DeFi-Exploit-PoCs --add-topic value-flow
gh repo edit Yudis-bit/DeFi-Exploit-PoCs --add-topic security-testing
gh repo edit Yudis-bit/DeFi-Exploit-PoCs --add-topic audit-readiness
gh repo edit Yudis-bit/DeFi-Exploit-PoCs --add-topic test-coverage
gh repo edit Yudis-bit/DeFi-Exploit-PoCs --add-topic security-research
gh repo edit Yudis-bit/DeFi-Exploit-PoCs --add-topic web3-security
gh repo edit Yudis-bit/DeFi-Exploit-PoCs --add-topic local-first
gh repo edit Yudis-bit/DeFi-Exploit-PoCs --add-topic sarif
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

Use wording around local-first value-flow review, local/static analysis,
authorized repositories, security memory, evidence-backed findings, missing
tests, and defensive security research. Pre-audit readiness should be framed
as an advanced workflow, not the only public entry point.

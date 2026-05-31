# GitHub Repository Surface

This page keeps Arkheionx's public GitHub About panel aligned with the current
project identity.

Arkheionx is a Foundry-style local security workbench for DeFi protocol
understanding, money-flow mapping, hunter target ranking, proof/trace evidence,
and responsible report drafting. The historical DeFi exploit-reproduction
archive remains documented and still backs the workbench's pattern knowledge.

Latest stable release: **v2.7.0 — Guided Demo Fixtures & First Real Workflow**.

## Recommended GitHub About

Use this as the repository description:

> Foundry-style local security workbench for DeFi protocol mapping, money-flow analysis, proof/trace evidence, and report drafting.

Alternative shorter version (if length is tight):

> Local DeFi security workbench for protocol mapping, money-flow analysis, proof evidence, and report drafting.

No hype. No "world-leading". No formal-audit, guaranteed-bug-discovery, or
exploit-automation claims.

## Recommended Topics

Recommended final topic set (GitHub allows up to 20):

- `arkheionx`
- `defi-security`
- `smart-contract-security`
- `foundry`
- `solidity`
- `security-tools`
- `security-research`
- `web3-security`
- `defi`
- `audit-readiness`
- `money-flow`
- `value-flow`
- `proof-of-concept`
- `local-first`
- `static-analysis`
- `sarif`
- `bug-bounty`
- `invariant-testing`
- `trace-analysis`
- `developer-tools`

If fewer topics are preferred, use: `arkheionx`, `defi-security`,
`smart-contract-security`, `foundry`, `solidity`, `security-tools`,
`web3-security`, `audit-readiness`, `local-first`, `static-analysis`,
`trace-analysis`, `invariant-testing`, `developer-tools`.

## Recommended Resource

Recommended website/resource field:

```text
https://github.com/Yudis-bit/DeFi-Exploit-PoCs#readme
```

## Optional GitHub CLI Commands

Do not run these from automation unless the maintainer explicitly chooses to
update repository metadata. They require authenticated `gh` CLI access.

```sh
gh repo edit Yudis-bit/DeFi-Exploit-PoCs \
  --description "Foundry-style local security workbench for DeFi protocol mapping, money-flow analysis, proof/trace evidence, and report drafting." \
  --homepage "https://github.com/Yudis-bit/DeFi-Exploit-PoCs#readme"

gh repo edit Yudis-bit/DeFi-Exploit-PoCs \
  --add-topic arkheionx --add-topic defi-security \
  --add-topic smart-contract-security --add-topic foundry \
  --add-topic solidity --add-topic security-tools \
  --add-topic web3-security --add-topic audit-readiness \
  --add-topic local-first --add-topic static-analysis \
  --add-topic trace-analysis --add-topic invariant-testing \
  --add-topic developer-tools
```

`gh repo edit --help` confirms support for `--description`, `--homepage`, and
`--add-topic`.

## Manual GitHub UI Steps

1. Open the repository on GitHub.
2. Go to **Settings -> General -> About** (or the About gear on the repo home).
3. Update **Description** with the recommended About text.
4. Update **Website** with the recommended resource URL.
5. Update **Topics** with the recommended topic set, then **Save changes**.

## Safety And Claim Boundaries

Do not add About text or topics that imply:

- formal audit coverage;
- replacing audits or Foundry;
- security guarantees;
- bug bounty guarantees;
- exploit automation;
- live target scanning;
- customers, adoption, auditor trust, or partnerships without committed public
  evidence.

Use wording around local-first analysis, money-flow mapping, honest evidence
levels, proof/trace evidence, responsible report drafting, authorized
repositories, and defensive security research.

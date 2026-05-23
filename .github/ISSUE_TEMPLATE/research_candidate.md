---
name: Research candidate
about: Propose a historical DeFi exploit incident as a candidate for the registry.
title: "[candidate] <YYYY-MM> <protocol>"
labels: ["candidate"]
---

## Incident

- **Protocol**:
- **Incident date** (YYYY-MM-DD):
- **Chain** (`ethereum`, `base`, `arbitrum`, ...):
- **Suspected root cause** (one line):
- **Category** (from `docs/EXPLOIT_TAXONOMY.md`):

## Public sources

<!-- At least one independent post-mortem, advisory, or contest report.
     Twitter alone is not enough. -->

-

## Known on-chain artifacts

- **Attack tx** (if known):
- **Suggested fork block** (if known):
- **Attacker address** (if known):

## Why this belongs

<!-- Two or three sentences. What does an asserted PoC of this incident
     teach that the existing corpus does not already cover? Cite category
     gaps in `reports/research_dashboard.md` when relevant. -->

## Reproduction notes

- Archival RPC required? (mainnet, base, arbitrum, ...):
- Anything time-sensitive (rebases, oracle staleness windows, governance
  timelocks)?
- Estimated reproduction difficulty (`trivial`, `easy`, `moderate`,
  `hard`, `very-hard`):

## Safety

- [ ] Incident is fully patched / the protocol is no longer exposed.
- [ ] No live-target details would be added to this repo.
- [ ] No private exploit material that has not already been disclosed.

## Disclosure / patch status

<!-- Link the patch commit, advisory, or post-mortem confirming the
     vulnerability is closed. If the incident is unpatched, do NOT open a
     public issue — see `docs/SECURITY.md` and contact the maintainer
     privately. -->

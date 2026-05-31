# Value Flow Roadmap

This roadmap captures the public product direction after v2.0.0. It is
honest, local-first, and subject to change. A milestone is not claimed until
the committed artifacts support it.

## Direction

Arkheionx is moving from pre-audit-first positioning to a DeFi value-flow
workbench for builders and researchers.

Core promise:

```text
Map the money flow. Find the missing tests.
```

Existing audit-prep, SARIF, CI, issue-plan, report, search, and test-plan
outputs remain supported. Future work prioritizes value-flow mapping, missing
tests, developer workflow, and researcher review maps.

Current milestone: v2.0.1 — Packaging + Product Repositioning Hotfix.
Next milestone: v2.1.0 — Value Flow Map MVP.
v3.0.0 target: DeFi Value Flow Workbench.

## Milestones

| Version | Milestone | Status |
|---|---|---|
| v2.0.1 | Packaging + Product Repositioning Hotfix | Current local prep |
| v2.1.0 | Value Flow Map MVP | Next milestone |
| v2.2.0 | Value Flow Test Gaps | Planned |
| v2.3.0 | Flow Explain Mode | Planned |
| v2.4.0 | Flow-Based Foundry Test Templates | Planned |
| v2.5.0 | Researcher Review Map | Planned |
| v2.6.0 | Flow Verify / Before-After | Planned |
| v2.7.0 | Flow Baseline + Diff | Planned |
| v2.8.0 | AI-Agent Fix Specs from Value Flows | Planned |
| v2.9.0 | Pre-v3 Hardening | Planned |
| v3.0.0 | DeFi Value Flow Workbench | Target |

## Current Functional Foundation

Available in v2.0.1:

- `arkheionx scan`;
- `arkheionx test-plan`;
- `arkheionx search`;
- `arkheionx validate-config`;
- `arkheionx doctor`;
- `arkheionx version`;
- `arkheionx open` (workbench preview);
- `arkheionx map` (workbench preview);
- `arkheionx flow` (workbench preview, money-flow map);
- `arkheionx hunt` (workbench preview);
- `arkheionx prove` (workbench preview, Foundry proof scaffold);
- module CLI equivalents;
- legacy script entrypoints.

Planned for future releases, not available in v2.0.1:

- `arkheionx flow --test-gaps`;
- `arkheionx flow explain`;
- `arkheionx flow test-template`;
- `arkheionx flow review-map`;
- `arkheionx flow verify`.

## Non-Goals

The value-flow roadmap does not add:

- RPC calls or live-chain calls;
- deployed-contract scanning;
- transaction execution;
- private key or mnemonic handling;
- exploit payload generation;
- attack automation;
- target enumeration;
- hosted web app, database, or external API dependency;
- package publishing workflow.

The roadmap also does not claim formal audit coverage, proof of safety,
formal verification, customer adoption, auditor trust, or security guarantees.

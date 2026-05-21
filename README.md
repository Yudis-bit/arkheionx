# Arkheionx Vault

**Independent DeFi exploit PoC research archive.** Reproducibility,
metadata discipline, and root-cause analysis for historical incidents.

Maintained by Yudistira Putra (`arkheionx` /
[@Yudis-bit](https://github.com/Yudis-bit)).

---

## Overview

Arkheionx Vault is being developed as an independent DeFi exploit PoC
archive focused on reproducibility, metadata discipline, and root-cause
analysis. It collects historical Web3 exploit proofs-of-concept for
defensive research, auditor training, and reproducible study of failure
modes that have already occurred in production protocols.

The current archive is small. The standards, taxonomy, and verification
process under [`docs/`](docs/) are the foundation for it to grow safely
past 100 and beyond verified entries — see
[`docs/EXPANSION_PLAN.md`](docs/EXPANSION_PLAN.md). Counts in this
README reflect the actual state of `metadata/registry.json`.

Each entry is structured around three things:

- a pinned environment that reproduces the pre-exploit state,
- a PoC that triggers the vulnerability,
- hard assertions that prove the resulting compromise.

The goal is not to glorify exploits. It is to preserve them, accurately, so
they can be studied and prevented.

## What this repository is

- A registry of historical and patched DeFi exploits, with code that
  reproduces each one against pinned chain state.
- A working set of Foundry tests under `EVM/test/` that fork mainnet (and
  other supported chains) at the block of each incident.
- A canonical metadata file (`metadata/registry.json`) that drives the
  registry table below and the web app under `web/`.
- Documentation of the standard each PoC must meet before it is merged.

## What this repository is not

- A live-target attack toolkit.
- A scanner, an autonomous exploit runner, or detection-evasion tooling.
- A consultancy product. References to security firms, contest platforms,
  and bounty programs in this repository are attributions to public
  post-mortems, not partnerships.
- A commitment that every listed PoC currently runs on every machine.
  See [docs/REPRODUCIBILITY.md](docs/REPRODUCIBILITY.md) and the
  `reproducibility` and `status` fields on each entry.

## Research framework

This archive is governed by a set of standards, not by tribal knowledge.
Each document is small and load-bearing.

- [`docs/POC_STANDARD.md`](docs/POC_STANDARD.md) — what counts as a valid PoC.
- [`docs/EXPLOIT_TAXONOMY.md`](docs/EXPLOIT_TAXONOMY.md) — vulnerability categories used as the registry's `category` field.
- [`docs/ASSERTION_STANDARD.md`](docs/ASSERTION_STANDARD.md) — required assertion families per category.
- [`docs/REPRODUCIBILITY_STANDARD.md`](docs/REPRODUCIBILITY_STANDARD.md) — what each `reproducibility` value means and how a PoC reaches `deterministic-confirmed`.
- [`docs/FORK_VERIFICATION.md`](docs/FORK_VERIFICATION.md) — how PoCs are run against pinned chain state and how results are recorded.
- [`docs/AUDITOR_CHECKLIST.md`](docs/AUDITOR_CHECKLIST.md) — per-category review prompts.
- [`docs/ROOT_CAUSE_PLAYBOOK.md`](docs/ROOT_CAUSE_PLAYBOOK.md) — how to write a credible root-cause section.
- [`docs/INCIDENT_INTAKE.md`](docs/INCIDENT_INTAKE.md) — pipeline for adding a new incident.
- [`docs/EXPANSION_PLAN.md`](docs/EXPANSION_PLAN.md) — milestones from 25 to 700+ verified PoCs.
- [`docs/VERIFICATION_REPORT_TEMPLATE.md`](docs/VERIFICATION_REPORT_TEMPLATE.md) — per-PoC verification artifact format.

The earlier [`docs/RESEARCH_STANDARD.md`](docs/RESEARCH_STANDARD.md) and
[`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md) remain as
introductions; the documents above are the authoritative standard.

## Research standard

The full standard is in [docs/RESEARCH_STANDARD.md](docs/RESEARCH_STANDARD.md).
Summary:

- One PoC per file. No shared state across tests.
- Pinned fork block. Documented chain alias.
- Hard assertions on post-exploit state, in the families required by the
  PoC's category — see [`docs/ASSERTION_STANDARD.md`](docs/ASSERTION_STANDARD.md).
- At least one external reference (post-mortem, advisory, contest report,
  original PoC author) unless the entry is `embargoed` or `educational`.
- Canonical metadata in `metadata/registry.json`.

## Supported environments

Honest current state. See [docs/VM_SUPPORT.md](docs/VM_SUPPORT.md).

| VM | Status | Notes |
|---|---|---|
| EVM (Foundry) | Supported | All currently merged PoCs are EVM. Most are `deterministic-likely-but-unverified` — code looks correct, fork test has not been re-run in the current environment. See [`docs/REPRODUCIBILITY_STANDARD.md`](docs/REPRODUCIBILITY_STANDARD.md). |
| SVM (Anchor) | Template | Directory is scaffolding; no real PoC yet. |
| MoveVM (Aptos) | Template | Directory is scaffolding; no real PoC yet. |

## Repository layout

```
.
├── EVM/                Foundry project: PoCs under test/, helpers under src/
├── SVM/                Anchor scaffold (template only)
├── MoveVM/             Aptos Move scaffold (template only)
├── metadata/           Canonical registry + JSON Schema
├── scripts/            Validation, registry generation, PoC tooling
├── web/                Next.js archive interface
├── docs/               Brand, ethics, research standard, reproducibility
└── README.md           This file
```

## Running an EVM PoC

From `EVM/`:

```sh
# One-time setup.
forge install
export ETH_RPC_URL=https://your-archive-node-endpoint

# Run a single PoC.
forge test --match-path "test/2017-07/*.t.sol" -vvvv

# Run all PoCs.
forge test -vvv
```

Most PoCs require an **archival** RPC. See
[docs/FORK_VERIFICATION.md](docs/FORK_VERIFICATION.md) for chain
aliases, required env vars, and how to record verification results.

## Vulnerability registry

The table below is generated from `metadata/registry.json`. Do not
hand-edit. Run `python scripts/generate_registry.py` to regenerate.

A static-readiness scoring of the registry — metadata completeness,
assertion presence, root-cause clarity — is at
[`reports/poc_quality_matrix.md`](reports/poc_quality_matrix.md),
generated by `python scripts/score_pocs.py`. Per-PoC verification
reports live under
[`reports/verification/`](reports/verification/), generated by
`python scripts/generate_verification_report.py`. Until an entry has a
verification report containing real run output, it remains at
`deterministic-likely-but-unverified` regardless of how complete its
metadata looks.

## Severity classification

| Level | Meaning |
|---|---|
| critical | Unconditional fund loss or full protocol takeover. |
| high | Conditional fund loss, or permanent DoS of core flow. |
| medium | Fund risk under specific conditions, governance manipulation, or reversible DoS. |
| low | Bounded value impact or significant griefing without direct loss. |
| informational | Defensive note; not exploitable in isolation. |

## Responsible use

This repository is for defensive security research only. By using anything
here you accept the terms in [docs/ETHICS.md](docs/ETHICS.md):

- No unauthorized testing against live systems.
- No adapting these PoCs to extract value without consent.
- Compliance with applicable law, contracts, and disclosure obligations.

If you believe content in this repository may aid attack against an
unpatched live system, contact the maintainer privately. See
[docs/SECURITY.md](docs/SECURITY.md).

## Contact

- GitHub: [@Yudis-bit](https://github.com/Yudis-bit)
- Web3 handle: `arkheionx`
- Maintainer identity: Yudistira Putra

For substantive issues, prefer the GitHub issue templates under
`.github/ISSUE_TEMPLATE/`.

---

<!-- BEGIN: registry -->

_Generated from `metadata/registry.json`. Run `python scripts/generate_registry.py` to regenerate. Total entries: 18._

| Date | Protocol | Chain | Severity | Category | Status | PoC |
|------|----------|-------|----------|----------|--------|-----|
| 2017-07 | Parity Multisig — initWallet hijack | ethereum | critical | access-control-failure | historical | [`EVM/test/2017-07/Exploit_2017-07.t.sol`](EVM/test/2017-07/Exploit_2017-07.t.sol) |
| 2017-11 | Parity Wallet Library — suicide | ethereum | critical | access-control-failure | historical | [`EVM/test/2017-11/Exploit_2017-11.t.sol`](EVM/test/2017-11/Exploit_2017-11.t.sol) |
| 2018-04 | BeautyChain (BEC) — batchTransfer overflow | ethereum | critical | arithmetic-precision-rounding | historical | [`EVM/test/2018-04/Exploit_2018-04.t.sol`](EVM/test/2018-04/Exploit_2018-04.t.sol) |
| 2018-10 | SpankChain — payment channel reentrancy | ethereum | high | reentrancy | historical | [`EVM/test/2018-10/Exploit_2018-10.t.sol`](EVM/test/2018-10/Exploit_2018-10.t.sol) |
| 2020-04 | Uniswap V1 — imBTC reentrancy | ethereum | high | reentrancy | historical | [`EVM/test/2020-04/Exploit_2020-04.t.sol`](EVM/test/2020-04/Exploit_2020-04.t.sol) |
| 2020-06 | Balancer — deflationary token rounding | ethereum | high | fee-on-transfer-rebasing-assumption | historical | [`EVM/test/2020-06/Exploit_2020-06.t.sol`](EVM/test/2020-06/Exploit_2020-06.t.sol) |
| 2020-08 | Opyn — duplicate ETH option exercise | ethereum | high | invariant-bypass | historical | [`EVM/test/2020-08/Exploit_2020-08.t.sol`](EVM/test/2020-08/Exploit_2020-08.t.sol) |
| 2020-09 | bZx — iToken duplicate transfer | ethereum | critical | accounting-mismatch | historical | [`EVM/test/2020-09/Exploit_2020-09.t.sol`](EVM/test/2020-09/Exploit_2020-09.t.sol) |
| 2020-10 | Harvest Finance — fUSDT/fUSDC oracle manipulation | ethereum | critical | flash-loan-price-manipulation | historical | [`EVM/test/2020-10/Exploit_2020-10.t.sol`](EVM/test/2020-10/Exploit_2020-10.t.sol) |
| 2020-11 | Cheese Bank — Uniswap LP price oracle manipulation | ethereum | critical | flash-loan-price-manipulation | historical | [`EVM/test/2020-11/Exploit_2020-11.t.sol`](EVM/test/2020-11/Exploit_2020-11.t.sol) |
| 2020-12 | Warp Finance — LP token oracle manipulation | ethereum | critical | flash-loan-price-manipulation | historical | [`EVM/test/2020-12/Exploit_2020-12.t.sol`](EVM/test/2020-12/Exploit_2020-12.t.sol) |
| 2021-01 | Saddle Finance — early swap rounding | ethereum | medium | arithmetic-precision-rounding | incomplete | [`EVM/test/2021-01/Exploit_2021-01.t.sol`](EVM/test/2021-01/Exploit_2021-01.t.sol) |
| 2021-02 | Yearn v1 DAI vault — Curve 3pool oracle manipulation | ethereum | critical | flash-loan-price-manipulation | historical | [`EVM/test/2021-02/Exploit_2021-02.t.sol`](EVM/test/2021-02/Exploit_2021-02.t.sol) |
| 2021-03 | DODO — CrowdPooling init reentrancy | ethereum | high | initialization-bug | historical | [`EVM/test/2021-03/Exploit_2021-03.t.sol`](EVM/test/2021-03/Exploit_2021-03.t.sol) |
| 2021-10 | Indexed Finance — DEFI5/CC10 reweight manipulation | ethereum | critical | amm-invariant-manipulation | historical | [`EVM/test/2021-10/Exploit_2021-10.t.sol`](EVM/test/2021-10/Exploit_2021-10.t.sol) |
| 2022-02 | Dexible — preApproved selfSwap drain | ethereum | high | unsafe-external-call | historical | [`EVM/test/2022-02/Exploit_2022-02.t.sol`](EVM/test/2022-02/Exploit_2022-02.t.sol) |
| 2025-11 | Moonwell — Chainlink oracle staleness on Base | base | high | oracle-manipulation | historical | [`EVM/test/2025-11/Exploit_2025-11.t.sol`](EVM/test/2025-11/Exploit_2025-11.t.sol) |
| 2025-12 | yETH — pool invariant manipulation | ethereum | critical | amm-invariant-manipulation | historical | [`EVM/test/2025-12/Exploit_2025-12.t.sol`](EVM/test/2025-12/Exploit_2025-12.t.sol) |

<!-- END: registry -->

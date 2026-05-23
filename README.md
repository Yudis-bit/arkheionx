# Arkheionx Vault

**Independent DeFi Exploit PoC Research Archive**

Maintained by Yudistira Putra — `arkheionx` /
[@Yudis-bit](https://github.com/Yudis-bit).

---

## Overview

Arkheionx Vault is an independent archive of historical DeFi exploit
proofs-of-concept. The project is built around reproducibility, assertion
quality, exploit anatomy, and root-cause analysis rather than raw exploit
collection.

Each entry pairs Foundry-based fork reproduction of a real, already-resolved
incident with metadata that records the exploit primitive, the broken
invariant, the protocol assumption that failed, and the assertions that
prove the resulting compromise. The work is defensive: studying failed
designs in detail so they are not repeated.

The archive is small by design. Standards, taxonomy, and verification
process come first; corpus growth follows.

## Current status

Honest snapshot of the repository on the current branch.

| Metric | Value |
|---|---|
| Total PoCs | 18 |
| Deterministic-confirmed | 0 (archival fork verification pending) |
| Strong static assertions | 7 |
| Medium static assertions | 4 |
| Weak static assertions | 7 |
| Maturity distribution | L0:0 · L1:7 · L2:10 · L3:1 · L4:0 · L5:0 |
| Public RPC smoke testing | supported |
| Archival RPC verification | required for historical fork confirmation |
| EVM (Foundry) | active |
| SVM (Anchor) | scaffold only |
| MoveVM (Aptos) | scaffold only |

`deterministic-confirmed` is reserved for entries that have been re-run on a
pinned archival fork on this branch and have a verification report under
[`reports/verification/`](reports/verification/). Static assertion quality
is measured separately and is not a substitute for runtime verification.

## Why this exists

Replaying an exploit in code is necessary but not sufficient. A PoC that
ends with `console.log(attackerBalance)` proves nothing — the call could
have reverted silently, the balance could have been pre-seeded, the
attacker pool could have already held the funds. Without hard assertions,
a green test says nothing about whether the vulnerability actually
triggered.

Arkheionx Vault treats each historical incident as a security primitive
worth dissecting precisely:

- the exploit primitive that was abused,
- the invariant that was broken,
- the protocol assumption that turned out to be false,
- attacker profit and victim loss measured against pinned pre-state,
- a reference to the original post-mortem.

The goal is defensive learning and auditor training, not exploit
collection.

## What this repository is

- An archive of historical DeFi exploits with code that reproduces each
  one against pinned chain state.
- A working set of Foundry tests under `EVM/test/` that fork mainnet (and
  other supported chains) at the block of each incident.
- A canonical metadata file (`metadata/registry.json`) that drives the
  registry table below.
- A documented research standard each PoC is held to before promotion.

## What this repository is not

- Not a live-target attack toolkit.
- Not a scanner, autonomous exploit runner, or detection-evasion tooling.
- Not affiliated with any audit firm, contest platform, or bounty
  program. External references in this repository are attributions to
  public post-mortems, not partnerships.
- Not a claim that every listed PoC is currently runtime-verified. See
  the `reproducibility` and `verification_status` fields on each entry.
- Not the largest archive of exploit code. There are larger collections.
  This one optimises for a different axis: assertion quality and
  reproducibility per entry.

## Research standard

Every mature PoC in this archive aims to carry:

- a pinned fork block and explicit chain alias;
- the protocol identity, attack transaction, and incident date;
- the exploit primitive and the attacker path that abuses it;
- the invariant that was broken;
- the protocol assumption that failed;
- an attacker profit assertion against pinned pre-state;
- a victim loss or state-damage assertion where the on-chain shape
  allows;
- a documented reproducibility status;
- at least one external reference (post-mortem, advisory, original PoC
  author);
- a verification report once runtime confirmation is achieved.

Hard assertions are required. A PoC that compiles and forks but ends
without `assert*` is treated as incomplete regardless of how clean its
narrative reads.

The full standard is in
[`docs/RESEARCH_STANDARD.md`](docs/RESEARCH_STANDARD.md). Related
documents:

- [`docs/POC_STANDARD.md`](docs/POC_STANDARD.md) — what counts as a valid PoC.
- [`docs/EXPLOIT_TAXONOMY.md`](docs/EXPLOIT_TAXONOMY.md) — vulnerability categories used by the registry's `category` field.
- [`docs/ASSERTION_STANDARD.md`](docs/ASSERTION_STANDARD.md) — required assertion families per category.
- [`docs/REPRODUCIBILITY_STANDARD.md`](docs/REPRODUCIBILITY_STANDARD.md) — what each `reproducibility` value means.
- [`docs/FORK_VERIFICATION.md`](docs/FORK_VERIFICATION.md) — chain aliases, RPC requirements, verification recording.
- [`docs/AUDITOR_CHECKLIST.md`](docs/AUDITOR_CHECKLIST.md) — per-category review prompts.
- [`docs/ROOT_CAUSE_PLAYBOOK.md`](docs/ROOT_CAUSE_PLAYBOOK.md) — how to write a credible root-cause section.
- [`docs/INCIDENT_INTAKE.md`](docs/INCIDENT_INTAKE.md) — pipeline for adding a new incident.
- [`docs/EXPANSION_PLAN.md`](docs/EXPANSION_PLAN.md) — milestones from the current corpus onward.

## Repository layout

```
.
├── EVM/        Foundry project: PoCs under test/, helpers under src/
├── SVM/        Anchor scaffold (template only)
├── MoveVM/     Aptos Move scaffold (template only)
├── metadata/   Canonical registry + JSON Schema
├── reports/    PoC quality matrix + per-PoC verification reports
├── scripts/    Validation, registry generation, scoring tooling
├── docs/       Brand, ethics, research standard, reproducibility
└── README.md
```

## PoC maturity ladder

Every entry sits at a level on this ladder. The current distribution is
in the status table above and in
[`reports/poc_maturity_index.md`](reports/poc_maturity_index.md).

| Level | Label | What it means |
|---|---|---|
| L0 | Raw Replay | Compiles, but proof is weak — only logs or balance modifiers. |
| L1 | Structured Metadata | Required metadata fields populated; no `unknown` placeholders. |
| L2 | Assertion-Hardened | Hard assertions cover the documented exploit primitive (static readiness). |
| L3 | Public RPC Smoke-Tested | A public RPC fork run has been recorded honestly. |
| L4 | Archival Verified | `forge test` runs to green on a pinned archival fork; verification report has real run output. |
| L5 | Research-Grade Case Study | L4 plus long-form root-cause writeup, patch lesson, and auditor checklist exercised. |

Public-RPC limitations (`public-rpc-not-archival`,
`public-rpc-rate-limited`, `public-rpc-unstable`) are RPC capability
issues, not progress, and do not promote an entry past L2. The full
ladder is defined in
[`docs/POC_MATURITY_MODEL.md`](docs/POC_MATURITY_MODEL.md).

## Verification model

A PoC moves through three distinct readiness levels:

1. **Static review** — code compiles, fork block is pinned, metadata is
   complete, hard assertions cover the documented exploit primitive.
   Recorded in `assertion_quality` and reflected in
   [`reports/poc_quality_matrix.md`](reports/poc_quality_matrix.md).
2. **Smoke test (public RPC)** — `setUp()` and exploit body execute
   without reverting against a public RPC where archival history is
   available. Useful for recent incidents; insufficient for older ones.
3. **Deterministic confirmation (archival RPC)** — `forge test` runs to
   green against a pinned archival fork on this branch, with a recorded
   verification artifact under
   [`reports/verification/`](reports/verification/).

Most historical exploits in this archive require step 3. Public RPCs
typically do not retain state old enough to fork at, for example, block
4,043,799 (Parity Multisig, 2017). When a public RPC returns *historical
state is not available*, that is recorded as an RPC limitation, not a
PoC failure. The entry stays at `deterministic-likely-but-unverified`
until an archival RPC is configured and the fork test passes.

## Assertion quality

Each entry is tagged with one of four levels:

| Level | Meaning |
|---|---|
| strong | Hard assertions cover attacker profit, victim loss, and the broken invariant — sufficient to fail loudly if the exploit logic regresses. |
| medium | At least one hard assertion against post-state; one or more required families partially covered. |
| weak | PoC executes the exploit shape but ends without assertions strong enough to prove the compromise (e.g. only `console.log` of balances). |
| none | No `assert*` calls present. |

Static assertion hardening is independent of runtime verification. A
strong-assertion PoC can still sit at
`deterministic-likely-but-unverified` until archival fork execution
confirms it.

## Severity

| Level | Meaning |
|---|---|
| critical | Unconditional fund loss or full protocol takeover. |
| high | Conditional fund loss, or permanent denial of service of core flow. |
| medium | Fund risk under specific conditions, governance manipulation, or reversible DoS. |
| low | Bounded value impact or significant griefing without direct loss. |
| informational | Defensive note; not exploitable in isolation. |

Severity is recorded in metadata and is not asserted by the test code.

## Running an EVM PoC

From `EVM/`:

```sh
forge install
export ETH_RPC_URL=https://your-archival-node-endpoint

# Single PoC.
forge test --match-path "test/2017-07/*.t.sol" -vvvv

# Full suite.
forge test -vvv
```

Most historical PoCs require an **archival** RPC endpoint. Public RPCs
will accept the connection but error out with *historical state is not
available* during `vm.createSelectFork`. See
[`docs/FORK_VERIFICATION.md`](docs/FORK_VERIFICATION.md) for chain
aliases, required environment variables, and how to record verification
results.

## Ethics and responsible use

This repository is defensive security research. By using the contents
you accept the terms in [`docs/ETHICS.md`](docs/ETHICS.md):

- No unauthorized testing against live systems.
- No adapting these PoCs to extract value without consent.
- Compliance with applicable law, contracts, and disclosure obligations.

If you believe content here may aid an attack against an unpatched live
system, contact the maintainer privately. See
[`docs/SECURITY.md`](docs/SECURITY.md).

## Researcher

Maintained by **Yudistira Putra** — `arkheionx` /
[@Yudis-bit](https://github.com/Yudis-bit).

Focus areas:

- DeFi exploit reproduction
- Smart contract security research
- Fork-based PoC engineering
- Root-cause analysis and exploit taxonomy
- Assertion-driven verification

## Roadmap

Honest near-term plan:

- Finish assertion hardening for the current 18-entry corpus.
- Configure an archival RPC and produce verification reports for entries
  that already pass static review.
- Normalise retained legacy id slugs where reclassification has
  occurred, without churning file paths.
- Expand to ~25 verified-ready PoCs.
- Expand to ~100 PoCs with the same quality gate.
- Build out SVM and MoveVM only when there is a real PoC to merge, not
  as scaffolding.

See [`docs/ROADMAP.md`](docs/ROADMAP.md) and
[`docs/EXPANSION_PLAN.md`](docs/EXPANSION_PLAN.md).

## Vulnerability registry

The table below is generated from `metadata/registry.json`. Do not
hand-edit. Run `python scripts/generate_registry.py` to regenerate.

A static-readiness scoring of the registry — metadata completeness,
assertion presence, root-cause clarity — lives at
[`reports/poc_quality_matrix.md`](reports/poc_quality_matrix.md),
generated by `python scripts/score_pocs.py`. The maturity index lives
at [`reports/poc_maturity_index.md`](reports/poc_maturity_index.md),
generated by `python scripts/poc_maturity_index.py`. An aggregated
view is at
[`reports/research_dashboard.md`](reports/research_dashboard.md),
generated by `python scripts/research_dashboard.py`. Per-PoC
verification reports go under
[`reports/verification/`](reports/verification/), generated by
`python scripts/generate_verification_report.py`. Until an entry has
a verification report containing real run output, it stays at
`deterministic-likely-but-unverified` regardless of how complete its
metadata looks.

Where an `id` slug was retained from an earlier label after Phase 6A
reclassification, the `Protocol` column reflects current truth. The slug
is preserved only to keep file paths stable; see the relevant entry's
`notes` field in `metadata/registry.json` for the reclassification
record.

## License and disclaimer

All content is provided for defensive research and educational use.
Reproductions target historical, patched, or otherwise resolved
incidents. Nothing in this repository is investment, legal, or security
advice. The maintainer assumes no liability for downstream use.

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
| 2020-06 | Bancor — public safeTransferFrom on newly deployed contract | ethereum | high | access-control-failure | needs-verification | [`EVM/test/2020-06/Exploit_2020-06.t.sol`](EVM/test/2020-06/Exploit_2020-06.t.sol) |
| 2020-08 | Opyn — duplicate ETH option exercise | ethereum | high | invariant-bypass | historical | [`EVM/test/2020-08/Exploit_2020-08.t.sol`](EVM/test/2020-08/Exploit_2020-08.t.sol) |
| 2020-09 | bZx — iETH self-transfer double-write | ethereum | critical | accounting-mismatch | needs-verification | [`EVM/test/2020-09/Exploit_2020-09.t.sol`](EVM/test/2020-09/Exploit_2020-09.t.sol) |
| 2020-10 | Harvest Finance — fUSDT/fUSDC oracle manipulation | ethereum | critical | flash-loan-price-manipulation | historical | [`EVM/test/2020-10/Exploit_2020-10.t.sol`](EVM/test/2020-10/Exploit_2020-10.t.sol) |
| 2020-11 | Pickle Finance — swapExactJarForJar arbitrary-call drains cDAI strategy | ethereum | critical | unsafe-external-call | needs-verification | [`EVM/test/2020-11/Exploit_2020-11.t.sol`](EVM/test/2020-11/Exploit_2020-11.t.sol) |
| 2020-12 | Cover Protocol — Blacksmith claimRewards infinite mint | ethereum | critical | accounting-mismatch | needs-verification | [`EVM/test/2020-12/Exploit_2020-12.t.sol`](EVM/test/2020-12/Exploit_2020-12.t.sol) |
| 2021-01 | SushiSwap SushiMaker — DIGG/WBTC missing-bridge convert exploit | ethereum | high | amm-invariant-manipulation | needs-verification | [`EVM/test/2021-01/Exploit_2021-01.t.sol`](EVM/test/2021-01/Exploit_2021-01.t.sol) |
| 2021-02 | Yearn v1 DAI vault — Curve 3pool oracle manipulation | ethereum | critical | flash-loan-price-manipulation | historical | [`EVM/test/2021-02/Exploit_2021-02.t.sol`](EVM/test/2021-02/Exploit_2021-02.t.sol) |
| 2021-03 | DODO — CrowdPooling init reentrancy | ethereum | high | initialization-bug | historical | [`EVM/test/2021-03/Exploit_2021-03.t.sol`](EVM/test/2021-03/Exploit_2021-03.t.sol) |
| 2021-10 | Indexed Finance — DEFI5/CC10 reweight manipulation | ethereum | critical | amm-invariant-manipulation | historical | [`EVM/test/2021-10/Exploit_2021-10.t.sol`](EVM/test/2021-10/Exploit_2021-10.t.sol) |
| 2022-02 | BUILD Finance — governance takeover via low-quorum proposal | ethereum | high | governance-attack | needs-verification | [`EVM/test/2022-02/Exploit_2022-02.t.sol`](EVM/test/2022-02/Exploit_2022-02.t.sol) |
| 2025-11 | Moonwell — Chainlink oracle staleness on Base | base | high | oracle-manipulation | historical | [`EVM/test/2025-11/Exploit_2025-11.t.sol`](EVM/test/2025-11/Exploit_2025-11.t.sol) |
| 2025-12 | yETH — pool invariant manipulation | ethereum | critical | amm-invariant-manipulation | historical | [`EVM/test/2025-12/Exploit_2025-12.t.sol`](EVM/test/2025-12/Exploit_2025-12.t.sol) |

<!-- END: registry -->

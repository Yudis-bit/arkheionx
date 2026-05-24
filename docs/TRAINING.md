# Training

Arkheionx Vault can support paid training for auditors, protocol engineers, and
security researchers who want to learn from historical DeFi failures.

Training uses public incidents and defensive exercises. It does not teach live
targeting, scanner construction, or value extraction against production systems.

## Workshop Menu

| Workshop | Length | Audience | Starting range |
|---|---:|---|---:|
| Assertion-Driven PoCs | 90 minutes | Researchers who already know basic Foundry | USD 1,000 |
| Exploit Anatomy for Auditors | 2.5 hours | Auditors and protocol engineers | USD 1,750 |
| Oracle and Accounting Failure Lab | Half day | DeFi teams and audit groups | USD 3,000 |
| Private Corpus Walkthrough | Custom | Teams using the archive for internal learning | Scoped quote |

Ranges are starting points for remote sessions. In-person work, custom
curriculum, and team-specific preparation should be scoped separately.

## Core Modules

### 1. Reading a Historical PoC

- Identify the fork block, chain alias, target contracts, and attacker path.
- Separate setup code from exploit code.
- Spot replay-only code that does not prove compromise.
- Map source comments back to registry metadata.

### 2. Assertion Families

- Use F1-F9 from `docs/ASSERTION_STANDARD.md`.
- Convert logs into hard assertions.
- Avoid tautological assertions and loose `assertGt(profit, 0)` checks.
- Decide when an entry is `weak`, `medium`, or `strong`.

### 3. Root Cause and Invariant Mapping

- Write the vulnerable assumption.
- Name the invariant that should have held.
- Identify attacker-controlled variables.
- Turn post-mortem language into auditor review prompts.

### 4. Fork Verification

- Read `metadata/registry.json` as the source of truth.
- Distinguish public-RPC smoke tests from archival verification.
- Interpret fork setup failures without weakening the PoC.
- Prepare a verification report without leaking RPC endpoints.

### 5. Case Study Walkthrough

Suggested incidents:

- Parity Multisig: access control and initialization.
- BEC Token: arithmetic overflow and supply invariant break.
- bZx iETH: accounting mismatch.
- Harvest Finance: flash-loan-funded price manipulation.
- DODO CrowdPooling: initialization bug.

## Deliverables

A standard training engagement can include:

- Session agenda.
- Slide deck or notes.
- PoC walkthrough list.
- Exercise prompts.
- Follow-up reading path.
- Optional written feedback on participant exercises.

## Prerequisites

Participants should know:

- Basic Solidity.
- Foundry test structure.
- ERC-20 balance and allowance flows.
- The difference between a fork test and a live transaction.

For advanced sessions, participants should also be comfortable reading traces,
AMM math, lending markets, and oracle assumptions.

## Boundaries

Training does not include:

- Help attacking live systems.
- Help bypassing detection.
- Private exploit adaptation.
- Unpatched vulnerability disclosure through a public channel.
- Guarantee of bounty payouts.

For live or unpatched findings, follow coordinated disclosure through the
protocol's published security channel.

## Related Pages

- [`COMMERCIAL.md`](COMMERCIAL.md) — scoped commercial work.
- [`CASE_STUDY_SAMPLE.md`](CASE_STUDY_SAMPLE.md) — example case-study output.
- [`CONTENT_PLAYBOOK.md`](CONTENT_PLAYBOOK.md) — public teaching topics.
- [`PROPOSAL_TEMPLATE.md`](PROPOSAL_TEMPLATE.md) — engagement template.

# Priority Lanes

The backlog is not first-in-first-out. Candidates are ranked by lane,
and lanes are worked top-down. The lane system exists so the corpus
grows toward defensive-research value, not toward whatever incident is
loudest on Twitter / X this week.

A candidate must declare its lane in `lanes` (array; primary first).
Lanes are documented here so triage decisions are reviewable.

---

## Lane 1 — Historical high-impact DeFi incidents

Incidents with a public, well-attributed post-mortem and a six-figure-
USD-or-greater documented loss.

**Why this lane exists.** These are the cases the field already studies.
Adding them with assertion-hardened PoCs and root-cause notes raises the
floor for new researchers reading the archive.

**Triage signal.** Public post-mortem from the protocol team or a
respected third party; attack tx visible on a block explorer; patch
landed.

**Examples already in the registry.** Parity Multisig (2017-07), BeC
Token overflow (2018-04), bZx (2020-09), Cover (2020-12), DODO V2
crowd-pool (2021-03).

---

## Lane 2 — Oracle manipulation

Manipulation of price feeds, TWAPs, spot oracles, or single-block
liquidity reads. Includes flash-loan-driven oracle manipulation.

**Why this lane exists.** The most repeatedly-exploited DeFi primitive.
A category-thick lane forces the assertion standard's F1/F2/F5 family
to be exercised across many shapes (constant-product spot, TWAP, lending
collateral oracles, vault share-price oracles).

**Triage signal.** Loss is traceable to a price input that diverged
from honest market state during the attack tx.

---

## Lane 3 — Reentrancy and callback failures

Classic single-function reentrancy, cross-function reentrancy, and
read-only reentrancy. Callback-misuse from ERC-777, ERC-1155, native
transfer hooks, and external-protocol hooks.

**Why this lane exists.** Still finding fresh victims a decade after
The DAO. Read-only reentrancy in particular is under-represented in
educational material relative to its frequency.

**Triage signal.** Attack involves a re-entered call into the same or
related contract during an external interaction.

---

## Lane 4 — Accounting / share-price manipulation

Vault share-price inflation, donation attacks against ERC-4626-shaped
vaults, fee-on-transfer accounting drift, rebasing-token assumptions,
direct-token-transfer accounting bypass.

**Why this lane exists.** A whole category of bugs whose root cause is
"the protocol believed `balanceOf(self)` reflected internal accounting".
Documenting this lane creates a clean reference set.

**Triage signal.** Attacker mint / redeem creates value asymmetry without
a bug in pricing math alone.

---

## Lane 5 — Governance and access-control failures

Unprotected admin functions, mis-scoped role checks, governance
takeover via flash-loan-borrowed voting power, mis-deployed proxies,
unprotected initializers.

**Why this lane exists.** Often catastrophic, often easy to assert
against (control / ownership families F4 and F7), often the result of a
single missing modifier.

**Triage signal.** Attack succeeds because a privileged function did
not gate on the privileged actor.

---

## Lane 6 — Bridge and cross-chain failures

Validation-layer failures in bridges and cross-chain messaging:
signature verification bugs, replay across domains, mis-encoded
messages, fake-deposit proofs.

**Why this lane exists.** High blast radius, low replay-friendly
material. A small but important corner of the corpus that is
disproportionately important to study at depth.

**Triage signal.** Attack crosses a domain boundary (chain, rollup,
appchain) and exploits how the boundary validates state.

---

## Lane 7 — Vault and lending protocol failures

Liquidation-logic flaws, bad-debt socialization bugs, broken
collateral accounting, interest accrual mistakes, isolation-mode
edge cases.

**Why this lane exists.** Lending and vault primitives compose with
everything else; documenting their failure modes is high-leverage.

**Triage signal.** Attack manipulates the protocol's view of borrower
or vault solvency.

---

## Lane 8 — Weird edge-case primitives

Everything that does not fit cleanly above: novel signature-permit
abuse, callback ordering bugs, gas-griefing flow attacks, MEV-adjacent
protocol-layer bugs, unusual invariant breaks.

**Why this lane exists.** Some of the most instructive PoCs come from
this lane. It exists explicitly so the priority order does not pre-empt
them.

**Triage signal.** Anything credible enough to attribute and reproduce
that does not match Lanes 1–7.

---

## Cross-lane rules

- A candidate may list multiple lanes. The first lane in `lanes` is the
  primary lane.
- Lane assignment is independent of severity. A high-severity bridge
  bug and a low-severity oracle bug can both belong to their primary
  lanes simultaneously.
- A candidate that does not match any lane is held in the backlog with
  `blocked_on: taxonomy-review` until the taxonomy is updated or the
  candidate is rejected.
- Re-classification is allowed and recorded in `notes`. Hidden
  re-classification is not.

---

## How lanes interact with milestones

The milestones in [`docs/launch/EXPANSION_PLAN.md`](../../docs/launch/EXPANSION_PLAN.md)
gate by quality, not by lane balance. Lanes only set triage order.
That said, M3 (100 PoCs) declares a quality bar of "every taxonomy
category has at least one verified entry" — the lanes here are the
intake-side mirror of that goal.

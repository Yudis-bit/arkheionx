# Backlog Priority Lanes

The backlog is not first-come-first-served. Candidates are organized
into priority lanes that align with the corpus's quality gaps and the
lessons each lane teaches. Lanes are deliberately defensive — every
lane is justified by what an asserted PoC of that incident class
contributes to learning, not by hype.

A candidate may belong to more than one lane. The first lane listed in
the candidate's notes is treated as primary.

## Lane: oracle manipulation

Why: oracles remain the single most exploited surface in DeFi.
Asserted PoCs in this lane teach the difference between spot,
TWAP, and Chainlink-style feeds, and how each fails.

Required assertion families: F1, F2, F5.

Already represented: Harvest Finance (2020-10), Yearn v1 DAI (2021-02),
Moonwell (2025-11).

## Lane: reentrancy and callback misuse

Why: callbacks remain a foundational primitive. ERC-777 hooks,
ERC-721 onReceived, flash loan callbacks, and protocol-specific
hooks all show up here.

Required assertion families: F1, F2 (or F4|F1 for callback misuse).

Already represented: SpankChain (2018-10), Uniswap V1 imBTC (2020-04),
DODO CrowdPooling (2021-03).

## Lane: accounting and share-price manipulation

Why: vault economics depend on share-price math being honest. This
lane teaches share inflation, donation attacks, and balance / supply
mismatches.

Required assertion families: F3, F6, F9 depending on subtype.

Already represented: bZx iETH (2020-09), Cover Blacksmith (2020-12),
yETH (2025-12).

## Lane: governance and access control

Why: governance attacks rarely look like hacks at the moment of
execution. They look like proposals. This lane teaches quorum design,
proposal validation, and timelock assumptions.

Required assertion families: F4|F7, with F2 on protocol-treasury
post-state.

Already represented: Parity Multisig (2017-07), Parity Suicide
(2017-11), Bancor public-safeTransferFrom (2020-06), BUILD Finance
(2022-02).

## Lane: lending and liquidation

Why: liquidation engines are where bad-debt creation, oracle
manipulation, and accounting bugs intersect. Asserted PoCs here teach
borrow / repay invariants and liquidation-fairness assumptions.

Required assertion families: F8, F1, F3.

Already represented: bZx iETH double-write (2020-09).
Underrepresented overall — high priority for new candidates.

## Lane: bridge and cross-chain

Why: bridges concentrate the largest absolute USD impact. Their
failures teach signature replay, message validation, asset
canonicalization, and finality assumptions.

Required assertion families: F1, F2, plus message-validity assertions.

Not yet represented in the registry. High priority once an archival
multi-chain RPC is configured.

## Lane: vault strategy and yield routing

Why: yield strategies expose users to integration-level risk that
single-protocol audits miss. Asserted PoCs teach strategy
permissioning, harvest accounting, and reward-token assumptions.

Required assertion families: F3, F6.

Already represented: Pickle Finance ControllerV4 (2020-11).

## Lane: AMM invariant manipulation

Why: AMM math is where flash loans, weight shifts, and rebases meet.
Asserted PoCs teach invariant preservation across non-standard
sequences.

Required assertion families: F3, F1.

Already represented: SushiSwap SushiMaker bridge (2021-01),
Indexed Finance reweight (2021-10), yETH (2025-12).

## Lane: token-standard edge cases

Why: ERC-20 implementations diverge on transfer return values,
fee-on-transfer, rebasing, and pre-existing approvals. Asserted PoCs
here teach integration-level safety.

Required assertion families: F6, F1.

Already represented: BEC overflow (2018-04). Underrepresented overall.

## Lane: historical high-impact incidents

Why: incidents above ~$50M in observed impact deserve a slot
regardless of category, because their exploitation patterns get
re-used in later attacks.

Required assertion families: per category.

This is a meta-lane: a candidate that already fits another lane and
has high historical impact ranks higher within its category lane.

## Lane: weird primitives

Why: not every important PoC fits a tidy category. SELFDESTRUCT
semantics, delegatecall to libraries, signature replay, MEV
sandwich-only exploits, and chain-fork edge cases live here. A small
number of slots per milestone are reserved for weird primitives that
teach a lesson the named lanes do not.

Required assertion families: per case.

Already represented: Parity Suicide (2017-11), Opyn duplicate
exercise (2020-08).

## How a lane is chosen for a candidate

1. Match the incident's primary mechanism to one lane.
2. If the candidate fits two lanes equally, pick the one currently
   weaker in the corpus.
3. Record the chosen lane in the candidate's `notes` field.
4. The lane fixes the required assertion families for the eventual
   PoC; deviations require explicit justification.

# Auditor Checklist

Reusable per-category checklists for security auditors and security
researchers using this archive. These are not exhaustive; they are
the questions that, in hindsight, would have caught the incidents
catalogued under each category.

Use them as discussion prompts during an audit, not as a substitute
for reading the code.

---

## General checklist (every protocol)

- [ ] Compiler version pinned; `unchecked` blocks justified.
- [ ] Reentrancy guards applied at the function-family level, not just
      individual functions.
- [ ] Every external call is reviewed for callbacks (ERC-777, ERC-1155,
      flash hooks).
- [ ] Every privileged function has a single documented authorization
      path.
- [ ] Initializers are protected and run once.
- [ ] Implementation contracts disable initializers.
- [ ] Storage layout documented; no reordering between upgrades.
- [ ] All approvals scoped (no infinite approvals to user-driven
      routers).
- [ ] All loops bounded.
- [ ] All math reviewed for rounding direction.
- [ ] Pause / freeze paths exist and are reachable.

## oracle-manipulation / flash-loan-price-manipulation

- [ ] All price reads classified: spot, TWAP, signed feed, LP, custom.
- [ ] Spot prices are not used for borrow / mint / liquidation.
- [ ] TWAP windows long enough that a manipulator's risk budget
      exceeds their realistic capital.
- [ ] LP token valuations use sqrt(reserve product) or fair-share
      pricing, not instantaneous reserves.
- [ ] Pegged-asset assumptions documented and tested under depeg.
- [ ] No protocol action's safety assumes the caller has bounded
      capital.

## reentrancy / read-only-reentrancy

- [ ] Checks-effects-interactions ordering on every external-call path.
- [ ] All callback-bearing token interfaces in scope identified.
- [ ] Cross-function reentrancy: state shared across functions guarded
      by the same lock.
- [ ] View functions returning derived quantities are guarded if
      callers may be inside a callback.
- [ ] ETH `.call` recipients are trusted or guarded.
- [ ] Reentrancy on the *family* of functions, not just one.

## access-control-failure / initialization-bug

- [ ] Every state-changing function has explicit authorization.
- [ ] Initializers protected, run at deploy.
- [ ] Implementation contracts disable initializers in their
      constructor.
- [ ] Roles updated through documented timelock / multisig path.
- [ ] No public function shadows a privileged one via fallback /
      proxy.
- [ ] Function visibility (`public` vs `external`) reviewed for
      unintended exposure.

## arithmetic-precision-rounding

- [ ] Solidity ≥0.8 OR every arithmetic op covered by SafeMath.
- [ ] Conversions round in the protocol's favor.
- [ ] Decimals normalized at the boundary, not deep inside math.
- [ ] Boundary values tested: 0, 1 wei, max, min, decimal mismatches.
- [ ] No division before multiplication where order matters.

## accounting-mismatch / fee-on-transfer-rebasing-assumption

- [ ] Token allowlist or explicit rejection of fee-on-transfer / rebase.
- [ ] Internal balances reconciled against `balanceOf` on every
      transfer where supported.
- [ ] Single source of truth per accounting concept.
- [ ] No "assume amount transferred = amount requested" anywhere on
      the value path.

## share-price-manipulation / donation-inflation

- [ ] First-deposit attack mitigated (virtual shares, seed deposit, or
      both).
- [ ] `totalAssets` cannot be moved by a third-party donation in a way
      the protocol does not anticipate.
- [ ] `convertToAssets` round-trip tested at edge sizes.
- [ ] Fees do not break invariants under boundary conditions.

## governance-attack

- [ ] Voting power source not flash-loanable.
- [ ] Snapshot / lock / escrow used for vote weighting.
- [ ] Timelock on proposal execution longer than realistic detection
      window.
- [ ] Quorum tied to circulating supply.
- [ ] Emergency veto / guardian path documented.

## signature-permit-misuse

- [ ] Domain separator includes chain ID and verifying contract.
- [ ] Nonces monotonic and per-signer.
- [ ] Deadlines enforced.
- [ ] Signature malleability handled (low-S, EIP-2098).
- [ ] EIP-712 struct hashing reviewed for type collisions.
- [ ] `permit` failure handled in router flows.

## bridge-validation-failure

- [ ] Proof verification reads receipt-level data, not just events.
- [ ] Withdrawal markers persist.
- [ ] Validator set rotation auditable.
- [ ] Reorg / finality assumptions match each chain's actual finality.

## liquidation-logic-flaw

- [ ] Oracle source for liquidation manipulation-resistant.
- [ ] Self-liquidation forbidden or economically neutral.
- [ ] Partial liquidation closes the right fraction; no dust loophole.
- [ ] Liquidation incentive bounded.
- [ ] Liquidation feasibility tested under stress.

## vault-strategy-accounting-flaw

- [ ] Strategy reported balance does not depend on a manipulable spot
      value.
- [ ] Harvest path attributes rewards correctly.
- [ ] Emergency withdraw path tested.
- [ ] Drift between strategy and vault accounting bounded.

## amm-invariant-manipulation

- [ ] Invariant proven over the full reachable input space.
- [ ] Rate updates ordered after liquidity moves, or guarded.
- [ ] Rebase / fee-on-transfer tokens explicitly out of scope unless
      supported.
- [ ] Boundary cases (empty pool, single-sided liquidity) modelled.

## callback-misuse / unsafe-external-call

- [ ] Callback target validated (allowlist or interface check).
- [ ] Caller's state finalized before callback or guarded.
- [ ] Reentry into the same family of functions blocked.
- [ ] No `target.call(data)` paths without strict allowlisting.
- [ ] Approvals scoped tightly.

## proxy-upgradeability-issue

- [ ] Storage layout diffed between versions.
- [ ] UUPS `_authorizeUpgrade` overridden and gated.
- [ ] No `delegatecall` to user-supplied target.
- [ ] No `selfdestruct` reachable via `delegatecall`.
- [ ] Upgrade authority documented and reviewed.

## bad-debt-creation / invariant-bypass / economic-design-flaw

- [ ] Liquidation feasibility tested under stress.
- [ ] Bad-debt socialization or insurance present.
- [ ] All entry points reach the same invariant check.
- [ ] Reward / fee model simulated against rational adversary.
- [ ] "What if everyone does X" written down.

---

## Using the checklist

For each PoC in this archive:

1. Identify its category (and tags).
2. Read its `root_cause`, `invariant_broken`,
   `protocol_assumption_failure`, and `attacker_path`.
3. Walk the relevant checklist against the original protocol code.
4. Note which checklist items would have caught the incident.

This is the artifact this archive most directly produces for auditors:
a structured way to learn from the actual sequence of failures, not
just from the bug class in the abstract.

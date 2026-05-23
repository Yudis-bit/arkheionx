---
name: Assertion hardening
about: Propose strengthening assertions on an existing PoC, without changing the exploit shape.
title: "[assertion-hardening] <YYYY-MM-protocol>"
labels: ["assertion-hardening"]
---

## PoC

- **Registry id** (`metadata/registry.json`):
- **Path**: `EVM/test/<folder>/<file>.t.sol`
- **Current `assertion_quality`**:
- **Current category**:

## Proposed proof target

<!-- Which attacker / victim / invariant fact will the new assertions
     prove? One paragraph. Reference the family codes in
     docs/ASSERTION_STANDARD.md (F1..F9). -->

## Expected invariant

<!-- The protocol invariant the exploit broke, stated as something a
     reviewer can verify on post-state. -->

## Attacker impact

<!-- The attacker-side proof. Profit, control change, role acquisition,
     etc. Cite balances, allowances, or storage slots, not log lines. -->

## Victim / protocol impact

<!-- The victim-side proof. Drained balance, broken supply, frozen
     state, lost ownership. Same standard: post-state, not logs. -->

## RPC requirement

- [ ] Public RPC sufficient.
- [ ] Archival RPC required.
- [ ] Already verified against archival; this is a defense-in-depth
      tightening.

## False-positive risk

<!-- What could make these assertions pass without the exploit actually
     triggering? Pre-seeded balances? Mock contracts? Address those
     here. -->

## Out of scope

- [ ] No `EVM/src/**` changes.
- [ ] No exploit logic changes.
- [ ] Single PoC only — one PoC per patch.

---
name: Assertion hardening
about: Propose strengthening an existing PoC's assertions (weak/none -> medium/strong).
title: "[harden] <registry-id>"
labels: ["assertion-hardening"]
---

<!-- Use this template to propose lifting a PoC from L1 to L2 (or L2 to
     stronger L2) per docs/POC_MATURITY_MODEL.md. -->

## Target PoC

- **Registry id** (`metadata/registry.json`):
- **PoC path** (`EVM/test/...`):
- **Current `assertion_quality`** (`weak` / `medium` / `strong` / `none`):
- **Current maturity level** (from `reports/poc_maturity_index.md`):

## Proposed proof

- **Required assertion families** (from `docs/ASSERTION_STANDARD.md`,
  resolved against the entry's `category`):
- **Attacker profit assertion you intend to add**:
- **Victim loss / state-damage assertion you intend to add**:
- **Invariant break assertion you intend to add**:
- **Ownership / control assertion** (if the category requires F4/F7):

## Expected post-state

<!-- Quote concrete pre/post values you expect the pinned fork block to
     produce. e.g. "balance of victim pool drops from 1.2M USDC to ~30k
     USDC; share-price LP token drops from 1.42 to 0.31". -->

## Risk to existing test

- [ ] Change does not modify the exploit path itself.
- [ ] Change does not silently skip assertions on revert.
- [ ] Change does not introduce a `try/catch` that masks failure.
- [ ] If the test currently passes on a public RPC, the new assertions
      do not depend on archival-only state. If they do, that is called
      out below.

## Archival RPC requirement

- [ ] Yes — assertions read pre-attack state at the pinned block.
- [ ] No — assertions can be evaluated from `setUp()` deployment alone.

## Test command

```sh
cd EVM && forge test --match-path "test/<folder>/<file>.t.sol" -vvv
```

## Notes

<!-- Anything else worth recording: prior attempts, related PoCs that
     would benefit from the same hardening, etc. -->

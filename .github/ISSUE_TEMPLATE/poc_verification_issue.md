---
name: Validation fixture reproducibility issue
about: A historical validation fixture builds, but the assertions do not match what is documented.
title: "[reproducibility] <YYYY-MM-protocol>"
labels: ["reproducibility"]
---

## Validation fixture

- **Path**: `EVM/test/<folder>/<file>.t.sol`
- **Registry id**:
- **Documented `reproducibility` value** (`deterministic`, `requires-archival-rpc`, etc.):

## What is documented

<!-- Quote the relevant assertion, balance, or post-state from the PoC or its references. -->

## What you observed

<!-- Actual values you saw on your run. -->

## Reproduction

```
$ forge test --match-path "test/<folder>/*.t.sol" -vvv
```

- Fork block (from the test): 
- Chain alias used: 
- Archival RPC? yes / no:

## Notes

<!-- Anything that might explain divergence: state pruning, post-fork pool
     activity, time-sensitive oracle data, etc. -->

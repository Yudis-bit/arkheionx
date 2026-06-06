---
name: Broken PoC
about: A previously listed PoC no longer reproduces, fails to build, or asserts the wrong post-state.
title: "[broken-poc] <YYYY-MM-protocol>"
labels: ["broken-poc"]
---

## PoC

- **Path**: `EVM/test/<folder>/<file>.t.sol`
- **Registry id** (`metadata/registry.json`):

## What broke

<!-- What command did you run, what did you expect, what happened? -->

## Environment

- Foundry version (`forge --version`):
- Chain alias used:
- RPC provider (without URL/key):
- Archival? yes / no:

## Logs

```
<paste the relevant forge output, omit RPC URLs>
```

## Suspected cause

<!-- Optional: state pruning, RPC drift, broken submodule, refactor regression, etc. -->

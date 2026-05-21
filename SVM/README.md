# SVM (Solana / Anchor)

**Status: Template only.** No real PoC yet.

This directory is scaffolding for future Solana / SVM exploit PoCs. The
existing `tests/exploit.ts` is an empty Mocha block; it does not reproduce
any vulnerability.

The directory exists so contributors can submit the first real SVM PoC
without first having to invent the layout. Do not interpret its presence
as a claim of SVM coverage.

See [../docs/VM_SUPPORT.md](../docs/VM_SUPPORT.md) for the honest current
state of each VM family.

## Layout

```
SVM/
├── Anchor.toml          Localnet configuration
└── tests/
    └── exploit.ts       Empty Mocha stub (placeholder)
```

## Running (once a real PoC exists)

```sh
# From SVM/
anchor build
anchor test
```

## Contributing

The first real SVM PoC should:

- Reproduce a historical, patched Solana / SVM incident.
- Use a deterministic local test environment (bankrun, anchor test, or a
  pinned localnet snapshot).
- Include hard assertions on post-exploit state.
- Add a corresponding entry to `../metadata/registry.json` with `vm: SVM`
  and `reproducibility: local-only` (or whatever value matches reality).

See [../docs/CONTRIBUTING.md](../docs/CONTRIBUTING.md) and
[../docs/RESEARCH_STANDARD.md](../docs/RESEARCH_STANDARD.md).

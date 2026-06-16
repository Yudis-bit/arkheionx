# SVM Validation Fixture Scaffold

**Status: Template only.** No real validation fixture yet.

This directory is scaffolding for future Solana / SVM historical vulnerable-case
fixtures. The existing `tests/exploit.ts` file name is a legacy placeholder;
the file itself is an empty Mocha block and does not reproduce any
vulnerability.

The directory exists so contributors can submit the first real SVM fixture
without first having to invent the layout. Do not interpret its presence as a
claim of SVM coverage.

ArkheionX does not automate exploitation, confirm severity automatically, or
replace human review. Any future SVM fixture must be local, deterministic,
authorized, and framed as validation evidence.

See [../docs/VM_SUPPORT.md](../docs/VM_SUPPORT.md) for the honest current
state of each VM family.

## Layout

```
SVM/
├── Anchor.toml          Localnet configuration
└── tests/
    └── exploit.ts       Empty legacy-named validation placeholder
```

## Running (once a real validation fixture exists)

```sh
# From SVM/
anchor build
anchor test
```

## Contributing

The first real SVM fixture should:

- Reproduce a historical, patched Solana / SVM incident.
- Use a deterministic local test environment (bankrun, anchor test, or a
  pinned localnet snapshot).
- Include hard assertions on the relevant post-condition.
- Add a corresponding entry to `../metadata/registry.json` with `vm: SVM`
  and `reproducibility: local-only` (or whatever value matches reality).

See [../docs/CONTRIBUTING.md](../docs/CONTRIBUTING.md) and
[../docs/RESEARCH_STANDARD.md](../docs/RESEARCH_STANDARD.md).

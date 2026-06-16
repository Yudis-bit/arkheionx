# MoveVM Validation Fixture Scaffold

**Status: Template only.** No real validation fixture yet.

This directory is scaffolding for future MoveVM historical vulnerable-case
fixtures. The existing `sources/exploit.move` file name is a legacy placeholder;
the file itself is an empty `public entry fun execute(attacker: &signer)` stub
and does not reproduce any vulnerability.

The directory exists so contributors can submit the first real MoveVM fixture
without first having to invent the layout. Do not interpret its presence as a
claim of MoveVM coverage.

ArkheionX does not automate exploitation, confirm severity automatically, or
replace human review. Any future MoveVM fixture must be local, deterministic,
authorized, and framed as validation evidence.

See [../docs/VM_SUPPORT.md](../docs/VM_SUPPORT.md) for the honest current
state of each VM family.

## Layout

```
MoveVM/
├── Move.toml            Aptos framework dependency
└── sources/
    └── exploit.move     Empty legacy-named validation placeholder
```

## Running (once a real validation fixture exists)

```sh
# From MoveVM/
aptos move test
```

This currently requires the `aptos` CLI installed locally; see
[Aptos developer docs](https://aptos.dev/tools/aptos-cli/).

## Contributing

The first real MoveVM fixture should:

- Reproduce a historical, patched Aptos / Sui / MoveVM incident.
- Use a deterministic local test setup.
- Include hard assertions on the relevant post-condition.
- Add a corresponding entry to `../metadata/registry.json` with `vm: MoveVM`
  and `chain` set appropriately (`aptos`, `sui`).

See [../docs/CONTRIBUTING.md](../docs/CONTRIBUTING.md) and
[../docs/RESEARCH_STANDARD.md](../docs/RESEARCH_STANDARD.md).

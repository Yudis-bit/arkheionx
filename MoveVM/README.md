# MoveVM (Aptos)

**Status: Template only.** No real PoC yet.

This directory is scaffolding for future MoveVM exploit PoCs. The existing
`sources/exploit.move` is an empty `public entry fun execute(attacker: &signer)`
stub; it does not reproduce any vulnerability.

The directory exists so contributors can submit the first real MoveVM PoC
without first having to invent the layout. Do not interpret its presence
as a claim of MoveVM coverage.

See [../docs/VM_SUPPORT.md](../docs/VM_SUPPORT.md) for the honest current
state of each VM family.

## Layout

```
MoveVM/
├── Move.toml            Aptos framework dependency
└── sources/
    └── exploit.move     Empty entry function (placeholder)
```

## Running (once a real PoC exists)

```sh
# From MoveVM/
aptos move test
```

This currently requires the `aptos` CLI installed locally; see
[Aptos developer docs](https://aptos.dev/tools/aptos-cli/).

## Contributing

The first real MoveVM PoC should:

- Reproduce a historical, patched Aptos / Sui / MoveVM incident.
- Use a deterministic local test setup.
- Include hard assertions on post-exploit state.
- Add a corresponding entry to `../metadata/registry.json` with `vm: MoveVM`
  and `chain` set appropriately (`aptos`, `sui`).

See [../docs/CONTRIBUTING.md](../docs/CONTRIBUTING.md) and
[../docs/RESEARCH_STANDARD.md](../docs/RESEARCH_STANDARD.md).

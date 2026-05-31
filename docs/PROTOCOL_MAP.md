# Protocol Map

`arkheionx map` draws a DeFi protocol so a solo researcher can understand it
quickly: what kind of protocol it is, how users interact with it, where value
moves, which contracts hold value, and which functions deserve attention first.

```sh
arkheionx map examples/oracle-staking-fixture
```

## What it produces

- Protocol snapshot (type, contracts analyzed, Foundry status, evidence level).
- User journeys (plain-language stories built from entry/exit functions).
- Money-flow overview (enters / stored / exits / moved by / depends on).
- Contract role map.
- Function risk map.
- Top hunter targets.
- Suggested tests.
- Artifacts and the recommended next command.

## Contract roles

`User Entry`, `Value Holder`, `Share Token`, `Accounting`, `Pricing / Oracle`,
`Strategy`, `Reward Distributor`, `Queue / Escrow`, `Router`, `Manager`,
`Token`, `Privileged Controller`, `External Adapter`, `Test / Mock`, `Unknown`.

## Function roles

`Money Entry`, `Money Exit`, `Asset Transfer`, `Share Mint`, `Share Burn`,
`Accounting Update`, `Pricing Update`, `Oracle Read`, `Reward Claim`,
`Strategy Movement`, `Privileged Movement`, `External Call`,
`Pause / Emergency`, `Config Change`, `Unknown`.

## Evidence

Classification starts at `HEURISTIC`. Passing `--build` runs `forge build`; when
it succeeds, confirmed contracts are upgraded to `COMPILER_CONFIRMED`. See
[`FOUNDRY_INTEGRATION.md`](FOUNDRY_INTEGRATION.md).

## Flags

- `--show-all` — include interfaces/tests/mocks/fixtures hidden by default.
- `--full` — detailed terminal output (tables).
- `--json` — print machine-readable JSON to stdout.
- `--no-artifacts` — do not write artifact files.
- `--artifacts-dir <dir>` — base directory for `.arkheionx/out/`.
- `--top <N>` — number of hunter targets to include.

Output follows the shared [`OUTPUT_STANDARD.md`](OUTPUT_STANDARD.md).

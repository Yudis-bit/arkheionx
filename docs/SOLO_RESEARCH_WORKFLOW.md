# Solo Research Workflow

Arkheionx is a Foundry-powered solo security testing workbench.

```text
Find the money. Map the protocol. Prove the bug.
```

Foundry proves. Arkheionx guides, maps, explains, ranks, packages, and reports.

## The loop

```text
open  ->  map  ->  flow  ->  hunt  ->  prove  ->  (forge test)
```

1. **Orient** — understand the project in one command.

   ```sh
   arkheionx open .
   ```

2. **Map** — draw the protocol: roles, journeys, money flow, hunter targets.

   ```sh
   arkheionx map .
   ```

3. **Flow** — build the money-flow graph (Mermaid + JSON).

   ```sh
   arkheionx flow . --mermaid
   ```

4. **Hunt** — rank the highest-value review surfaces for a solo researcher.

   ```sh
   arkheionx hunt . --top 10
   ```

5. **Prove** — generate a local Foundry proof scaffold for a chosen target.

   ```sh
   arkheionx prove . --target claimReward
   forge test --match-contract Arkheionx<...>ProofTest
   ```

## Evidence discipline

Results are labeled `HEURISTIC`, `COMPILER_CONFIRMED`, `EXECUTION_CONFIRMED`, or
`REPORT_READY`. A scaffold is a starting point, not a proof. No bug is confirmed
until a real test or trace passes. See [`OUTPUT_STANDARD.md`](OUTPUT_STANDARD.md)
and [`FOUNDRY_INTEGRATION.md`](FOUNDRY_INTEGRATION.md).

## Planned commands

These are roadmap items, not yet available:

- `arkheionx trace <repo> --target <test>` — summarize Foundry traces into
  human-readable evidence (raw traces stored as artifacts).
- `arkheionx report <repo> --from-proof <artifact>` — build a structured report
  draft from proof artifacts.

## Safety boundaries

Local/static and defensive only:

- no RPC or live-chain calls;
- no deployed-contract scanning;
- no transaction execution;
- no private key, mnemonic, token, or secret handling;
- no exploit payload generation or attack automation;
- no formal audit or security guarantee claims.

Use Arkheionx only on repositories you own or are authorized to review.

## Related

- [`PROTOCOL_MAP.md`](PROTOCOL_MAP.md)
- [`VALUE_FLOW_WORKBENCH.md`](VALUE_FLOW_WORKBENCH.md)
- [`OUTPUT_STANDARD.md`](OUTPUT_STANDARD.md)
- [`FOUNDRY_INTEGRATION.md`](FOUNDRY_INTEGRATION.md)

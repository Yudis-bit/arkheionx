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

5. **Prove** — generate a local Foundry proof scaffold and optionally run it.

   ```sh
   arkheionx prove . --target Vault.withdraw            # scaffold only
   arkheionx prove . --target Vault.withdraw --run      # run targeted Foundry tests
   ```

6. **Trace** — summarize the latest proof/trace into human-readable evidence.

   ```sh
   arkheionx trace . --target Vault.withdraw
   ```

7. **Evidence** — package proof + trace into a structured evidence bundle.

   ```sh
   arkheionx evidence . --target Vault.withdraw
   ```

8. **Report** — draft a responsible local report (then review manually).

   ```sh
   arkheionx report . --target Vault.withdraw
   ```

## Evidence discipline

Results are labeled `HEURISTIC`, `COMPILER_CONFIRMED`, `EXECUTION_CONFIRMED`, or
`EVIDENCE_READY`. A scaffold is a starting point, not a proof. A bug is only
EXECUTION_CONFIRMED when a relevant Foundry test actually executed. See
[`EXECUTION_PROOF.md`](EXECUTION_PROOF.md), [`TRACE_ENGINE.md`](TRACE_ENGINE.md),
[`EVIDENCE_PACKAGE.md`](EVIDENCE_PACKAGE.md), [`REPORT_DRAFTS.md`](REPORT_DRAFTS.md),
[`OUTPUT_STANDARD.md`](OUTPUT_STANDARD.md), and
[`FOUNDRY_INTEGRATION.md`](FOUNDRY_INTEGRATION.md).

## Planned commands

Roadmap (v2.4.0 — Evidence Workflow Hardening): stronger evidence/report
quality, existing-test matching, and optional CI flows. No additional commands
are claimed as available until implemented.

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

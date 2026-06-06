# Execution Proof

`arkheionx prove` turns a hunter target into a local Foundry proof workflow. It
never fakes a result: a bug is only ever "proven" when a relevant Foundry test
actually executed.

```sh
arkheionx prove . --target Vault.withdraw            # scaffold only
arkheionx prove . --target Vault.withdraw --build    # + forge build (compiler-confirmed)
arkheionx prove . --target Vault.withdraw --run      # + targeted forge test
```

## Evidence levels

- `HEURISTIC` — static scan only.
- `COMPILER_CONFIRMED` — `forge build` passed.
- `EXECUTION_CONFIRMED` — at least one relevant Foundry test actually executed
  (passed or failed).

A skipped test, a `vm.skip(true)` scaffold, a build-only run, or a run that
matched no tests is **never** EXECUTION_CONFIRMED.

## Proof statuses

| Status | Meaning | Evidence |
|---|---|---|
| `scaffolded` | Scaffold generated, not executed | HEURISTIC (or COMPILER_CONFIRMED with `--build`) |
| `build_failed` | `forge build` failed | HEURISTIC |
| `no_foundry` | No `foundry.toml` or no `forge` | HEURISTIC |
| `no_tests_matched` | Build passed; no test matched the target | COMPILER_CONFIRMED |
| `skipped_not_proof` | Matched tests were skipped | COMPILER_CONFIRMED |
| `tested_passed` | A relevant test executed and passed | EXECUTION_CONFIRMED |
| `tested_failed` | A relevant test executed and failed | EXECUTION_CONFIRMED |
| `tested_mixed` | Relevant tests executed with mixed results | EXECUTION_CONFIRMED |

A passing test does not prove the absence of a bug. A failing test does not by
itself prove an exploitable vulnerability. Arkheionx never assigns final
severity.

## proof.json

Written to `.arkheionx/out/proof/<target-slug>/proof.json`:

```text
schema_version, arkheionx_version, target, target_id, project_root, status,
evidence_level, foundry{available,version,build_status,test_command,cwd},
test_result{tests_run,passed,failed,skipped,duration,failed_tests,
skipped_tests,raw_output_path}, trace{raw_trace_path,trace_json_path,
summary_available}, generated_files, limitations, next_commands
```

Schema: [`../schemas/proof-artifact.schema.json`](../schemas/proof-artifact.schema.json).

## Safety

- `--run` executes only targeted tests (`forge test --match-test`); a broad run
  is refused.
- No broadcast, no `cast send`, no RPC by default, no private keys.
- Raw Foundry output is captured to artifacts, not streamed to the terminal.

See also [`TRACE_ENGINE.md`](TRACE_ENGINE.md) and
[`FOUNDRY_INTEGRATION.md`](FOUNDRY_INTEGRATION.md).

# Trace Engine

`arkheionx trace` summarizes the latest Foundry proof/trace for a target into a
compact, human-readable view. It does not dump raw traces by default.

```sh
arkheionx trace . --target Vault.withdraw          # summarize latest proof
arkheionx trace . --target Vault.withdraw --run    # run targeted tests, then summarize
```

## Behavior

1. Resolve the fully-qualified target; reject ambiguity with suggestions.
2. With `--run`: run targeted `forge test`, parse output, write artifacts.
3. Without `--run`: summarize an existing `trace.json` for the target if
   present; otherwise report that no proof artifact was found and print the
   exact `prove --run` command.

## Conservative parsing

The parser extracts only what is plainly present in `forge test` output:

- tests run / passed / failed / skipped
- failing test names, skipped test names
- revert reasons (from `[FAIL: ...]`)
- assertion-failure lines
- call-like trace lines (lines containing `::` and `(`)
- emitted-log lines

It does **not** infer token balance deltas or invent state changes.

## trace.json

Written to `.arkheionx/out/proof/<target-slug>/trace.json`:

```text
schema_version, target, status, evidence_level, source_raw_output, tests_run,
passed, failed, skipped, failing_tests, skipped_tests, reverts,
assertion_failures, call_sequence, logs, limitations
```

Schema: [`../schemas/trace.schema.json`](../schemas/trace.schema.json).

## Limitations

- Trace parsing is intentionally conservative.
- `EXECUTION_CONFIRMED` requires a relevant test to actually execute.
- Raw output lives in `foundry-test.txt`; the terminal shows a summary only
  (use `--verbose`/`--raw` for more).

See also [`EXECUTION_PROOF.md`](EXECUTION_PROOF.md).

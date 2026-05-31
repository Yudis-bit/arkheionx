# Foundry Integration

Foundry is an optional precision backend. Arkheionx guides, maps, ranks, and
reports; Foundry compiles and runs. When Foundry is unavailable, every command
still works at `HEURISTIC` evidence.

## Detection

Arkheionx detects:

- `foundry.toml` at the target root;
- the `forge` binary on `PATH` (and `forge --version`);
- `src`/`contracts`, `test`/`tests`, and `out` directories;
- compiled artifacts under `out/<File>.sol/<Contract>.json`.

## Status values

- `unavailable` — no `foundry.toml`, or `forge` not on `PATH`.
- `available_not_built` — Foundry project detected, no build attempted.
- `build_failed` — `forge build` ran but failed.
- `build_passed` — `forge build` succeeded.

## Evidence mapping

- No Foundry → `HEURISTIC`.
- `forge build` passed and artifacts parsed → `COMPILER_CONFIRMED`.
- Foundry tests run and parsed → `EXECUTION_CONFIRMED` (roadmap for `trace`).

A failed or missing build never fails the command:

```text
Foundry is installed, but forge build failed. Arkheionx generated a heuristic
protocol map only. See .arkheionx/out/proof/<target>/foundry-build.txt.
```

## Safety

- Local only. No transactions, no mainnet, no fork unless an explicit flag is
  added in a future release.
- `subprocess` calls use argument lists (no shell) with timeouts.
- Raw build/test output is captured to artifact files, not streamed to the
  terminal unless `--verbose` is passed.

## Commands that consult Foundry

- `map --build`, `flow --build`, `hunt --build` — upgrade evidence to
  `COMPILER_CONFIRMED` when the build passes.
- `prove --build` — runs `forge build`, captures output, and records build
  status. Generated test scaffolds are never claimed as `EXECUTION_CONFIRMED`
  until a real run is parsed.

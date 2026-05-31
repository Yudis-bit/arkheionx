# Demo Workflow — First Real Run

A safe, local, reproducible walkthrough of the full Arkheionx loop on a bundled
toy fixture. No RPC, no private keys, no secrets, no mainnet.

## 1. Purpose

Show what Arkheionx sees in a DeFi repo and how the
open → hunt → prove → trace → evidence → report loop produces honest, local
evidence — and where human review remains required.

## 2. Install / verify

```sh
arkheionx version
arkheionx doctor
```

See [`INSTALLATION.md`](INSTALLATION.md) / [`INSTALLER.md`](INSTALLER.md).

## 3. List demos

```sh
arkheionx demo --list
arkheionx demo --show oracle-staking
```

## 4. Copy the demo fixture

```sh
arkheionx demo --copy oracle-staking ./arkheionx-demo
```

The copy includes only source entries (`README.md`, `foundry.toml`, `src/`,
`test/`). It refuses a non-empty destination unless you pass `--force`, and never
writes outside the destination you choose.

Fixtures ship as bundled package data, so this works from an installed package
(not only a source checkout). `arkheionx demo --show oracle-staking` reports the
resolved source. See [`PACKAGE_DATA.md`](PACKAGE_DATA.md).

## 5. Run doctor in the demo

```sh
cd ./arkheionx-demo
arkheionx doctor
```

## 6. Map and rank (heuristic, no Foundry required)

```sh
arkheionx open .
arkheionx map .
arkheionx flow .
arkheionx hunt . --top 5
```

In `HEURISTIC` mode (no Foundry) `open`/`hunt` exit `1` to signal static-only
ranking, not execution-confirmed results.

## 7. Prove (Foundry optional)

If `forge` is available:

```sh
arkheionx prove . --target OracleRewardFixture.stake --run
```

Without Foundry, `prove` generates a scaffold and stays heuristic. Print the
exact commands any time:

```sh
arkheionx demo --commands oracle-staking
```

## 8–11. Trace, evidence, report, status

```sh
arkheionx trace . --target OracleRewardFixture.stake
arkheionx evidence . --target OracleRewardFixture.stake
arkheionx report . --target OracleRewardFixture.stake
arkheionx evidence-status .
arkheionx validate-artifacts .
```

## 12. Clean up

```sh
cd ..
rm -rf ./arkheionx-demo
```

Generated artifacts live under `.arkheionx/out/` in the demo dir and are removed
with it. Nothing is written outside the demo destination.

## 13. What is proven

- `COMPILER_CONFIRMED`: the target compiles locally (Foundry).
- `EXECUTION_CONFIRMED`: a relevant local Foundry test executed.
- `EVIDENCE_READY`: proof + trace artifacts are packaged for review.

## 14. What is not proven

- A passing test does not prove absence of bugs.
- A failing test does not by itself prove a vulnerability.
- Heuristic findings are ranking signals, not confirmations.
- This is a toy fixture, not a real protocol, and not a vulnerability report or
  severity claim. Human review is always required.

## 15. Troubleshooting

- `--target ... is required`: run `arkheionx hunt . --top 5` to find a target.
- `not-a-foundry-project` / heuristic only: expected without `forge`.
- destination not empty: choose a new path or pass `--force`.
- See [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md).

## 16. Safety boundaries

Local/static only. No RPC, no private keys, no secrets, no live-chain calls, no
auto-submission, no bounty framing, no final severity. Use only on repositories
you own or are authorized to review.

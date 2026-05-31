# Onboarding

A first-run path for new Arkheionx users. Everything here is local and static:
no RPC, no private keys, no secrets, no network calls beyond the install step.

## 1. Install

See [`INSTALLER.md`](INSTALLER.md). The short version, from a local checkout:

```sh
ARKHEIONX_LOCAL_PATH="$PWD" sh install.sh
export PATH="$HOME/.arkheionx/bin:$PATH"   # venv method only
```

Or a plain editable install:

```sh
python3 -m pip install -e .
```

## 2. Verify the install

```sh
arkheionx version
arkheionx doctor --install
```

`doctor --install` shows the resolved command path, Python executable, package
version, optional Foundry status, and a PATH hint.

## 3. Run doctor on a project

```sh
arkheionx doctor
```

This reports Arkheionx, Python, Git, Foundry, and project layout, plus the next
command to run.

## 4. Run on a repository

Use the bundled demo fixture (no Foundry required):

```sh
arkheionx open examples/oracle-staking-fixture
arkheionx hunt examples/oracle-staking-fixture --top 5
```

## 5. Heuristic vs Foundry-backed mode

- Without Foundry, Arkheionx runs in `HEURISTIC` mode: static analysis and
  ranking only. `hunt`/`open` exit `1` to signal heuristic-only output.
- With Foundry (`forge`) in a Foundry project, `prove --run` can reach
  `COMPILER_CONFIRMED` and `EXECUTION_CONFIRMED`, and the evidence package can
  reach `EVIDENCE_READY`.

A passing test does not prove absence of bugs. Human review is always required.

## 6. Try the 5-minute demo

See [`TRY_IN_5_MINUTES.md`](TRY_IN_5_MINUTES.md) for the full local demo,
including the heuristic path and the optional Foundry-backed loop.

## 7. Where artifacts go

Generated artifacts are written under `.arkheionx/out/` in the working
directory (or the `--artifacts-dir` you pass). They are gitignored and are not
committed. Inspect them with:

```sh
arkheionx evidence-status examples/oracle-staking-fixture
arkheionx validate-artifacts examples/oracle-staking-fixture
```

## 8. Uninstall

See [`UNINSTALL.md`](UNINSTALL.md):

```sh
sh uninstall.sh --dry-run
sh uninstall.sh
```

## Troubleshooting

If anything fails, see [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md).

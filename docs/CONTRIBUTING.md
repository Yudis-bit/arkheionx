# Contributing

How to add a PoC, improve metadata, tune readiness rules, or improve docs in
Arkheionx.

## Before you submit

1. Read [ETHICS.md](ETHICS.md). If your PoC targets an unpatched live system,
   stop. Coordinate disclosure first.
2. Read [RESEARCH_STANDARD.md](RESEARCH_STANDARD.md). Submissions that don't
   meet the standard will not be merged.
3. Read [METADATA_SCHEMA.md](METADATA_SCHEMA.md). Every PoC needs metadata.

## Pre-audit readiness contributions

Good readiness contributions are defensive, local, and explainable:

- scanner signal calibration;
- false positive reductions;
- new protocol-specific readiness checks;
- safe Foundry invariant skeleton improvements;
- mini fixtures under `examples/`;
- search metadata in `metadata/search_terms.json`;
- docs that help indie builders prepare for formal audit.

Run the scanner before opening a PR that touches readiness code:

```sh
python3 -m py_compile scripts/pre_audit_scan.py
python3 -m unittest discover -s tests -p "test_*.py"
python3 scripts/pre_audit_scan.py \
  --root examples/mini-vault \
  --protocol-type auto \
  --output examples/reports/mini-vault-pre-audit-report.md \
  --json-output examples/reports/mini-vault-pre-audit-report.json \
  --generate-invariant-skeletons
python3 scripts/generate_search_index.py --check
```

Scanner output must use readiness language: risk signal, readiness gap,
historical pattern similarity, missing invariant, review recommended, and
defensive check. Do not add language that claims static scanning proves
exploitability or guarantees safety.

## Submitting a PoC

1. **Branch off `main`.** Use a descriptive branch name, e.g.
   `add/2024-09-some-protocol` or `fix/2017-07-block-pin`.

2. **Place the PoC in the right directory.**

   ```
   EVM/test/<YYYY-MM>/<Exploit file>.t.sol
   SVM/tests/<YYYY-MM-Protocol>/...
   MoveVM/sources/<YYYY-MM-Protocol>/...
   ```

3. **Include attribution.** If the PoC is ported from another repository, the
   file header must cite the original author and the upstream commit SHA.

4. **Pin determinism.** EVM PoCs must declare `FORK_BLOCK` and use
   `vm.createSelectFork` against a chain alias declared in `EVM/foundry.toml`.

5. **Assert post-state.** A PoC without hard assertions on the resulting state
   does not qualify (see [RESEARCH_STANDARD.md](RESEARCH_STANDARD.md)).

6. **Add a metadata entry.** Append to `metadata/registry.json` per
   [METADATA_SCHEMA.md](METADATA_SCHEMA.md). Run:

   ```sh
   python3 scripts/validate_metadata.py
   python3 scripts/generate_registry.py
   ```

7. **Run the test locally.** Document the exact command in the PR description,
   including which RPC alias was used.

## Submitting a fix

- **Reproducibility regression** (a previously listed PoC no longer reproduces):
  open a **Reproducibility issue** first; we triage before fixing.
- **Metadata mismatch**: PR directly with the metadata diff and the validator
  output.
- **Documentation correction**: PR directly. Keep the change scoped.

## Pull request checklist

Every PR must answer, in the PR description:

- [ ] Metadata updated (`metadata/registry.json`).
- [ ] `python3 scripts/validate_metadata.py` passes locally.
- [ ] `python3 scripts/generate_registry.py` ran; `README.md` registry
      regenerated.
- [ ] EVM PoCs: `forge fmt --check` and `forge build` from `EVM/` pass locally.
- [ ] EVM PoCs: at least one `forge test --match-path "..."` run is documented
      with the chain alias used.
- [ ] No live-target instructions, no scanners, no automation against
      production systems.
- [ ] No secrets, RPC URLs, or private credentials in committed files.
- [ ] Attribution preserved for any ported PoC (original author + upstream SHA).

The `.github/pull_request_template.md` mirrors this checklist.

## Style

See [STYLEGUIDE.md](STYLEGUIDE.md) for naming, file structure, and prose
conventions.

## What gets rejected

- PoCs without metadata.
- PoCs without assertions.
- PoCs that target unpatched production systems.
- PoCs ported without attribution.
- Submissions that include scanner code, autonomous attack runners, or
  detection-evasion tooling.
- README or web-app changes that introduce inflated claims, unverified
  metrics, or service offerings the maintainer has not actually delivered.
- Scanner rules that call live chains, require RPC, submit transactions,
  inspect deployed contracts, or adapt historical PoCs to active systems.

## Conduct

Be useful. Be precise. Disagree with arguments, not with people. Don't ship
work the brand can't stand behind.

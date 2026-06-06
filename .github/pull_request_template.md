## Summary

<!-- One paragraph: what this PR changes and why. Link any issues. -->

## Type

- [ ] New PoC
- [ ] PoC fix (reproducibility, assertions, attribution)
- [ ] Metadata change
- [ ] Documentation change
- [ ] CI / tooling change

## Checklist

<!-- All items must be honestly checked. If something does not apply, mark N/A
     and say why in the summary. -->

- [ ] No live-target instructions, no scanners, no automation against
      production systems.
- [ ] No secrets, RPC URLs, private keys, or proprietary protocol material
      committed.
- [ ] If a PoC was ported from another repository, original author and
      upstream commit SHA are preserved in the file header.
- [ ] `metadata/registry.json` updated for any added or changed PoC.
- [ ] `python3 scripts/validate_metadata.py` passes locally.
- [ ] `python3 scripts/generate_registry.py --check` passes locally
      (no stale README registry).
- [ ] `python3 scripts/score_pocs.py --check` passes locally
      (no stale `reports/poc_quality_matrix.md`).
- [ ] `python3 scripts/poc_maturity_index.py --check` passes locally
      (no stale `reports/poc_maturity_index.md`).
- [ ] If a PoC was promoted to L4 (archival verified) or L5
      (case study), the corresponding artifacts exist and are honest
      per `docs/POC_MATURITY_MODEL.md`. No level was claimed without
      evidence.
- [ ] EVM PoCs: `forge fmt --check` and `forge build` pass from `EVM/`.
- [ ] EVM PoCs: at least one `forge test --match-path "..."` invocation is
      documented below with the chain alias used.
- [ ] Documentation under `docs/` updated if behaviour or scope changed.
- [ ] No overclaiming. The README, registry, and maturity index do not
      assert verification, affiliation, or coverage that the artifacts
      do not back.

## Test evidence

<!-- Paste the relevant `forge test` invocation and a short summary of the
     output, or explain why local execution wasn't possible. -->

```
$ forge test --match-path "test/<folder>/*.t.sol" -vvv
...
```

## Safety review

<!-- Confirm: nothing in this PR aids attack against an unpatched live
     system. If the PoC corresponds to a real protocol, link the public
     post-mortem or patch evidence. -->

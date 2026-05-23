## Summary

<!-- One paragraph: what this PR changes and why. Link any issues. -->

## Type

- [ ] New PoC
- [ ] PoC fix (reproducibility, assertions, attribution)
- [ ] Metadata change
- [ ] Documentation change
- [ ] CI / tooling change
- [ ] Release / launch material

## Scope rules

- [ ] One PoC per patch — multi-PoC PRs are split or justified in the
      summary.
- [ ] No `EVM/src/**` change unless this PR explicitly says so up front.
- [ ] No exploit-logic change unless this PR explicitly says so up
      front.
- [ ] No new live-target tooling, scanners, or drain helpers.
- [ ] No secrets, RPC URLs, or private keys.

## Verification claims

- [ ] No PoC was promoted to `deterministic-confirmed` without a
      verification report containing real run output.
- [ ] No `verification_status` was set to `verified` without a real
      run recorded.
- [ ] Public-RPC observations are recorded as observations only, not
      as verification.

## Generated artifacts

If metadata or PoC source changed:

- [ ] `python scripts/validate_metadata.py` passes locally.
- [ ] `python scripts/generate_registry.py --check` passes locally.
- [ ] `python scripts/score_pocs.py --check` passes locally.
- [ ] `python scripts/generate_verification_report.py --check` passes
      locally.
- [ ] `python scripts/poc_maturity_index.py --check` passes locally.
- [ ] `python scripts/research_dashboard.py --check` passes locally.

## EVM build

- [ ] `forge fmt --check` passes from `EVM/`.
- [ ] `forge build` passes from `EVM/`.
- [ ] If a fork test was run, the chain alias and block are recorded
      in test evidence below.

## Test evidence

```
$ forge test --match-path "test/<folder>/*.t.sol" -vvv
...
```

## Safety review

<!-- Confirm: nothing in this PR aids attack against an unpatched live
     system. If the PoC corresponds to a real protocol, link the public
     post-mortem or patch evidence. -->

## Documentation

- [ ] If behaviour or scope changed, relevant docs under `docs/` are
      updated.
- [ ] If a new PoC was added, the registry entry references at least
      one independent post-mortem.
- [ ] If category, severity, or reproducibility changed, the change is
      explained in `notes` on the entry.

# Scope Fixture (synthetic)

A fully synthetic, local Foundry-style fixture for the Arkheionx **v7 scope-aware
orchestration** workflow (`scope-map`, `scope-lanes`, `scope-tasks`, `scope-pack`,
`evidence-judge`, `report-filter`).

Every contract uses invented `Example*` names and models only generic DeFi
patterns (stablecoin mint/redeem, ERC4626 vault, rewards, withdrawal-NFT queue,
oracle, signed mint, external adapter, cross-chain compose, compliance list). It
does **not** describe any real protocol, sponsor, or contest.

`scope-note.md` is a synthetic scope note that exercises the scope parser
(in/out of scope, severity rules, trusted roles, known/accepted issues, focus
areas, invalid patterns).

The `test/` directory deliberately contains a **strong**, a **weak**, and an
**invalid** test so `arkheionx evidence-judge` has graded examples to show.

```bash
arkheionx scope-map   examples/scope-fixture --scope-file examples/scope-fixture/scope-note.md
arkheionx scope-lanes examples/scope-fixture --scope-file examples/scope-fixture/scope-note.md
arkheionx scope-tasks examples/scope-fixture --scope-file examples/scope-fixture/scope-note.md
arkheionx scope-pack  examples/scope-fixture --scope-file examples/scope-fixture/scope-note.md --out .arkheionx/scope-pack
arkheionx evidence-judge examples/scope-fixture --scope-file examples/scope-fixture/scope-note.md
arkheionx report-filter  examples/scope-fixture --scope-file examples/scope-fixture/scope-note.md
```

Local/static only. Nothing here is a finding, a severity, or a confirmed
vulnerability. Human review is required.

# Arkheionx Oracle Staking Fixed Fixture

This is a toy improved fixture for Arkheionx demo and calibration workflows.

It is not production code, not a deployable recommendation, and not a security
guarantee. It exists to show how clearer tests and assumptions can reduce or
reclassify pre-audit readiness gaps.

Compared with `examples/oracle-staking-fixture`, this fixture adds visible
readiness signals for:

- stale oracle handling;
- decimals normalization and price bounds;
- access-control negative tests;
- reward conservation and no-overclaim checks;
- invariant and fuzz test names;
- known limitations and role assumptions.

Use it only for local/static Arkheionx demonstrations and before/after case
studies.

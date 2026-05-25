# Changelog

All notable Arkheionx changes are tracked here. Releases are not tagged until a
maintainer explicitly cuts them.

## v0.2.0 - Unreleased

### Added

- Vault Rule Pack for ERC4626-like vaults, strategy vaults, share/accounting
  systems, withdrawal queues, fee logic, and oracle-dependent vaults.
- Vault-specific readiness scoring path.
- Vault Rule Pack coverage section in generated Markdown reports.
- `vault_rule_pack` object in JSON reports.
- Vault-risk fixture under `examples/vault-risk-fixture/`.
- Generated vault-risk sample Markdown and JSON reports.
- Standard-library scanner unit tests under `tests/`.
- GitHub Action `summary` input for job summary excerpts.
- `docs/VAULT_RULE_PACK.md`.

### Improved

- More precise vault historical pattern similarity mapping.
- More actionable readiness gap formatting with detected signals, why it
  matters, historical pattern similarity, defensive checks, suggested tests,
  and priority.
- Safer placeholder invariant skeleton handling so generated skeletons do not
  inflate readiness scoring.
- Search metadata and generated search index for vault and ERC4626 topics.
- README v0.2 path for vault builders.
- GitHub Action and CI validation coverage.

### Safety

- Scanner remains local-only: no RPC, no live-chain calls, no transactions, no
  deployed-contract testing, and no secret handling.
- Reports continue to use readiness-gap and risk-signal language.
- v0.2.0 does not change archive verification claims.

### Documentation

- Added vault rule pack documentation.
- Updated readiness score documentation with vault-specific scoring.
- Updated GitHub Action usage with vault examples and summary behavior.
- Updated indie builder, services, monetization, marketing, roadmap, and search
  docs for the vault-builder path.

### Known Limitations

- Vault detection remains heuristic and term-based.
- No semantic Solidity analysis, call graph, or Slither integration yet.
- No PR comment mode yet.
- No automated GitHub issue creation.
- SVM/Anchor and MoveVM/Aptos remain scaffolds only.

## v0.1.0

### Added

- Pre-audit readiness scanner.
- GitHub Action wrapper.
- Markdown and JSON report generation.
- Mini-vault example fixture.
- Safe Foundry invariant skeleton generator.
- Search guide, search index, and search metadata.
- Monetization, sponsorship, services, ethics, and issue intake surfaces.

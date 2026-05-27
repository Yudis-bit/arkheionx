# Changelog

All notable Arkheionx changes are tracked here. Releases are not tagged until a
maintainer explicitly cuts them.

## v2.0.0 - Unreleased

### Added

- Installable local Arkheionx package metadata.
- `arkheionx` console entrypoint.
- Editable install workflow.
- Package-data/path-resolution helpers.
- Installation docs.
- Packaging docs.
- Console entrypoint tests.
- Package-data tests.

### Improved

- CLI command surface can now be used through `arkheionx ...`.
- CI validates editable install and console command behavior.
- v2 migration path from scripts/module CLI to console CLI is documented.

### Safety

- Package remains local/static only.
- No PyPI publishing workflow added.
- No RPC/live-chain behavior added.
- No exploit automation added.
- Existing scripts remain supported.

### Known Limitations

- v2.0.0 prepares local package installation but does not publish to PyPI.
- Package-data strategy remains source-tree compatible.
- Some scanner internals still rely on legacy script modules.

## v1.9.0

### Added

- Pre-v2 local module CLI candidate.
- `scan` CLI command.
- `validate-config` CLI command.
- `test-plan` CLI command.
- `search` CLI command.
- CLI command docs.
- CLI migration-to-v2 docs.
- CLI exit-code conventions.
- CLI tests.

### Improved

- Version/doctor CLI output.
- Scan terminal output consistency.
- CLI and script compatibility coverage.
- Documentation for future v2 package path.

### Safety

- CLI remains local/static only.
- No package publishing.
- No RPC/live-chain behavior added.
- No exploit automation added.
- Existing scripts remain supported.

### Known Limitations

- This is not the final v2 installable package.
- No pyproject/package publishing is added yet.
- CLI wraps existing scripts/modules and some legacy scanner internals remain.

## v1.8.0

### Added

- Report profile documentation.
- Fix First report section.
- Report UX helpers.
- Output profile docs.
- Noise reduction docs.

### Improved

- Executive summary readability.
- Finding grouping by rule family and confidence.
- Suppression summary.
- Config summary in reports.
- Issue-plan readability.
- Terminal scan summary.
- CI-oriented report profile.

### Safety

- Findings remain readiness signals, not vulnerability confirmations.
- No RPC/live-chain behavior added.
- No exploit automation added.
- No customer/adoption/security guarantee claims added.

### Known Limitations

- Report UX improvements do not change the underlying static/heuristic nature
  of findings.
- Manual review remains required.
- Some legacy report sections remain for backward compatibility.

## v1.7.0

### Added

- Stable Arkheionx config schema.
- Config validator script.
- Safe config defaults.
- Rule-pack registry helpers.
- Config examples.
- Suppression reference docs.
- Rule-pack configuration docs.
- Config safety docs.

### Improved

- Scanner config handling.
- Rule pack enable/disable behavior.
- Version/config validation tests.
- CI checks for config examples.

### Safety

- Dangerous config keys are rejected.
- No RPC/live-chain behavior added.
- No exploit automation added.
- Config is local/static only.

### Known Limitations

- Config stabilization is not the final v2 CLI interface.
- Some scanner internals still use legacy script-level logic.
- Config schema is stdlib-validated, not external JSON-schema-runtime enforced.

## v1.6.0

### Added

- Internal `arkheionx/` package scaffold.
- Shared version module.
- Core helper modules.
- Rule registry module.
- Generator module extraction.
- Preview internal CLI commands.
- Internal engine split docs.
- Package architecture docs.
- CLI roadmap docs.

### Improved

- Generator scripts now begin using reusable package modules.
- Version and rule-pack metadata are easier to maintain.
- v2.0 CLI/package path is documented.

### Safety

- No scanner capability expansion.
- No RPC/live-chain behavior added.
- No exploit automation added.
- Existing script entrypoints preserved.

### Known Limitations

- This is not the final v2 CLI.
- `scripts/pre_audit_scan.py` remains the primary scanner entrypoint.
- Only low-risk helpers were extracted.

## v1.5.0

### Added

- Finding-to-test-plan map.
- Defensive test-plan generator.
- Foundry invariant skeleton generator.
- AMM, Lending, and hybrid test-plan examples.
- Test-plan JSON schema.
- Invariant generator safety documentation.

### Improved

- Scanner JSON findings now include mapped suggested tests and invariant
  candidates where available.
- Issue plans now include suggested test and invariant-candidate content.
- SARIF help text includes compact defensive test-plan guidance.
- Search index includes invariant/test-plan generator surfaces.

### Safety

- Generated skeletons are local-only starter scaffolds with TODO placeholders.
- No live-chain/RPC behavior added.
- No exploit automation added.
- Generated invariants are not formal verification or proof of safety.

### Known Limitations

- Generated plans are heuristic and require human review.
- Skeletons require project-specific wiring before use.
- The generator does not claim complete property coverage.

## v1.4.0

### Added

- AMM Rule Pack.
- Lending Rule Pack.
- AMM fixture.
- Lending fixture.
- AMM/Lending hybrid fixture.
- Example reports for AMM and Lending fixtures.
- AMM/Lending knowledge mappings.
- AMM/Lending search metadata.

### Improved

- Protocol-type auto detection for AMM and Lending shapes.
- Report, JSON, SARIF, and issue-plan coverage for AMM/Lending readiness
  findings.
- Rule-pack docs and search index.

### Safety

- No live-chain/RPC behavior added.
- No exploit automation added.
- AMM/Lending findings are readiness signals, not vulnerability confirmations.

### Known Limitations

- Static/heuristic readiness signals only.
- AMM/Lending rules require manual review.
- No formal verification or protocol-specific audit claim.

## v1.3.0

### Added

- Ecosystem Pack documentation.
- Multi-repo readiness workflow.
- Ecosystem intake template.
- Ecosystem pilot scope template.
- Synthetic ecosystem pilot data model.
- Ecosystem report generator.
- Synthetic ecosystem readiness reports.

### Improved

- Paid offer docs now include Ecosystem Readiness Pilot.
- README now links to ecosystem readiness workflow.
- Search index includes ecosystem readiness terms.

### Safety

- Ecosystem summaries are anonymized by default.
- No unauthorized repo scanning added.
- No live-chain/RPC behavior added.
- No customer/adoption/partnership claims added.

### Known Limitations

- Ecosystem reports are generated from local/synthetic or user-provided
  authorized JSON reports.
- No automatic cloning or remote scanning.
- Multi-repo workflow still requires human scoping and authorization checks.

## v1.2.0

### Added

- Paid offer documentation.
- Pricing ladder.
- Service package guide.
- Client intake template.
- Sample scope-of-work templates.
- Paid offer catalog.
- Paid offer index generator.
- Sales FAQ.
- Paid work boundaries.

### Improved

- Commercial positioning.
- Monetization docs.
- Proposal templates.
- README paid support section.

### Safety

- Paid offers are clearly positioned as readiness support, not formal audits.
- No security guarantees, bounty guarantees, or customer/adoption claims added.
- No live-chain/RPC/offensive behavior added.

### Known Limitations

- Pricing is guidance only.
- Paid work requires human scoping.
- External validation and customer claims require explicit public permission.

## v1.1.1

### Improved

- Polished README front page and public repository positioning.
- Added GitHub repository surface guidance.
- Updated recommended About description, topics, and resources.
- Clarified Arkheionx's current identity as both a DeFi security memory system
  and pre-audit readiness workflow.

### Safety

- Preserved "not an audit" positioning.
- No live-chain/RPC behavior added.
- No exploit automation added.
- No fake adoption/customer claims added.

## v1.1.0

### Added

- Feedback issue templates.
- Feedback data schema.
- Rule calibration backlog.
- Feedback dashboard.
- Public feedback guide.
- Feedback triage workflow.
- Validation level guide.
- Feedback dashboard generator.

### Improved

- External validation language.
- README feedback section.
- Rule calibration workflow.

### Safety

- Feedback templates warn against public disclosure of unpatched
  vulnerabilities.
- Feedback templates warn against secrets, private keys, and unauthorized
  target details.
- No live-chain/RPC behavior added.

### Known Limitations

- Feedback dashboard starts with synthetic/internal entries.
- External validation requires public permission before being claimed.
- Rule calibration still requires maintainer review.

## v1.0.1

### Fixed

- Documentation link validation hotfix.
- Release consistency checks for stable public docs.

### Safety

- No scanner behavior changes.
- No live-chain/RPC behavior added.

## v1.0.0

### Added

- Stable public release documentation.
- CLI reference for the v1.0.0 scanner surface.
- Schema reference and JSON schemas for stable outputs.
- Output artifact naming guide.
- Documentation link checker.
- Version consistency checker.
- Safety wording checker.
- v1.0.0 release notes draft.

### Improved

- README onboarding and latest-release positioning.
- GitHub Action usage docs and stable input reference.
- Try-in-5-minutes flow with `make demo`.
- Release checklist for stable public release preparation.
- CI validation hooks for docs, version, and safety checks.

### Stability

- CLI surface documented as stable for v1.0.0.
- GitHub Action inputs documented as stable for v1.0.0.
- Main JSON output schemas documented.
- Generated artifacts remain ignored by default.
- Negative evidence and self-ingestion regression coverage preserved.

### Safety

- No live-chain/RPC behavior added.
- No exploit automation added.
- Findings remain readiness signals, not vulnerability confirmations.

### Known Limitations

- Static/heuristic analysis only.
- Manual review remains required.
- Optional Slither enrichment depends on local installation or provided JSON.
- v1.0 schemas cover the main output shape, not every future optional field.

## v0.9.2

### Fixed

- Generated Arkheionx reports, SARIF files, baselines, issue plans, dry-run
  outputs, launch reports, contest readiness reports, and remediation roadmaps
  are ignored as source evidence by default.
- Repeated scans no longer ingest previous Arkheionx outputs.
- Negative evidence no longer comes from generated report text.
- Scan source accounting now reports ignored generated artifacts.

### Safety

- No live-chain/RPC behavior added.
- No exploit automation added.
- Generated outputs remain local/static artifacts.

## v0.9.1

### Fixed

- Negative-context comments such as "missing invariant tests" are no longer
  counted as positive coverage evidence.
- Explicitly missing coverage can now appear as negative evidence in reports
  and JSON.
- Score calibration now avoids awarding readiness points for missing-test
  statements.

### Safety

- No live-chain/RPC behavior added.
- No exploit automation added.
- Findings remain readiness signals, not vulnerability confirmations.

## v0.9.0

### Added

- Security memory graph JSON.
- Finding knowledge map.
- Rule calibration matrix.
- Knowledge graph Markdown report.
- Local search helper CLI.
- Finding-to-pattern mapping.
- Related Knowledge sections in reports and issue plans.
- Security memory graph documentation.
- Search knowledge documentation.

### Improved

- Search index and search metadata.
- Rule pack docs and calibration discoverability.
- Case study knowledge links.
- Report explainability.
- Historical pattern similarity wording.

### Safety

- Knowledge graph is local/static.
- Historical similarity does not imply the scanned repo has the same
  vulnerability.
- No live-chain calls, RPC, exploit automation, or vulnerability confirmation.

### Known Limitations

- Mapping is curated and heuristic.
- Historical references are educational readiness context.
- Manual review remains required.

## v0.8.0

### Added

- Try Arkheionx in 5 minutes guide.
- Public demo workflow.
- Oracle/staking demo case study.
- Toy before/after readiness case study.
- Rule calibration documentation.
- False-positive calibration workflow.
- External validation feedback workflow.
- Demo launch and outreach material.

### Improved

- README demo-first onboarding.
- External user evaluation path.
- Rule calibration visibility.
- Demo artifact discoverability.
- Service explanation through reproducible examples.

### Safety

- Demo workflows are local/static and use toy fixtures.
- No live-chain scanning, RPC, exploit automation, or bounty guarantee.
- No fake adoption, customer, or partnership claims.

### Known Limitations

- Demo case studies are internal toy examples.
- External validation still requires real user feedback.
- Rule calibration remains heuristic.

## v0.7.0

### Added

- Launch Report output.
- Pre-Audit Sprint plan output.
- Contest Readiness report output.
- Executive summary output.
- Remediation roadmap output.
- Delivery artifact documentation.

### Improved

- Monetization and service delivery alignment.
- GitHub Action delivery output inputs.
- Client-facing report structure.
- Contest and pre-audit preparation workflows.

### Safety

- Delivery artifacts are readiness documents, not formal audit reports.
- No live-chain scanning, RPC, exploit automation, or bounty guarantee.
- Contest Readiness Mode is defensive and intended for authorized maintainers.

### Known Limitations

- Delivery artifacts are generated from heuristic readiness findings.
- Manual review is still required.
- Formal audit remains recommended before handling real user funds.

## v0.6.0

### Added

- Semantic-lite Solidity structure extraction for contracts, functions,
  modifiers, state variables, selected calls, and test coverage terms.
- Evidence records for readiness findings.
- Confidence reasons, evidence summaries, detection sources, affected
  contracts, and affected functions.
- Optional local Slither integration through `--slither` or
  `--slither-json`.
- Test coverage mapping for oracle, access-control, reentrancy/value-flow,
  reward-accounting, and vault readiness areas.
- False-positive reduction documentation.

### Improved

- SARIF locations now prefer semantic-lite or Slither evidence locations.
- Rule-pack findings are calibrated using evidence and mapped test coverage.
- Issue plans include confidence reasons and top evidence.
- Markdown reports include an Analysis Quality section and evidence per
  finding.
- JSON schema includes `analysis_quality`, `semantic_lite`, and `slither`
  metadata.

### Safety

- Slither is optional and local only.
- Slither absence does not break normal scans unless strict mode is explicitly
  enabled.
- No RPC, live-chain calls, transaction execution, deployed-contract scanning,
  or secret handling were added.
- Findings remain readiness signals, not vulnerability confirmations.

### Known Limitations

- Semantic-lite extraction is heuristic and not a full Solidity AST.
- Slither is optional and not required in CI.
- False positives remain possible.
- Manual review is still required before launch, mainnet, or formal audit
  intake.

## v0.5.0

### Added

- Generated GitHub issue plan output for readiness findings.
- Optional dry-run/create/update GitHub issue workflow.
- Idempotent issue markers for duplicate prevention.
- Oracle Rule Pack.
- Access Control / Upgradeability Rule Pack.
- Reentrancy / Value Flow Rule Pack.
- Staking / Reward Accounting Rule Pack.
- Rule pack documentation and oracle/staking example fixture.

### Improved

- Markdown report, JSON, SARIF, checklist, PR comment, and baseline/diff
  integration with expanded rule-pack findings.
- GitHub Action inputs for issue plan and optional issue workflows.
- Generated issue checklist conversion path for remediation planning.
- Monetization docs for Launch Report and Pre-Audit Sprint remediation plans.

### Safety

- Issue creation is disabled by default.
- Dry-run mode makes no GitHub API calls.
- Token and explicit create/update mode are required for real issue writes.
- Generated issues are readiness tasks, not formal audit findings.

### Known Limitations

- Rule packs are heuristic.
- No semantic Solidity call graph.
- Issue creation depends on GitHub token permissions.
- False positives remain possible.

## v0.4.1

### Changed

- README first impression and public onboarding polish.
- Release consistency across README, docs, roadmap, and changelog after
  v0.4.0.
- Stable GitHub Action examples updated to `@v0.4.0`.
- Documentation navigation tightened for builders and security researchers.

### Safety

- No scanner behavior changes.
- No new live-chain, RPC, transaction, deployed-contract, or secret-handling
  behavior.
- Defensive-only positioning preserved.

## v0.4.0

### Added

- SARIF output for GitHub Code Scanning-compatible workflows.
- Baseline output for compact readiness snapshots.
- Report diff mode for new, resolved, unchanged, changed, and suppressed
  readiness gap classification.
- Stable finding fingerprints for baseline comparison.
- Optional CI threshold flags: `--fail-score-below`, `--fail-on-new-high`,
  and `--fail-on-unsuppressed-high`.
- SARIF, baseline diff, and CI gating documentation.

### Improved

- GitHub Action inputs for SARIF, baseline, diff, and fail thresholds.
- JSON schema with `fingerprint_version`, finding fingerprints, diff data, and
  v0.4 generated output paths.
- Markdown report, Actions summary, PR comment, and issue checklist integration
  with baseline diff counts.
- CI validation for SARIF, baseline, diff outputs, and threshold behavior.

### Safety

- SARIF results are readiness gaps, not confirmed vulnerabilities.
- Default action behavior remains non-blocking unless thresholds are explicitly
  enabled.
- No live-chain calls, RPC use, transaction execution, deployed-contract
  scanning, or secret handling were added.

### Known Limitations

- SARIF locations are heuristic and usually point to the first affected file.
- No semantic Solidity call graph yet.
- Diff mode depends on stable fingerprints and can change when rules are
  renamed or recalibrated.
- Code Scanning upload requires user workflow permissions and a separate
  `github/codeql-action/upload-sarif` step.

## v0.3.0

### Added

- GitHub Actions job summary output generated by the scanner.
- Optional PR comment mode with marker-based update behavior.
- Generated issue checklist output.
- Stable readiness finding IDs.
- Local `.arkheionx.json` config support.
- False-positive suppression by finding ID with visible suppressed sections.
- PR comment body generation.
- `scripts/post_pr_comment.py` for optional GitHub REST API posting.
- Better JSON schema with canonical `findings`, `suppressed_findings`,
  `summary`, and `generated_outputs`.

### Improved

- Markdown report UX with top gap tables, all finding sections, generated
  output references, and suppression visibility.
- GitHub Action inputs for summary, PR comments, issue checklist, config, and
  verbose mode.
- External repository onboarding docs.
- CI validation for v0.3 generated files.
- Scanner tests for finding IDs, summaries, comments, checklists, config
  suppression, invalid config handling, and ignored paths.

### Safety

- PR comment mode is opt-in.
- Default scan remains local/static.
- No RPC, no live-chain calls, no transaction execution, and no secret
  handling were added.
- Suppressed findings are shown rather than silently hidden.

### Known Limitations

- Heuristic static detection.
- No semantic Solidity call graph.
- SARIF output deferred to v0.4.0.
- PR comments depend on GitHub token permissions.
- Fork PR restrictions may apply.

## v0.2.0

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

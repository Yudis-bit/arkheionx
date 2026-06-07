# ArkheionX documentation index

ArkheionX is a local-first, deterministic review-map tool for Solidity / Foundry
repositories. This index points to the docs that matter, in reading order. The
core workflow is:

> repo → review-map → value paths → assumptions → test gaps → proof direction → human review

Everything ArkheionX produces is review guidance for a human. It does not confirm
vulnerabilities, assign severity, or replace an audit.

## Start here

1. [`TRY_IN_5_MINUTES.md`](TRY_IN_5_MINUTES.md) — run the canonical workflow on the bundled demo.
2. [`INTERPRET_RESULTS.md`](INTERPRET_RESULTS.md) — what each output section means (and does not).
3. [`WHAT_ARKHEIONX_IS_NOT.md`](WHAT_ARKHEIONX_IS_NOT.md) — the boundaries, stated plainly.
4. [`BUG_BOUNTY_WORKFLOW.md`](BUG_BOUNTY_WORKFLOW.md) — safe triage and hypothesis workflow.
5. [`PUBLIC_ALPHA_READINESS.md`](PUBLIC_ALPHA_READINESS.md) — what is ready and what is deferred.
6. [`START_HERE.md`](START_HERE.md) · [`INSTALLATION.md`](INSTALLATION.md) — orientation and install.

## Core workflow

- [`CLI_REFERENCE.md`](CLI_REFERENCE.md) — every command and its options.
- [`REVIEW_MAP.md`](REVIEW_MAP.md) — the review-map model in depth.
- [`VALUE_FLOW_WORKBENCH.md`](VALUE_FLOW_WORKBENCH.md) — value-path thinking.
- [`PROTOCOL_MAP.md`](PROTOCOL_MAP.md) — roles, journeys, money flow.
- [`TRACE_ENGINE.md`](TRACE_ENGINE.md) · [`EVIDENCE_PACKAGE.md`](EVIDENCE_PACKAGE.md) · [`LOCAL_VALIDATION.md`](LOCAL_VALIDATION.md) — proof and evidence steps.
- [`PUBLIC_SURFACE.md`](PUBLIC_SURFACE.md) · [`STABILITY_CONTRACT.md`](STABILITY_CONTRACT.md) — the supported, stable surface.

## Advanced / project

- [`PACKAGING.md`](PACKAGING.md) — installed vs source-tree commands.
- [`REAL_PROTOCOL_PROOF_PLAN.md`](REAL_PROTOCOL_PROOF_PLAN.md) — how real-protocol proof will be earned.
- [`REPO_IDENTITY_MIGRATION.md`](REPO_IDENTITY_MIGRATION.md) — the broad-public identity blocker and its fix.
- [`FIXTURE_HARNESS.md`](FIXTURE_HARNESS.md) · [`FIXTURE_BENCHMARKS.md`](FIXTURE_BENCHMARKS.md) — deterministic fixture benchmarks.
- [`ROADMAP.md`](ROADMAP.md) — direction, including planned (not shipped) work.
- [`../CONTRIBUTING.md`](../CONTRIBUTING.md) · [`../SECURITY.md`](../SECURITY.md) — contribute and report.

## Reference (long tail)

The legacy pre-audit scanner, rule packs, schema references, and service/business
materials remain available for teams that need them, but they are **not** the
canonical first-run path:

- Rule packs: [`VAULT_RULE_PACK.md`](VAULT_RULE_PACK.md), [`LENDING_RULE_PACK.md`](LENDING_RULE_PACK.md), [`AMM_RULE_PACK.md`](AMM_RULE_PACK.md), [`ORACLE_RULE_PACK.md`](ORACLE_RULE_PACK.md).
- Schema/output references: [`SCHEMA_REFERENCE.md`](SCHEMA_REFERENCE.md), [`OUTPUT_ARTIFACTS.md`](OUTPUT_ARTIFACTS.md), [`SARIF_OUTPUT.md`](SARIF_OUTPUT.md).
- Legacy scanner & CI: [`GITHUB_ACTION_USAGE.md`](GITHUB_ACTION_USAGE.md), [`PRE_AUDIT_SPRINT_WORKFLOW.md`](PRE_AUDIT_SPRINT_WORKFLOW.md).
- Case studies: [`CASE_STUDY_SAMPLE.md`](CASE_STUDY_SAMPLE.md) and the `case-studies/` directory.

Other documents in this directory are deeper references; the curated paths above
are the recommended entry points.

# Arkheionx Search Index

GitHub-searchable index for Arkheionx Memory, Readiness, Tests, Search, and Market.

Use this page with GitHub search or local `rg` to find exploit primitives,
broken invariants, failed assumptions, readiness gaps, services, templates,
examples, and reports.

Current truth: 18 structured PoCs, 0 deterministic-confirmed L4+ entries,
EVM/Foundry active, SVM/Anchor and MoveVM/Aptos scaffold only.

## Product Surface Index

| Surface | Path | Search tags |
|---|---|---|
| README landing page | [`README.md`](../README.md) | arkheionx, pre-audit-readiness, security-memory |
| GitHub repository surface | [`docs/GITHUB_REPO_SURFACE.md`](../docs/GITHUB_REPO_SURFACE.md) | GitHub repo surface, repository about, public surface polish |
| Changelog | [`CHANGELOG.md`](../CHANGELOG.md) | v1.0.0, stable public release, release notes |
| CLI reference | [`docs/CLI_REFERENCE.md`](../docs/CLI_REFERENCE.md) | CLI reference, stable flags, v1.0.0 |
| Schema reference | [`docs/SCHEMA_REFERENCE.md`](../docs/SCHEMA_REFERENCE.md) | schema freeze, JSON Schema, stable outputs |
| Output artifacts | [`docs/OUTPUT_ARTIFACTS.md`](../docs/OUTPUT_ARTIFACTS.md) | output naming, generated artifacts, reports directory |
| Invariant test plan generator | [`docs/INVARIANT_TEST_PLAN_GENERATOR.md`](../docs/INVARIANT_TEST_PLAN_GENERATOR.md) | invariant generator, test plan generator, suggested tests |
| Foundry invariant skeletons | [`docs/FOUNDRY_INVARIANT_SKELETONS.md`](../docs/FOUNDRY_INVARIANT_SKELETONS.md) | Foundry invariant skeleton, invariant candidates, local scaffold |
| Invariant safety boundaries | [`docs/INVARIANT_SAFETY_BOUNDARIES.md`](../docs/INVARIANT_SAFETY_BOUNDARIES.md) | invariant safety, local-only skeletons, human review |
| v1.0 release notes draft | [`docs/V1_0_RELEASE_NOTES_DRAFT.md`](../docs/V1_0_RELEASE_NOTES_DRAFT.md) | v1.0.0, release notes, stable public release |
| Feedback loop | [`docs/FEEDBACK_LOOP.md`](../docs/FEEDBACK_LOOP.md) | feedback loop, false positive report, external calibration |
| Public feedback guide | [`docs/PUBLIC_FEEDBACK_GUIDE.md`](../docs/PUBLIC_FEEDBACK_GUIDE.md) | public feedback, safe disclosure, report quality |
| Feedback triage workflow | [`docs/FEEDBACK_TRIAGE_WORKFLOW.md`](../docs/FEEDBACK_TRIAGE_WORKFLOW.md) | feedback triage, calibration status, severity |
| Validation levels | [`docs/VALIDATION_LEVELS.md`](../docs/VALIDATION_LEVELS.md) | validation levels, external evaluation, allowed claims |
| Paid offer | [`docs/business/PAID_OFFER.md`](../docs/business/PAID_OFFER.md) | paid offer, readiness support, commercial positioning |
| Pricing ladder | [`docs/business/PRICING_LADDER.md`](../docs/business/PRICING_LADDER.md) | pricing ladder, pilot pricing, service packages |
| Service packages | [`docs/business/SERVICE_PACKAGES.md`](../docs/business/SERVICE_PACKAGES.md) | service packages, Readiness Snapshot, Pre-Audit Sprint |
| Client intake | [`docs/business/CLIENT_INTAKE.md`](../docs/business/CLIENT_INTAKE.md) | client intake, authorized repository, scope of work |
| Sample scope of work | [`docs/business/SAMPLE_SCOPE_OF_WORK.md`](../docs/business/SAMPLE_SCOPE_OF_WORK.md) | scope of work, proposal template, not a formal audit |
| Sales FAQ | [`docs/business/SALES_FAQ.md`](../docs/business/SALES_FAQ.md) | sales FAQ, paid readiness support, no guarantees |
| Paid work boundaries | [`docs/business/PAID_WORK_BOUNDARIES.md`](../docs/business/PAID_WORK_BOUNDARIES.md) | paid work boundaries, safety boundaries, commercial |
| Ecosystem Pack | [`docs/ecosystem/ECOSYSTEM_PACK.md`](../docs/ecosystem/ECOSYSTEM_PACK.md) | ecosystem pack, ecosystem readiness, multi-repo readiness |
| Multi-repo readiness workflow | [`docs/ecosystem/MULTI_REPO_READINESS_WORKFLOW.md`](../docs/ecosystem/MULTI_REPO_READINESS_WORKFLOW.md) | multi-repo readiness, authorized repositories, local reports |
| Ecosystem intake | [`docs/ecosystem/ECOSYSTEM_INTAKE.md`](../docs/ecosystem/ECOSYSTEM_INTAKE.md) | ecosystem intake, authorization, anonymization |
| Anonymized reporting | [`docs/ecosystem/ANONYMIZED_REPORTING.md`](../docs/ecosystem/ANONYMIZED_REPORTING.md) | anonymized reporting, common gap report, repo aliases |
| Ecosystem readiness pilot | [`docs/ecosystem/ECOSYSTEM_READINESS_PILOT.md`](../docs/ecosystem/ECOSYSTEM_READINESS_PILOT.md) | readiness pilot, ecosystem operator, cohort readiness |
| Ecosystem readiness summary | [`reports/ecosystem_readiness_summary.md`](../reports/ecosystem_readiness_summary.md) | ecosystem readiness summary, repo-by-repo readiness, rule-family heatmap |
| Ecosystem common gaps | [`reports/ecosystem_common_gaps.md`](../reports/ecosystem_common_gaps.md) | common gap report, recurring findings, anonymized recommendations |
| Ecosystem pilot metadata | [`metadata/ecosystem_pilot_example.json`](../metadata/ecosystem_pilot_example.json) | synthetic ecosystem pilot, ecosystem data model, repo aliases |
| Ecosystem report generator | [`scripts/generate_ecosystem_report.py`](../scripts/generate_ecosystem_report.py) | ecosystem report generator, check mode, local static |
| Test plan generator | [`scripts/generate_test_plan.py`](../scripts/generate_test_plan.py) | test plan generator, invariant generator, check mode |
| Services | [`SERVICES.md`](../SERVICES.md) | Launch Report, Pre-Audit Sprint, Contest Readiness Pack, Ecosystem Pack |
| Pre-Audit Readiness OS | [`docs/PRE_AUDIT_READINESS_OS.md`](../docs/PRE_AUDIT_READINESS_OS.md) | scanner, readiness gap, historical pattern similarity |
| GitHub Action usage | [`docs/GITHUB_ACTION_USAGE.md`](../docs/GITHUB_ACTION_USAGE.md) | github-action, SARIF, baseline diff, PR comment |
| PR comment mode | [`docs/PR_COMMENT_MODE.md`](../docs/PR_COMMENT_MODE.md) | pull-request, comment marker, GitHub token |
| Generated issue checklist | [`docs/GENERATED_ISSUE_CHECKLIST.md`](../docs/GENERATED_ISSUE_CHECKLIST.md) | issue checklist, remediation, finding IDs |
| GitHub issue workflow | [`docs/GITHUB_ISSUE_WORKFLOW.md`](../docs/GITHUB_ISSUE_WORKFLOW.md) | issue plan, dry-run, duplicate prevention |
| Arkheionx config | [`docs/ARKHEIONX_CONFIG.md`](../docs/ARKHEIONX_CONFIG.md) | config, suppression, ignore paths |
| SARIF output | [`docs/SARIF_OUTPUT.md`](../docs/SARIF_OUTPUT.md) | SARIF, GitHub Code Scanning, readiness gap |
| Baseline diff mode | [`docs/BASELINE_DIFF_MODE.md`](../docs/BASELINE_DIFF_MODE.md) | baseline, diff mode, new resolved unchanged |
| Semantic-lite analysis | [`docs/SEMANTIC_LITE_ANALYSIS.md`](../docs/SEMANTIC_LITE_ANALYSIS.md) | semantic-lite, Solidity structure extraction, evidence |
| Slither integration | [`docs/SLITHER_INTEGRATION.md`](../docs/SLITHER_INTEGRATION.md) | Slither, Slither JSON, local static analysis |
| False-positive reduction | [`docs/FALSE_POSITIVE_REDUCTION.md`](../docs/FALSE_POSITIVE_REDUCTION.md) | false positives, confidence scoring, keyword-only downgrade |
| Try in 5 minutes | [`docs/TRY_IN_5_MINUTES.md`](../docs/TRY_IN_5_MINUTES.md) | try Arkheionx in 5 minutes, quick demo, demo reports |
| Public demo workflow | [`docs/PUBLIC_DEMO_WORKFLOW.md`](../docs/PUBLIC_DEMO_WORKFLOW.md) | public demo workflow, demo GitHub Action workflow, demo artifacts |
| Rule calibration | [`docs/RULE_CALIBRATION.md`](../docs/RULE_CALIBRATION.md) | rule calibration, false positive calibration, confidence model |
| False-positive review workflow | [`docs/FALSE_POSITIVE_REVIEW_WORKFLOW.md`](../docs/FALSE_POSITIVE_REVIEW_WORKFLOW.md) | false positive review, calibration workflow, downgrade logic |
| External validation | [`docs/EXTERNAL_VALIDATION.md`](../docs/EXTERNAL_VALIDATION.md) | external validation, feedback workflow, sanitized reports |
| Launch Report OS | [`docs/LAUNCH_REPORT_OS.md`](../docs/LAUNCH_REPORT_OS.md) | Launch Report, client-ready report, audit handoff package |
| Pre-Audit Sprint Workflow | [`docs/PRE_AUDIT_SPRINT_WORKFLOW.md`](../docs/PRE_AUDIT_SPRINT_WORKFLOW.md) | Pre-Audit Sprint, sprint plan, remediation backlog |
| Contest Readiness Mode | [`docs/CONTEST_READINESS_MODE.md`](../docs/CONTEST_READINESS_MODE.md) | Contest Readiness, scope checklist, researcher onboarding |
| Delivery Artifacts | [`docs/DELIVERY_ARTIFACTS.md`](../docs/DELIVERY_ARTIFACTS.md) | delivery artifacts, executive summary, remediation roadmap |
| CI gating | [`docs/CI_GATING.md`](../docs/CI_GATING.md) | fail threshold, fail-score-below, CI readiness gate |
| Readiness score | [`docs/READINESS_SCORE.md`](../docs/READINESS_SCORE.md) | score bands, audit blockers, invariant testing |
| Vault Rule Pack | [`docs/VAULT_RULE_PACK.md`](../docs/VAULT_RULE_PACK.md) | ERC4626, vault accounting, share accounting |
| Rule Packs | [`docs/RULE_PACKS.md`](../docs/RULE_PACKS.md) | oracle rule pack, access control, reward accounting |
| Oracle Rule Pack | [`docs/ORACLE_RULE_PACK.md`](../docs/ORACLE_RULE_PACK.md) | oracle, stale price, price bounds |
| Access Control Rule Pack | [`docs/ACCESS_CONTROL_RULE_PACK.md`](../docs/ACCESS_CONTROL_RULE_PACK.md) | access control, upgradeability, initializer |
| Reentrancy Value Flow Rule Pack | [`docs/REENTRANCY_VALUE_FLOW_RULE_PACK.md`](../docs/REENTRANCY_VALUE_FLOW_RULE_PACK.md) | reentrancy, external calls, claim flow |
| Reward Accounting Rule Pack | [`docs/REWARD_ACCOUNTING_RULE_PACK.md`](../docs/REWARD_ACCOUNTING_RULE_PACK.md) | staking, reward accounting, accumulator |
| AMM Rule Pack | [`docs/AMM_RULE_PACK.md`](../docs/AMM_RULE_PACK.md) | AMM rule pack, AMM invariant, LP share accounting, slippage boundary |
| Lending Rule Pack | [`docs/LENDING_RULE_PACK.md`](../docs/LENDING_RULE_PACK.md) | lending rule pack, collateral debt invariant, liquidation boundary, interest index |
| Indie builder offer | [`docs/business/INDIE_BUILDER_OFFER.md`](../docs/business/INDIE_BUILDER_OFFER.md) | indie-defi, launch preparation, paid path |
| Search guide | [`docs/SEARCH_GUIDE.md`](../docs/SEARCH_GUIDE.md) | search tags, root-cause analysis, broken invariant |
| Security Memory Graph | [`docs/SECURITY_MEMORY_GRAPH.md`](../docs/SECURITY_MEMORY_GRAPH.md) | security memory graph, finding knowledge map, historical pattern similarity |
| Search Knowledge | [`docs/SEARCH_KNOWLEDGE.md`](../docs/SEARCH_KNOWLEDGE.md) | search_knowledge.py, oracle stale price, local search helper |
| Finding Knowledge Map | [`docs/FINDING_KNOWLEDGE_MAP.md`](../docs/FINDING_KNOWLEDGE_MAP.md) | finding knowledge map, suggested defensive tests, failed assumptions |
| Marketing engine | [`docs/marketing/MARKETING_ENGINE.md`](../docs/marketing/MARKETING_ENGINE.md) | growth, positioning, GitHub-only funnel |
| Monetization | [`docs/business/MONETIZATION.md`](../docs/business/MONETIZATION.md) | sponsors, revenue ladder, services |
| Sponsorship | [`docs/business/SPONSORSHIP.md`](../docs/business/SPONSORSHIP.md) | funding, research sponsorship, public work |
| Ethics | [`docs/ETHICS.md`](../docs/ETHICS.md) | defensive-only, authorized review, no live targeting |
| Roadmap | [`docs/ROADMAP.md`](../docs/ROADMAP.md) | release roadmap, rule packs, GitHub-native |
| Oracle staking demo case study | [`docs/case-studies/ORACLE_STAKING_FIXTURE_CASE_STUDY.md`](../docs/case-studies/ORACLE_STAKING_FIXTURE_CASE_STUDY.md) | oracle staking demo, case study, public demo |
| Oracle staking before/after case study | [`docs/case-studies/ORACLE_STAKING_BEFORE_AFTER.md`](../docs/case-studies/ORACLE_STAKING_BEFORE_AFTER.md) | before after case study, fixed fixture, remediation demo |
| Rule calibration summary | [`reports/rule_calibration_summary.md`](../reports/rule_calibration_summary.md) | rule calibration, common false positives, downgrade logic |
| Feedback dashboard | [`reports/feedback_dashboard.md`](../reports/feedback_dashboard.md) | feedback dashboard, synthetic feedback, calibration |
| Rule calibration backlog report | [`reports/rule_calibration_backlog.md`](../reports/rule_calibration_backlog.md) | rule calibration backlog, feedback status, calibration work |
| Paid offer index | [`reports/paid_offer_index.md`](../reports/paid_offer_index.md) | paid offer index, pricing ladder, service packages |
| Security memory graph report | [`reports/security_memory_graph.md`](../reports/security_memory_graph.md) | security memory graph, finding to pattern map, historical PoC nodes |
| Security memory graph summary | [`reports/security_memory_graph_summary.md`](../reports/security_memory_graph_summary.md) | security memory graph, mapped findings, mapped patterns |
| Security memory graph JSON | [`metadata/security_memory_graph.json`](../metadata/security_memory_graph.json) | security memory graph, nodes, edges |
| Finding knowledge map JSON | [`metadata/finding_knowledge_map.json`](../metadata/finding_knowledge_map.json) | finding knowledge map, related patterns, suggested tests |
| Rule calibration matrix JSON | [`metadata/rule_calibration_matrix.json`](../metadata/rule_calibration_matrix.json) | rule calibration matrix, confidence requirements, downgrade conditions |
| Finding test plan map JSON | [`metadata/finding_test_plan_map.json`](../metadata/finding_test_plan_map.json) | finding test plan map, suggested tests, invariant candidates |
| Feedback schema JSON | [`metadata/feedback_schema.json`](../metadata/feedback_schema.json) | feedback schema, feedback loop, calibration |
| Feedback examples JSON | [`metadata/feedback_examples.json`](../metadata/feedback_examples.json) | synthetic feedback, feedback examples, no adoption claims |
| Rule calibration backlog JSON | [`metadata/rule_calibration_backlog.json`](../metadata/rule_calibration_backlog.json) | rule calibration backlog, feedback dashboard, calibration |
| Case study template | [`templates/case_study_template.md`](../templates/case_study_template.md) | case study template, before after, readiness case study |
| v0.8 launch posts | [`docs/launch/V0_8_LAUNCH_POSTS.md`](../docs/launch/V0_8_LAUNCH_POSTS.md) | launch post, outreach kit, public demo |
| Mini-vault fixture | [`examples/mini-vault/README.md`](../examples/mini-vault/README.md) | vault, fixture, scanner demo |
| Vault-risk fixture | [`examples/vault-risk-fixture/README.md`](../examples/vault-risk-fixture/README.md) | ERC4626, strategy vault, Vault Rule Pack |
| Oracle staking fixture | [`examples/oracle-staking-fixture/README.md`](../examples/oracle-staking-fixture/README.md) | oracle, staking, reward rule pack |
| Oracle staking fixed fixture | [`examples/oracle-staking-fixture-fixed/README.md`](../examples/oracle-staking-fixture-fixed/README.md) | oracle, staking, before after, fixed fixture |
| Semantic-lite fixture | [`examples/semantic-lite-fixture/README.md`](../examples/semantic-lite-fixture/README.md) | semantic-lite, false-positive reduction, evidence |
| AMM fixture | [`examples/amm-fixture/README.md`](../examples/amm-fixture/README.md) | AMM fixture, swap readiness, liquidity pool |
| Lending fixture | [`examples/lending-fixture/README.md`](../examples/lending-fixture/README.md) | lending fixture, borrow repay, liquidation boundary |
| AMM Lending hybrid fixture | [`examples/amm-lending-hybrid-fixture/README.md`](../examples/amm-lending-hybrid-fixture/README.md) | hybrid fixture, AMM price dependency, lending health factor |
| Sample Markdown report | [`examples/reports/mini-vault-pre-audit-report.md`](../examples/reports/mini-vault-pre-audit-report.md) | readiness report, vault, example |
| Vault-risk Markdown report | [`examples/reports/vault-risk-fixture-pre-audit-report.md`](../examples/reports/vault-risk-fixture-pre-audit-report.md) | vault readiness, ERC4626, readiness gaps |
| Sample JSON report | [`examples/reports/mini-vault-pre-audit-report.json`](../examples/reports/mini-vault-pre-audit-report.json) | json-output, automation, example |
| Vault-risk JSON report | [`examples/reports/vault-risk-fixture-pre-audit-report.json`](../examples/reports/vault-risk-fixture-pre-audit-report.json) | vault_rule_pack, json-output, example |
| Mini-vault action summary | [`examples/reports/mini-vault-action-summary.md`](../examples/reports/mini-vault-action-summary.md) | GitHub Actions summary, score, top gaps |
| Vault-risk PR comment | [`examples/reports/vault-risk-fixture-pr-comment.md`](../examples/reports/vault-risk-fixture-pr-comment.md) | PR comment, marker, top gaps |
| Vault-risk issue checklist | [`examples/reports/vault-risk-fixture-issue-checklist.md`](../examples/reports/vault-risk-fixture-issue-checklist.md) | issue checklist, readiness remediation, finding IDs |
| Vault-risk issue plan | [`examples/reports/vault-risk-fixture-issue-plan.json`](../examples/reports/vault-risk-fixture-issue-plan.json) | issue plan, remediation issue, GitHub issue workflow |
| Oracle staking issue plan | [`examples/reports/oracle-staking-fixture-issue-plan.json`](../examples/reports/oracle-staking-fixture-issue-plan.json) | oracle rule pack, reward accounting, issue plan |
| Oracle staking launch report | [`examples/reports/oracle-staking-fixture-launch-report.md`](../examples/reports/oracle-staking-fixture-launch-report.md) | Launch Report, executive summary, launch readiness |
| Oracle staking sprint plan | [`examples/reports/oracle-staking-fixture-sprint-plan.md`](../examples/reports/oracle-staking-fixture-sprint-plan.md) | Pre-Audit Sprint, sprint checklist, remediation plan |
| Oracle staking contest readiness | [`examples/reports/oracle-staking-fixture-contest-readiness.md`](../examples/reports/oracle-staking-fixture-contest-readiness.md) | Contest Readiness, scope checklist, researcher onboarding |
| Oracle staking remediation roadmap | [`examples/reports/oracle-staking-fixture-remediation-roadmap.md`](../examples/reports/oracle-staking-fixture-remediation-roadmap.md) | remediation roadmap, launch blockers, audit handoff |
| AMM fixture report | [`examples/reports/amm-fixture-pre-audit-report.md`](../examples/reports/amm-fixture-pre-audit-report.md) | AMM report, ARK-AMM, readiness findings |
| AMM fixture SARIF | [`examples/reports/amm-fixture.sarif.json`](../examples/reports/amm-fixture.sarif.json) | AMM SARIF, ARK-AMM, Code Scanning |
| AMM fixture test plan | [`examples/reports/amm-fixture-test-plan.md`](../examples/reports/amm-fixture-test-plan.md) | AMM test plan, invariant candidates, Foundry skeleton |
| AMM Foundry invariant skeleton | [`examples/reports/ArkheionxAMMInvariants.t.sol`](../examples/reports/ArkheionxAMMInvariants.t.sol) | AMM invariant skeleton, Foundry, TODO assertions |
| Lending fixture report | [`examples/reports/lending-fixture-pre-audit-report.md`](../examples/reports/lending-fixture-pre-audit-report.md) | lending report, ARK-LEND, readiness findings |
| Lending fixture SARIF | [`examples/reports/lending-fixture.sarif.json`](../examples/reports/lending-fixture.sarif.json) | lending SARIF, ARK-LEND, Code Scanning |
| Lending fixture test plan | [`examples/reports/lending-fixture-test-plan.md`](../examples/reports/lending-fixture-test-plan.md) | lending test plan, collateral debt invariant, Foundry skeleton |
| Lending Foundry invariant skeleton | [`examples/reports/ArkheionxLendingInvariants.t.sol`](../examples/reports/ArkheionxLendingInvariants.t.sol) | lending invariant skeleton, Foundry, liquidation boundary |
| AMM Lending hybrid report | [`examples/reports/amm-lending-hybrid-fixture-pre-audit-report.md`](../examples/reports/amm-lending-hybrid-fixture-pre-audit-report.md) | hybrid report, ARK-AMM, ARK-LEND |
| AMM Lending hybrid test plan | [`examples/reports/amm-lending-hybrid-fixture-test-plan.md`](../examples/reports/amm-lending-hybrid-fixture-test-plan.md) | hybrid test plan, AMM, lending |
| Hybrid Foundry invariant skeleton | [`examples/reports/ArkheionxHybridInvariants.t.sol`](../examples/reports/ArkheionxHybridInvariants.t.sol) | hybrid invariant skeleton, AMM lending, Foundry |
| Demo pre-audit report | [`examples/reports/demo-pre-audit-report.md`](../examples/reports/demo-pre-audit-report.md) | public demo reports, demo protocol, readiness report |
| Demo launch report | [`examples/reports/demo-launch-report.md`](../examples/reports/demo-launch-report.md) | Launch Report, public demo, client-ready report |
| Demo contest readiness | [`examples/reports/demo-contest-readiness.md`](../examples/reports/demo-contest-readiness.md) | Contest Readiness, scope checklist, public demo |
| Demo issue plan | [`examples/reports/demo-issue-plan.json`](../examples/reports/demo-issue-plan.json) | issue plan JSON, demo artifact, remediation |
| Oracle staking fixed report | [`examples/reports/oracle-staking-fixture-fixed-pre-audit-report.md`](../examples/reports/oracle-staking-fixture-fixed-pre-audit-report.md) | before after case study, fixed fixture, readiness improvement |
| Vault-risk SARIF report | [`examples/reports/vault-risk-fixture.sarif.json`](../examples/reports/vault-risk-fixture.sarif.json) | SARIF, Code Scanning, readiness result |
| Vault-risk baseline | [`examples/reports/vault-risk-fixture.baseline.json`](../examples/reports/vault-risk-fixture.baseline.json) | baseline, finding fingerprint, readiness snapshot |
| Vault-risk diff report | [`examples/reports/vault-risk-fixture-diff.md`](../examples/reports/vault-risk-fixture-diff.md) | baseline diff, new resolved unchanged, remediation tracking |
| Arkheionx config example | [`examples/arkheionx.config.example.json`](../examples/arkheionx.config.example.json) | config, suppression, ignore paths |
| Pre-audit scanner | [`scripts/pre_audit_scan.py`](../scripts/pre_audit_scan.py) | cli, scanner, standard-library |
| PR comment poster | [`scripts/post_pr_comment.py`](../scripts/post_pr_comment.py) | GitHub API, PR comment, marker update |
| GitHub issue creator | [`scripts/create_github_issues.py`](../scripts/create_github_issues.py) | GitHub API, issue plan, dry-run |
| Knowledge graph generator | [`scripts/generate_knowledge_graph.py`](../scripts/generate_knowledge_graph.py) | security memory graph, knowledge graph, check mode |
| Knowledge search helper | [`scripts/search_knowledge.py`](../scripts/search_knowledge.py) | search knowledge, oracle stale price, local search |
| Feedback dashboard generator | [`scripts/generate_feedback_dashboard.py`](../scripts/generate_feedback_dashboard.py) | feedback dashboard, rule calibration backlog, check mode |
| Paid offer index generator | [`scripts/generate_paid_offer_index.py`](../scripts/generate_paid_offer_index.py) | paid offer index, paid offer catalog, check mode |
| Docs link checker | [`scripts/check_docs_links.py`](../scripts/check_docs_links.py) | docs link check, release validation, v1.0.0 |
| Version consistency checker | [`scripts/check_version_consistency.py`](../scripts/check_version_consistency.py) | version consistency, release validation, v1.0.0 |
| Safety wording checker | [`scripts/check_safety_wording.py`](../scripts/check_safety_wording.py) | safety wording, release validation, defensive |
| Make demo | [`Makefile`](../Makefile) | make demo, make validate, try in 5 minutes |
| Pre-audit report schema | [`schemas/pre-audit-report.schema.json`](../schemas/pre-audit-report.schema.json) | JSON schema, pre-audit report, schema freeze |
| Issue plan schema | [`schemas/issue-plan.schema.json`](../schemas/issue-plan.schema.json) | JSON schema, issue plan, schema freeze |
| Baseline schema | [`schemas/baseline.schema.json`](../schemas/baseline.schema.json) | JSON schema, baseline, schema freeze |
| Diff schema | [`schemas/diff.schema.json`](../schemas/diff.schema.json) | JSON schema, diff, schema freeze |
| Security memory graph schema | [`schemas/security-memory-graph.schema.json`](../schemas/security-memory-graph.schema.json) | JSON schema, security memory graph, schema freeze |
| Finding knowledge map schema | [`schemas/finding-knowledge-map.schema.json`](../schemas/finding-knowledge-map.schema.json) | JSON schema, finding knowledge map, schema freeze |
| Rule calibration matrix schema | [`schemas/rule-calibration-matrix.schema.json`](../schemas/rule-calibration-matrix.schema.json) | JSON schema, rule calibration matrix, schema freeze |
| Test plan schema | [`schemas/test_plan.schema.json`](../schemas/test_plan.schema.json) | JSON schema, test plan, invariant candidates |
| Report template | [`templates/pre_audit_report.md`](../templates/pre_audit_report.md) | template, Markdown report, disclaimer |
| Invariant skeleton template | [`templates/invariant_skeletons/ArkheionxReadinessInvariants.t.sol`](../templates/invariant_skeletons/ArkheionxReadinessInvariants.t.sol) | Foundry, invariant, skeleton |
| AMM invariant skeleton template | [`templates/invariant_skeletons/amm_invariants.sol`](../templates/invariant_skeletons/amm_invariants.sol) | AMM, Foundry, invariant skeleton |
| Lending invariant skeleton template | [`templates/invariant_skeletons/lending_invariants.sol`](../templates/invariant_skeletons/lending_invariants.sol) | lending, Foundry, invariant skeleton |
| Hybrid invariant skeleton template | [`templates/invariant_skeletons/hybrid_invariants.sol`](../templates/invariant_skeletons/hybrid_invariants.sol) | hybrid, Foundry, invariant skeleton |

## Search Term Index

| Term | Aliases | Category | Related checks | Tags |
|---|---|---|---|---|
| `Arkheionx` | Arkheionx Security Memory, Arkheionx Readiness, pre-audit readiness OS, GitHub-native security memory | product | GitHub Action, Markdown report, SARIF output, baseline diff | arkheionx, security-memory, pre-audit-readiness, indie-defi |
| `GitHub repo surface` | repository about, repository topics, public surface polish, GitHub About description | public surface | docs/GITHUB_REPO_SURFACE.md, README.md, scripts/github_surface_setup.sh | github-repo-surface, repository-about, public-surface-polish |
| `security memory OS` | DeFi Security Memory OS, Arkheionx positioning, pre-audit readiness OS | product positioning | README.md, docs/GITHUB_REPO_SURFACE.md, docs/SECURITY_MEMORY_GRAPH.md | security-memory-os, arkheionx-positioning, pre-audit-readiness |
| `GitHub Action` | pre-audit action, Arkheionx action, GitHub-native scanner, Actions summary | GitHub-native workflow | Markdown report, JSON report, PR comment, issue checklist, SARIF | github-action, ci, pre-audit-readiness |
| `security memory` | DeFi security memory, historical exploit memory, root-cause knowledge base, security knowledge base | research archive | registry, search index, research dashboard, PoC maturity index | security-memory, root-cause-analysis, exploit-research |
| `readiness gap` | audit blocker, risk signal, review recommended, missing invariant | pre-audit readiness | finding ID, finding fingerprint, issue checklist, baseline diff | readiness-gap, audit-readiness, defensive-review |
| `historical exploit pattern` | historical pattern similarity, exploit primitive, broken invariant, failed assumption | research archive | registry metadata, search guide, scanner historical patterns | historical-exploit-pattern, root-cause-analysis, defi-security |
| `indie DeFi` | indie builder, solo DeFi founder, grant-funded builder, small DAO | audience | Launch Report, Pre-Audit Sprint, GitHub Action | indie-defi, builder-security, pre-audit |
| `vault accounting` | share accounting, totalAssets, pricePerShare, convertToShares, convertToAssets | pre-audit readiness | totalAssets consistency, deposit-withdraw roundtrip, share price manipulation resistance | vault-security, invariant-testing, audit-readiness |
| `oracle manipulation` | price manipulation, stale oracle, TWAP, latestRoundData, spot price | historical exploit pattern | stale price rejection, decimals normalization, price bounds, TWAP or sanity check | oracle-risk, price-assumptions, defi-security |
| `reentrancy` | callback, external call, value flow, nonReentrant, checks effects interactions | historical exploit pattern | malicious local receiver test, state update order, callback boundary review | reentrancy-review, value-flow, smart-contract-security |
| `access control` | onlyOwner, AccessControl, admin, role, privileged setter | pre-audit readiness | unauthorized role rejection, privileged setter tests, pause behavior | access-control-review, admin-risk, operational-security |
| `upgradeability` | initializer, reinitializer, proxy, UUPS, implementation, storage gap | pre-audit readiness | initializer runs once, upgrade authorization, storage layout documentation | upgradeability, initialization-bug, proxy-review |
| `reward accounting` | rewardPerToken, accumulator, index, claim, emission | pre-audit readiness | reward conservation, no overclaim, index monotonicity, precision tests | reward-accounting, staking, precision |
| `AMM invariant` | reserve manipulation, liquidity, swap invariant, kLast, sqrtPriceX96 | historical exploit pattern | invariant conservation, swap does not create value, liquidity proportionality | amm-invariant, liquidity, reserve-manipulation |
| `lending liquidation` | collateral, debt, healthFactor, liquidate, loanToValue | pre-audit readiness | collateralization invariant, liquidation solvency, interest index monotonicity | lending, liquidation, collateral, oracle-risk |
| `cross-chain validation` | bridge, endpoint, relayer, message, LayerZero, CCIP, Hyperlane, Wormhole | pre-audit readiness | source validation, sender validation, replay rejection, trusted endpoint documentation | cross-chain, bridge-validation, message-authentication |
| `pre-audit readiness` | audit preparation, readiness score, audit blocker, missing invariant, launch report | product | readiness report, GitHub Action, Markdown report, JSON report | pre-audit, audit-readiness, indie-defi, github-action |
| `ERC4626` | vault standard, previewDeposit, previewWithdraw, maxRedeem, asset() | vault rule pack | preview/action equivalence, convertToShares/convertToAssets consistency, max function boundaries | erc4626, vault-security, share-accounting, pre-audit |
| `share inflation` | donation sensitivity, low supply share accounting, share price manipulation, donation risk class | vault rule pack | donation tests, first deposit tests, rounding direction tests, low supply tests | share-inflation-risk, donation-sensitivity, vault-invariant |
| `strategy accounting` | strategy debt, harvest, gain, loss, totalDebt, withdrawFromStrategy | vault rule pack | mock strategy gain, mock strategy loss, debt update, harvest/report tests | strategy-accounting, gain-loss, vault-lifecycle |
| `withdrawal queue` | requestWithdraw, claimWithdraw, cooldown, pendingWithdraw, liquidityBuffer | vault rule pack | request lifecycle, claim lifecycle, cancel lifecycle, liquidity buffer tests | withdrawal-queue, vault-lifecycle, liquidity-buffer |
| `oracle-dependent vault` | LP token pricing, pool price, Chainlink vault, Yearn-style vault risk, Harvest-style oracle risk | vault rule pack | stale price rejection, pool price bounds, TWAP sanity check, decimals normalization | oracle-risk, vault-pricing, pool-pricing |
| `vault invariant tests` | totalAssets invariant, share accounting invariant, fee accounting invariant, strategy loss invariant | vault rule pack | totalAssets consistency, deposit-withdraw roundtrip, fee accounting conservation, strategy loss handling | vault-invariant, foundry, invariant-testing |
| `PR readiness comment` | pull request comment, GitHub Action comment, Arkheionx PR comment, readiness comment | GitHub Action UX | score summary, top readiness gaps, marker update mode | github-action, pull-request, pre-audit-readiness |
| `generated issue checklist` | issue checklist, remediation checklist, launch checklist, readiness checklist | GitHub Action UX | finding IDs, suggested tests, documentation tasks | issue-checklist, audit-readiness, indie-defi |
| `finding IDs` | ARK-VLT-001, ARK-ORC-001, stable readiness finding, readiness gap ID | report UX | JSON findings, Markdown gap sections, suppression by ID | finding-id, json-schema, report-ux |
| `Arkheionx config` | .arkheionx.json, false positive suppression, ignore paths, suppress findings | configuration | suppressed_findings, ignore_paths, additional_search_tags | config, false-positive, local-static-analysis |
| `SARIF` | SARIF output, sarif-output, GitHub Code Scanning, upload-sarif | GitHub security workflow | readiness_gap properties, not_formal_audit, SARIF rules and results | sarif, code-scanning, github-security-workflow |
| `GitHub Code Scanning` | code scanning, security-events, upload-sarif, CodeQL upload SARIF | GitHub security workflow | security-events: write, github/codeql-action/upload-sarif, readiness result severity | github-code-scanning, sarif, pre-audit-readiness |
| `baseline diff` | readiness baseline, compare baseline, diff mode, pre-audit diff | report UX | new findings, resolved findings, unchanged findings, changed findings | baseline-diff, readiness-tracking, report-diff |
| `finding fingerprint` | stable fingerprint, fingerprint_version, readiness fingerprint, finding hash | report UX | id, category, title, detected signals, affected files | finding-fingerprint, baseline, json-schema |
| `CI gating` | fail threshold, fail-score-below, fail-on-new-high, fail-on-unsuppressed-high | GitHub Action UX | score threshold, new high readiness gaps, unsuppressed high readiness gaps | ci-gating, fail-threshold, audit-readiness |
| `new readiness gaps` | new findings, new gaps, regression readiness, diff new | baseline diff | compare-baseline, diff-output, diff-json-output | new-readiness-gaps, baseline-diff, pre-audit-diff |
| `resolved readiness gaps` | resolved findings, closed gaps, remediated readiness, diff resolved | baseline diff | baseline comparison, remediation tracking, diff report | resolved-readiness-gaps, baseline-diff, remediation |
| `pre-audit diff` | readiness diff, report diff, baseline comparison, diff report | GitHub-native workflow | new/resolved/unchanged counts, PR comment diff, issue checklist diff | pre-audit-diff, readiness-baseline, github-action |
| `GitHub security workflow` | Actions security workflow, Code Scanning workflow, pre-audit CI workflow, security-events | GitHub-native workflow | SARIF upload, Actions summary, PR comment, baseline diff | github-security-workflow, code-scanning, pre-audit-readiness |
| `GitHub issue workflow` | generated issue plan, issue creation dry-run, readiness remediation, issue plan JSON | GitHub-native workflow | issue markers, duplicate prevention, dry-run output, max issue limit | github-issue-workflow, issue-plan, readiness-remediation |
| `oracle rule pack` | ARK-ORC, price feed checks, stale price tests, oracle readiness | rule pack | stale round rejection, decimals normalization, price bounds, oracle update access control | oracle-rule-pack, oracle-risk, pre-audit-readiness |
| `access control rule pack` | ARK-ACC, upgradeability rule pack, ARK-UPG, privileged setters | rule pack | role-boundary tests, initializer tests, upgrade authorization, emergency constraints | access-control-rule-pack, upgradeability, admin-risk |
| `reentrancy value flow rule pack` | ARK-REENT, external call review, claim flow tests, callback path | rule pack | state transition tests, double claim prevention, callback receiver mock, external call ordering | reentrancy-rule-pack, value-flow, defensive-review |
| `reward accounting rule pack` | ARK-RWD, staking rule pack, rewardPerToken, accumulator | rule pack | reward conservation, no overclaim, accumulator monotonicity, emission update constraints | reward-accounting-rule-pack, staking, precision |
| `semantic-lite analysis` | Solidity structure extraction, semantic lite, function evidence, local parser | analysis quality | contracts, functions, modifiers, state variables, test coverage mapping | semantic-lite, solidity-structure, false-positive-reduction |
| `evidence-based findings` | finding evidence, confidence reason, detection sources, affected functions | analysis quality | semantic-lite evidence, test coverage evidence, Slither evidence, keyword evidence | finding-evidence, confidence-scoring, readiness-gap |
| `Slither integration` | Slither JSON, slither analyzer, optional Slither, local Slither | analysis quality | --slither, --slither-json, --slither-output, --slither-strict | slither-integration, slither-json, local-static-analysis |
| `false positive reduction` | keyword-only downgrade, low-confidence findings, noise reduction, confidence scoring | analysis quality | downgrade_keyword_only, min_confidence_for_issue_plan, test coverage mapping | false-positive-reduction, low-confidence, evidence-based |
| `Launch Report OS` | Launch Readiness Report, launch report, client-ready report, audit handoff package | delivery artifact | executive summary, remediation roadmap, generated artifacts, formal audit preparation | launch-report, client-ready-report, pre-audit-readiness |
| `Pre-Audit Sprint` | sprint plan, pre-audit sprint workflow, remediation sprint, sprint checklist | delivery artifact | 3 day sprint, 5 day sprint, 7 day sprint, 10 day sprint, sprint exit criteria | pre-audit-sprint, remediation-roadmap, delivery-artifacts |
| `Contest Readiness Mode` | Contest Readiness Report, pre-contest readiness, bug bounty readiness, audit contest preparation | delivery artifact | scope checklist, researcher onboarding checklist, known limitations, pre-contest priorities | contest-readiness, scope-checklist, researcher-onboarding |
| `remediation roadmap` | phase-based remediation, readiness roadmap, remediation phases, owner-ready tasks | delivery artifact | launch blockers, high-priority gaps, documentation hardening, audit handoff | remediation-roadmap, issue-plan, launch-readiness |
| `executive summary` | founder summary, stakeholder summary, one-page summary, grant update | delivery artifact | top themes, top actions, readiness status, recommended next step | executive-summary, founder-ready, delivery-artifacts |
| `delivery artifacts` | client-ready artifacts, Launch Report, Sprint Plan, Contest Readiness Report | delivery workflow | Markdown report, JSON report, SARIF, issue plan, launch report | delivery-artifacts, github-native, service-delivery |
| `try Arkheionx in 5 minutes` | five minute demo, quick demo, demo scan, try in 5 minutes | public demo | demo reports, demo issue dry-run, toy fixture | try-in-5-minutes, public-demo, onboarding |
| `public demo workflow` | demo GitHub Action workflow, arkheionx-demo.yml, demo artifacts, public demo reports | public demo | upload artifact, no issue creation, no token required | public-demo-workflow, github-action, demo-artifacts |
| `oracle staking demo` | demo protocol, oracle staking fixture, reproducible readiness demo | case study | oracle rule pack, reward accounting rule pack, case study | oracle-staking-demo, case-study, rule-calibration |
| `before after case study` | before/after remediation, fixed fixture, readiness improvement demo | case study | before report, after report, score comparison, evidence improvements | before-after, case-study, remediation |
| `rule calibration` | calibration summary, false positive calibration, confidence calibration | analysis quality | confidence model, downgrade logic, common false positives | rule-calibration, false-positive-review, confidence-scoring |
| `external validation feedback` | external feedback, validation feedback, public feedback, feedback workflow | community feedback | external validation issue template, false positive issue template, no secrets | external-validation, feedback, open-source-growth |
| `case study template` | case_study_template.md, generated case study, case study outline | case study | scope, score, top findings, evidence examples, limitations | case-study-template, documentation, demo |
| `launch post` | launch posts, outreach kit, v0.8 launch posts, release announcement draft | growth | no unsupported traction claims, no guarantee claims, demo workflow CTA | launch-post, outreach-kit, public-demo |
| `security memory graph` | finding knowledge map, local knowledge graph, security memory map | security memory | metadata/security_memory_graph.json, reports/security_memory_graph.md, search_knowledge.py | security-memory-graph, knowledge-map, local-static-analysis |
| `finding knowledge map` | finding-to-pattern mapping, ARK finding map, readiness knowledge map | security memory | ARK-ORC-001, ARK-VLT-001, related_pocs, suggested_tests | finding-knowledge-map, finding-id, historical-pattern-similarity |
| `rule calibration matrix` | calibration matrix, confidence matrix, rule confidence requirements | analysis quality | high confidence requires, downgrade conditions, common false positives | rule-calibration-matrix, confidence-scoring, false-positive-reduction |
| `oracle stale price` | Chainlink updatedAt, heartbeat validation, stale round, oracle freshness | security memory | ARK-ORC-001, stale round rejection, heartbeat bound test | oracle-stale-price, chainlink, historical-pattern |
| `vault donation attack` | share inflation, donation sensitivity, first deposit attack class | security memory | ARK-VLT-001, ARK-VLT-003, donation resistance, share accounting invariant | vault-donation, share-accounting, vault-security |
| `reentrancy value flow` | callback capable token, external call before state update, claim refund flow | security memory | ARK-REENT-001, reentrant receiver mock, double claim prevention | reentrancy-value-flow, callback, defensive-test |
| `reward overclaim` | accumulator precision, reward conservation, claim twice | security memory | ARK-RWD-001, reward conservation, rewardPerToken monotonicity | reward-overclaim, staking, accounting-invariant |
| `initializer protection` | upgrade authorization, proxy initializer, initializer runs once | security memory | ARK-UPG-001, ARK-ACC-001, initializer cannot run twice | initializer-protection, upgradeability, access-control |
| `broken invariant mapping` | failed assumption mapping, exploit primitive mapping, suggested defensive tests | security memory | security memory graph, finding knowledge map, rule calibration matrix | broken-invariant, failed-assumption, suggested-tests |
| `stable public release` | v1.0.0, schema freeze, production-ready documentation | release | CLI reference, GitHub Action stable inputs, schema reference | v1.0.0, stable-release, schema-freeze |
| `CLI reference` | stable CLI flags, pre_audit_scan.py help, scanner interface | documentation | --root, --json-output, --sarif-output, --issue-plan-output | cli-reference, stable-flags, pre-audit-scanner |
| `JSON schema` | schema reference, pre-audit report schema, issue plan schema, baseline schema | schema | schemas/pre-audit-report.schema.json, schemas/issue-plan.schema.json | json-schema, schema-freeze, stable-output |
| `output artifact naming` | recommended output names, generated artifacts, reports directory | documentation | ARKHEIONX_PRE_AUDIT_REPORT.md, arkheionx-report.json, arkheionx.sarif.json | output-artifacts, generated-artifacts, reports |
| `feedback loop` | external calibration, feedback workflow, calibration workflow | feedback | false positive report, false negative report, report quality feedback | feedback-loop, external-calibration, v1.1.0 |
| `false positive report` | noisy finding, false positive calibration, finding too noisy | feedback | rule calibration backlog, feedback dashboard | false-positive, calibration, report-feedback |
| `false negative report` | missed finding, missed readiness signal, missing readiness gap | feedback | rule calibration request, feedback triage | false-negative, calibration, readiness-signal |
| `rule calibration backlog` | calibration backlog, rule tuning backlog, feedback backlog | feedback | metadata/rule_calibration_backlog.json, reports/rule_calibration_backlog.md | rule-calibration, backlog, feedback-dashboard |
| `feedback dashboard` | feedback summary, calibration dashboard, external feedback dashboard | feedback | reports/feedback_dashboard.md, generate_feedback_dashboard.py | feedback-dashboard, external-validation, calibration |
| `public feedback guide` | feedback guide, safe feedback, public feedback | feedback | docs/PUBLIC_FEEDBACK_GUIDE.md, docs/FEEDBACK_LOOP.md | public-feedback, safe-disclosure, feedback-guide |
| `validation levels` | external validation levels, validation maturity, allowed claims | external validation | docs/VALIDATION_LEVELS.md, docs/EXTERNAL_VALIDATION.md | validation-levels, external-evaluation, honest-claims |
| `GitHub Action feedback` | action feedback, workflow feedback, CI feedback | feedback | docs/GITHUB_ACTION_USAGE.md, .github/ISSUE_TEMPLATE/github_action_feedback.yml | github-action-feedback, ci, workflow |
| `report quality feedback` | report wording, report clarity, next-step feedback | feedback | Launch Report, Pre-Audit Report, Executive Summary | report-quality, readability, actionability |
| `paid offer` | paid readiness support, commercial positioning, service package | business | docs/business/PAID_OFFER.md, reports/paid_offer_index.md | paid-offer, readiness-support, commercial |
| `readiness snapshot` | Arkheionx Readiness Snapshot, quick readiness scan, blocker scan | business | docs/business/SERVICE_PACKAGES.md, templates/readiness_snapshot_scope.md | readiness-snapshot, pre-audit, paid-offer |
| `pre-audit sprint` | Arkheionx Pre-Audit Sprint, sprint plan, guided readiness workflow | business | docs/business/SERVICE_PACKAGES.md, templates/pre_audit_sprint_scope.md | pre-audit-sprint, remediation-roadmap, paid-offer |
| `contest readiness pack` | Contest Readiness Pack, scope checklist, researcher onboarding | business | docs/business/SERVICE_PACKAGES.md, templates/contest_readiness_scope.md | contest-readiness-pack, scope-checklist, paid-offer |
| `GitHub Action setup` | CI setup, SARIF setup, report artifact setup | business | docs/GITHUB_ACTION_USAGE.md, docs/business/SERVICE_PACKAGES.md | github-action-setup, ci, paid-offer |
| `paid work boundaries` | commercial boundaries, service exclusions, safety boundaries | business | docs/business/PAID_WORK_BOUNDARIES.md, docs/business/SALES_FAQ.md | paid-work-boundaries, safety, commercial |
| `client intake` | client intake template, repo intake, readiness intake | business | docs/business/CLIENT_INTAKE.md, templates/client_intake.md | client-intake, scope-of-work, paid-offer |
| `scope of work` | SOW, scope template, proposal template | business | docs/business/SAMPLE_SCOPE_OF_WORK.md, docs/business/PROPOSAL_TEMPLATE.md | scope-of-work, proposal-template, paid-offer |
| `pricing ladder` | pricing guidance, pilot pricing, service pricing | business | docs/business/PRICING_LADDER.md, metadata/paid_offer_catalog.json | pricing-ladder, paid-offer, commercial |
| `ecosystem pack` | Arkheionx Ecosystem Pack, ecosystem readiness pack, multi-repo readiness pack | ecosystem readiness | docs/ecosystem/ECOSYSTEM_PACK.md, reports/ecosystem_readiness_summary.md | ecosystem-pack, multi-repo-readiness, readiness-support |
| `ecosystem readiness` | ecosystem-level readiness, portfolio readiness, cohort readiness | ecosystem readiness | docs/ecosystem/ECOSYSTEM_READINESS_PILOT.md, templates/ecosystem_readiness_pilot_scope.md | ecosystem-readiness, cohort-readiness, audit-prep |
| `multi-repo readiness` | multiple repo readiness, repo cohort scan, authorized multi-repo workflow | ecosystem readiness | docs/ecosystem/MULTI_REPO_READINESS_WORKFLOW.md, templates/ecosystem_manifest.example.json | multi-repo-readiness, authorized-repositories, local-static |
| `ecosystem intake` | ecosystem client intake, multi-repo intake, cohort intake | ecosystem readiness | docs/ecosystem/ECOSYSTEM_INTAKE.md, templates/ecosystem_intake.md | ecosystem-intake, authorization, scope |
| `anonymized reporting` | anonymized gap summary, repo aliases, redacted ecosystem report | ecosystem readiness | docs/ecosystem/ANONYMIZED_REPORTING.md, reports/ecosystem_common_gaps.md | anonymized-reporting, common-gap-report, safe-disclosure |
| `common gap report` | common readiness gaps, recurring findings, rule-family heatmap | ecosystem readiness | reports/ecosystem_common_gaps.md, metadata/ecosystem_pilot_example.json | common-gap-report, recurring-findings, rule-family-heatmap |
| `cohort readiness` | audit-prep cohort, builder cohort readiness, accelerator readiness | ecosystem readiness | docs/ecosystem/COHORT_READINESS_GUIDE.md, docs/ecosystem/ECOSYSTEM_OPERATOR_FAQ.md | cohort-readiness, ecosystem-operator, readiness-pilot |
| `repo-by-repo readiness` | repo readiness table, repository readiness table, repository aliases | ecosystem readiness | reports/ecosystem_readiness_summary.md, metadata/ecosystem_pack_schema.json | repo-by-repo-readiness, ecosystem-summary, anonymized |
| `ecosystem readiness summary` | ecosystem summary, ecosystem pilot report, readiness distribution | ecosystem readiness | reports/ecosystem_readiness_summary.md, scripts/generate_ecosystem_report.py | ecosystem-readiness-summary, synthetic-report, markdown |
| `AMM rule pack` | AMM readiness, liquidity pool readiness, swap readiness | rule pack | docs/AMM_RULE_PACK.md, examples/amm-fixture/README.md | amm-rule-pack, amm-readiness, liquidity-pool |
| `AMM invariant` | constant product, stableswap invariant, reserve invariant | AMM | ARK-AMM-001, docs/AMM_RULE_PACK.md | amm-invariant, constant-product, reserve-accounting |
| `LP share accounting` | liquidity shares, pool token accounting, mint burn boundary | AMM | ARK-AMM-002, docs/AMM_RULE_PACK.md | lp-share-accounting, mint-burn, dust-handling |
| `slippage boundary` | minOut, amountOutMin, deadline, stale quote | AMM | ARK-AMM-005, docs/AMM_RULE_PACK.md | slippage, min-output, quote-boundary |
| `reserve accounting` | reserve0 reserve1, getReserves, pool reserve accounting | AMM | ARK-AMM-001, ARK-AMM-003, docs/AMM_RULE_PACK.md | reserve-accounting, spot-price, amm |
| `lending rule pack` | lending readiness, borrow repay readiness, lending market readiness | rule pack | docs/LENDING_RULE_PACK.md, examples/lending-fixture/README.md | lending-rule-pack, lending-readiness, borrow-repay |
| `collateral debt invariant` | solvency invariant, health factor invariant, lending solvency | lending | ARK-LEND-001, docs/LENDING_RULE_PACK.md | collateral-debt, solvency, health-factor |
| `liquidation boundary` | liquidation threshold, close factor, liquidation bonus | lending | ARK-LEND-002, docs/LENDING_RULE_PACK.md | liquidation-boundary, threshold, lending |
| `interest index` | borrow index, accrueInterest, interest accounting | lending | ARK-LEND-003, docs/LENDING_RULE_PACK.md | interest-index, borrow-index, rounding-drift |
| `lending health factor` | healthFactor, collateral value, oracle-dependent liquidation | lending | ARK-LEND-004, docs/LENDING_RULE_PACK.md, docs/ORACLE_RULE_PACK.md | health-factor, lending-oracle, price-shock |
| `invariant generator` | test plan generator, Arkheionx test plan generator, generate_test_plan.py | test planning | scripts/generate_test_plan.py, docs/INVARIANT_TEST_PLAN_GENERATOR.md | invariant-generator, test-plan-generator, foundry |
| `Foundry invariant skeleton` | invariant skeleton, Foundry skeleton, Arkheionx invariant skeleton | test planning | docs/FOUNDRY_INVARIANT_SKELETONS.md, templates/invariant_skeletons/ | foundry-invariant-skeleton, local-testing, defensive-scaffold |
| `suggested tests` | finding suggested tests, test recommendations, defensive test ideas | test planning | metadata/finding_test_plan_map.json, examples/reports/amm-fixture-test-plan.md | suggested-tests, readiness-remediation, test-plan |
| `invariant candidates` | candidate invariants, property candidates, invariant ideas | test planning | metadata/finding_test_plan_map.json, schemas/test_plan.schema.json | invariant-candidates, property-testing, foundry |
| `AMM invariant skeleton` | AMM test plan, AMM Foundry skeleton, pool invariant skeleton | AMM | examples/reports/ArkheionxAMMInvariants.t.sol, docs/AMM_RULE_PACK.md | amm-invariant-skeleton, constant-product, reserve-accounting |
| `lending invariant skeleton` | lending test plan, lending Foundry skeleton, collateral debt skeleton | lending | examples/reports/ArkheionxLendingInvariants.t.sol, docs/LENDING_RULE_PACK.md | lending-invariant-skeleton, collateral-debt, liquidation-boundary |
| `oracle test plan` | stale oracle test plan, oracle freshness tests, oracle invariant candidates | oracle | ARK-ORC-001, metadata/finding_test_plan_map.json | oracle-test-plan, stale-price, heartbeat |
| `reward index invariant` | reward accumulator invariant, reward index monotonicity, staking index test | reward | ARK-RWD-002, docs/REWARD_ACCOUNTING_RULE_PACK.md | reward-index, accumulator, staking |

## Historical Memory Index

Generated from `metadata/registry.json`.

| ID | Protocol | Category | Severity | Tags | Path |
|---|---|---|---|---|---|
| `2017-07-parity-multisig` | Parity Multisig Wallet | `access-control-failure` | `critical` | template-reference, phase-5-strong | [`EVM/test/2017-07/Exploit_2017-07.t.sol`](../EVM/test/2017-07/Exploit_2017-07.t.sol) |
| `2017-11-parity-suicide` | Parity Multisig Library | `access-control-failure` | `critical` | - | [`EVM/test/2017-11/Exploit_2017-11.t.sol`](../EVM/test/2017-11/Exploit_2017-11.t.sol) |
| `2018-04-bec-token` | BeautyChain Token (BEC) | `arithmetic-precision-rounding` | `critical` | - | [`EVM/test/2018-04/Exploit_2018-04.t.sol`](../EVM/test/2018-04/Exploit_2018-04.t.sol) |
| `2018-10-spankchain` | SpankChain | `reentrancy` | `high` | - | [`EVM/test/2018-10/Exploit_2018-10.t.sol`](../EVM/test/2018-10/Exploit_2018-10.t.sol) |
| `2020-04-uniswap-imbtc` | Uniswap V1 / imBTC | `reentrancy` | `high` | - | [`EVM/test/2020-04/Exploit_2020-04.t.sol`](../EVM/test/2020-04/Exploit_2020-04.t.sol) |
| `2020-06-balancer-deflationary` | Bancor | `access-control-failure` | `high` | phase-6a-reclassified, phase-6e-assertion-patch | [`EVM/test/2020-06/Exploit_2020-06.t.sol`](../EVM/test/2020-06/Exploit_2020-06.t.sol) |
| `2020-08-opyn` | Opyn v1 | `invariant-bypass` | `high` | - | [`EVM/test/2020-08/Exploit_2020-08.t.sol`](../EVM/test/2020-08/Exploit_2020-08.t.sol) |
| `2020-09-bzx-ifusdc` | bZx | `accounting-mismatch` | `critical` | phase-6a-reclassified, phase-6f-asserted | [`EVM/test/2020-09/Exploit_2020-09.t.sol`](../EVM/test/2020-09/Exploit_2020-09.t.sol) |
| `2020-10-harvest` | Harvest Finance | `flash-loan-price-manipulation` | `critical` | - | [`EVM/test/2020-10/Exploit_2020-10.t.sol`](../EVM/test/2020-10/Exploit_2020-10.t.sol) |
| `2020-11-cheese-bank` | Pickle Finance | `unsafe-external-call` | `critical` | phase-6a-reclassified | [`EVM/test/2020-11/Exploit_2020-11.t.sol`](../EVM/test/2020-11/Exploit_2020-11.t.sol) |
| `2020-12-warp-finance` | Cover Protocol | `accounting-mismatch` | `critical` | phase-6a-reclassified, phase-6g-asserted | [`EVM/test/2020-12/Exploit_2020-12.t.sol`](../EVM/test/2020-12/Exploit_2020-12.t.sol) |
| `2021-01-saddle` | SushiSwap (SushiMaker) | `amm-invariant-manipulation` | `high` | phase-6a-reclassified | [`EVM/test/2021-01/Exploit_2021-01.t.sol`](../EVM/test/2021-01/Exploit_2021-01.t.sol) |
| `2021-02-yearn-v1-dai` | Yearn v1 (yDAI vault) | `flash-loan-price-manipulation` | `critical` | - | [`EVM/test/2021-02/Exploit_2021-02.t.sol`](../EVM/test/2021-02/Exploit_2021-02.t.sol) |
| `2021-03-dodo-crowdpool` | DODO V2 CrowdPooling | `initialization-bug` | `high` | - | [`EVM/test/2021-03/Exploit_2021-03.t.sol`](../EVM/test/2021-03/Exploit_2021-03.t.sol) |
| `2021-10-indexed-finance` | Indexed Finance | `amm-invariant-manipulation` | `critical` | - | [`EVM/test/2021-10/Exploit_2021-10.t.sol`](../EVM/test/2021-10/Exploit_2021-10.t.sol) |
| `2022-02-dexible` | BUILD Finance | `governance-attack` | `high` | phase-6a-reclassified, phase-7b-asserted | [`EVM/test/2022-02/Exploit_2022-02.t.sol`](../EVM/test/2022-02/Exploit_2022-02.t.sol) |
| `2025-11-moonwell` | Moonwell | `oracle-manipulation` | `high` | - | [`EVM/test/2025-11/Exploit_2025-11.t.sol`](../EVM/test/2025-11/Exploit_2025-11.t.sol) |
| `2025-12-yeth` | yETH | `amm-invariant-manipulation` | `critical` | - | [`EVM/test/2025-12/Exploit_2025-12.t.sol`](../EVM/test/2025-12/Exploit_2025-12.t.sol) |

## High-Value Searches

```text
vault accounting
ERC4626
totalAssets
convertToShares
convertToAssets
share price manipulation
share inflation
donation risk class
strategy accounting
withdrawal queue
fee accounting
oracle-dependent vault
vault invariant tests
PR readiness comment
generated issue checklist
finding IDs
.arkheionx.json
SARIF
GitHub Code Scanning
baseline diff
readiness baseline
finding fingerprint
CI gating
fail threshold
new readiness gaps
resolved readiness gaps
pre-audit diff
GitHub security workflow
GitHub issue workflow
generated issue plan
issue creation dry-run
issue marker
duplicate prevention
readiness remediation
oracle rule pack
access control rule pack
upgradeability rule pack
reentrancy value flow rule pack
reward accounting rule pack
staking rule pack
issue plan JSON
semantic-lite analysis
Solidity structure extraction
false positive reduction
evidence-based findings
confidence scoring
detection sources
Slither integration
Slither JSON
test coverage mapping
affected functions
SARIF locations
finding evidence
low-confidence findings
keyword-only downgrade
Launch Report OS
Launch Readiness Report
Pre-Audit Sprint
Contest Readiness Mode
Contest Readiness Report
remediation roadmap
executive summary
client-ready report
audit handoff package
researcher onboarding checklist
scope checklist
pre-contest readiness
bug bounty readiness
delivery artifacts
try Arkheionx in 5 minutes
public demo workflow
demo protocol
oracle staking demo
before after case study
external validation
rule calibration
false positive calibration
false positive review workflow
external validation feedback
public demo reports
case study template
launch post
outreach kit
demo GitHub Action workflow
reproducible readiness demo
security memory graph
finding knowledge map
historical pattern similarity
exploit primitive mapping
broken invariant mapping
failed assumption mapping
suggested defensive tests
rule calibration matrix
oracle stale price
Chainlink updatedAt
heartbeat validation
vault donation attack
share accounting invariant
reentrancy value flow
callback capable token
reward overclaim
accumulator precision
access control failure
initializer protection
upgrade authorization
liquidation boundary
AMM invariant
cross chain replay
contest readiness search
launch report knowledge
oracle manipulation
flash loan price manipulation
reentrancy
access control
initialization bug
upgradeability
reward accounting
AMM invariant
lending liquidation
bridge validation
historical exploit pattern
pre-audit readiness
indie DeFi
audit blocker
missing invariant
Foundry invariant testing
root-cause analysis
feedback loop
false positive report
false negative report
rule calibration backlog
feedback dashboard
external validation
public feedback guide
validation levels
GitHub Action feedback
report quality feedback
GitHub repo surface
repository about
public surface polish
security memory OS
Arkheionx positioning
paid offer
readiness snapshot
pre-audit sprint
contest readiness pack
GitHub Action setup
paid work boundaries
client intake
scope of work
pricing ladder
commercial positioning
proposal template
ecosystem pack
ecosystem readiness
multi-repo readiness
ecosystem intake
anonymized reporting
common gap report
readiness pilot
cohort readiness
ecosystem operator
repo-by-repo readiness
ecosystem readiness summary
invariant generator
test plan generator
Foundry invariant skeleton
suggested tests
invariant candidates
AMM invariant skeleton
lending invariant skeleton
oracle test plan
vault invariant
liquidation boundary test
collateral debt invariant
reward index invariant
```

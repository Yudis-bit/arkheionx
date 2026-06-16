# ArkheionX Docs Inventory

Date: 2026-06-16

This inventory was created before moving or archiving docs. It classifies the current docs surface by public purpose and cleanup risk. Directory globs are used where files share the same category, status, and recommended action.

| file | category | status | reason | recommended action |
|---|---|---|---|---|
| `docs/README.md` | canonical public | update | Existing index is useful but version-heavy and not the requested clean public path. | Rewrite as navigation page only. |
| `docs/START_HERE.md` | canonical public | update | Stale first command and v3.3 references; still useful as orientation. | Rewrite around ArkheionX review infrastructure and current CLI truth. |
| `docs/WHAT_IS_ARKHEIONX.md` | canonical public | needs review | Missing canonical explainer. | Create as the project-definition page. |
| `docs/WHAT_ARKHEIONX_IS_NOT.md` | canonical public | update | Good safety boundary, but wording should align with current review-infrastructure positioning. | Keep and update. |
| `docs/INSTALLATION.md` | canonical public | update | Exists, but must reflect source install and repo identity migration. | Keep canonical, update. |
| `docs/CLI_REFERENCE.md` | CLI | update | Exists but starts with `review-map` and carries historical version sections. | Rewrite from live `arkheionx --help`. |
| `docs/CORE_WORKFLOW.md` | workflow | update | Good current `arkheionx review` explanation. | Keep canonical, tighten wording. |
| `docs/INTERPRET_RESULTS.md` | artifacts/output | update | Strong safety framing but old v4-v7 layering dominates. | Keep canonical, update for current outputs. |
| `docs/OUTPUT_ARTIFACTS.md` | artifacts/output | update | v1 scanner-centric; does not describe current review pack clearly. | Rewrite around review pack, generated local artifacts, and legacy scanner outputs. |
| `docs/EVIDENCE_PACKAGE.md` | artifacts/output | update | Useful but proof/evidence language needs current limitation framing. | Keep canonical, update. |
| `docs/CASE_STUDIES.md` | case study | needs review | Missing canonical case-study entry point. | Create. |
| `docs/EXTERNAL_VALIDATION.md` | canonical public | update | Exists but old demo/report-feedback framing is too narrow for EF feedback. | Rewrite around external reviewer and protocol-team validation. |
| `docs/ROADMAP.md` | canonical public | update | Version-confused; says v8.0.1/v8.1.0 and later latest stable v7.0.0. | Rewrite as credibility/validation roadmap, not feature sprawl. |
| `docs/REPO_IDENTITY_MIGRATION.md` | canonical public | update | Strong existing blocker doc but should reflect public project name and recommended `arkheionx` repo. | Keep and update. |
| `docs/PUBLIC_ALPHA_READINESS.md` | canonical public | update | Useful but v8-era and says real-protocol case studies are absent. | Update to current status and validation blockers. |
| `docs/VERSIONING.md` | canonical public | needs review | Missing version truth document. | Create. |
| `docs/PUBLIC_FEEDBACK_GUIDE.md` | workflow | update | Existing feedback guide is scanner/report-quality oriented. | Rewrite for auditor/protocol reviewer feedback. |
| `docs/ARKHEIONX_CONFIG.md`, `docs/CONFIG_REFERENCE.md`, `docs/CONFIG_SAFETY.md`, `docs/SUPPRESSIONS.md` | CLI | keep | Configuration references remain useful for operators. | Keep as reference, link only from advanced docs. |
| `docs/ARKUP.md`, `docs/INSTALLER.md`, `docs/UNINSTALL.md`, `docs/UPDATE_FLOW.md`, `docs/PACKAGING.md`, `docs/PACKAGE_DATA.md`, `docs/PACKAGE_ARCHITECTURE.md` | CLI | keep | Installer/package docs are useful but not first-run narrative. | Keep as advanced reference; update only if touched by identity/version changes. |
| `docs/CLI_CANDIDATE.md`, `docs/CLI_COMMANDS.md`, `docs/CLI_INSTALLABLE.md`, `docs/CLI_MIGRATION_TO_V2.md`, `docs/CLI_ROADMAP.md`, `docs/CLI_UX.md` | CLI | archive | Historical CLI evolution docs duplicate current `CLI_REFERENCE.md`. | Move to `docs/archive/legacy-workflows/` if tests do not assert paths. |
| `docs/REVIEW_MAP.md`, `docs/VALUE_FLOW_WORKBENCH.md`, `docs/PROTOCOL_MAP.md`, `docs/SCOPE_MAP.md`, `docs/SCOPE_ORCHESTRATION.md`, `docs/SCOPE_TASKS.md` | workflow | keep | Useful deeper workflow/model references. | Keep as deep docs; canonical pages should link selectively. |
| `docs/PROTOCOL_LENS_PACKS.md`, `docs/FIXED_CREDIT_MARKET_LENS.md` | workflow | keep | Current protocol-family context. | Keep as advanced workflow docs. |
| `docs/EVIDENCE_GRAPH.md`, `docs/EVIDENCE_JUDGE.md`, `docs/INTERACTION_MATRIX.md`, `docs/UNRESOLVED_MAP.md`, `docs/REPORT_FILTER.md`, `docs/COMPLETE_REVIEW.md` | artifacts/output | keep | Current/recent evidence and review packaging references. | Keep as deep docs, avoid version-heavy first-run framing. |
| `docs/REVIEW_PACKAGE.md`, `docs/REVIEW_PACKAGE_WORKFLOW.md`, `docs/REVIEW_PACKAGE_SMOKE_TEST.md` | artifacts/output | keep | Useful generated package docs. | Keep as advanced reference. |
| `docs/LOCAL_VALIDATION.md`, `docs/LOCAL_VALIDATION_WORKFLOW.md`, `docs/LOCAL_VALIDATION_SMOKE_TEST.md`, `docs/EXECUTION_PROOF.md`, `docs/TRACE_ENGINE.md`, `docs/FORK_VERIFICATION.md`, `docs/ARTIFACT_VALIDATION.md`, `docs/EVIDENCE_WORKFLOW_HARDENING.md`, `docs/VALIDATION_LEVELS.md` | artifacts/output | keep | Evidence/proof docs are useful and several are referenced by tests/scripts. | Keep, with links from canonical evidence docs. |
| `docs/SCHEMAS.md`, `docs/SCHEMA_REFERENCE.md`, `docs/METADATA_SCHEMA.md`, `docs/OUTPUT_STANDARD.md`, `docs/OUTPUT_PROFILES.md`, `docs/SARIF_OUTPUT.md` | artifacts/output | keep | Schema and output references remain useful for tool consumers. | Keep as reference. |
| `docs/ACCESS_CONTROL_RULE_PACK.md`, `docs/AMM_RULE_PACK.md`, `docs/LENDING_RULE_PACK.md`, `docs/ORACLE_RULE_PACK.md`, `docs/REENTRANCY_VALUE_FLOW_RULE_PACK.md`, `docs/REWARD_ACCOUNTING_RULE_PACK.md`, `docs/VAULT_RULE_PACK.md`, `docs/RULE_PACKS.md`, `docs/RULE_PACK_CONFIGURATION.md`, `docs/RULE_CALIBRATION.md`, `docs/ASSERTION_STANDARD.md`, `docs/INVARIANT_SAFETY_BOUNDARIES.md`, `docs/INVARIANT_TEST_PLAN_GENERATOR.md`, `docs/FOUNDRY_INVARIANT_SKELETONS.md` | rule pack | keep | Rule-pack and invariant references remain useful technical docs. | Keep as advanced reference. |
| `docs/AUDITOR_CHECKLIST.md`, `docs/RESEARCH_STANDARD.md`, `docs/REPRODUCIBILITY.md`, `docs/REPRODUCIBILITY_STANDARD.md`, `docs/POC_STANDARD.md`, `docs/POC_MATURITY_MODEL.md`, `docs/VERIFICATION_REPORT_TEMPLATE.md`, `docs/ROOT_CAUSE_PLAYBOOK.md` | research standard | keep | Useful standards for responsible review and case-study quality. | Keep, link from case-study/external validation docs where relevant. |
| `docs/CASE_STUDY_SAMPLE.md`, `docs/case-studies/ORACLE_STAKING_BEFORE_AFTER.md`, `docs/case-studies/ORACLE_STAKING_FIXTURE_CASE_STUDY.md` | case study | update | Existing case studies are fixture-oriented; public need is real workflow case-study framing. | Keep existing files, add canonical case-study README/template and new real workflow case studies. |
| `docs/BUG_BOUNTY_WORKFLOW.md`, `docs/SOLO_RESEARCH_WORKFLOW.md`, `docs/DEVELOPER_RESEARCHER_WORKFLOW.md`, `docs/PRE_AUDIT_WORKFLOW.md`, `docs/PRE_AUDIT_SPRINT_WORKFLOW.md`, `docs/CONTEST_READINESS_MODE.md`, `docs/PRE_AUDIT_READINESS_OS.md` | workflow | merge | Useful but overlapping and sometimes bounty/pre-audit framed too strongly for current public positioning. | Keep as advanced docs; canonical workflow should absorb safe concepts. |
| `docs/PUBLIC_DEMO_WORKFLOW.md`, `docs/TRY_IN_5_MINUTES.md`, `docs/DEMO_WORKFLOW.md`, `docs/ONBOARDING.md`, `docs/TROUBLESHOOTING.md`, `docs/TRAINING.md` | workflow | keep | Useful onboarding support. | Keep but do not make them the canonical first path until refreshed. |
| `docs/FIXTURE_HARNESS.md`, `docs/FIXTURE_BENCHMARKS.md`, `docs/FIXTURE_SNAPSHOT_WORKFLOW.md`, `docs/PROTOCOL_GRAPH_WORKFLOW.md`, `docs/PROTOCOL_GRAPH_SMOKE_TEST.md`, `docs/PROTOCOL_INTELLIGENCE_CORE.md`, `docs/SEMANTIC_LITE_ANALYSIS.md`, `docs/INTERNAL_ENGINE_SPLIT.md` | internal/private | leave internal | Useful engineering docs but too deep for public first impression. | Keep out of canonical docs path. |
| `docs/NOISE_REDUCTION.md`, `docs/FALSE_POSITIVE_REDUCTION.md`, `docs/FALSE_POSITIVE_REVIEW_WORKFLOW.md`, `docs/FEEDBACK_LOOP.md`, `docs/FEEDBACK_TRIAGE_WORKFLOW.md`, `docs/FINDING_KNOWLEDGE_MAP.md`, `docs/SECURITY_MEMORY_GRAPH.md`, `docs/SEARCH_GUIDE.md`, `docs/SEARCH_KNOWLEDGE.md`, `docs/VULNERABILITY_REGISTRY.md` | research standard | keep | Useful calibration/search docs and metadata references. | Keep as advanced reference. |
| `docs/LAUNCH_REPORT_OS.md`, `docs/DELIVERY_ARTIFACTS.md`, `docs/REPORT_DRAFTS.md`, `docs/REPORT_UX.md`, `docs/FIX_FIRST.md`, `docs/GENERATED_ISSUE_CHECKLIST.md`, `docs/GITHUB_ISSUE_WORKFLOW.md`, `docs/PR_COMMENT_MODE.md`, `docs/GITHUB_ACTION_USAGE.md`, `docs/CI_GATING.md`, `docs/BASELINE_DIFF_MODE.md`, `docs/SLITHER_INTEGRATION.md` | workflow | keep | Useful legacy/scanner/CI delivery docs; some are test or gate referenced. | Keep, update identity only where public-facing. |
| `docs/GITHUB_REPO_SURFACE.md`, `docs/STYLEGUIDE.md`, `docs/SAFETY_BOUNDARIES.md`, `docs/SECURITY.md`, `docs/ETHICS.md`, `docs/CONTRIBUTING.md`, `docs/STABILITY_CONTRACT.md`, `docs/PUBLIC_SURFACE.md` | canonical public | keep | Repo governance and public-surface controls; some are test-protected. | Keep; update only if required by README/public positioning. |
| `docs/READINESS_SCORE.md`, `docs/REAL_PROTOCOL_PROOF_PLAN.md`, `docs/INCIDENT_INTAKE.md`, `docs/VM_SUPPORT.md`, `docs/FOUNDRY_INTEGRATION.md`, `docs/GENERATED_ARTIFACT_IGNORE.md` | workflow | keep | Useful support docs; not canonical first path. | Keep as advanced reference. |
| `docs/V1_0_RELEASE_NOTES_DRAFT.md`, `docs/V3_READINESS.md` | historical version | keep | Historical and stale, but tests/scripts assert these exact paths. | Leave in place unless tests/scripts are migrated. |
| `docs/V4_INFORMATION_ARCHITECTURE.md`, `docs/V4_STABLE_SCOPE.md`, `docs/V4_1_RESEARCH_WORKFLOW.md`, `docs/V5_WORKFLOW.md`, `docs/V6_WORKFLOW.md`, `docs/V7_WORKFLOW.md`, `docs/V7_5_PROTOCOL_LENS.md` | historical version | archive | Version-specific workflow docs are not the public first-run path. | Move to `docs/archive/versions/` if links are updated. |
| `docs/V10_GODEYE_ARCHITECTURE.md`, `docs/V10_GODEYE_ARTIFACTS.md`, `docs/V10_GODEYE_BENCHMARK.md`, `docs/V10_1_AUTH_SIGNATURE_ENGINE.md`, `docs/V10_1_BOUNTY_REALITY_GATE.md`, `docs/V10_1_ROOT_CAUSE_FINGERPRINTS.md`, `docs/V10_1_UNIVERSAL_INGESTION.md` | internal/private | archive | Version/codename-heavy experimental docs are not public hero material. | Move to `docs/archive/versions/` or internal archive; describe as experimental/internal. |
| `docs/VALUE_FLOW_ROADMAP.md` | historical version | keep | Test-protected and used by version consistency checks. | Leave in place. |
| `docs/WEBSITE_DEPLOYMENT.md`, `docs/SITE_NGINX_NOTES.md`, `docs/SITE_VISUAL_QA.md` | internal/private | keep | Operational website docs; not public first path. | Keep as internal reference. |
| `docs/assets/*.svg` | artifacts/output | keep | Diagram assets used by existing docs. | Keep unless referenced docs are archived and assets become unused. |
| `docs/business/*.md` | internal/private | leave internal | Service/business docs are not the public documentation path. | Keep outside canonical path; do not promote from docs README. |
| `docs/ecosystem/*.md` | workflow | keep | Ecosystem readiness docs are useful but should not imply endorsement. | Keep; align claims if edited later. |
| `docs/internal/*.md` | internal/private | leave internal | Internal triage mode. | Keep internal. |
| `docs/private/*.md` | internal/private | leave internal | Private/internal hunter-mode docs. | Keep private; do not link from canonical docs. |
| `docs/launch/*.md` | launch/marketing | keep | Historical launch docs; `V0_8_LAUNCH_POSTS.md` is test-referenced. | Leave in place unless tests are migrated; exclude from canonical docs. |
| `docs/marketing/*.md` | launch/marketing | keep | Marketing/outreach docs; `BRAND.md` is test-referenced. | Keep but do not make first-run docs. |
| `docs/papers/*` | historical version | archive candidate | v4 paper is useful historical material but not current onboarding. | Leave for now or move under archive only with link updates. |
| `docs/releases/*.md`, `release-notes/*.md` | historical version | keep | Release history; useful but not canonical first path. | Keep in release/history area. |
| `docs/templates/POC_WRITEUP_TEMPLATE.md` | research standard | keep | Useful template. | Keep. |

## Archive Candidate Summary

Safe archive candidates for this session are files that are version-heavy, duplicate current canonical docs, not asserted by tests/scripts, and not required by the CLI:

- CLI history: `CLI_CANDIDATE.md`, `CLI_COMMANDS.md`, `CLI_INSTALLABLE.md`, `CLI_MIGRATION_TO_V2.md`, `CLI_ROADMAP.md`, `CLI_UX.md`.
- Version workflow history: `V4_INFORMATION_ARCHITECTURE.md`, `V4_STABLE_SCOPE.md`, `V4_1_RESEARCH_WORKFLOW.md`, `V5_WORKFLOW.md`, `V6_WORKFLOW.md`, `V7_WORKFLOW.md`, `V7_5_PROTOCOL_LENS.md`.
- Experimental/codename docs: `V10_GODEYE_*`, `V10_1_*`.

Hold in place because tests or scripts reference exact paths:

- `docs/V1_0_RELEASE_NOTES_DRAFT.md`
- `docs/V3_READINESS.md`
- `docs/VALUE_FLOW_ROADMAP.md`
- `docs/launch/V0_8_LAUNCH_POSTS.md`
- `docs/marketing/BRAND.md`
- `docs/PUBLIC_SURFACE.md`
- `docs/STABILITY_CONTRACT.md`
- `docs/GITHUB_ACTION_USAGE.md`
- `docs/GITHUB_REPO_SURFACE.md`

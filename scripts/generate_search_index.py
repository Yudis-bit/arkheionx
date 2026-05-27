#!/usr/bin/env python3
"""Generate the Arkheionx GitHub search index."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from arkheionx.rules.registry import RULE_PACKS  # noqa: E402

REGISTRY_PATH = REPO_ROOT / "metadata" / "registry.json"
SEARCH_TERMS_PATH = REPO_ROOT / "metadata" / "search_terms.json"
OUTPUT_PATH = REPO_ROOT / "reports" / "search_index.md"


STATIC_INDEX = [
    ("README landing page", "README.md", ["arkheionx", "value-flow workbench", "map the money flow"]),
    ("Value Flow Workbench", "docs/VALUE_FLOW_WORKBENCH.md", ["value flow", "money flow", "missing security tests"]),
    ("Value Flow Roadmap", "docs/VALUE_FLOW_ROADMAP.md", ["Value Flow Map MVP", "flow map", "DeFi Value Flow Workbench"]),
    ("Developer and researcher workflow", "docs/DEVELOPER_RESEARCHER_WORKFLOW.md", ["developer researcher workflow", "review map", "what you forgot to test"]),
    ("GitHub repository surface", "docs/GITHUB_REPO_SURFACE.md", ["GitHub repo surface", "value-flow workbench", "repository about"]),
    ("Changelog", "CHANGELOG.md", ["v2.0.1", "value-flow workbench", "release notes"]),
    ("CLI reference", "docs/CLI_REFERENCE.md", ["CLI reference", "stable flags", "planned flow commands"]),
    ("Pre-v2 CLI candidate", "docs/CLI_CANDIDATE.md", ["CLI candidate", "module CLI", "pre-v2 CLI"]),
    ("CLI commands", "docs/CLI_COMMANDS.md", ["arkheionx scan", "validate-config", "test-plan"]),
    ("CLI migration to v2", "docs/CLI_MIGRATION_TO_V2.md", ["CLI migration to v2", "command surface", "installable CLI"]),
    ("Installation", "docs/INSTALLATION.md", ["installable CLI", "editable install", "arkheionx command"]),
    ("CLI installable guide", "docs/CLI_INSTALLABLE.md", ["console entrypoint", "local package install", "v2 CLI"]),
    ("Packaging", "docs/PACKAGING.md", ["pyproject", "package metadata", "console script"]),
    ("Package data", "docs/PACKAGE_DATA.md", ["package data", "path resolution", "runtime data"]),
    ("Project package metadata", "pyproject.toml", ["pyproject", "arkheionx command", "console entrypoint"]),
    ("Schema reference", "docs/SCHEMA_REFERENCE.md", ["schema freeze", "JSON Schema", "stable outputs"]),
    ("Output artifacts", "docs/OUTPUT_ARTIFACTS.md", ["output naming", "generated artifacts", "reports directory"]),
    ("Report UX", "docs/REPORT_UX.md", ["report UX", "findings by rule family", "confidence summary"]),
    ("Output profiles", "docs/OUTPUT_PROFILES.md", ["output profile", "concise report", "CI report", "full report"]),
    ("Fix First", "docs/FIX_FIRST.md", ["fix first", "remediation priority", "top readiness blockers"]),
    ("Noise reduction", "docs/NOISE_REDUCTION.md", ["noise reduction", "suppressed findings", "keyword-only review"]),
    ("Invariant test plan generator", "docs/INVARIANT_TEST_PLAN_GENERATOR.md", ["invariant generator", "test plan generator", "suggested tests"]),
    ("Foundry invariant skeletons", "docs/FOUNDRY_INVARIANT_SKELETONS.md", ["Foundry invariant skeleton", "invariant candidates", "local scaffold"]),
    ("Invariant safety boundaries", "docs/INVARIANT_SAFETY_BOUNDARIES.md", ["invariant safety", "local-only skeletons", "human review"]),
    ("Internal engine split", "docs/INTERNAL_ENGINE_SPLIT.md", ["internal engine split", "package scaffold", "script compatibility"]),
    ("Package architecture", "docs/PACKAGE_ARCHITECTURE.md", ["package architecture", "arkheionx package", "core engine"]),
    ("CLI roadmap", "docs/CLI_ROADMAP.md", ["CLI roadmap", "installable CLI", "v2 package path"]),
    ("v1.0 release notes draft", "docs/V1_0_RELEASE_NOTES_DRAFT.md", ["v1.0.0", "release notes", "stable public release"]),
    ("Feedback loop", "docs/FEEDBACK_LOOP.md", ["feedback loop", "false positive report", "external calibration"]),
    ("Public feedback guide", "docs/PUBLIC_FEEDBACK_GUIDE.md", ["public feedback", "safe disclosure", "report quality"]),
    ("Feedback triage workflow", "docs/FEEDBACK_TRIAGE_WORKFLOW.md", ["feedback triage", "calibration status", "severity"]),
    ("Validation levels", "docs/VALIDATION_LEVELS.md", ["validation levels", "external evaluation", "allowed claims"]),
    ("Paid offer", "docs/business/PAID_OFFER.md", ["paid offer", "readiness support", "commercial positioning"]),
    ("Pricing ladder", "docs/business/PRICING_LADDER.md", ["pricing ladder", "pilot pricing", "service packages"]),
    ("Service packages", "docs/business/SERVICE_PACKAGES.md", ["service packages", "Readiness Snapshot", "Pre-Audit Sprint"]),
    ("Client intake", "docs/business/CLIENT_INTAKE.md", ["client intake", "authorized repository", "scope of work"]),
    ("Sample scope of work", "docs/business/SAMPLE_SCOPE_OF_WORK.md", ["scope of work", "proposal template", "not a formal audit"]),
    ("Sales FAQ", "docs/business/SALES_FAQ.md", ["sales FAQ", "paid readiness support", "no guarantees"]),
    ("Paid work boundaries", "docs/business/PAID_WORK_BOUNDARIES.md", ["paid work boundaries", "safety boundaries", "commercial"]),
    ("Ecosystem Pack", "docs/ecosystem/ECOSYSTEM_PACK.md", ["ecosystem pack", "ecosystem readiness", "multi-repo readiness"]),
    ("Multi-repo readiness workflow", "docs/ecosystem/MULTI_REPO_READINESS_WORKFLOW.md", ["multi-repo readiness", "authorized repositories", "local reports"]),
    ("Ecosystem intake", "docs/ecosystem/ECOSYSTEM_INTAKE.md", ["ecosystem intake", "authorization", "anonymization"]),
    ("Anonymized reporting", "docs/ecosystem/ANONYMIZED_REPORTING.md", ["anonymized reporting", "common gap report", "repo aliases"]),
    ("Ecosystem readiness pilot", "docs/ecosystem/ECOSYSTEM_READINESS_PILOT.md", ["readiness pilot", "ecosystem operator", "cohort readiness"]),
    ("Ecosystem readiness summary", "reports/ecosystem_readiness_summary.md", ["ecosystem readiness summary", "repo-by-repo readiness", "rule-family heatmap"]),
    ("Ecosystem common gaps", "reports/ecosystem_common_gaps.md", ["common gap report", "recurring findings", "anonymized recommendations"]),
    ("Ecosystem pilot metadata", "metadata/ecosystem_pilot_example.json", ["synthetic ecosystem pilot", "ecosystem data model", "repo aliases"]),
    ("Ecosystem report generator", "scripts/generate_ecosystem_report.py", ["ecosystem report generator", "check mode", "local static"]),
    ("Test plan generator", "scripts/generate_test_plan.py", ["test plan generator", "invariant generator", "check mode"]),
    ("Arkheionx package", "arkheionx/__init__.py", ["arkheionx package", "internal engine split", "package imports"]),
    ("Version module", "arkheionx/version.py", ["version module", "stable release", "current milestone"]),
    ("Rule registry module", "arkheionx/rules/registry.py", ["rule registry", "rule packs", "core engine"]),
    ("Generator modules", "arkheionx/generators/test_plan.py", ["generator modules", "test plan module", "package extraction"]),
    ("Services", "SERVICES.md", ["Launch Report", "Pre-Audit Sprint", "Contest Readiness Pack", "Ecosystem Pack"]),
    ("Pre-Audit Readiness OS", "docs/PRE_AUDIT_READINESS_OS.md", ["scanner", "readiness gap", "historical pattern similarity"]),
    ("GitHub Action usage", "docs/GITHUB_ACTION_USAGE.md", ["github-action", "SARIF", "baseline diff", "PR comment"]),
    ("PR comment mode", "docs/PR_COMMENT_MODE.md", ["pull-request", "comment marker", "GitHub token"]),
    ("Generated issue checklist", "docs/GENERATED_ISSUE_CHECKLIST.md", ["issue checklist", "remediation", "finding IDs"]),
    ("GitHub issue workflow", "docs/GITHUB_ISSUE_WORKFLOW.md", ["issue plan", "dry-run", "duplicate prevention"]),
    ("Arkheionx config", "docs/ARKHEIONX_CONFIG.md", ["config", "suppression", "ignore paths"]),
    ("Config reference", "docs/CONFIG_REFERENCE.md", ["config reference", "config validation", "output profile"]),
    ("Rule pack configuration", "docs/RULE_PACK_CONFIGURATION.md", ["rule pack configuration", "rule_packs", "min confidence"]),
    ("Suppressions", "docs/SUPPRESSIONS.md", ["suppressions", "suppression reason", "review_after"]),
    ("Config safety", "docs/CONFIG_SAFETY.md", ["config safety", "dangerous keys", "generated artifact ignore"]),
    ("Config validator", "scripts/validate_config.py", ["validate_config.py", "config validation", "strict audit prep config"]),
    ("Arkheionx config schema", "schemas/arkheionx_config.schema.json", ["arkheionx config schema", "schema_version 1.7.0", "CI config"]),
    ("Config examples", "examples/configs/minimal.config.json", ["minimal config", "CI config", "amm lending config"]),
    ("CI profile report", "examples/reports/ci-profile-report.md", ["CI report", "output profile", "Fix First"]),
    ("Full profile report", "examples/reports/full-profile-report.md", ["full report", "output profile", "detailed evidence"]),
    ("CLI AMM report", "examples/reports/cli-amm-report.md", ["CLI candidate", "arkheionx scan", "AMM report"]),
    ("CLI test plan", "examples/reports/cli-test-plan.md", ["arkheionx test-plan", "module CLI", "Foundry skeleton"]),
    ("Package CLI AMM report", "examples/reports/package-cli-amm-report.md", ["installable CLI", "arkheionx command", "AMM report"]),
    ("Package CLI test plan", "examples/reports/package-cli-test-plan.md", ["arkheionx test-plan", "console entrypoint", "Foundry skeleton"]),
    ("SARIF output", "docs/SARIF_OUTPUT.md", ["SARIF", "GitHub Code Scanning", "readiness gap"]),
    ("Baseline diff mode", "docs/BASELINE_DIFF_MODE.md", ["baseline", "diff mode", "new resolved unchanged"]),
    ("Semantic-lite analysis", "docs/SEMANTIC_LITE_ANALYSIS.md", ["semantic-lite", "Solidity structure extraction", "evidence"]),
    ("Slither integration", "docs/SLITHER_INTEGRATION.md", ["Slither", "Slither JSON", "local static analysis"]),
    ("False-positive reduction", "docs/FALSE_POSITIVE_REDUCTION.md", ["false positives", "confidence scoring", "keyword-only downgrade"]),
    ("Try in 5 minutes", "docs/TRY_IN_5_MINUTES.md", ["try Arkheionx in 5 minutes", "quick demo", "demo reports"]),
    ("Public demo workflow", "docs/PUBLIC_DEMO_WORKFLOW.md", ["public demo workflow", "demo GitHub Action workflow", "demo artifacts"]),
    ("Rule calibration", "docs/RULE_CALIBRATION.md", ["rule calibration", "false positive calibration", "confidence model"]),
    ("False-positive review workflow", "docs/FALSE_POSITIVE_REVIEW_WORKFLOW.md", ["false positive review", "calibration workflow", "downgrade logic"]),
    ("External validation", "docs/EXTERNAL_VALIDATION.md", ["external validation", "feedback workflow", "sanitized reports"]),
    ("Launch Report OS", "docs/LAUNCH_REPORT_OS.md", ["Launch Report", "client-ready report", "audit handoff package"]),
    ("Pre-Audit Sprint Workflow", "docs/PRE_AUDIT_SPRINT_WORKFLOW.md", ["Pre-Audit Sprint", "sprint plan", "remediation backlog"]),
    ("Contest Readiness Mode", "docs/CONTEST_READINESS_MODE.md", ["Contest Readiness", "scope checklist", "researcher onboarding"]),
    ("Delivery Artifacts", "docs/DELIVERY_ARTIFACTS.md", ["delivery artifacts", "executive summary", "remediation roadmap"]),
    ("CI gating", "docs/CI_GATING.md", ["fail threshold", "fail-score-below", "CI readiness gate"]),
    ("Readiness score", "docs/READINESS_SCORE.md", ["score bands", "audit blockers", "invariant testing"]),
    ("Vault Rule Pack", "docs/VAULT_RULE_PACK.md", ["ERC4626", "vault accounting", "share accounting"]),
    ("Rule Packs", "docs/RULE_PACKS.md", ["oracle rule pack", "access control", "reward accounting"]),
    ("Oracle Rule Pack", "docs/ORACLE_RULE_PACK.md", ["oracle", "stale price", "price bounds"]),
    ("Access Control Rule Pack", "docs/ACCESS_CONTROL_RULE_PACK.md", ["access control", "upgradeability", "initializer"]),
    ("Reentrancy Value Flow Rule Pack", "docs/REENTRANCY_VALUE_FLOW_RULE_PACK.md", ["reentrancy", "external calls", "claim flow"]),
    ("Reward Accounting Rule Pack", "docs/REWARD_ACCOUNTING_RULE_PACK.md", ["staking", "reward accounting", "accumulator"]),
    ("AMM Rule Pack", "docs/AMM_RULE_PACK.md", ["AMM rule pack", "AMM invariant", "LP share accounting", "slippage boundary"]),
    ("Lending Rule Pack", "docs/LENDING_RULE_PACK.md", ["lending rule pack", "collateral debt invariant", "liquidation boundary", "interest index"]),
    ("Indie builder offer", "docs/business/INDIE_BUILDER_OFFER.md", ["indie-defi", "launch preparation", "paid path"]),
    ("Search guide", "docs/SEARCH_GUIDE.md", ["search tags", "root-cause analysis", "broken invariant"]),
    ("Security Memory Graph", "docs/SECURITY_MEMORY_GRAPH.md", ["security memory graph", "finding knowledge map", "historical pattern similarity"]),
    ("Search Knowledge", "docs/SEARCH_KNOWLEDGE.md", ["search_knowledge.py", "oracle stale price", "local search helper"]),
    ("Finding Knowledge Map", "docs/FINDING_KNOWLEDGE_MAP.md", ["finding knowledge map", "suggested defensive tests", "failed assumptions"]),
    ("Marketing engine", "docs/marketing/MARKETING_ENGINE.md", ["growth", "positioning", "GitHub-only funnel"]),
    ("Monetization", "docs/business/MONETIZATION.md", ["sponsors", "revenue ladder", "services"]),
    ("Sponsorship", "docs/business/SPONSORSHIP.md", ["funding", "research sponsorship", "public work"]),
    ("Ethics", "docs/ETHICS.md", ["defensive-only", "authorized review", "no live targeting"]),
    ("Roadmap", "docs/ROADMAP.md", ["release roadmap", "rule packs", "GitHub-native"]),
    ("Oracle staking demo case study", "docs/case-studies/ORACLE_STAKING_FIXTURE_CASE_STUDY.md", ["oracle staking demo", "case study", "public demo"]),
    ("Oracle staking before/after case study", "docs/case-studies/ORACLE_STAKING_BEFORE_AFTER.md", ["before after case study", "fixed fixture", "remediation demo"]),
    ("Rule calibration summary", "reports/rule_calibration_summary.md", ["rule calibration", "common false positives", "downgrade logic"]),
    ("Feedback dashboard", "reports/feedback_dashboard.md", ["feedback dashboard", "synthetic feedback", "calibration"]),
    ("Rule calibration backlog report", "reports/rule_calibration_backlog.md", ["rule calibration backlog", "feedback status", "calibration work"]),
    ("Paid offer index", "reports/paid_offer_index.md", ["paid offer index", "pricing ladder", "service packages"]),
    ("Security memory graph report", "reports/security_memory_graph.md", ["security memory graph", "finding to pattern map", "historical PoC nodes"]),
    ("Security memory graph summary", "reports/security_memory_graph_summary.md", ["security memory graph", "mapped findings", "mapped patterns"]),
    ("Security memory graph JSON", "metadata/security_memory_graph.json", ["security memory graph", "nodes", "edges"]),
    ("Finding knowledge map JSON", "metadata/finding_knowledge_map.json", ["finding knowledge map", "related patterns", "suggested tests"]),
    ("Rule calibration matrix JSON", "metadata/rule_calibration_matrix.json", ["rule calibration matrix", "confidence requirements", "downgrade conditions"]),
    ("Finding test plan map JSON", "metadata/finding_test_plan_map.json", ["finding test plan map", "suggested tests", "invariant candidates"]),
    ("Feedback schema JSON", "metadata/feedback_schema.json", ["feedback schema", "feedback loop", "calibration"]),
    ("Feedback examples JSON", "metadata/feedback_examples.json", ["synthetic feedback", "feedback examples", "no adoption claims"]),
    ("Rule calibration backlog JSON", "metadata/rule_calibration_backlog.json", ["rule calibration backlog", "feedback dashboard", "calibration"]),
    ("Case study template", "templates/case_study_template.md", ["case study template", "before after", "readiness case study"]),
    ("v0.8 launch posts", "docs/launch/V0_8_LAUNCH_POSTS.md", ["launch post", "outreach kit", "public demo"]),
    ("Mini-vault fixture", "examples/mini-vault/README.md", ["vault", "fixture", "scanner demo"]),
    ("Vault-risk fixture", "examples/vault-risk-fixture/README.md", ["ERC4626", "strategy vault", "Vault Rule Pack"]),
    ("Oracle staking fixture", "examples/oracle-staking-fixture/README.md", ["oracle", "staking", "reward rule pack"]),
    ("Oracle staking fixed fixture", "examples/oracle-staking-fixture-fixed/README.md", ["oracle", "staking", "before after", "fixed fixture"]),
    ("Semantic-lite fixture", "examples/semantic-lite-fixture/README.md", ["semantic-lite", "false-positive reduction", "evidence"]),
    ("AMM fixture", "examples/amm-fixture/README.md", ["AMM fixture", "swap readiness", "liquidity pool"]),
    ("Lending fixture", "examples/lending-fixture/README.md", ["lending fixture", "borrow repay", "liquidation boundary"]),
    ("AMM Lending hybrid fixture", "examples/amm-lending-hybrid-fixture/README.md", ["hybrid fixture", "AMM price dependency", "lending health factor"]),
    ("Sample Markdown report", "examples/reports/mini-vault-pre-audit-report.md", ["readiness report", "vault", "example"]),
    ("Vault-risk Markdown report", "examples/reports/vault-risk-fixture-pre-audit-report.md", ["vault readiness", "ERC4626", "readiness gaps"]),
    ("Sample JSON report", "examples/reports/mini-vault-pre-audit-report.json", ["json-output", "automation", "example"]),
    ("Vault-risk JSON report", "examples/reports/vault-risk-fixture-pre-audit-report.json", ["vault_rule_pack", "json-output", "example"]),
    ("Mini-vault action summary", "examples/reports/mini-vault-action-summary.md", ["GitHub Actions summary", "score", "top gaps"]),
    ("Vault-risk PR comment", "examples/reports/vault-risk-fixture-pr-comment.md", ["PR comment", "marker", "top gaps"]),
    ("Vault-risk issue checklist", "examples/reports/vault-risk-fixture-issue-checklist.md", ["issue checklist", "readiness remediation", "finding IDs"]),
    ("Vault-risk issue plan", "examples/reports/vault-risk-fixture-issue-plan.json", ["issue plan", "remediation issue", "GitHub issue workflow"]),
    ("Oracle staking issue plan", "examples/reports/oracle-staking-fixture-issue-plan.json", ["oracle rule pack", "reward accounting", "issue plan"]),
    ("Oracle staking launch report", "examples/reports/oracle-staking-fixture-launch-report.md", ["Launch Report", "executive summary", "launch readiness"]),
    ("Oracle staking sprint plan", "examples/reports/oracle-staking-fixture-sprint-plan.md", ["Pre-Audit Sprint", "sprint checklist", "remediation plan"]),
    ("Oracle staking contest readiness", "examples/reports/oracle-staking-fixture-contest-readiness.md", ["Contest Readiness", "scope checklist", "researcher onboarding"]),
    ("Oracle staking remediation roadmap", "examples/reports/oracle-staking-fixture-remediation-roadmap.md", ["remediation roadmap", "launch blockers", "audit handoff"]),
    ("AMM fixture report", "examples/reports/amm-fixture-pre-audit-report.md", ["AMM report", "ARK-AMM", "readiness findings"]),
    ("AMM fixture SARIF", "examples/reports/amm-fixture.sarif.json", ["AMM SARIF", "ARK-AMM", "Code Scanning"]),
    ("AMM fixture test plan", "examples/reports/amm-fixture-test-plan.md", ["AMM test plan", "invariant candidates", "Foundry skeleton"]),
    ("AMM Foundry invariant skeleton", "examples/reports/ArkheionxAMMInvariants.t.sol", ["AMM invariant skeleton", "Foundry", "TODO assertions"]),
    ("Lending fixture report", "examples/reports/lending-fixture-pre-audit-report.md", ["lending report", "ARK-LEND", "readiness findings"]),
    ("Lending fixture SARIF", "examples/reports/lending-fixture.sarif.json", ["lending SARIF", "ARK-LEND", "Code Scanning"]),
    ("Lending fixture test plan", "examples/reports/lending-fixture-test-plan.md", ["lending test plan", "collateral debt invariant", "Foundry skeleton"]),
    ("Lending Foundry invariant skeleton", "examples/reports/ArkheionxLendingInvariants.t.sol", ["lending invariant skeleton", "Foundry", "liquidation boundary"]),
    ("AMM Lending hybrid report", "examples/reports/amm-lending-hybrid-fixture-pre-audit-report.md", ["hybrid report", "ARK-AMM", "ARK-LEND"]),
    ("AMM Lending hybrid test plan", "examples/reports/amm-lending-hybrid-fixture-test-plan.md", ["hybrid test plan", "AMM", "lending"]),
    ("Hybrid Foundry invariant skeleton", "examples/reports/ArkheionxHybridInvariants.t.sol", ["hybrid invariant skeleton", "AMM lending", "Foundry"]),
    ("Demo pre-audit report", "examples/reports/demo-pre-audit-report.md", ["public demo reports", "demo protocol", "readiness report"]),
    ("Demo launch report", "examples/reports/demo-launch-report.md", ["Launch Report", "public demo", "client-ready report"]),
    ("Demo contest readiness", "examples/reports/demo-contest-readiness.md", ["Contest Readiness", "scope checklist", "public demo"]),
    ("Demo issue plan", "examples/reports/demo-issue-plan.json", ["issue plan JSON", "demo artifact", "remediation"]),
    ("Oracle staking fixed report", "examples/reports/oracle-staking-fixture-fixed-pre-audit-report.md", ["before after case study", "fixed fixture", "readiness improvement"]),
    ("Vault-risk SARIF report", "examples/reports/vault-risk-fixture.sarif.json", ["SARIF", "Code Scanning", "readiness result"]),
    ("Vault-risk baseline", "examples/reports/vault-risk-fixture.baseline.json", ["baseline", "finding fingerprint", "readiness snapshot"]),
    ("Vault-risk diff report", "examples/reports/vault-risk-fixture-diff.md", ["baseline diff", "new resolved unchanged", "remediation tracking"]),
    ("Arkheionx config example", "examples/arkheionx.config.example.json", ["config", "suppression", "ignore paths"]),
    ("Pre-audit scanner", "scripts/pre_audit_scan.py", ["cli", "scanner", "standard-library"]),
    ("Module CLI main", "arkheionx/cli/main.py", ["module CLI", "pre-v2 CLI", "command surface"]),
    ("Module CLI commands", "arkheionx/cli/commands.py", ["arkheionx scan", "arkheionx search", "script compatibility"]),
    ("PR comment poster", "scripts/post_pr_comment.py", ["GitHub API", "PR comment", "marker update"]),
    ("GitHub issue creator", "scripts/create_github_issues.py", ["GitHub API", "issue plan", "dry-run"]),
    ("Knowledge graph generator", "scripts/generate_knowledge_graph.py", ["security memory graph", "knowledge graph", "check mode"]),
    ("Knowledge search helper", "scripts/search_knowledge.py", ["search knowledge", "oracle stale price", "local search"]),
    ("Feedback dashboard generator", "scripts/generate_feedback_dashboard.py", ["feedback dashboard", "rule calibration backlog", "check mode"]),
    ("Paid offer index generator", "scripts/generate_paid_offer_index.py", ["paid offer index", "paid offer catalog", "check mode"]),
    ("Docs link checker", "scripts/check_docs_links.py", ["docs link check", "release validation", "v1.0.0"]),
    ("Version consistency checker", "scripts/check_version_consistency.py", ["version consistency", "release validation", "v1.0.0"]),
    ("Safety wording checker", "scripts/check_safety_wording.py", ["safety wording", "release validation", "defensive"]),
    ("Make demo", "Makefile", ["make demo", "make validate", "try in 5 minutes"]),
    ("Pre-audit report schema", "schemas/pre-audit-report.schema.json", ["JSON schema", "pre-audit report", "schema freeze"]),
    ("Issue plan schema", "schemas/issue-plan.schema.json", ["JSON schema", "issue plan", "schema freeze"]),
    ("Baseline schema", "schemas/baseline.schema.json", ["JSON schema", "baseline", "schema freeze"]),
    ("Diff schema", "schemas/diff.schema.json", ["JSON schema", "diff", "schema freeze"]),
    ("Security memory graph schema", "schemas/security-memory-graph.schema.json", ["JSON schema", "security memory graph", "schema freeze"]),
    ("Finding knowledge map schema", "schemas/finding-knowledge-map.schema.json", ["JSON schema", "finding knowledge map", "schema freeze"]),
    ("Rule calibration matrix schema", "schemas/rule-calibration-matrix.schema.json", ["JSON schema", "rule calibration matrix", "schema freeze"]),
    ("Test plan schema", "schemas/test_plan.schema.json", ["JSON schema", "test plan", "invariant candidates"]),
    ("Report template", "templates/pre_audit_report.md", ["template", "Markdown report", "disclaimer"]),
    ("Invariant skeleton template", "templates/invariant_skeletons/ArkheionxReadinessInvariants.t.sol", ["Foundry", "invariant", "skeleton"]),
    ("AMM invariant skeleton template", "templates/invariant_skeletons/amm_invariants.sol", ["AMM", "Foundry", "invariant skeleton"]),
    ("Lending invariant skeleton template", "templates/invariant_skeletons/lending_invariants.sol", ["lending", "Foundry", "invariant skeleton"]),
    ("Hybrid invariant skeleton template", "templates/invariant_skeletons/hybrid_invariants.sol", ["hybrid", "Foundry", "invariant skeleton"]),
]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def render_registry_section() -> list[str]:
    registry = load_json(REGISTRY_PATH)
    entries = registry.get("entries", [])
    lines = ["## Historical Memory Index", ""]
    lines.append("Generated from `metadata/registry.json`.")
    lines.append("")
    lines.append("| ID | Protocol | Category | Severity | Tags | Path |")
    lines.append("|---|---|---|---|---|---|")
    for entry in sorted(entries, key=lambda item: item.get("date", "")):
        tags = ", ".join(entry.get("tags", [])[:8])
        lines.append(
            "| `{id}` | {protocol} | `{category}` | `{severity}` | {tags} | [`{path}`](../{path}) |".format(
                id=entry.get("id", ""),
                protocol=entry.get("protocol") or entry.get("title", ""),
                category=entry.get("category", ""),
                severity=entry.get("severity", ""),
                tags=tags or "-",
                path=entry.get("poc_path", ""),
            )
        )
    lines.append("")
    return lines


def render_search_terms_section() -> list[str]:
    terms = load_json(SEARCH_TERMS_PATH).get("topics", [])
    lines = ["## Search Term Index", ""]
    lines.append("| Term | Aliases | Category | Related checks | Tags |")
    lines.append("|---|---|---|---|---|")
    for item in terms:
        lines.append(
            "| `{term}` | {aliases} | {category} | {checks} | {tags} |".format(
                term=item["term"],
                aliases=", ".join(item.get("aliases", [])),
                category=item.get("category", ""),
                checks=", ".join(item.get("related_checks", [])),
                tags=", ".join(item.get("search_tags", [])),
            )
        )
    lines.append("")
    return lines


def render_rule_pack_registry_section() -> list[str]:
    lines = ["## Rule Pack Registry", ""]
    lines.append("Generated from `arkheionx.rules.registry.RULE_PACKS`.")
    lines.append("")
    lines.append("| Key | Rule pack | Prefix | Docs |")
    lines.append("|---|---|---|---|")
    for key, item in sorted(RULE_PACKS.items()):
        lines.append(
            "| `{key}` | {name} | `{prefix}` | [`{docs}`](../{docs}) |".format(
                key=key,
                name=item["display_name"],
                prefix=item["prefix"],
                docs=item["docs"],
            )
        )
    lines.append("")
    return lines


def render_static_section() -> list[str]:
    lines = ["## Product Surface Index", ""]
    lines.append("| Surface | Path | Search tags |")
    lines.append("|---|---|---|")
    for title, path, tags in STATIC_INDEX:
        lines.append(f"| {title} | [`{path}`](../{path}) | {', '.join(tags)} |")
    lines.append("")
    return lines


def render() -> str:
    lines: list[str] = [
        "# Arkheionx Search Index",
        "",
        "GitHub-searchable index for Arkheionx value flows, memory, tests, search, and advanced workflows.",
        "",
        "Use this page with GitHub search or local `rg` to find value flows,",
        "missing tests, exploit primitives, broken invariants, failed assumptions,",
        "readiness gaps, services, templates, examples, and reports.",
        "",
        "Current truth: 18 structured PoCs, 0 deterministic-confirmed L4+ entries,",
        "11 assertion-hardened entries, 7 strong static assertions, 4 medium",
        "static assertions, 7 weak static assertions, 18 not-run/no-RPC entries,",
        "EVM/Foundry active, SVM/Anchor and MoveVM/Aptos scaffold only.",
        "",
    ]
    lines.extend(render_static_section())
    lines.extend(render_search_terms_section())
    lines.extend(render_rule_pack_registry_section())
    lines.extend(render_registry_section())
    lines.extend(
        [
            "## High-Value Searches",
            "",
            "```text",
            "value flow",
            "money flow",
            "asset flow",
            "DeFi value flow",
            "value-flow workbench",
            "missing security tests",
            "flow map",
            "value flow roadmap",
            "developer researcher workflow",
            "review map",
            "map the money flow",
            "Foundry tells you if tests pass",
            "what you forgot to test",
            "Value Flow Map MVP",
            "where value moves",
            "vault accounting",
            "ERC4626",
            "totalAssets",
            "convertToShares",
            "convertToAssets",
            "share price manipulation",
            "share inflation",
            "donation risk class",
            "strategy accounting",
            "withdrawal queue",
            "fee accounting",
            "oracle-dependent vault",
            "vault invariant tests",
            "PR readiness comment",
            "generated issue checklist",
            "finding IDs",
            ".arkheionx.json",
            "SARIF",
            "GitHub Code Scanning",
            "baseline diff",
            "readiness baseline",
            "finding fingerprint",
            "CI gating",
            "fail threshold",
            "new readiness gaps",
            "resolved readiness gaps",
            "pre-audit diff",
            "GitHub security workflow",
            "GitHub issue workflow",
            "generated issue plan",
            "issue creation dry-run",
            "issue marker",
            "duplicate prevention",
            "readiness remediation",
            "oracle rule pack",
            "access control rule pack",
            "upgradeability rule pack",
            "reentrancy value flow rule pack",
            "reward accounting rule pack",
            "staking rule pack",
            "issue plan JSON",
            "semantic-lite analysis",
            "Solidity structure extraction",
            "false positive reduction",
            "evidence-based findings",
            "confidence scoring",
            "detection sources",
            "Slither integration",
            "Slither JSON",
            "test coverage mapping",
            "affected functions",
            "SARIF locations",
            "finding evidence",
            "low-confidence findings",
            "keyword-only downgrade",
            "Launch Report OS",
            "Launch Readiness Report",
            "Pre-Audit Sprint",
            "Contest Readiness Mode",
            "Contest Readiness Report",
            "remediation roadmap",
            "executive summary",
            "client-ready report",
            "audit handoff package",
            "researcher onboarding checklist",
            "scope checklist",
            "pre-contest readiness",
            "bug bounty readiness",
            "delivery artifacts",
            "try Arkheionx in 5 minutes",
            "public demo workflow",
            "demo protocol",
            "oracle staking demo",
            "before after case study",
            "external validation",
            "rule calibration",
            "false positive calibration",
            "false positive review workflow",
            "external validation feedback",
            "public demo reports",
            "case study template",
            "launch post",
            "outreach kit",
            "demo GitHub Action workflow",
            "reproducible readiness demo",
            "security memory graph",
            "finding knowledge map",
            "historical pattern similarity",
            "exploit primitive mapping",
            "broken invariant mapping",
            "failed assumption mapping",
            "suggested defensive tests",
            "rule calibration matrix",
            "oracle stale price",
            "Chainlink updatedAt",
            "heartbeat validation",
            "vault donation attack",
            "share accounting invariant",
            "reentrancy value flow",
            "callback capable token",
            "reward overclaim",
            "accumulator precision",
            "access control failure",
            "initializer protection",
            "upgrade authorization",
            "liquidation boundary",
            "AMM invariant",
            "cross chain replay",
            "contest readiness search",
            "launch report knowledge",
            "oracle manipulation",
            "flash loan price manipulation",
            "reentrancy",
            "access control",
            "initialization bug",
            "upgradeability",
            "reward accounting",
            "AMM invariant",
            "lending liquidation",
            "bridge validation",
            "historical exploit pattern",
            "pre-audit readiness",
            "indie DeFi",
            "audit blocker",
            "missing invariant",
            "Foundry invariant testing",
            "root-cause analysis",
            "feedback loop",
            "false positive report",
            "false negative report",
            "rule calibration backlog",
            "feedback dashboard",
            "external validation",
            "public feedback guide",
            "validation levels",
            "GitHub Action feedback",
            "report quality feedback",
            "GitHub repo surface",
            "repository about",
            "public surface polish",
            "security memory OS",
            "Arkheionx positioning",
            "paid offer",
            "readiness snapshot",
            "pre-audit sprint",
            "contest readiness pack",
            "GitHub Action setup",
            "paid work boundaries",
            "client intake",
            "scope of work",
            "pricing ladder",
            "commercial positioning",
            "proposal template",
            "ecosystem pack",
            "ecosystem readiness",
            "multi-repo readiness",
            "ecosystem intake",
            "anonymized reporting",
            "common gap report",
            "readiness pilot",
            "cohort readiness",
            "ecosystem operator",
            "repo-by-repo readiness",
            "ecosystem readiness summary",
            "invariant generator",
            "test plan generator",
            "Foundry invariant skeleton",
            "suggested tests",
            "invariant candidates",
            "AMM invariant skeleton",
            "lending invariant skeleton",
            "oracle test plan",
            "vault invariant",
            "liquidation boundary test",
            "collateral debt invariant",
            "reward index invariant",
            "internal engine split",
            "package architecture",
            "CLI roadmap",
            "arkheionx package",
            "core engine",
            "rule registry",
            "config reference",
            "config validation",
            "rule pack configuration",
            "suppressions",
            "min confidence",
            "output profile",
            "generated artifact ignore",
            "strict audit prep config",
            "CI config",
            "config safety",
            "generator modules",
            "installable CLI",
            "v2 package path",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Exit 1 if the index would change.")
    args = parser.parse_args()

    content = render()
    current = OUTPUT_PATH.read_text(encoding="utf-8") if OUTPUT_PATH.exists() else ""
    if current == content:
        print("ok: search index up to date")
        return 0
    if args.check:
        print(f"would update: {OUTPUT_PATH.relative_to(REPO_ROOT)}", file=sys.stderr)
        return 1
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(content, encoding="utf-8")
    print(f"updated: {OUTPUT_PATH.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

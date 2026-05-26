#!/usr/bin/env python3
"""Generate the Arkheionx GitHub search index."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = REPO_ROOT / "metadata" / "registry.json"
SEARCH_TERMS_PATH = REPO_ROOT / "metadata" / "search_terms.json"
OUTPUT_PATH = REPO_ROOT / "reports" / "search_index.md"


STATIC_INDEX = [
    ("README landing page", "README.md", ["arkheionx", "pre-audit-readiness", "security-memory"]),
    ("GitHub repository surface", "docs/GITHUB_REPO_SURFACE.md", ["GitHub repo surface", "repository about", "public surface polish"]),
    ("Changelog", "CHANGELOG.md", ["v1.0.0", "stable public release", "release notes"]),
    ("CLI reference", "docs/CLI_REFERENCE.md", ["CLI reference", "stable flags", "v1.0.0"]),
    ("Schema reference", "docs/SCHEMA_REFERENCE.md", ["schema freeze", "JSON Schema", "stable outputs"]),
    ("Output artifacts", "docs/OUTPUT_ARTIFACTS.md", ["output naming", "generated artifacts", "reports directory"]),
    ("v1.0 release notes draft", "docs/V1_0_RELEASE_NOTES_DRAFT.md", ["v1.0.0", "release notes", "stable public release"]),
    ("Feedback loop", "docs/FEEDBACK_LOOP.md", ["feedback loop", "false positive report", "external calibration"]),
    ("Public feedback guide", "docs/PUBLIC_FEEDBACK_GUIDE.md", ["public feedback", "safe disclosure", "report quality"]),
    ("Feedback triage workflow", "docs/FEEDBACK_TRIAGE_WORKFLOW.md", ["feedback triage", "calibration status", "severity"]),
    ("Validation levels", "docs/VALIDATION_LEVELS.md", ["validation levels", "external evaluation", "allowed claims"]),
    ("Services", "SERVICES.md", ["Launch Report", "Pre-Audit Sprint", "Contest Readiness Pack", "Ecosystem Pack"]),
    ("Pre-Audit Readiness OS", "docs/PRE_AUDIT_READINESS_OS.md", ["scanner", "readiness gap", "historical pattern similarity"]),
    ("GitHub Action usage", "docs/GITHUB_ACTION_USAGE.md", ["github-action", "SARIF", "baseline diff", "PR comment"]),
    ("PR comment mode", "docs/PR_COMMENT_MODE.md", ["pull-request", "comment marker", "GitHub token"]),
    ("Generated issue checklist", "docs/GENERATED_ISSUE_CHECKLIST.md", ["issue checklist", "remediation", "finding IDs"]),
    ("GitHub issue workflow", "docs/GITHUB_ISSUE_WORKFLOW.md", ["issue plan", "dry-run", "duplicate prevention"]),
    ("Arkheionx config", "docs/ARKHEIONX_CONFIG.md", ["config", "suppression", "ignore paths"]),
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
    ("Security memory graph report", "reports/security_memory_graph.md", ["security memory graph", "finding to pattern map", "historical PoC nodes"]),
    ("Security memory graph summary", "reports/security_memory_graph_summary.md", ["security memory graph", "mapped findings", "mapped patterns"]),
    ("Security memory graph JSON", "metadata/security_memory_graph.json", ["security memory graph", "nodes", "edges"]),
    ("Finding knowledge map JSON", "metadata/finding_knowledge_map.json", ["finding knowledge map", "related patterns", "suggested tests"]),
    ("Rule calibration matrix JSON", "metadata/rule_calibration_matrix.json", ["rule calibration matrix", "confidence requirements", "downgrade conditions"]),
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
    ("PR comment poster", "scripts/post_pr_comment.py", ["GitHub API", "PR comment", "marker update"]),
    ("GitHub issue creator", "scripts/create_github_issues.py", ["GitHub API", "issue plan", "dry-run"]),
    ("Knowledge graph generator", "scripts/generate_knowledge_graph.py", ["security memory graph", "knowledge graph", "check mode"]),
    ("Knowledge search helper", "scripts/search_knowledge.py", ["search knowledge", "oracle stale price", "local search"]),
    ("Feedback dashboard generator", "scripts/generate_feedback_dashboard.py", ["feedback dashboard", "rule calibration backlog", "check mode"]),
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
    ("Report template", "templates/pre_audit_report.md", ["template", "Markdown report", "disclaimer"]),
    ("Invariant skeleton template", "templates/invariant_skeletons/ArkheionxReadinessInvariants.t.sol", ["Foundry", "invariant", "skeleton"]),
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
        "GitHub-searchable index for Arkheionx Memory, Readiness, Tests, Search, and Market.",
        "",
        "Use this page with GitHub search or local `rg` to find exploit primitives,",
        "broken invariants, failed assumptions, readiness gaps, services, templates,",
        "examples, and reports.",
        "",
        "Current truth: 18 structured PoCs, 0 deterministic-confirmed L4+ entries,",
        "EVM/Foundry active, SVM/Anchor and MoveVM/Aptos scaffold only.",
        "",
    ]
    lines.extend(render_static_section())
    lines.extend(render_search_terms_section())
    lines.extend(render_registry_section())
    lines.extend(
        [
            "## High-Value Searches",
            "",
            "```text",
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

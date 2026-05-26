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
    ("Changelog", "CHANGELOG.md", ["v0.6.0", "semantic-lite", "false-positive reduction", "release notes"]),
    ("Services", "SERVICES.md", ["Launch Report", "Pre-Audit Sprint", "Ecosystem Pack"]),
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
    ("CI gating", "docs/CI_GATING.md", ["fail threshold", "fail-score-below", "CI readiness gate"]),
    ("Readiness score", "docs/READINESS_SCORE.md", ["score bands", "audit blockers", "invariant testing"]),
    ("Vault Rule Pack", "docs/VAULT_RULE_PACK.md", ["ERC4626", "vault accounting", "share accounting"]),
    ("Rule Packs", "docs/RULE_PACKS.md", ["oracle rule pack", "access control", "reward accounting"]),
    ("Oracle Rule Pack", "docs/ORACLE_RULE_PACK.md", ["oracle", "stale price", "price bounds"]),
    ("Access Control Rule Pack", "docs/ACCESS_CONTROL_RULE_PACK.md", ["access control", "upgradeability", "initializer"]),
    ("Reentrancy Value Flow Rule Pack", "docs/REENTRANCY_VALUE_FLOW_RULE_PACK.md", ["reentrancy", "external calls", "claim flow"]),
    ("Reward Accounting Rule Pack", "docs/REWARD_ACCOUNTING_RULE_PACK.md", ["staking", "reward accounting", "accumulator"]),
    ("Indie builder offer", "docs/INDIE_BUILDER_OFFER.md", ["indie-defi", "launch preparation", "paid path"]),
    ("Search guide", "docs/SEARCH_GUIDE.md", ["search tags", "root-cause analysis", "broken invariant"]),
    ("Marketing engine", "docs/MARKETING_ENGINE.md", ["growth", "positioning", "GitHub-only funnel"]),
    ("Monetization", "docs/MONETIZATION.md", ["sponsors", "revenue ladder", "services"]),
    ("Sponsorship", "docs/SPONSORSHIP.md", ["funding", "research sponsorship", "public work"]),
    ("Ethics", "docs/ETHICS.md", ["defensive-only", "authorized review", "no live targeting"]),
    ("Roadmap", "docs/ROADMAP.md", ["release roadmap", "rule packs", "GitHub-native"]),
    ("Mini-vault fixture", "examples/mini-vault/README.md", ["vault", "fixture", "scanner demo"]),
    ("Vault-risk fixture", "examples/vault-risk-fixture/README.md", ["ERC4626", "strategy vault", "Vault Rule Pack"]),
    ("Oracle staking fixture", "examples/oracle-staking-fixture/README.md", ["oracle", "staking", "reward rule pack"]),
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
    ("Vault-risk SARIF report", "examples/reports/vault-risk-fixture.sarif.json", ["SARIF", "Code Scanning", "readiness result"]),
    ("Vault-risk baseline", "examples/reports/vault-risk-fixture.baseline.json", ["baseline", "finding fingerprint", "readiness snapshot"]),
    ("Vault-risk diff report", "examples/reports/vault-risk-fixture-diff.md", ["baseline diff", "new resolved unchanged", "remediation tracking"]),
    ("Arkheionx config example", "examples/arkheionx.config.example.json", ["config", "suppression", "ignore paths"]),
    ("Pre-audit scanner", "scripts/pre_audit_scan.py", ["cli", "scanner", "standard-library"]),
    ("PR comment poster", "scripts/post_pr_comment.py", ["GitHub API", "PR comment", "marker update"]),
    ("GitHub issue creator", "scripts/create_github_issues.py", ["GitHub API", "issue plan", "dry-run"]),
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

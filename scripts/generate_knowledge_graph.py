#!/usr/bin/env python3
"""Generate the local Arkheionx security memory graph.

The graph is intentionally lightweight and deterministic:
- local metadata only;
- no network, RPC, or live target access;
- historical pattern mapping for defensive readiness explanations only.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = REPO_ROOT / "metadata" / "registry.json"
FINDING_MAP_PATH = REPO_ROOT / "metadata" / "finding_knowledge_map.json"
CALIBRATION_PATH = REPO_ROOT / "metadata" / "rule_calibration_matrix.json"
GRAPH_PATH = REPO_ROOT / "metadata" / "security_memory_graph.json"
MARKDOWN_PATH = REPO_ROOT / "reports" / "security_memory_graph.md"
SUMMARY_PATH = REPO_ROOT / "reports" / "security_memory_graph_summary.md"


PATTERN_TITLES = {
    "pattern-vault-accounting-drift": "Vault accounting drift or share/asset mismatch",
    "pattern-share-inflation-donation": "Vault share inflation or donation sensitivity",
    "pattern-pool-price-accounting": "Pool price or external balance used as accounting truth",
    "pattern-oracle-stale-price": "Oracle stale price or freshness assumption failure",
    "pattern-spot-price-manipulation": "Spot or reserve price manipulation risk class",
    "pattern-precision-rounding-loss": "Precision, rounding, or normalization failure",
    "pattern-unprotected-initializer": "Initializer or privileged setup boundary failure",
    "pattern-privileged-operation-boundary": "Privileged operation boundary failure",
    "pattern-upgrade-authorization-gap": "Upgrade authorization or storage assumption gap",
    "pattern-external-call-before-state-update": "External call before state update",
    "pattern-callback-capable-token": "Callback-capable token or receiver assumption failure",
    "pattern-reward-overclaim": "Reward overclaim or emission accounting mismatch",
    "pattern-accounting-index-drift": "Accounting index or accumulator drift",
    "pattern-missing-invariant-coverage": "Critical assumption not encoded as invariant",
    "pattern-assumption-not-encoded-in-tests": "Failed assumption not represented in tests",
    "pattern-undocumented-trust-assumption": "Undocumented trust or operational assumption",
    "pattern-scope-ambiguity": "External review scope ambiguity",
    "pattern-amm-invariant-steering": "AMM invariant steering or liquidity manipulation",
    "pattern-collateral-debt-invariant": "Collateral and debt invariant failure",
    "pattern-cross-chain-message-validation": "Cross-chain message validation failure",
    "pattern-replay-or-source-assumption": "Replay or trusted-source assumption failure",
}

DELIVERY_ARTIFACTS = {
    "artifact-pre-audit-report": "Pre-Audit Readiness Report",
    "artifact-sarif": "SARIF Code Scanning-compatible readiness output",
    "artifact-issue-plan": "GitHub issue plan",
    "artifact-launch-report": "Launch Readiness Report",
    "artifact-contest-readiness": "Contest Readiness Report",
    "artifact-remediation-roadmap": "Remediation Roadmap",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def add_node(nodes: dict[str, dict[str, object]], node_id: str, node_type: str, title: str, **extra: object) -> None:
    current = nodes.setdefault(node_id, {"id": node_id, "type": node_type, "title": title})
    current.update({key: value for key, value in extra.items() if value not in (None, [], {})})


def add_edge(edges: list[dict[str, object]], source: str, target: str, relation: str, reason: str) -> None:
    edge = {"from": source, "to": target, "relation": relation, "reason": reason}
    if edge not in edges:
        edges.append(edge)


def normalize_poc_id(value: str) -> str:
    return value if value.startswith("poc-") else f"poc-{value}"


def poc_registry_id(value: str) -> str:
    return value.removeprefix("poc-")


def tags_from_text(*values: object) -> list[str]:
    tags: set[str] = set()
    for value in values:
        if isinstance(value, list):
            for item in value:
                tags.update(tags_from_text(item))
            continue
        for token in str(value).replace("_", "-").replace("/", "-").split():
            token = token.strip("`.,:;()[]{}").lower()
            if len(token) >= 3:
                tags.add(token)
    return sorted(tags)[:12]


def build_graph() -> dict[str, object]:
    registry = load_json(REGISTRY_PATH)
    finding_map = load_json(FINDING_MAP_PATH)
    calibration = load_json(CALIBRATION_PATH)
    findings = finding_map.get("findings", {})
    nodes: dict[str, dict[str, object]] = {}
    edges: list[dict[str, object]] = []

    add_node(
        nodes,
        "arkheionx-security-memory",
        "doc",
        "Arkheionx Security Memory Graph",
        path="docs/SECURITY_MEMORY_GRAPH.md",
        tags=["security-memory", "pre-audit-readiness", "local-static-analysis"],
    )
    add_node(
        nodes,
        "rule-calibration-matrix",
        "doc",
        "Arkheionx Rule Calibration Matrix",
        path="metadata/rule_calibration_matrix.json",
        tags=["rule-calibration", "confidence-scoring", "false-positive-reduction"],
    )

    for artifact_id, title in DELIVERY_ARTIFACTS.items():
        add_node(nodes, artifact_id, "delivery_artifact", title, tags=["delivery-artifact", "readiness-output"])

    for family in calibration.get("families", []):
        pack = str(family.get("rule_pack", "generic"))
        pack_id = f"rule-pack-{pack.replace('_', '-')}"
        add_node(
            nodes,
            pack_id,
            "rule_pack",
            pack.replace("_", " ").title(),
            finding_family=family.get("finding_family", ""),
            tags=[pack, "rule-pack", "calibration"],
        )
        add_edge(edges, pack_id, "arkheionx-security-memory", "documented_in", "Rule pack calibration is part of the local security memory graph.")
        add_edge(edges, "rule-calibration-matrix", pack_id, "calibrates_rule", "The calibration matrix documents confidence and downgrade logic for this rule pack.")

    registry_by_id = {entry.get("id", ""): entry for entry in registry.get("entries", [])}
    for registry_id, entry in sorted(registry_by_id.items()):
        poc_id = normalize_poc_id(registry_id)
        add_node(
            nodes,
            poc_id,
            "poc",
            str(entry.get("title", registry_id)),
            registry_id=registry_id,
            category=entry.get("category", ""),
            severity=entry.get("severity", ""),
            path=entry.get("poc_path", ""),
            tags=entry.get("tags", []) or tags_from_text(entry.get("category", ""), entry.get("root_cause", "")),
        )
        root_id = f"root-cause-{registry_id}"
        add_node(nodes, root_id, "root_cause", str(entry.get("root_cause", "Root cause not documented"))[:160], registry_id=registry_id)
        add_edge(edges, poc_id, root_id, "has_root_cause", "Registry metadata records the historical root cause.")
        invariant = entry.get("invariant_broken")
        if invariant:
            invariant_id = f"broken-invariant-{registry_id}"
            add_node(nodes, invariant_id, "broken_invariant", str(invariant), registry_id=registry_id)
            add_edge(edges, poc_id, invariant_id, "has_broken_invariant", "Registry metadata records the invariant broken in the historical case.")
        primitive = entry.get("exploit_primitive")
        if primitive:
            primitive_id = f"primitive-{registry_id}"
            add_node(nodes, primitive_id, "exploit_primitive", str(primitive), registry_id=registry_id)
            add_edge(edges, poc_id, primitive_id, "has_root_cause", "The primitive is stored as historical memory for defensive review.")

    for finding_id, data in sorted(findings.items()):
        pack = str(data.get("rule_pack", "generic"))
        pack_id = f"rule-pack-{pack.replace('_', '-')}"
        add_node(
            nodes,
            finding_id,
            "finding",
            str(data.get("title", finding_id)),
            rule_pack=pack,
            category=data.get("category", ""),
            tags=data.get("search_terms", [])[:8],
        )
        add_edge(edges, finding_id, pack_id, "belongs_to_rule_pack", "Finding ID belongs to this Arkheionx rule pack.")
        for artifact_id in DELIVERY_ARTIFACTS:
            add_edge(edges, finding_id, artifact_id, "supports_delivery_artifact", "Readiness findings can be surfaced in delivery artifacts when generated.")
        for pattern_id in data.get("historical_patterns", []):
            add_node(
                nodes,
                pattern_id,
                "historical_pattern",
                PATTERN_TITLES.get(pattern_id, pattern_id.replace("-", " ").title()),
                tags=tags_from_text(pattern_id, data.get("search_terms", [])),
            )
            add_edge(edges, finding_id, pattern_id, "maps_to_pattern", "The finding maps to this historical readiness pattern for defensive explanation.")
        for root in data.get("root_causes", []):
            root_id = f"root-cause-{root}"
            add_node(nodes, root_id, "root_cause", root.replace("-", " ").title(), tags=tags_from_text(root))
            add_edge(edges, finding_id, root_id, "has_root_cause", "The readiness finding is calibrated against this root-cause class.")
        for assumption in data.get("failed_assumptions", []):
            assumption_id = f"failed-assumption-{assumption}"
            add_node(nodes, assumption_id, "failed_assumption", assumption.replace("-", " ").title(), tags=tags_from_text(assumption))
            add_edge(edges, finding_id, assumption_id, "has_failed_assumption", "The finding asks maintainers to validate this assumption defensively.")
        for invariant in data.get("broken_invariants", []):
            invariant_id = f"broken-invariant-{invariant}"
            add_node(nodes, invariant_id, "broken_invariant", invariant.replace("-", " ").title(), tags=tags_from_text(invariant))
            add_edge(edges, finding_id, invariant_id, "has_broken_invariant", "The suggested review should encode or document this invariant.")
        for test in data.get("suggested_tests", []):
            test_id = f"test-{test}"
            add_node(nodes, test_id, "suggested_test", test.replace("-", " ").title(), tags=tags_from_text(test))
            add_edge(edges, finding_id, test_id, "has_suggested_test", "This test is defensive remediation guidance for the readiness finding.")
        for doc in data.get("related_docs", []):
            doc_id = f"doc-{doc}"
            add_node(nodes, doc_id, "doc", doc, path=doc, tags=["documentation"])
            add_edge(edges, finding_id, doc_id, "documented_in", "Related documentation explains the finding family or workflow.")
        for poc in data.get("related_pocs", []):
            poc_id = normalize_poc_id(str(poc))
            add_node(nodes, poc_id, "poc", registry_by_id.get(poc_registry_id(poc_id), {}).get("title", poc_id), registry_id=poc_registry_id(poc_id))
            add_edge(edges, finding_id, poc_id, "historical_example", "Historical PoC metadata provides defensive context for this readiness pattern.")
            for pattern_id in data.get("historical_patterns", [])[:2]:
                add_edge(edges, pattern_id, poc_id, "historical_example", "The PoC is a historical example for this pattern family.")

    graph = {
        "schema_version": "1.0.0",
        "generated_at": "deterministic-local",
        "description": "Local Arkheionx security memory graph connecting historical exploit patterns, PoCs, rule packs, readiness findings, and suggested defensive tests.",
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes": [nodes[key] for key in sorted(nodes)],
        "edges": sorted(edges, key=lambda edge: (edge["from"], edge["relation"], edge["to"])),
    }
    return graph


def render_markdown(graph: dict[str, object]) -> str:
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    by_type: dict[str, list[dict[str, object]]] = {}
    for node in nodes:
        if isinstance(node, dict):
            by_type.setdefault(str(node.get("type", "unknown")), []).append(node)

    lines = [
        "# Arkheionx Security Memory Graph",
        "",
        "This repository-native graph connects readiness findings to historical",
        "pattern classes, root causes, failed assumptions, broken invariants,",
        "suggested defensive tests, docs, and delivery artifacts.",
        "",
        "This is local/static security memory. It is not a formal audit, not a",
        "vulnerability confirmation, and not proof that a scanned repository has",
        "the same issue as any historical PoC.",
        "",
        f"- Schema version: `{graph.get('schema_version')}`",
        f"- Nodes: `{graph.get('node_count')}`",
        f"- Edges: `{graph.get('edge_count')}`",
        "",
        "## Node Counts",
        "",
        "| Type | Count |",
        "|---|---:|",
    ]
    for node_type in sorted(by_type):
        lines.append(f"| `{node_type}` | {len(by_type[node_type])} |")
    lines.extend(["", "## Finding To Pattern Map", "", "| Finding | Rule Pack | Historical Patterns | Suggested Tests |", "|---|---|---|---|"])
    finding_nodes = [node for node in nodes if isinstance(node, dict) and node.get("type") == "finding"]
    edge_lookup: dict[str, dict[str, list[str]]] = {}
    title_lookup = {str(node.get("id")): str(node.get("title")) for node in nodes if isinstance(node, dict)}
    for edge in edges:
        if not isinstance(edge, dict):
            continue
        edge_lookup.setdefault(str(edge.get("from")), {}).setdefault(str(edge.get("relation")), []).append(str(edge.get("to")))
    for node in sorted(finding_nodes, key=lambda item: str(item.get("id"))):
        node_id = str(node.get("id"))
        patterns = [title_lookup.get(item, item) for item in edge_lookup.get(node_id, {}).get("maps_to_pattern", [])[:4]]
        tests = [title_lookup.get(item, item) for item in edge_lookup.get(node_id, {}).get("has_suggested_test", [])[:4]]
        lines.append(f"| `{node_id}` {node.get('title')} | `{node.get('rule_pack', '')}` | {', '.join(patterns) or '-'} | {', '.join(tests) or '-'} |")
    lines.extend(["", "## Historical PoC Nodes", "", "| PoC | Category | Path |", "|---|---|---|"])
    for node in sorted(by_type.get("poc", []), key=lambda item: str(item.get("id"))):
        lines.append(f"| `{node.get('id')}` {node.get('title')} | `{node.get('category', '')}` | `{node.get('path', '')}` |")
    lines.extend(["", "## How To Search", "", "```sh", "python3 scripts/search_knowledge.py \"oracle stale price\"", "python3 scripts/search_knowledge.py \"vault accounting invariant\"", "python3 scripts/search_knowledge.py \"missing invariant\" --json", "```", ""])
    return "\n".join(lines)


def render_summary(graph: dict[str, object]) -> str:
    nodes = graph.get("nodes", [])
    findings = [node for node in nodes if isinstance(node, dict) and node.get("type") == "finding"]
    patterns = [node for node in nodes if isinstance(node, dict) and node.get("type") == "historical_pattern"]
    pocs = [node for node in nodes if isinstance(node, dict) and node.get("type") == "poc"]
    lines = [
        "# Security Memory Graph Summary",
        "",
        f"- Findings mapped: `{len(findings)}`",
        f"- Historical patterns mapped: `{len(patterns)}`",
        f"- PoC nodes mapped: `{len(pocs)}`",
        f"- Total edges: `{graph.get('edge_count')}`",
        "",
        "This summary is generated from local metadata and is intended for search,",
        "calibration, and defensive readiness explanation.",
        "",
    ]
    return "\n".join(lines)


def write_outputs(graph: dict[str, object]) -> None:
    GRAPH_PATH.parent.mkdir(parents=True, exist_ok=True)
    MARKDOWN_PATH.parent.mkdir(parents=True, exist_ok=True)
    GRAPH_PATH.write_text(json.dumps(graph, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MARKDOWN_PATH.write_text(render_markdown(graph), encoding="utf-8")
    SUMMARY_PATH.write_text(render_summary(graph), encoding="utf-8")


def check_outputs(graph: dict[str, object]) -> int:
    expected_graph = json.dumps(graph, indent=2, sort_keys=True) + "\n"
    expected_markdown = render_markdown(graph)
    expected_summary = render_summary(graph)
    stale = []
    comparisons = [
        (GRAPH_PATH, expected_graph),
        (MARKDOWN_PATH, expected_markdown),
        (SUMMARY_PATH, expected_summary),
    ]
    for path, expected in comparisons:
        if not path.exists() or path.read_text(encoding="utf-8") != expected:
            stale.append(path.as_posix())
    if stale:
        print("stale generated knowledge graph outputs:", ", ".join(stale), file=sys.stderr)
        return 1
    print("ok: security memory graph up to date")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate Arkheionx security memory graph outputs.")
    parser.add_argument("--check", action="store_true", help="Fail if generated graph outputs are stale.")
    args = parser.parse_args(argv)
    graph = build_graph()
    if args.check:
        return check_outputs(graph)
    write_outputs(graph)
    print(f"Arkheionx security memory graph generated: {GRAPH_PATH}")
    print(f"Arkheionx security memory graph Markdown generated: {MARKDOWN_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

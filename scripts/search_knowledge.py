#!/usr/bin/env python3
"""Search the local Arkheionx security memory graph.

This helper is local-only and reads repository metadata. It does not call
external services, RPC endpoints, or GitHub APIs.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
GRAPH_PATH = REPO_ROOT / "metadata" / "security_memory_graph.json"
FINDING_MAP_PATH = REPO_ROOT / "metadata" / "finding_knowledge_map.json"
SEARCH_TERMS_PATH = REPO_ROOT / "metadata" / "search_terms.json"
SEARCH_INDEX_PATH = REPO_ROOT / "reports" / "search_index.md"


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def tokens(value: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9][a-z0-9-]{1,}", value.lower().replace("_", "-"))
        if len(token) >= 2
    }


def flatten(value: object) -> str:
    if isinstance(value, dict):
        return " ".join(f"{key} {flatten(item)}" for key, item in value.items())
    if isinstance(value, list):
        return " ".join(flatten(item) for item in value)
    return str(value)


def collect_documents() -> list[dict[str, object]]:
    graph = load_json(GRAPH_PATH)
    finding_map = load_json(FINDING_MAP_PATH).get("findings", {})
    search_terms = load_json(SEARCH_TERMS_PATH).get("topics", [])
    documents: list[dict[str, object]] = []

    title_lookup = {
        str(node.get("id")): str(node.get("title", node.get("id")))
        for node in graph.get("nodes", [])
        if isinstance(node, dict)
    }
    related_by_source: dict[str, dict[str, list[str]]] = {}
    for edge in graph.get("edges", []):
        if not isinstance(edge, dict):
            continue
        related_by_source.setdefault(str(edge.get("from")), {}).setdefault(str(edge.get("relation")), []).append(str(edge.get("to")))

    for node in graph.get("nodes", []):
        if not isinstance(node, dict):
            continue
        node_id = str(node.get("id", ""))
        relations = related_by_source.get(node_id, {})
        documents.append(
            {
                "id": node_id,
                "type": node.get("type", "unknown"),
                "title": node.get("title", node_id),
                "body": flatten(node),
                "rule_pack": node.get("rule_pack", ""),
                "relations": relations,
                "related_titles": {
                    relation: [title_lookup.get(item, item) for item in targets]
                    for relation, targets in relations.items()
                },
            }
        )

    for finding_id, data in finding_map.items():
        relations = {
            "maps_to_pattern": data.get("historical_patterns", []),
            "historical_example": data.get("related_pocs", []),
            "has_suggested_test": data.get("suggested_tests", []),
            "documented_in": data.get("related_docs", []),
        }
        existing = next((item for item in documents if item.get("id") == finding_id), None)
        if existing:
            existing["body"] = f"{existing.get('body', '')} {flatten(data)}"
            existing["knowledge"] = data
            existing["rule_pack"] = data.get("rule_pack", existing.get("rule_pack", ""))
            merged = existing.setdefault("relations", {})
            if isinstance(merged, dict):
                for relation, targets in relations.items():
                    merged.setdefault(relation, [])
                    if isinstance(merged[relation], list):
                        merged[relation].extend(target for target in targets if target not in merged[relation])
            continue
        documents.append(
            {
                "id": finding_id,
                "type": "finding",
                "title": data.get("title", finding_id),
                "body": flatten(data),
                "rule_pack": data.get("rule_pack", ""),
                "relations": relations,
                "related_titles": {},
                "knowledge": data,
            }
        )

    for item in search_terms:
        term = item.get("term", "")
        documents.append(
            {
                "id": f"search-term:{term}",
                "type": "doc",
                "title": term,
                "body": flatten(item),
                "rule_pack": "",
                "relations": {},
                "related_titles": {},
            }
        )

    if SEARCH_INDEX_PATH.exists():
        documents.append(
            {
                "id": "reports/search_index.md",
                "type": "doc",
                "title": "Arkheionx Search Index",
                "body": SEARCH_INDEX_PATH.read_text(encoding="utf-8", errors="ignore"),
                "rule_pack": "",
                "relations": {},
                "related_titles": {},
            }
        )
    return documents


def score_document(query_tokens: set[str], phrase: str, document: dict[str, object]) -> int:
    haystack = f"{document.get('id', '')} {document.get('title', '')} {document.get('body', '')}".lower()
    doc_tokens = tokens(haystack)
    score = len(query_tokens & doc_tokens) * 5
    if phrase and phrase.lower() in haystack:
        score += 12
    for token in query_tokens:
        if str(document.get("id", "")).lower().find(token) >= 0:
            score += 4
        if str(document.get("title", "")).lower().find(token) >= 0:
            score += 3
    return score


def search(query: str, limit: int, node_type: str) -> list[dict[str, object]]:
    query_tokens = tokens(query)
    documents = collect_documents()
    matches = []
    for document in documents:
        if node_type != "all" and document.get("type") != node_type:
            continue
        score = score_document(query_tokens, query, document)
        if score <= 0:
            continue
        result = {
            "id": document.get("id"),
            "type": document.get("type"),
            "title": document.get("title"),
            "score": score,
            "rule_pack": document.get("rule_pack", ""),
            "relations": document.get("relations", {}),
            "related_titles": document.get("related_titles", {}),
            "knowledge": document.get("knowledge", {}),
        }
        matches.append(result)
    matches.sort(key=lambda item: (-int(item["score"]), str(item["type"]), str(item["id"])))
    return matches[:limit]


def render_text(query: str, matches: list[dict[str, object]]) -> str:
    lines = [f"Query: {query}", "", "Top matches:"]
    if not matches:
        lines.append("- No local knowledge matches found.")
        return "\n".join(lines)
    for index, item in enumerate(matches, 1):
        lines.append(f"{index}. {item['id']} - {item['title']}")
        lines.append(f"   Type: {item['type']}")
        if item.get("rule_pack"):
            lines.append(f"   Rule pack: {item['rule_pack']}")
        knowledge = item.get("knowledge") if isinstance(item.get("knowledge"), dict) else {}
        if knowledge:
            patterns = knowledge.get("historical_patterns", [])[:4]
            tests = knowledge.get("suggested_tests", [])[:4]
            pocs = knowledge.get("related_pocs", [])[:4]
            docs = knowledge.get("related_docs", [])[:4]
            if patterns:
                lines.append("   Historical patterns:")
                for pattern in patterns:
                    lines.append(f"   - {pattern}")
            if tests:
                lines.append("   Suggested tests:")
                for test in tests:
                    lines.append(f"   - {test}")
            if pocs:
                lines.append("   Related PoCs:")
                for poc in pocs:
                    lines.append(f"   - {poc}")
            if docs:
                lines.append("   Docs:")
                for doc in docs:
                    lines.append(f"   - {doc}")
        else:
            related_titles = item.get("related_titles") if isinstance(item.get("related_titles"), dict) else {}
            for relation, targets in related_titles.items():
                if targets:
                    lines.append(f"   {relation}: {', '.join(str(target) for target in targets[:4])}")
        lines.append("")
    return "\n".join(lines).rstrip()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Search the local Arkheionx security memory graph.")
    parser.add_argument("query", help="Search query, for example: oracle stale price")
    parser.add_argument("--json", action="store_true", help="Output JSON.")
    parser.add_argument("--limit", type=int, default=10, help="Maximum matches to return.")
    parser.add_argument("--type", choices=["finding", "historical_pattern", "poc", "doc", "rule_pack", "suggested_test", "all"], default="all", help="Filter by node type.")
    args = parser.parse_args(argv)
    matches = search(args.query, max(1, args.limit), args.type)
    if args.json:
        print(json.dumps({"query": args.query, "matches": matches}, indent=2, sort_keys=True))
    else:
        print(render_text(args.query, matches))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

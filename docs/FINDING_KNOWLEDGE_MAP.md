# Finding Knowledge Map

`metadata/finding_knowledge_map.json` maps Arkheionx readiness finding IDs to
historical pattern categories, root causes, failed assumptions, broken
invariants, suggested defensive tests, related PoCs, related docs, and search
terms.

## Why This Exists

Finding IDs are more useful when maintainers can answer:

- What historical pattern does this resemble?
- Which assumption should be tested or documented?
- Which invariant should be encoded?
- Which rule pack owns the finding?
- Which docs explain the finding?

The map turns scanner output into searchable security memory without requiring
a database or external service.

## Maintainer Update Rules

When adding or changing a mapping:

1. Keep language defensive and readiness-oriented.
2. Use historical examples as context, not vulnerability confirmation.
3. Prefer suggested tests over exploit steps.
4. Link only committed local docs and registry IDs.
5. Run:

```sh
python3 scripts/generate_knowledge_graph.py
python3 scripts/generate_knowledge_graph.py --check
python3 scripts/search_knowledge.py "oracle stale price"
python3 scripts/search_knowledge.py "AMM invariant"
python3 scripts/search_knowledge.py "liquidation boundary"
```

## Mapping Fields

- `title`
- `rule_pack`
- `category`
- `historical_patterns`
- `root_causes`
- `failed_assumptions`
- `broken_invariants`
- `suggested_tests`
- `related_pocs`
- `related_docs`
- `search_terms`

## Safety Boundary

This map does not confirm vulnerabilities and does not prove safety. It helps
maintainers explain and prioritize defensive pre-audit readiness work.

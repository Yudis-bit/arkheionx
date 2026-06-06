# Security Memory Graph

Arkheionx v0.9.0 adds a local security memory graph that connects readiness
findings to historical pattern classes, root causes, failed assumptions,
broken invariants, suggested defensive tests, docs, and delivery artifacts.

This graph is repository-native JSON and Markdown. It is not a graph database,
does not call external services, and does not inspect live deployments.

## Why It Exists

Security reviews often lose context between historical incidents and current
pre-audit work. The Arkheionx graph makes that context searchable:

Historical PoC -> exploit primitive -> root cause -> failed assumption ->
broken invariant -> readiness finding ID -> rule pack -> suggested test ->
delivery artifact -> search term.

## Generated Files

- `metadata/security_memory_graph.json`
- `metadata/finding_knowledge_map.json`
- `metadata/rule_calibration_matrix.json`
- `reports/security_memory_graph.md`
- `reports/security_memory_graph_summary.md`

Regenerate locally:

```sh
python3 scripts/generate_knowledge_graph.py
python3 scripts/generate_knowledge_graph.py --check
```

## Node Types

- `finding`: Arkheionx readiness finding ID such as `ARK-ORC-001`.
- `rule_pack`: rule family such as oracle, vault, access control, or reward
  accounting.
- `historical_pattern`: defensive category inspired by historical exploit
  memory.
- `root_cause`: recurring reason a failure class appears.
- `failed_assumption`: assumption that should be tested or documented.
- `broken_invariant`: invariant that historical failures violated.
- `suggested_test`: defensive local test idea.
- `poc`: historical PoC metadata node from `metadata/registry.json`.
- `doc`: local documentation reference.
- `delivery_artifact`: report or workflow output that can surface the finding.

## Edge Types

- `maps_to_pattern`
- `belongs_to_rule_pack`
- `has_suggested_test`
- `has_root_cause`
- `has_failed_assumption`
- `has_broken_invariant`
- `historical_example`
- `documented_in`
- `supports_delivery_artifact`
- `calibrates_rule`

## How To Use It

Search locally:

```sh
python3 scripts/search_knowledge.py "oracle stale price"
python3 scripts/search_knowledge.py "vault accounting invariant"
python3 scripts/search_knowledge.py "AMM invariant"
python3 scripts/search_knowledge.py "liquidation boundary"
python3 scripts/search_knowledge.py "missing invariant" --json
```

Use the results to understand which finding IDs, rule packs, suggested tests,
docs, and historical categories are related to a readiness gap.

For remediation planning, pair this graph with
`metadata/finding_test_plan_map.json` and `scripts/generate_test_plan.py`.

## What It Does Not Prove

- It does not confirm a vulnerability.
- It does not prove a repository is safe.
- It does not mean a scanned repository has the same issue as a historical
  PoC.
- It does not replace manual review or a formal audit.

The graph is defensive context for authorized, local/static pre-audit
readiness work.

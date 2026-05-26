# Search Knowledge

`scripts/search_knowledge.py` searches the local Arkheionx security memory
graph, finding knowledge map, search metadata, and generated search index.

It is local-only. It does not call RPC, GitHub, or external search services.

## Examples

```sh
python3 scripts/search_knowledge.py "oracle stale price"
python3 scripts/search_knowledge.py "vault accounting invariant"
python3 scripts/search_knowledge.py "reentrancy value flow"
python3 scripts/search_knowledge.py "missing invariant"
```

JSON output:

```sh
python3 scripts/search_knowledge.py "oracle stale price" --json
```

Limit results:

```sh
python3 scripts/search_knowledge.py "reward overclaim" --limit 5
```

Filter by node type:

```sh
python3 scripts/search_knowledge.py "oracle" --type finding
python3 scripts/search_knowledge.py "Yearn" --type poc
```

## What Results Mean

Results may include:

- readiness finding IDs;
- related rule packs;
- historical pattern categories;
- related historical PoC metadata;
- suggested defensive tests;
- related docs.

Historical similarity is educational readiness context. It does not imply the
scanned repository has the same vulnerability.

## Useful Queries

| Query | Use When |
|---|---|
| `oracle stale price` | Checking oracle freshness assumptions. |
| `vault accounting invariant` | Checking share/accounting readiness. |
| `reentrancy value flow` | Reviewing withdraw, claim, refund, or transfer paths. |
| `reward overclaim` | Reviewing staking or reward accounting. |
| `missing invariant` | Planning property tests before audit. |
| `initializer protection` | Reviewing upgradeability or initialization paths. |

Search can help interpret negative evidence too. For example, if a scan reports
`missing invariant tests` as negative evidence, `python3 scripts/search_knowledge.py
"missing invariant"` points to related findings, suggested defensive tests, and
readiness docs. Search results remain educational context, not vulnerability
confirmation.

## Limitations

Search is token-based and local. It is meant for fast navigation and
explanation, not semantic code search or vulnerability confirmation.

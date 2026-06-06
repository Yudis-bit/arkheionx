# Search Knowledge

`scripts/search_knowledge.py` searches the local Arkheionx security memory
graph, finding knowledge map, search metadata, and generated search index.

It is local-only. It does not call RPC, GitHub, or external search services.

## Examples

```sh
python3 scripts/search_knowledge.py "oracle stale price"
python3 scripts/search_knowledge.py "vault accounting invariant"
python3 scripts/search_knowledge.py "AMM invariant"
python3 scripts/search_knowledge.py "collateral debt invariant"
python3 scripts/search_knowledge.py "reentrancy value flow"
python3 scripts/search_knowledge.py "missing invariant"
python3 scripts/search_knowledge.py "fix first"
python3 scripts/search_knowledge.py "output profile"
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
| `AMM invariant` | Reviewing swaps, reserves, and liquidity pool accounting. |
| `LP share accounting` | Reviewing liquidity mint/burn and low-liquidity behavior. |
| `liquidation boundary` | Reviewing lending liquidation thresholds and close factors. |
| `interest index` | Reviewing borrow index and accrual readiness. |
| `missing invariant` | Planning property tests before audit. |
| `invariant generator` | Finding the v1.5 test-plan generator. |
| `Foundry invariant skeleton` | Finding local skeleton docs and examples. |
| `fix first` | Finding v1.8 remediation-priority report guidance. |
| `output profile` | Finding concise, standard, full, and CI report profile docs. |
| `noise reduction` | Finding confidence grouping and suppression UX docs. |
| `initializer protection` | Reviewing upgradeability or initialization paths. |

Search can help interpret negative evidence too. For example, if a scan reports
`missing invariant tests` as negative evidence, `python3 scripts/search_knowledge.py
"missing invariant"` points to related findings, suggested defensive tests, and
readiness docs. Search results remain educational context, not vulnerability
confirmation.

## Limitations

Search is token-based and local. It is meant for fast navigation and
explanation, not semantic code search or vulnerability confirmation.

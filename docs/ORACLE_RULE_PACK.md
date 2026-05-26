# Oracle Rule Pack

The Oracle Rule Pack helps builders identify readiness gaps around price feeds,
TWAP/spot assumptions, stale rounds, decimals, bounds, and oracle update paths.

This is local/static readiness analysis. It is not a formal audit and does not
confirm exploitability.

## Signals

- `oracle`, `priceFeed`, `getPrice`, `latestRoundData`, `latestAnswer`
- `roundId`, `answeredInRound`, `updatedAt`, `decimals`
- `AggregatorV3Interface`, `Chainlink`, `consult`, `twap`, `spot`
- `getReserves`, `sqrtPriceX96`, `observe`, `reserve0`, `reserve1`
- `stale`, `heartbeat`, `minPrice`, `maxPrice`, `bounds`, `fallbackOracle`

## Readiness Findings

- `ARK-ORC-001`: Oracle-dependent logic without stale-price tests.
- `ARK-ORC-002`: Oracle decimals or normalization not covered by tests.
- `ARK-ORC-003`: Spot or reserve-based pricing without manipulation-resistance tests.
- `ARK-ORC-004`: Oracle setter/admin path without role-boundary tests.
- `ARK-ORC-005`: Missing price bounds or fallback assumptions documentation.

## Suggested Defensive Tests

- stale round rejection,
- decimals normalization,
- min/max price bounds,
- TWAP versus spot behavior,
- fallback oracle behavior,
- oracle update access control,
- sequencer downtime assumptions for L2 deployments.

## Limitations

The rule pack is heuristic. It cannot prove oracle safety, liquidity depth,
manipulation resistance, or integration correctness. Use findings to guide
review and formal audit preparation.

## Related Security Memory

- Finding IDs: `ARK-ORC-001`, `ARK-ORC-002`, `ARK-ORC-003`, `ARK-ORC-004`, `ARK-ORC-005`
- Historical patterns: oracle stale price, spot or reserve price manipulation,
  pool-price accounting assumptions.
- Suggested searches:

```sh
python3 scripts/search_knowledge.py "oracle stale price"
python3 scripts/search_knowledge.py "Chainlink updatedAt"
python3 scripts/search_knowledge.py "spot price manipulation"
```

Use these results as defensive test inspiration, not vulnerability
confirmation.

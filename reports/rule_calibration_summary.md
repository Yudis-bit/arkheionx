# Arkheionx Rule Calibration Summary

This summary describes current rule-pack calibration for local/static
pre-audit readiness findings.

Arkheionx findings are readiness prompts, not formal audit findings or
confirmed vulnerabilities.

| Rule Pack | Signal Sources | High-Confidence Requirements | Common False Positives | Downgrade Logic | Suggested Improvements |
|---|---|---|---|---|---|
| Vault | ERC4626-like functions, totalAssets, share conversion, fees, strategy terms | Source-level vault functions plus missing invariant/roundtrip tests | Docs mentioning shares or vaults without vault code | Downgrade docs-only or test-only signals | More function-level accounting relation extraction |
| Oracle | latestRoundData, getReserves, observe, getPrice, bounds terms | Source-level oracle call plus missing stale/bounds/decimals tests | README references to oracle integrations | Downgrade keyword-only docs signals | Better mapping between mock oracle tests and source functions |
| Access / Upgradeability | onlyOwner, roles, setters, pause, initializer, upgradeTo | Public/external privileged function plus missing negative tests | Owner variables in harmless fixtures | Downgrade if role-boundary tests exist | Detect timelock/multisig docs more accurately |
| Reentrancy / Value Flow | transfer, call, claim, refund, withdraw, callbacks | External value-flow call in user flow plus no guard/order tests | Transfer terms in tests or docs | Downgrade if nonReentrant/order evidence exists | Improve state-write-before-call evidence |
| Reward / Staking | stake, claim, rewardPerToken, accumulator, emissions | Reward/index functions plus missing conservation/no-overclaim tests | Reward terms in docs only | Downgrade when conservation tests are visible | Better multi-user lifecycle detection |
| Test Readiness | test files, invariant/fuzz names, assertion terms | Protocol-like source shape plus no property/invariant evidence | Tiny demo fixtures | Keep as readiness reminder, not vulnerability claim | Add protocol-specific test coverage maps |
| Documentation | README/docs scope, roles, oracle assumptions, known limitations | Missing docs for detected privileged/oracle/accounting complexity | Private docs outside scanned repo | Keep visible with explicit limitation notes | Config support for external documentation paths |

## Calibration Review Process

1. Inspect finding evidence and confidence reason.
2. Check whether semantic-lite found source-level context.
3. Check whether tests contain matching defensive terms.
4. Decide whether to downgrade, suppress locally, or update the rule.
5. Add or update fixture coverage and tests.

## Current Limitations

- Semantic-lite extraction is heuristic.
- Slither is optional.
- No full Solidity call graph exists yet.
- False positives remain possible.
- Manual review is still required.

## v0.9.0 Matrix Outputs

Machine-readable calibration now lives in:

- `metadata/rule_calibration_matrix.json`
- `metadata/finding_knowledge_map.json`
- `metadata/security_memory_graph.json`

Each major family documents high-confidence requirements, medium-confidence
requirements, low-confidence conditions, downgrade conditions, common false
positives, and recommended manual review prompts.

Search examples:

```sh
python3 scripts/search_knowledge.py "oracle stale price"
python3 scripts/search_knowledge.py "vault donation attack"
python3 scripts/search_knowledge.py "reward overclaim"
```

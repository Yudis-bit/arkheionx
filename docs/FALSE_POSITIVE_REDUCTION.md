# False-Positive Reduction

Arkheionx v0.6.0 focuses on better signal quality. The goal is not to hide
readiness gaps; it is to separate stronger evidence from weak keyword-only
matches so indie builders can prioritize real pre-audit work.

## Confidence Levels

| Confidence | Meaning |
|---|---|
| `high` | Solidity function-level evidence exists and matching test coverage was not detected. |
| `medium` | Solidity evidence exists, but some related test coverage or mitigating signal was found. |
| `low` | Keyword-only or weak contextual signal. Manual review recommended before creating remediation tasks. |

Confidence is not a vulnerability verdict. It is a prioritization aid.

## Keyword-Only Downgrades

When `downgrade_keyword_only` is enabled, Arkheionx avoids high-priority
findings from weak text-only matches. For example, a README that says
"oracle/reward planning" should not produce the same confidence as Solidity
code that calls `latestRoundData()` and lacks stale-price test evidence.

Low-confidence findings remain visible in Markdown and JSON. They can be
excluded from issue plans by setting `min_confidence_for_issue_plan`.

## Test Coverage Mapping

Semantic-lite maps tests to rule-pack themes:

- oracle: stale price, decimals, bounds, TWAP, spot pricing;
- access control: unauthorized caller, owner, role, admin, revert tests;
- reentrancy/value flow: reentrant receiver, callback, double claim;
- reward accounting: multi-user reward conservation, accumulator, precision;
- vault: deposit, withdraw, redeem, donation, rounding, totalAssets, preview.

Matching tests can reduce priority or confidence because Arkheionx has evidence
that the team is already reviewing that assumption.

## Config Tuning

```json
{
  "analysis": {
    "semantic_lite": true,
    "slither": false,
    "min_confidence_for_issue_plan": "medium",
    "downgrade_keyword_only": true,
    "max_evidence_per_finding": 5
  }
}
```

Suppression is still available by finding ID, but suppression is not proof of
safety. Prefer improving tests or documentation when possible.

## Limits

False positives remain possible. Arkheionx does not compile Solidity, build a
complete call graph, or prove whether a readiness gap is exploitable. Use the
output to focus defensive review and prepare for professional review.

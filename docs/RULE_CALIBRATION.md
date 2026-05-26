# Rule Calibration

Rule calibration is the process of making Arkheionx findings more useful:
high-signal when evidence is strong, lower priority when evidence is weak, and
transparent when manual review is required.

Arkheionx findings are readiness signals. They are not formal audit findings
and do not confirm vulnerabilities.

## Why Calibration Matters

Indie DeFi teams need practical guidance, not noisy alarm lists. Calibration
helps:

- reduce weak keyword-only findings;
- explain why a finding exists;
- attach affected files and functions;
- show when tests appear to cover a risk class;
- preserve useful low-confidence prompts without overstating them.

## Confidence Model

| Confidence | Typical Evidence |
|---|---|
| High | Semantic-lite code evidence plus missing/weak matching tests, or repeated aligned evidence across rule pack signals. |
| Medium | Function-level or source-file evidence with partial test/documentation context. |
| Low | Keyword-only or documentation-only signal without strong source context. |

## Evidence Sources

- `semantic-lite`: local Solidity structure and function evidence.
- `test-coverage`: local test names and body terms.
- `slither`: optional local Slither JSON or run output.
- `keyword`: repository text signals.
- `documentation`: docs and README context.
- `config`: local suppressions and tuning.

## Downgrade Logic

Arkheionx should usually downgrade when:

- a term appears only in docs, comments, or README;
- a signal appears in tests but not source;
- matching defensive test terms are present;
- semantic-lite cannot find affected functions;
- a finding would be better treated as a documentation reminder.

## Rule Pack Calibration Notes

| Rule Pack | High-Confidence Evidence | Common False Positives |
|---|---|---|
| Vault | `deposit`, `withdraw`, `totalAssets`, share conversion functions, and no invariant/roundtrip tests. | Docs mentioning shares without vault code. |
| Oracle | `latestRoundData`, `getReserves`, `observe`, or price functions without stale/bounds tests. | README mentions oracle integrations without source usage. |
| Access / Upgradeability | Public/external setters, role functions, initializer/upgrade functions without negative tests. | Owner variables in examples or docs only. |
| Reentrancy / Value Flow | External calls or token transfers in withdraw/claim/refund-like flows without ordering/guard evidence. | Generic `transfer` terms in tests or docs. |
| Reward / Staking | `stake`, `claim`, `rewardPerToken`, accumulator/index logic without conservation tests. | Reward terms in marketing docs or comments. |
| Test Readiness | Protocol-like source signals without invariant/fuzz/property test evidence. | Tiny fixtures that intentionally omit tests. |
| Documentation | Missing role/oracle/scope assumptions in docs. | Private docs outside the scanned repository. |

## False-Positive Review

When a report is noisy:

1. Check the finding ID and evidence section.
2. Confirm whether semantic-lite found source-level evidence.
3. Check whether matching tests or docs exist under ignored paths.
4. Decide whether to suppress locally, downgrade globally, or improve the rule.
5. Open a false-positive calibration issue with sanitized context.

See [`FALSE_POSITIVE_REVIEW_WORKFLOW.md`](FALSE_POSITIVE_REVIEW_WORKFLOW.md).

## Maintainer Review Rules

- Prefer reducing priority over deleting useful prompts.
- Never hide suppressed findings silently.
- Do not add rules that require RPC or live targets.
- Keep language defensive and evidence-based.
- Update examples and tests when calibration changes.

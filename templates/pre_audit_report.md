# Arkheionx Pre-Audit Readiness Report

## Scope

- Repository root: `{{ repo_root }}`
- Generated at: `{{ generated_at }}`
- Protocol type: `{{ protocol_type }}`
- Protocol confidence: `{{ protocol_confidence }}`
- Files scanned: `{{ files_scanned }}`
- Scanner version: `{{ scanner_version }}`

## Disclaimer

This is an automated pre-audit readiness report. It is not a formal audit. It
does not prove the absence or presence of vulnerabilities. It does not
authorize live-target testing. Use only on repositories you own or are
authorized to review. A formal audit is recommended before handling real user
funds.

## Executive Summary

- Readiness score: `{{ readiness_score }}/100`
- Score band: `{{ score_band }}`
- Top readiness gaps:
  - `{{ readiness_gap_1 }}`
  - `{{ readiness_gap_2 }}`
  - `{{ readiness_gap_3 }}`
- Top recommended actions:
  - `{{ next_action_1 }}`
  - `{{ next_action_2 }}`
  - `{{ next_action_3 }}`

## Detected Protocol Shape

- Detected protocol type: `{{ protocol_type }}`
- Confidence: `{{ protocol_confidence }}`
- Signal summary: `{{ signal_summary }}`

## Readiness Score Breakdown

| Category | Score | Max | Notes |
|---|---:|---:|---|
| Repository structure | `{{ repository_structure_score }}` | 15 | `{{ repository_structure_notes }}` |
| Test presence | `{{ test_presence_score }}` | 20 | `{{ test_presence_notes }}` |
| Invariant/fuzz readiness | `{{ invariant_fuzz_score }}` | 20 | `{{ invariant_fuzz_notes }}` |
| DeFi risk coverage | `{{ defi_risk_score }}` | 20 | `{{ defi_risk_notes }}` |
| Documentation readiness | `{{ documentation_score }}` | 10 | `{{ documentation_notes }}` |
| Operational/admin readiness | `{{ operational_score }}` | 15 | `{{ operational_notes }}` |

## Historical Exploit-Pattern Similarity

For each pattern, use risk-signal language only:

- Pattern name: `{{ pattern_name }}`
- Confidence: `{{ confidence }}`
- Detected signals: `{{ detected_signals }}`
- Why it matters: `{{ why_it_matters }}`
- Failed assumption class: `{{ failed_assumption_class }}`
- Broken invariant class: `{{ broken_invariant_class }}`
- Recommended defensive checks: `{{ defensive_checks }}`
- Suggested test/invariant: `{{ suggested_test }}`
- Search tags: `{{ search_tags }}`

## Missing Invariant And Test Coverage

- `{{ missing_invariant_or_test_coverage }}`

## Suggested Foundry Invariant Skeletons

- Generated skeleton path: `{{ invariant_skeleton_path }}`
- To generate locally: `python3 scripts/pre_audit_scan.py --root . --generate-invariant-skeletons`

## Audit Readiness Checklist

- [ ] Core user flows have deterministic tests.
- [ ] Accounting, oracle, reward, and role assumptions are documented.
- [ ] Invariant tests cover value conservation and access boundaries.
- [ ] Fuzz tests cover edge cases, rounding, and unexpected user sequences.
- [ ] Privileged roles, upgrade controls, and emergency controls are documented and tested.
- [ ] Known limitations are written down for auditors.
- [ ] A formal audit scope names contracts, commit hash, assumptions, and out-of-scope areas.

## Search Tags

`arkheionx`, `pre-audit-readiness`, `indie-defi`, `defi-security`,
`smart-contract-security`, `solidity-security`, `foundry`,
`invariant-testing`, `oracle-risk`, `vault-accounting`,
`reentrancy-review`, `access-control-review`, `historical-exploit-pattern`,
`root-cause-analysis`, `audit-preparation`

## What This Report Does Not Prove

- It does not prove protocol safety.
- It does not confirm exploitability.
- It does not replace manual review.
- It does not replace a formal audit.

## Formal Audit Recommendation

Run a formal smart contract audit before mainnet deployment, before material
TVL, or before handling real user funds.

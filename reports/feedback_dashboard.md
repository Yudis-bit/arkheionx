# Arkheionx Feedback Dashboard

This dashboard is generated from local metadata. Current entries are
synthetic/internal unless a public source and permission are explicitly
recorded.

Arkheionx does not claim customers, adoption, production use, or broad
external validation from synthetic examples.

## Feedback Summary

| Metric | Value |
| --- | --- |
| Feedback examples | 4 |
| Calibration backlog entries | 7 |
| Rule calibration families | 11 |
| Public external feedback with permission | 0 |
| Synthetic/internal examples | 4 |

## Feedback By Status

| Status | Count |
| --- | --- |
| documented | 1 |
| fixed | 2 |
| received | 1 |

## Backlog By Status

| Status | Count |
| --- | --- |
| accepted-calibration | 1 |
| deferred | 2 |
| fixed | 2 |
| needs-reproduction | 1 |
| received | 1 |

## Synthetic/Internal Feedback

| ID | Type | Findings | Status | Summary |
| --- | --- | --- | --- | --- |
| FB-SYN-001 | false_positive | ARK-TST-002 | fixed | A comment saying missing invariant tests should not count as positive invariant coverage. |
| FB-SYN-002 | false_positive | ARK-ACC-001, ARK-REENT-001 | fixed | Generated Arkheionx reports inside reports/ should not become source evidence on repeat scans. |
| FB-SYN-003 | report_quality | - | received | Builders need clearer distinction between readiness signals, evidence, and suggested next actions. |
| FB-SYN-004 | external_evaluation | ARK-ORC-001, ARK-RWD-001 | documented | Toy oracle/staking fixture feedback remains internal demo evidence and must not be described as external adoption. |

## External Feedback With Public Permission

| ID | Source | Repo Type | Permission | Summary |
| --- | --- | --- | --- | --- |
| - | - | - | - | None recorded |

## External Feedback Without Public Permission

| ID | Repo Type | Status | Notes |
| --- | --- | --- | --- |
| - | - | - | None recorded |

## Calibration Backlog

See [`rule_calibration_backlog.md`](rule_calibration_backlog.md).

## Safety Notes

- Do not store secrets, private keys, mnemonics, or RPC credentials.
- Do not publish unpatched vulnerability details.
- Do not describe synthetic/internal examples as external adoption.
- Use public validation claims only when permission and evidence are committed.

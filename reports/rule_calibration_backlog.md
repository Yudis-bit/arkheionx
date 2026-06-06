# Arkheionx Rule Calibration Backlog

Generated from `metadata/rule_calibration_backlog.json`.

Initial entries are synthetic/internal and exist to track calibration
work without claiming customers, adoption, or production validation.

| ID | Priority | Status | Rule Family | Title | Target |
| --- | --- | --- | --- | --- | --- |
| CAL-001 | P0 | fixed | testing | Negative-context coverage detection | v0.9.1 |
| CAL-002 | P0 | fixed | scan-source-accounting | Generated artifact self-ingestion guard | v0.9.2 |
| CAL-003 | P2 | received | report-quality | Report verbosity calibration | v1.1.0 |
| CAL-004 | P1 | needs-reproduction | readiness-score | Score optimism risk | v1.1.x |
| CAL-005 | P2 | deferred | protocol-detection | Multi-protocol classification calibration | v1.2.0 |
| CAL-006 | P1 | accepted-calibration | semantic-lite | Docs/comments false-positive risk | v1.1.0 |
| CAL-007 | P4 | deferred | amm-lending | AMM/lending runtime family expansion candidate | future |

## Details

### CAL-001 - Negative-context coverage detection

- Rule family: `testing`
- Source: `synthetic_internal`
- Status: `fixed`
- Priority: `P0`
- Target release: `v0.9.1`
- Problem: Comments such as missing invariant tests could be misread as positive coverage.
- Proposed action: Keep negative-context evidence tests and ensure missing coverage never inflates score.
- Safety notes: No private data. Calibration improves defensive readiness scoring.
- Linked tests: tests/test_negative_evidence.py

### CAL-002 - Generated artifact self-ingestion guard

- Rule family: `scan-source-accounting`
- Source: `synthetic_internal`
- Status: `fixed`
- Priority: `P0`
- Target release: `v0.9.2`
- Problem: Previous Arkheionx outputs could be read as source evidence on repeated scans.
- Proposed action: Ignore generated artifacts by default and report scan source accounting.
- Safety notes: No live-chain behavior. Prevents misleading evidence.
- Linked tests: tests/test_generated_artifact_ignore.py

### CAL-003 - Report verbosity calibration

- Rule family: `report-quality`
- Source: `synthetic_internal`
- Status: `received`
- Priority: `P2`
- Target release: `v1.1.0`
- Problem: Some audiences may need shorter summaries while researchers need evidence detail.
- Proposed action: Collect report-quality feedback by output type and audience.
- Safety notes: Do not include private report snippets unless authorized.
- Linked tests: tests/test_feedback_loop.py

### CAL-004 - Score optimism risk

- Rule family: `readiness-score`
- Source: `synthetic_internal`
- Status: `needs-reproduction`
- Priority: `P1`
- Target release: `v1.1.x`
- Problem: Certain toy repositories may receive an improving score despite multiple unresolved readiness gaps.
- Proposed action: Collect external evaluation score examples and compare finding confidence against score bands.
- Safety notes: Use sanitized scores only. Do not publish private repo names without permission.
- Linked tests: -

### CAL-005 - Multi-protocol classification calibration

- Rule family: `protocol-detection`
- Source: `synthetic_internal`
- Status: `deferred`
- Priority: `P2`
- Target release: `v1.2.0`
- Problem: Repositories combining vault, oracle, reward, and access-control patterns may need clearer protocol classification.
- Proposed action: Track public and toy examples before changing protocol detection.
- Safety notes: No live-chain data. Authorized repositories only.
- Linked tests: -

### CAL-006 - Docs/comments false-positive risk

- Rule family: `semantic-lite`
- Source: `synthetic_internal`
- Status: `accepted-calibration`
- Priority: `P1`
- Target release: `v1.1.0`
- Problem: Keyword-only docs or comments can be useful context but should not create high-confidence findings alone.
- Proposed action: Continue downgrading keyword-only evidence and collect false-positive reports by evidence source.
- Safety notes: Feedback snippets must be sanitized.
- Linked tests: tests/test_false_positive_reduction.py, tests/test_semantic_lite.py

### CAL-007 - AMM/lending runtime family expansion candidate

- Rule family: `amm-lending`
- Source: `synthetic_internal`
- Status: `deferred`
- Priority: `P4`
- Target release: `future`
- Problem: AMM and lending findings exist as knowledge/search categories, but runtime rule-pack expansion needs separate design.
- Proposed action: Collect feedback requests and avoid implying full runtime support before implementation.
- Safety notes: Future candidate only. No live-chain or deployed-contract scanning.
- Linked tests: -

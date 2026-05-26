# Feedback Loop

Arkheionx v1.1.0 adds a structured feedback loop for calibration, report
quality, and external evaluation.

The goal is practical: turn safe, sanitized feedback into better readiness
signals, confidence scoring, wording, docs, and GitHub Action behavior.

Arkheionx remains local/static and defensive. Feedback does not turn scanner
output into a formal audit finding or vulnerability confirmation.

## Feedback Types

- False positive reports.
- False negative reports.
- Report quality feedback.
- Rule calibration requests.
- External evaluation feedback.
- GitHub Action feedback.

Structured templates live in [`.github/ISSUE_TEMPLATE/`](../.github/ISSUE_TEMPLATE/).

## What Is Safe To Share

Safe:

- Arkheionx version.
- Finding IDs.
- Rule pack names.
- Sanitized report excerpts.
- Public toy fixture results.
- Public open-source repository results when allowed.
- High-level descriptions of confusing wording or noisy evidence.

Do not share publicly:

- secrets, private keys, mnemonics, tokens, RPC credentials;
- private repository contents unless authorized;
- unpatched vulnerability details;
- exploit steps for live targets;
- bounty-sensitive details outside the program's disclosure policy.

## Triage Flow

1. Confirm the feedback is safe to discuss publicly.
2. Classify feedback type and severity.
3. Reproduce on a toy, public, or sanitized fixture where possible.
4. Decide whether to tune scoring, confidence, evidence, docs, or templates.
5. Add or update tests before changing calibration behavior.
6. Record the status in the calibration backlog when useful.

## How Feedback Affects Arkheionx

Feedback can lead to:

- rule confidence changes;
- downgrade or suppression guidance;
- better negative-context detection;
- improved generated-artifact ignore logic;
- clearer report wording;
- better onboarding docs;
- stronger tests and fixtures.

Feedback should not be used to claim adoption, customers, production use, or
external validation unless committed public evidence and permission exist.

## Local Metadata

- [`metadata/feedback_schema.json`](../metadata/feedback_schema.json)
- [`metadata/feedback_examples.json`](../metadata/feedback_examples.json)
- [`metadata/rule_calibration_backlog.json`](../metadata/rule_calibration_backlog.json)
- [`reports/feedback_dashboard.md`](../reports/feedback_dashboard.md)
- [`reports/rule_calibration_backlog.md`](../reports/rule_calibration_backlog.md)

# Feedback Triage Workflow

This workflow helps maintainers turn feedback into safe calibration work.

## Statuses

| Status | Meaning |
|---|---|
| `received` | Feedback arrived and needs initial review. |
| `needs-reproduction` | Maintainer needs a toy, public, or sanitized reproduction. |
| `accepted-calibration` | Feedback is actionable and should affect rules, scoring, docs, or tests. |
| `rejected-not-actionable` | Feedback cannot be acted on safely or lacks enough detail. |
| `safety-review-required` | Feedback may include sensitive disclosure or private data. |
| `fixed` | The calibration or docs change has landed. |
| `documented` | The limitation or behavior is documented. |
| `deferred` | Valid but out of scope for the current milestone. |

## Severity

| Severity | Use When |
|---|---|
| `P0` | Misleading score, unsafe wording, disclosure risk, or severe trust issue. |
| `P1` | High-impact false positive or false negative. |
| `P2` | Report clarity or actionability issue. |
| `P3` | Docs, onboarding, or workflow friction. |
| `P4` | Future feature request or low-priority calibration idea. |

## Triage Questions

- Is the feedback safe to discuss publicly?
- Does it include private code, secrets, or credentials?
- Does it disclose unpatched vulnerability details?
- Does it affect readiness score?
- Does it affect finding confidence?
- Does it affect GitHub Action stability?
- Does it affect docs or onboarding?
- Can it be reproduced on a toy, public, or sanitized fixture?
- Does it need a new test before implementation?

## Outcomes

Good outcomes are small and auditable:

- add a regression test;
- adjust confidence or score calibration;
- improve report wording;
- document a known limitation;
- update rule calibration backlog status;
- request a safer reproduction.

Do not ask users to post sensitive vulnerability details publicly.

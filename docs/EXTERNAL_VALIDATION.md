# External Validation

Arkheionx external validation means collecting honest feedback from people who
run the tool on authorized repositories or inspect the public demo artifacts.

It does not mean Arkheionx has customers, partners, audit coverage, or proven
security outcomes unless those claims are backed by committed public evidence.

## Useful Feedback

- Was the five-minute demo easy to run?
- Which report was most useful?
- Which finding was noisy or confusing?
- Did the evidence point to the right file/function?
- Did the issue plan produce useful remediation tasks?
- Did Launch Report, Sprint Plan, or Contest Readiness output help explain the
  work to non-security stakeholders?

## What To Share

- Public repository link if authorized.
- Sanitized Markdown report excerpts.
- Finding IDs and evidence summaries.
- False-positive examples.
- Suggested rule calibration changes.

## What Not To Share

- Private keys.
- Mnemonics.
- RPC credentials.
- Secrets.
- Confidential production material.
- Undisclosed live-target exploit details.

## Feedback Paths

- `External evaluation feedback` issue template for sanitized evaluation
  results.
- `False positive report` issue template for noisy findings.
- `False negative report` issue template for missed readiness signals.
- `Report quality feedback` issue template for confusing output.
- `Rule calibration request` issue template for confidence/priority tuning.
- `GitHub Action feedback` issue template for CI and artifact workflow issues.

## Validation Levels

Arkheionx uses explicit validation levels so public language stays honest:

| Level | Meaning |
|---|---|
| Level 0 | Internal toy/demo only. |
| Level 1 | Public user tried the demo. |
| Level 2 | Public user ran on a toy/public repo. |
| Level 3 | Authorized private repo feedback, anonymized. |
| Level 4 | Public case study with permission. |
| Level 5 | Multiple public independent evaluations. |

Current status: v1.0.1 has internal demo and self-simulation coverage. v1.1.0
adds workflow for external calibration. Do not claim broad adoption, customers,
or production validation without committed public evidence and permission.

Read [`VALIDATION_LEVELS.md`](VALIDATION_LEVELS.md).

## How Feedback Improves Arkheionx

Feedback can lead to:

- lower-noise rule packs;
- better evidence summaries;
- clearer docs;
- improved fixture coverage;
- safer wording;
- better delivery artifacts for Launch Reports and Pre-Audit Sprints.

Arkheionx remains a pre-audit readiness tool. It is not a formal audit and not
a security guarantee.

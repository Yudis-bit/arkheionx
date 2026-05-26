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

- `External Validation Feedback` issue template for general product feedback.
- `False Positive Calibration` issue template for noisy findings.
- `Rule Request` issue template for new defensive checks.

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

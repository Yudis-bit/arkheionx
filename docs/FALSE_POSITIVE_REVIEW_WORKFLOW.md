# False-Positive Review Workflow

False-positive reports help Arkheionx become less noisy without hiding useful
readiness prompts.

## What To Report

Report a finding when:

- the affected file/function is wrong;
- the finding is keyword-only and should be lower priority;
- test coverage exists but was not recognized;
- a rule pack overstates the readiness gap;
- the wording is confusing or too broad.

Do not include secrets, private keys, undisclosed exploit details, or
confidential production material in public issues.

## How To Report

Use the `False Positive Calibration` issue template and include:

- Arkheionx version;
- finding ID;
- rule pack;
- sanitized JSON snippet;
- why the signal is noisy;
- whether semantic-lite or Slither evidence existed;
- suggested calibration change.

## Maintainer Triage

Maintainers should classify the report as one of:

- suppress locally: the user should document a local suppression;
- downgrade globally: the rule should reduce priority/confidence;
- improve evidence: semantic-lite or test mapping should be refined;
- update docs: the limitation should be documented;
- no change: the finding remains useful as a readiness prompt.

## Downgrade vs Suppression

Use downgrade when many users would see the same noisy signal.

Use suppression when the finding is useful generally but not applicable to one
repository because of local context.

Suppression is not proof of safety and must remain visible in reports.

## Safety

False-positive review is defensive calibration. Do not request live-target
testing, exploit payloads, bounty strategy, or unauthorized code review.

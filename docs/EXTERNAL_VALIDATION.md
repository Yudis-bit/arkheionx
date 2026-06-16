# External Validation

External validation is how ArkheionX earns credibility.

It means auditors, security researchers, and protocol teams inspect ArkheionX outputs or run the tool on authorized repositories and explain what was useful, noisy, missing, or unsafe.

It does not mean ArkheionX has endorsement, customers, audit coverage, or proven security outcomes unless public evidence supports that claim.

## Why external feedback matters

ArkheionX sits between security tooling and developer infrastructure.

The next stage is not random feature expansion. The next stage is:

- real-world usage on established DeFi protocols;
- external reviewer feedback from auditors and protocol teams;
- case studies showing what the tool clarified during actual review work;
- better language around what ArkheionX does and does not decide.

## Useful reviewer feedback

Auditors and security researchers should answer:

- Does the review map match how you reason through a protocol?
- Which outputs are useful?
- Which outputs are noise?
- What would you need before using this in a real audit?
- Which terminology feels wrong?
- What would make this safer?
- Which case study would make this credible?

## Useful protocol-team feedback

Protocol teams should answer:

- Did ArkheionX identify value paths the team cares about?
- Did it surface roles and trust assumptions accurately?
- Did it point at missing or weak tests the team agrees are worth adding?
- Were any outputs misleading, noisy, or too generic?
- Could the generated evidence tasks fit into the team’s internal review workflow?
- What would need to change before the team used it before an audit?

## How auditors can review outputs

Ask for:

- `00-run-context.md`;
- `02-value-flow-map.md`;
- `04-assumptions.md`;
- `05-review-lanes.md`;
- `06-evidence-tasks.md`;
- `08-report-filter.md`;
- `review.json` when structured review is useful.

Then check:

- Are value paths real?
- Are roles and assumptions missing anything important?
- Are review lanes ordered in a way that makes sense?
- Are evidence tasks testable?
- Are kill conditions useful?
- Does anything sound like an unsupported finding?

## How protocol teams can test ArkheionX

1. Choose an authorized repository.
2. Create a short scope note.
3. Run:

```bash
arkheionx review . --scope-file scope.md --out .arkheionx/review
```

4. Open the generated review pack.
5. Mark outputs as useful, noisy, wrong, or missing.
6. Add one or two local tests inspired by the evidence tasks.
7. Record whether ArkheionX helped clarify anything.

## What ArkheionX still does not decide

- Vulnerability validity.
- Final severity.
- Scope eligibility.
- Economic impact.
- Audit conclusions.
- Bounty outcomes.
- Protocol safety.

## Evidence levels for public claims

| level | public claim allowed |
|---|---|
| Internal fixture only | "Works on bundled examples." |
| Public demo tried by external user | "External user tried the demo." |
| Public repository run | "Ran on an authorized public repository." |
| Private authorized repo feedback | "Received anonymized authorized feedback." |
| Public case study with permission | "Case study available." |
| Multiple independent evaluations | "Multiple public independent evaluations." |

Do not skip levels in public language.

## Templates

- [`../templates/reviewer-feedback-request.md`](../templates/reviewer-feedback-request.md)
- [`../templates/protocol-team-feedback-request.md`](../templates/protocol-team-feedback-request.md)
- [`../templates/case-study-intake.md`](../templates/case-study-intake.md)

See also [`PUBLIC_FEEDBACK_GUIDE.md`](PUBLIC_FEEDBACK_GUIDE.md) and [`CASE_STUDIES.md`](CASE_STUDIES.md).

# Contest Readiness Mode

Contest Readiness Mode helps authorized maintainers prepare a repository before
a bug bounty launch, audit contest, competitive review, or public security
review.

It is not a contest strategy document for exploiting systems. It does not
generate exploit ideas, bounty claims, or live-target workflows.
It is not a formal audit and does not guarantee security.

## What It Helps With

- Scope preparation.
- Researcher onboarding checklist.
- Known limitations documentation.
- Invariant and test readiness.
- Pre-contest remediation priorities.
- Evidence-backed readiness findings.

## Generate Contest Readiness Output

```sh
python3 scripts/pre_audit_scan.py \
  --root . \
  --protocol-type auto \
  --contest-readiness-output ARKHEIONX_CONTEST_READINESS.md
```

## Scope Checklist

The generated report prompts teams to document:

- contracts in scope;
- contracts out of scope;
- privileged roles;
- oracle assumptions;
- upgradeability assumptions;
- test commands;
- known issues;
- emergency/admin procedures.

## Researcher Onboarding Checklist

Contest readiness improves when researchers can quickly understand:

- build and test commands;
- architecture overview;
- key invariants;
- state machines;
- threat model assumptions;
- known false positives.

## Safety Boundaries

- No exploit instructions.
- No bounty guarantee.
- No live target testing.
- Respect platform rules.
- Use only in repositories you own or are authorized to manage.

Formal audit and platform-specific review remain recommended where applicable.

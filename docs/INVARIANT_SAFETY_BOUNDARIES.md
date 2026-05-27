# Invariant Generation Safety Boundaries

Arkheionx invariant and test-plan generation is defensive, local, and static.

## Boundaries

- Use authorized repositories only.
- Use local mocks, local deployments, or project test harnesses.
- Keep TODO placeholders until project-specific behavior is reviewed.
- Treat findings as readiness signals, not vulnerability confirmations.
- Treat generated skeletons as starter scaffolds, not formal verification.

## Do Not Include

- production credentials;
- production addresses;
- remote cloning workflows;
- deployed-contract testing;
- transaction execution;
- attack automation;
- evasion logic;
- bounty-farming workflows;
- claims that generated tests prove security.

## Review Checklist

- [ ] Every TODO binding is project-specific and local.
- [ ] Every assertion matches documented protocol behavior.
- [ ] Rounding tolerances are explicit.
- [ ] Role assumptions are documented.
- [ ] Oracle assumptions are documented.
- [ ] Remaining limitations are written down before audit handoff.

Generated invariant skeletons should help teams prepare for manual review and formal audits. They are not a substitute for either.

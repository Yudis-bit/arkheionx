# Developer And Researcher Workflow

Arkheionx v2.0.1 is a repositioning hotfix. The current functional interface
is still `scan`, `test-plan`, `search`, `validate-config`, `doctor`, and
`version`. The future value-flow engine is planned, not implemented yet.

## Developer Workflow

Install locally:

```sh
python3 -m pip install -e .
arkheionx doctor
```

Run the current local/static scan:

```sh
arkheionx scan . \
  --protocol-type auto \
  --output reports/ARKHEIONX_PRE_AUDIT_REPORT.md \
  --json-output reports/arkheionx-report.json \
  --sarif-output reports/arkheionx.sarif.json \
  --issue-plan-output reports/ARKHEIONX_ISSUE_PLAN.json
```

Inspect:

- `Fix First` for the highest-signal review areas.
- Rule family grouping to see whether vault, oracle, AMM, lending, reward,
  access-control, or reentrancy/value-flow assumptions are involved.
- Evidence and confidence reasons before treating any item as actionable.
- Suggested tests and invariant candidates.

Generate a defensive test plan:

```sh
arkheionx test-plan \
  --report reports/arkheionx-report.json \
  --output reports/ARKHEIONX_TEST_PLAN.md \
  --json-output reports/ARKHEIONX_TEST_PLAN.json \
  --foundry-output reports/ArkheionxReadinessInvariants.t.sol
```

Future direction:

```text
flow map -> missing tests -> templates -> verify
```

In future releases, planned flow commands should help developers move from a
local value-flow map to missing-test prompts, Foundry templates, and
before/after checks.

## Researcher Workflow

Run a local/static scan on an authorized repository:

```sh
arkheionx scan . \
  --protocol-type auto \
  --output reports/ARKHEIONX_REVIEW_REPORT.md \
  --json-output reports/arkheionx-review.json
```

Review:

- rule family;
- `Fix First`;
- evidence;
- confidence reason;
- affected files/functions where available;
- Related Knowledge and suggested tests.

Use local security memory:

```sh
arkheionx search "oracle stale price"
arkheionx search "vault accounting invariant"
arkheionx search "missing invariant"
```

Future direction:

```text
flow review-map -> historical pattern -> issue candidate
```

In future releases, planned flow review maps should help researchers orient
around value-moving functions, connect them to historical patterns, and draft
evidence-backed issue candidates.

## Safety Boundaries

Use Arkheionx only on repositories you own or are authorized to review.

Arkheionx does not perform RPC calls, live-chain calls, transaction execution,
deployed-contract scanning, private key handling, exploit automation, or
security guarantees. Findings are review prompts, not formal audit findings.

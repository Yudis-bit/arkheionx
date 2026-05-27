# Arkheionx Invariant/Test Plan Generator

Arkheionx v1.5.0 can turn readiness findings into defensive test plans and safe Foundry invariant skeletons.

This is not a formal audit, not formal verification, and not proof of safety. It is a local planning aid for authorized repositories.

## What It Does

- Reads an Arkheionx JSON report.
- Maps finding IDs to suggested tests and invariant candidates.
- Groups work by rule family.
- Generates a Markdown test plan.
- Optionally generates JSON for automation.
- Optionally generates a Foundry-style invariant skeleton with TODO placeholders.

## What It Does Not Do

- It does not confirm vulnerabilities.
- It does not provide complete property coverage.
- It does not connect to deployed contracts.
- It does not execute transactions.
- It does not replace human review or a formal audit.

## Example

```sh
python3 scripts/generate_test_plan.py \
  --report examples/reports/amm-fixture-pre-audit-report.json \
  --output examples/reports/amm-fixture-test-plan.md \
  --json-output examples/reports/amm-fixture-test-plan.json \
  --foundry-output examples/reports/ArkheionxAMMInvariants.t.sol
```

## Finding Map

The generator uses `metadata/finding_test_plan_map.json`.

Each finding can map to:

- suggested tests;
- invariant candidates;
- Foundry skeleton function names;
- project bindings to fill in;
- safety notes;
- manual review notes.

## Check Mode

```sh
python3 scripts/generate_test_plan.py --check
```

Check mode verifies committed AMM, Lending, and hybrid fixture test-plan artifacts are current.

## Human Review Workflow

1. Read the source readiness report.
2. Generate a test plan.
3. Review each suggested test for project relevance.
4. Wire the skeleton to local mocks and project contracts.
5. Replace placeholder assertions with project-specific properties.
6. Run local tests.
7. Re-run Arkheionx and compare the new report or baseline.

Generated plans are intentionally conservative. Remove irrelevant suggestions and add protocol-specific properties before relying on them.

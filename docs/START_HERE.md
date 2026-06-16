# Start Here

ArkheionX is local-first review infrastructure for smart contract security.

It turns an authorized Solidity or Foundry repository into deterministic review context: value paths, roles, trust assumptions, reachable flows, missing tests, evidence tasks, and unresolved review gaps.

It does not replace auditors. It gives auditors a better map.

## The 30-second model

| Foundry | ArkheionX |
|---|---|
| Runs the tests you wrote. | Maps what still needs review. |
| Reports pass or fail. | Surfaces value paths, assumptions, and weak test areas. |
| Confirms a local test result. | Helps organize evidence and unresolved questions. |

ArkheionX output is not a finding by itself. A human reviewer still writes, runs, and judges the proof.

## First run

```bash
arkheionx version
arkheionx doctor
arkheionx review . --scope-file scope.md --out .arkheionx/review
```

If you do not have a scope file yet, create a short Markdown note with:

- contracts in scope;
- roles and trusted actors;
- assets and value paths worth reviewing;
- known limitations, accepted risks, or prior-audit context.

## No repo handy

Use a bundled demo:

```bash
arkheionx demo --list
arkheionx review-map examples/vault-strategy-oracle-fixture
```

`review-map` is still useful for a compact first read: value paths, assumptions, test gaps, proof suggestions, and evidence links. The primary pack workflow is `arkheionx review`.

## Read the output in this order

1. `00-run-context.md`
2. `01-scope-map.md`
3. `02-value-flow-map.md`
4. `04-assumptions.md`
5. `05-review-lanes.md`
6. `06-evidence-tasks.md`
7. `08-report-filter.md`

Open the value exits first, then the assumptions that guard them, then the missing or weak test areas.

## What to do next

- Write local tests for the highest-value unresolved paths.
- Record what evidence supports or kills each hypothesis.
- Keep severity and reportability decisions human-reviewed.
- Use case-study notes only when the workflow produced useful evidence.

## Boundaries

ArkheionX is local/static by default. It does not require private keys, RPC URLs, live-chain access, or production credentials. It does not automatically find vulnerabilities, confirm severity, or submit reports.

See [`WHAT_ARKHEIONX_IS_NOT.md`](WHAT_ARKHEIONX_IS_NOT.md), [`CLI_REFERENCE.md`](CLI_REFERENCE.md), and [`CORE_WORKFLOW.md`](CORE_WORKFLOW.md).

For a quick map of the repository tree, generated-output directories, and historical fixture folders, see [`REPOSITORY_STRUCTURE.md`](REPOSITORY_STRUCTURE.md).

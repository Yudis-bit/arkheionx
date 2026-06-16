# Output Artifacts

ArkheionX writes local artifacts for review. They are generated context, not source truth.

## Primary review pack

The current primary workflow is:

```bash
arkheionx review . --scope-file scope.md --out .arkheionx/review
```

Recommended output location:

```text
.arkheionx/review/
```

Core files:

| file | purpose |
|---|---|
| `00-run-context.md` | Run metadata, version info, scope/lens context, and read order. |
| `01-scope-map.md` | Structured scope and review rules. |
| `02-value-flow-map.md` | Value entry, movement, and exit context. |
| `03-interaction-map.md` | Contract and role interaction context. |
| `04-assumptions.md` | Trust assumptions and review dependencies. |
| `05-review-lanes.md` | Ordered lanes for human inspection. |
| `06-evidence-tasks.md` | Local proof tasks and kill conditions. |
| `07-evidence-rubric.md` | Evidence quality rubric. |
| `08-report-filter.md` | Pre-report triage and reasons to stop. |
| `09-agent-input.md` | Model-agnostic AI-assisted review context. |
| `review.json` | Consolidated machine-readable review context. |
| `manifest.json` | Artifact manifest and safety metadata. |

Protocol-lens runs may add files such as protocol model, behavior promises, economic invariants, temporal windows, and lens-specific evidence tasks.

## Focused review-map artifacts

`arkheionx review-map .` writes compact focused artifacts under `.arkheionx/out/review-map/`, including:

- `review-map.md`;
- `review-map.json`;
- value paths;
- assumptions;
- test gaps;
- proof suggestions;
- evidence links.

This is useful for a quick first read, but the canonical review-pack workflow is `arkheionx review`.

## Evidence artifacts

Evidence-related commands may write proof, trace, evidence, report, validation, and review-package artifacts under `.arkheionx/out/`.

These artifacts can support a hypothesis. They do not replace human validation, PoC review, severity analysis, or disclosure judgment.

## Legacy scanner artifacts

The older scanner workflow can still write report, SARIF, baseline, diff, issue-plan, test-plan, launch, sprint, and contest-readiness artifacts.

Those outputs remain supported as advanced/legacy workflows, but they are not the public first-run path.

## Generated artifact rules

- Keep generated artifacts out of source truth unless intentionally committed as fixtures or examples.
- Do not feed old generated reports back into a review as if they were protocol source.
- Treat all generated Markdown and JSON as review context.
- Do not infer severity, safety, exploitability, or acceptance from artifact names.

See [`GENERATED_ARTIFACT_IGNORE.md`](GENERATED_ARTIFACT_IGNORE.md), [`SCHEMAS.md`](SCHEMAS.md), and [`INTERPRET_RESULTS.md`](INTERPRET_RESULTS.md).

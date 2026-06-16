# Complete Review Package (v6, headline)

> Local/static review package. An evidence state is not a vulnerability claim.
> Interaction priority is not severity. Human review is required.

`arkheionx complete-review` is the headline V6 command. It generates a complete
local review package that combines the V4 review map, the V5 Blind Spot
Intelligence layer, and the V6 evidence graph, interaction matrix, and unresolved
map into one folder a researcher or an AI agent can work from.

```bash
arkheionx complete-review examples/blind-spot-fixture --out .arkheionx/complete-review
arkheionx complete-review . --json     # print the manifest only
arkheionx complete-review . --no-write  # build in memory only
```

Like `research-pack`, `complete-review` **writes by default** (to
`.arkheionx/complete-review/` unless `--out` is given); pass `--no-write` to build
the manifest in memory only.

## Files

| File | Purpose |
| --- | --- |
| `00-README.md` | What the package is, what it is not, how to use it. |
| `01-review-map-summary.md` | Protocol structure, value paths, assumptions, test gaps. |
| `02-blind-spots-summary.md` | Likely blind-spot candidates (v5). |
| `03-criticality-summary.md` | Criticality potential across surfaces (v5). |
| `04-counterfactuals-summary.md` | Testable "what if this assumption is false?" prompts (v5). |
| `05-evidence-graph.md` | Every important surface classified into an evidence state (v6). |
| `06-interaction-matrix.md` | Combinations of surfaces that may hide bugs (v6). |
| `07-unresolved-surfaces.md` | Everything important that local evidence does not close (v6). |
| `08-agent-input.md` | A scoped, model-agnostic task for a review agent. |
| `09-human-review-checklist.md` | The checklist a human completes before ending review. |
| `10-case-study-template.md` | A sanitized research-session report template. |
| `manifest.json` | Machine-readable index of the package. |

It also writes the machine-readable `evidence-graph.json`,
`interaction-matrix.json`, `unresolved-map.json`, and a combined
`complete-review.json`.

## Which file goes where

- A human reads `01`, `05`, `06`, and `07` to decide where to look.
- An AI agent or reviewer is given `08-agent-input.md` — it is scoped,
  vendor-neutral (it speaks of an "AI agent", "review agent", "human reviewer",
  and "local test runner", never a specific vendor), and asks the agent to write
  local tests for unresolved items, **not** to claim findings.
- A human completes `09-human-review-checklist.md` before ending the review.

## manifest.json

The manifest includes `schema_version`, `package_version`, `command`,
`repo_path`, `artifact_list`, `evidence_node_count`, `interaction_count`,
`unresolved_surface_count`, `unresolved_interaction_count`,
`evidence_state_summary`, `safety_flags`, and `human_review_required: true`.

## Safety

Local/static only. No RPC, no live-chain calls, no private keys, no exploit
automation, no auto-submit, no severity. The package makes no vulnerability
claims. A finding is only ever confirmed by a human with independent local proof.

## Related

- [`EVIDENCE_GRAPH.md`](EVIDENCE_GRAPH.md), [`INTERACTION_MATRIX.md`](INTERACTION_MATRIX.md),
  [`UNRESOLVED_MAP.md`](UNRESOLVED_MAP.md), [`V6_WORKFLOW.md`](archive/versions/V6_WORKFLOW.md).

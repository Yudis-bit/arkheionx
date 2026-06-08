# Arkheionx V7 Workflow

V7 turns audit scope into review lanes, task packs, evidence requirements, and
report filters so AI-assisted security review starts from rules and evidence
instead of vague prompts. This page shows the end-to-end loop.

## 1. Map the scope

```bash
arkheionx scope-map <repo> --scope-file <scope.md> --out .arkheionx/scope-map
```

Produces structured review rules: in/out of scope, severity conditions, trusted
assumptions, dependency assumptions, known/accepted issues, prior-audit notes,
design choices, invariants, focus areas, do-not-waste-time filters, and
report-candidate requirements. See [`SCOPE_MAP.md`](SCOPE_MAP.md).

## 2. Generate lanes and tasks (or the whole pack)

```bash
arkheionx scope-pack <repo> --scope-file <scope.md> --out .arkheionx/scope-pack
```

The pack contains the scope map, review lanes, scope tasks, a do-not-waste-time
list, an evidence template and rubric, a report-filter checklist, a human review
checklist, model-agnostic agent input, a case-study template, and a JSON manifest
with machine-readable sidecars. See [`SCOPE_TASKS.md`](SCOPE_TASKS.md).

## 3. Hand tasks to a reviewer or AI agent

Give `09-agent-input.md` plus `03-scope-tasks.md` from the pack to a human reviewer
or a model-agnostic AI agent. The agent input instructs: do not claim a finding
without local test evidence; do not rely on trusted-role misbehaviour unless the
scope says it is valid; do not treat known/accepted risks as new findings; do not
submit low-only issues when Medium/High is required.

## 4. Judge the evidence

After writing local Foundry tests, grade them:

```bash
arkheionx evidence-judge <repo> --scope-file <scope.md>
```

The judge reads local tests and evidence and grades each on a transparent rubric.
It does not confirm vulnerabilities. Candidate-with-evidence is not a confirmed
vulnerability. See [`EVIDENCE_JUDGE.md`](EVIDENCE_JUDGE.md).

## 5. Filter candidates before submission

```bash
arkheionx report-filter <repo> --scope-file <scope.md>
```

Classifies each candidate against the scope rules and surfaces a human
pre-submission checklist. The report filter is not final triage. See
[`REPORT_FILTER.md`](REPORT_FILTER.md).

## Using V7 on a private scope

Private scope details stay local and are never committed. `.arkheionx/` is
gitignored.

```bash
mkdir -p .arkheionx/private
# put your private scope note in .arkheionx/private/scope.md
# put terms to guard (target/sponsor/protocol names) in .arkheionx/private/private-terms.txt

arkheionx scope-map      . --scope-file .arkheionx/private/scope.md --out .arkheionx/private/scope-map
arkheionx scope-pack     . --scope-file .arkheionx/private/scope.md --out .arkheionx/private/scope-pack
arkheionx scope-lanes    . --scope-file .arkheionx/private/scope.md --out .arkheionx/private/scope-lanes
arkheionx scope-tasks    . --scope-file .arkheionx/private/scope.md --out .arkheionx/private/scope-tasks
arkheionx evidence-judge . --scope-file .arkheionx/private/scope.md --out .arkheionx/private/evidence-judge
arkheionx report-filter  . --scope-file .arkheionx/private/scope.md --out .arkheionx/private/report-filter
```

The leak guard scans the committed surface for any term in your private-terms
file, so a private target name never lands in public source, tests, fixtures,
docs, or generated output. Keep the public product generic; keep the private scope
local.

## Where V7 sits

See [`SCOPE_ORCHESTRATION.md`](SCOPE_ORCHESTRATION.md) for the model, the bundled
synthetic [`examples/scope-fixture`](../examples/scope-fixture/README.md), and the
[`BUG_BOUNTY_WORKFLOW.md`](BUG_BOUNTY_WORKFLOW.md) for how this fits a contest
triage flow. Human review is required for every conclusion.

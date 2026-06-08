# Scope Map (V7)

`arkheionx scope-map <repo> --scope-file <scope.md>` parses a contest/audit/program
scope note into structured review rules. It is a local/static planning artifact —
not a finding, not severity, not a confirmed vulnerability. Human review required.

## What it extracts

From the markdown scope note it routes sections into:

- scope summary and in-scope surface classes
- in-scope / out-of-scope areas
- valid severity / impact conditions (and whether Medium/High is required)
- trusted roles and trusted external integrations
- known issues and accepted risks
- prior-audit notes and changed-since-audit focus
- design choices that affect validity
- protocol invariants
- off-chain, admin, and external-dependency assumptions
- array / gas limitations and EIP/standard expectations
- compliance expectations
- recommended focus areas
- likely-invalid and likely-low-only patterns
- report-candidate requirements

## Output

Markdown (`scope-map.md`) with sections: Boundary, Scope Summary, In-Scope Surface
Classes, Trusted Assumptions, External Dependency Assumptions, Known Issues /
Accepted Risks, Prior Audit Notes, Design Choices That Affect Validity, Invariants
To Preserve, Focus Areas, Do-Not-Waste-Time Filters, and Report Candidate
Requirements.

JSON (`scope-map.json`, validated by `schemas/scope-map.schema.json`) includes
`schema_version`, `arkheionx_version`, `repo_summary`, `trusted_assumptions`,
`dependency_assumptions`, `known_issues`, `accepted_risks`, `invariants`,
`focus_areas`, `do_not_waste_time`, `report_candidate_requirements`,
`human_review_required`, and `safety_boundary`.

## No scope file

If `--scope-file` is omitted, scope-map produces a generic map inferred from
repository structure and clearly states that no explicit scope file was provided.
Confirm the real program scope manually before trusting any result.

## Example

```bash
arkheionx scope-map examples/scope-fixture --scope-file examples/scope-fixture/scope-note.md
```

See [`SCOPE_ORCHESTRATION.md`](SCOPE_ORCHESTRATION.md) and
[`V7_WORKFLOW.md`](V7_WORKFLOW.md).

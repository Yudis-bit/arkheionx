# Final Open-Source Productization Log

Final integration phase for Arkheionx Vault before public push. This is
an internal audit log; nothing in this file changes runtime behaviour.

## Snapshot

- Branch: `agent/03-release-redteam`
- Latest commit: `b8e7f40 chore(repo): polish GitHub repository surface`
- Working tree: clean at start of phase.
- EVM/src and EVM/test: untouched in this phase.

## Repository surface inventory

Top-level directories present:

```
EVM/         Foundry project (active)
SVM/         Anchor scaffold (template only)
MoveVM/      Aptos Move scaffold (template only)
metadata/    Canonical registry + JSON schema + backlog
reports/     Quality matrix + per-PoC verification reports
scripts/     Validation, registry, scoring, GitHub surface tooling
docs/        Standards, taxonomy, internal phase reports
.github/     Issue templates, workflows, pull request template
```

Top-level files: `README.md`, `.env.example`, `.gitignore`,
`.gitmodules`. No `web/`, no leftover frontend artifacts. The root is
clean.

## web/ status

`web/` is already removed. Confirmed via `find -type d -name web`. Stale
references found are limited to `docs/internal/` historical phase
reports — acceptable as historical record. No active script, README,
workflow, or template still depends on `web/public/metadata.json`.

`docs/ROADMAP.md` retains a single Next.js mention that is no longer
accurate; flagged for correction in this phase.

## Generated artifacts present

- `reports/poc_quality_matrix.md` — produced by `scripts/score_pocs.py`.
- `reports/verification/*.md` — produced by
  `scripts/generate_verification_report.py`.
- `README.md` registry table — between `<!-- BEGIN: registry -->` and
  `<!-- END: registry -->` markers, produced by
  `scripts/generate_registry.py`.

All three are deterministic and have `--check` modes used by CI.

## Existing docs

Standards layer is mature:

- `docs/RESEARCH_STANDARD.md`
- `docs/POC_STANDARD.md`
- `docs/ASSERTION_STANDARD.md`
- `docs/REPRODUCIBILITY_STANDARD.md`
- `docs/EXPLOIT_TAXONOMY.md`
- `docs/AUDITOR_CHECKLIST.md`
- `docs/ROOT_CAUSE_PLAYBOOK.md`
- `docs/FORK_VERIFICATION.md`
- `docs/INCIDENT_INTAKE.md`
- `docs/EXPANSION_PLAN.md`
- `docs/METADATA_SCHEMA.md`
- `docs/VERIFICATION_REPORT_TEMPLATE.md`
- `docs/BRAND.md`, `docs/ETHICS.md`, `docs/SECURITY.md`,
  `docs/STYLEGUIDE.md`, `docs/CONTRIBUTING.md`.

Missing for productization:

- `docs/POC_MATURITY_MODEL.md` (new)
- `docs/RELEASE_PROCESS.md` (new)
- `docs/RELEASE_CHECKLIST.md` (new)
- `docs/LAUNCH_PLAN.md` (new)
- `docs/launch/LINKEDIN_LAUNCH_POST.md` (new)
- `docs/launch/GITHUB_RELEASE_NOTES.md` (new)
- `docs/launch/X_THREAD.md` (new)

## Issue templates

Present:

- `bug_report.md` — broken-PoC reports.
- `documentation_issue.md` — covers docs corrections AND unsafe-content
  reports in one template.
- `poc_verification_issue.md` — reproducibility divergence reports.
- `config.yml` — points at `docs/ETHICS.md`.

To add for contributor system completeness:

- `research_candidate.md` — proposing a new incident.
- `assertion_hardening.md` — proposing a Phase-style assertion patch on
  an existing PoC.

`unsafe_content_report` is currently folded into `documentation_issue`.
Promoting it to its own dedicated template improves visibility.

## Scripts present

- `validate_metadata.py` — schema + repo-rule validation.
- `generate_registry.py` — README registry table.
- `score_pocs.py` — quality matrix.
- `generate_verification_report.py` — per-PoC reports.
- `poc_factory.py` — PoC scaffolding helper.
- `github_surface_setup.sh` — gh CLI dry-run/apply for description and
  topics.

To add:

- `poc_maturity_index.py` — produces `reports/poc_maturity_index.md`
  using L0-L5 maturity ladder.
- `research_dashboard.py` — produces `reports/research_dashboard.md`
  aggregating registry signals.

## CI workflows

- `metadata.yml` — runs `validate_metadata.py` and
  `generate_registry.py --check`. Needs to be extended to call
  `score_pocs.py --check`, `generate_verification_report.py --check`,
  `poc_maturity_index.py --check`, `research_dashboard.py --check`.
- `evm.yml` — `forge fmt --check` + `forge build`, plus optional fork
  job gated on RPC secret. Skipped runs are clearly labeled. No fake
  green.
- `docs.yml` — required-docs presence check. Will be extended to
  include the new docs files.

## Risks to keep in mind

- Do not modify `EVM/src/**` or `EVM/test/**/*.t.sol` in this phase.
- Do not raise any PoC to `deterministic-confirmed` — no archival fork
  run has been recorded.
- Do not invent stars, forks, audit work, or affiliations.
- Keep README current-state numbers consistent with
  `metadata/registry.json`.

# Release Checklist

A release is not cut until every applicable box is checked or marked N/A with a
written reason in the release PR.

## Scope

- [ ] Release type identified: scanner, rule pack, archive, verification,
      docs, or service surface.
- [ ] Version named in `CHANGELOG.md`.
- [ ] No unsupported claims added to README, docs, reports, or release notes.
- [ ] Current archive truth preserved: 18 structured PoCs, 0 L4+ archival
      confirmed entries unless regenerated artifacts prove otherwise.

## Scanner And Product Validation

- [ ] `python3 -m py_compile scripts/pre_audit_scan.py scripts/generate_search_index.py`
- [ ] `python3 -m py_compile scripts/post_pr_comment.py scripts/create_github_issues.py`
- [ ] `python3 -m unittest discover -s tests -p "test_*.py"`
- [ ] Mini-vault scan regenerated:

  ```sh
  python3 scripts/pre_audit_scan.py \
    --root examples/mini-vault \
    --protocol-type auto \
    --output examples/reports/mini-vault-pre-audit-report.md \
    --json-output examples/reports/mini-vault-pre-audit-report.json \
    --sarif-output examples/reports/mini-vault.sarif.json \
    --baseline-output examples/reports/mini-vault.baseline.json \
    --summary-output examples/reports/mini-vault-action-summary.md \
    --comment-output examples/reports/mini-vault-pr-comment.md \
    --issue-checklist-output examples/reports/mini-vault-issue-checklist.md \
    --generate-invariant-skeletons
  ```

- [ ] Vault-risk fixture scan regenerated:

  ```sh
  python3 scripts/pre_audit_scan.py \
    --root examples/vault-risk-fixture \
    --protocol-type vault \
    --output examples/reports/vault-risk-fixture-pre-audit-report.md \
    --json-output examples/reports/vault-risk-fixture-pre-audit-report.json \
    --sarif-output examples/reports/vault-risk-fixture.sarif.json \
    --baseline-output examples/reports/vault-risk-fixture.baseline.json \
    --summary-output examples/reports/vault-risk-fixture-action-summary.md \
    --comment-output examples/reports/vault-risk-fixture-pr-comment.md \
    --issue-checklist-output examples/reports/vault-risk-fixture-issue-checklist.md \
    --generate-invariant-skeletons
  ```

- [ ] Baseline diff scan regenerated:

  ```sh
  python3 scripts/pre_audit_scan.py \
    --root examples/vault-risk-fixture \
    --protocol-type vault \
    --compare-baseline examples/reports/vault-risk-fixture.baseline.json \
    --output examples/reports/vault-risk-fixture-diff-report.md \
    --json-output examples/reports/vault-risk-fixture-diff-report.json \
    --diff-output examples/reports/vault-risk-fixture-diff.md \
    --diff-json-output examples/reports/vault-risk-fixture-diff.json \
    --sarif-output examples/reports/vault-risk-fixture-diff.sarif.json \
    --summary-output examples/reports/vault-risk-fixture-diff-summary.md \
    --comment-output examples/reports/vault-risk-fixture-diff-comment.md \
    --issue-checklist-output examples/reports/vault-risk-fixture-diff-checklist.md
  ```

- [ ] Config suppression scan regenerated:

  ```sh
  python3 scripts/pre_audit_scan.py \
    --root examples/vault-risk-fixture \
    --protocol-type vault \
    --config examples/arkheionx.config.example.json \
    --output examples/reports/vault-risk-fixture-config-report.md \
    --json-output examples/reports/vault-risk-fixture-config-report.json \
    --summary-output examples/reports/vault-risk-fixture-config-summary.md \
    --comment-output examples/reports/vault-risk-fixture-config-comment.md \
    --issue-checklist-output examples/reports/vault-risk-fixture-config-checklist.md
  ```

- [ ] JSON outputs parse successfully.
- [ ] JSON outputs include canonical `findings`.
- [ ] SARIF outputs parse successfully and use SARIF `2.1.0`.
- [ ] SARIF outputs include rules, results, and readiness/not-vulnerability
      properties.
- [ ] Baseline JSON includes finding fingerprints.
- [ ] Diff JSON includes new, resolved, unchanged, changed, and suppressed
      counts.
- [ ] Diff report includes `Baseline Diff`.
- [ ] Markdown reports include the disclaimer.
- [ ] Vault report includes `Vault Rule Pack Coverage`.
- [ ] PR comment output contains `<!-- arkheionx-pre-audit-comment -->`.
- [ ] Summary output contains `Score:`.
- [ ] Generated issue checklist contains Markdown checkboxes.
- [ ] Config suppression output shows `Suppressed Readiness Gaps`.

## v0.5 Issue Workflow And Rule Pack Checks

- [ ] Issue plan JSON generated and parses successfully.
- [ ] Issue plan contains deterministic `<!-- arkheionx-issue:* -->` markers.
- [ ] Issue plan contains defensive disclaimers.
- [ ] `scripts/create_github_issues.py --mode dry-run` makes no API calls and
      writes dry-run output.
- [ ] Real issue creation is not used in CI.
- [ ] Rule pack coverage includes vault, oracle, access/upgradeability,
      reentrancy/value-flow, and reward accounting when relevant.
- [ ] SARIF output includes new rule-pack finding IDs as readiness gaps.
- [ ] Baseline/diff output supports new rule-pack findings.
- [ ] `docs/GITHUB_ISSUE_WORKFLOW.md` documents permissions, dry-run, create,
      update, duplicate prevention, and safety boundaries.

## v0.6 Semantic-Lite And False-Positive Checks

- [ ] JSON reports include `analysis_quality`.
- [ ] JSON reports include `semantic_lite` contracts/functions when enabled.
- [ ] Findings include `evidence`, `confidence_reason`, and
      `detection_sources`.
- [ ] Low-confidence keyword-only findings are visible but downgraded.
- [ ] Issue plans include confidence reasons and top evidence.
- [ ] SARIF locations prefer semantic-lite or Slither evidence where available.
- [ ] Slither absence is graceful unless strict mode is explicitly enabled.
- [ ] `--slither-json` works with a local mock/provided JSON file.
- [ ] `docs/SEMANTIC_LITE_ANALYSIS.md`, `docs/SLITHER_INTEGRATION.md`, and
      `docs/FALSE_POSITIVE_REDUCTION.md` are linked from README.

## v0.7 Delivery Artifact Checks

- [ ] Launch Report Markdown generated and includes `Executive Summary`.
- [ ] Pre-Audit Sprint Plan generated and includes the selected day schedule.
- [ ] Contest Readiness Report generated and includes the scope checklist.
- [ ] Executive Summary generated and fits a short stakeholder handoff format.
- [ ] Remediation Roadmap generated and groups tasks by phase.
- [ ] All delivery artifacts include defensive disclaimers.
- [ ] JSON output includes `delivery_outputs` and `delivery_summary`.
- [ ] GitHub Action exposes delivery output inputs.
- [ ] `docs/LAUNCH_REPORT_OS.md`, `docs/PRE_AUDIT_SPRINT_WORKFLOW.md`,
      `docs/CONTEST_READINESS_MODE.md`, and `docs/DELIVERY_ARTIFACTS.md` are
      linked from README.
- [ ] `SERVICES.md` and `docs/business/MONETIZATION.md` describe delivery artifacts as
      readiness support, not formal audit services.

## v0.8 Demo And Validation Checks

- [ ] `docs/TRY_IN_5_MINUTES.md` exists and the command runs locally.
- [ ] `docs/PUBLIC_DEMO_WORKFLOW.md` explains local and GitHub Action demos.
- [ ] `.github/workflows/arkheionx-demo.yml` is manual-only and creates no
      GitHub issues.
- [ ] Demo artifacts generated under `examples/reports/demo-*`.
- [ ] Demo issue dry-run says no GitHub API calls were made.
- [ ] `docs/case-studies/ORACLE_STAKING_FIXTURE_CASE_STUDY.md` exists.
- [ ] Before/after case study or template exists.
- [ ] `docs/RULE_CALIBRATION.md` and `reports/rule_calibration_summary.md`
      explain confidence, evidence, and false-positive handling.
- [ ] False-positive calibration and external validation issue templates exist.
- [ ] Launch/outreach posts avoid unsupported traction, user, or audit claims.

## Search And Registry

- [ ] `python3 scripts/generate_search_index.py --check`
- [ ] `python3 scripts/generate_registry.py --check`
- [ ] `python3 scripts/validate_metadata.py`
- [ ] `python3 scripts/score_pocs.py --check`
- [ ] `python3 scripts/generate_verification_report.py --check`
- [ ] `python3 scripts/poc_maturity_index.py --check`
- [ ] `python3 scripts/research_dashboard.py --check`

## README And Docs

- [ ] README renders cleanly on GitHub.
- [ ] README top section includes Start Here paths for builders and
      researchers.
- [ ] Latest release section names the current stable release accurately.
- [ ] Stable GitHub Action examples use the latest released tag.
- [ ] `@main` examples are labeled as development usage.
- [ ] Quick Start YAML is valid.
- [ ] Sample commands are readable.
- [ ] Registry table remains between generated markers.
- [ ] `docs/VAULT_RULE_PACK.md` linked from README and search index.
- [ ] `docs/GITHUB_ACTION_USAGE.md` matches action inputs.
- [ ] `docs/PR_COMMENT_MODE.md` documents permissions and update mode.
- [ ] `docs/GENERATED_ISSUE_CHECKLIST.md` documents manual issue workflow.
- [ ] `docs/ARKHEIONX_CONFIG.md` documents suppression behavior.
- [ ] `docs/SARIF_OUTPUT.md` documents Code Scanning upload and severity
      mapping.
- [ ] `docs/BASELINE_DIFF_MODE.md` documents baseline and diff usage.
- [ ] `docs/CI_GATING.md` documents fail thresholds and false-positive
      caution.
- [ ] `docs/READINESS_SCORE.md` matches scanner scoring categories.
- [ ] `SERVICES.md`, `docs/business/MONETIZATION.md`, and `docs/business/SPONSORSHIP.md` avoid
      formal-audit or guarantee claims.
- [ ] Stale release phrases are absent:

  ```sh
  python3 - <<'PY'
  from pathlib import Path

  version = "v0" + ".4" + ".0"
  phrases = [
      version + " - " + "Unreleased",
      "until " + version + " is tagged",
      "prepared, " + "not tagged",
      "prepared, " + "not released",
      "upcoming " + version,
      "planned " + version,
  ]
  for root in [Path("README.md"), Path("CHANGELOG.md"), Path("docs")]:
      files = [root] if root.is_file() else root.rglob("*.md")
      for path in files:
          text = path.read_text(encoding="utf-8", errors="ignore")
          for phrase in phrases:
              if phrase.lower() in text.lower():
                  raise SystemExit(f"stale release phrase: {path}: {phrase}")
  PY
  ```

- [ ] v0.7.0 or the next active milestone is visible in roadmap and release
      notes.

## v0.9.0 Security Memory Checks

- [ ] `metadata/security_memory_graph.json` exists and parses.
- [ ] `metadata/finding_knowledge_map.json` exists and parses.
- [ ] `metadata/rule_calibration_matrix.json` exists and parses.
- [ ] `reports/security_memory_graph.md` exists.
- [ ] `python3 scripts/generate_knowledge_graph.py --check` passes.
- [ ] `python3 scripts/search_knowledge.py "oracle stale price"` returns
      `ARK-ORC-001`.
- [ ] `python3 scripts/search_knowledge.py "missing invariant" --json`
      returns valid JSON.
- [ ] Generated reports include `Related Knowledge`.
- [ ] Generated issue plans include `Related Knowledge`.
- [ ] Search index and search metadata include v0.9 knowledge graph paths.
- [ ] Docs explain that historical similarity is not vulnerability
      confirmation.

## v0.9.2 Self-Ingestion Checks

- [ ] Generated Arkheionx artifacts inside `reports/` are ignored by default.
- [ ] JSON reports include `scan_sources.generated_artifacts_ignored`.
- [ ] Markdown reports include `Scan Source Summary`.
- [ ] Negative evidence does not come from generated report text.
- [ ] Repeated scans with previous outputs keep score and finding IDs stable
      unless source files changed.
- [ ] `tests/test_generated_artifact_ignore.py` passes.

## v1.0.0 Stable Public Release Checks

- [ ] README names v1.0.0 as the latest stable release.
- [ ] README documents what Arkheionx is, who it is for, what it produces, and
      how to try it in five minutes.
- [ ] Stable GitHub Action examples use the latest v1.0.x stable tag.
- [ ] `docs/CLI_REFERENCE.md` exists and matches `scripts/pre_audit_scan.py --help`.
- [ ] `docs/GITHUB_ACTION_USAGE.md` documents stable v1.0.0 inputs.
- [ ] `docs/SCHEMA_REFERENCE.md` exists.
- [ ] JSON schemas exist under `schemas/` and parse successfully.
- [ ] `docs/OUTPUT_ARTIFACTS.md` documents recommended names and generated
      artifact ignore behavior.
- [ ] `docs/V1_0_RELEASE_NOTES_DRAFT.md` exists.
- [ ] Generated artifacts are ignored by default.
- [ ] Negative evidence fixture passes.
- [ ] Self-ingestion fixture passes.
- [ ] `python3 scripts/generate_knowledge_graph.py --check` passes.
- [ ] `python3 scripts/check_docs_links.py --check` passes.
- [ ] `python3 scripts/check_version_consistency.py --check` passes.
- [ ] `python3 scripts/check_safety_wording.py` runs.
- [ ] Unit tests pass.
- [ ] Search index is up to date.
- [ ] Registry and metadata checks pass.
- [ ] `git diff --check` passes.
- [ ] No live-chain/RPC behavior added.
- [ ] No exploit automation added.
- [ ] No fake adoption, customer, or external-validation claims added.
- [ ] Release notes drafted but no tag/release/push performed.

## v1.1.0 Feedback Loop And External Calibration Checks

- [ ] Feedback issue templates exist.
- [ ] `metadata/feedback_schema.json` parses.
- [ ] `metadata/feedback_examples.json` parses and examples are synthetic or
      explicitly sourced.
- [ ] `metadata/rule_calibration_backlog.json` parses.
- [ ] `python3 scripts/generate_feedback_dashboard.py --check` passes.
- [ ] `reports/feedback_dashboard.md` exists.
- [ ] `reports/rule_calibration_backlog.md` exists.
- [ ] `docs/FEEDBACK_LOOP.md` exists.
- [ ] `docs/PUBLIC_FEEDBACK_GUIDE.md` exists.
- [ ] `docs/FEEDBACK_TRIAGE_WORKFLOW.md` exists.
- [ ] `docs/VALIDATION_LEVELS.md` exists.
- [ ] Feedback templates warn against secrets/private keys.
- [ ] Feedback templates warn against public disclosure of unpatched
      vulnerabilities.
- [ ] External validation docs distinguish toy/internal examples from public
      validation.
- [ ] No fake adoption or customer claims added.
- [ ] Docs link check passes.
- [ ] Version consistency check passes.
- [ ] Safety wording check passes.
- [ ] Unit tests pass.

## v1.2.0 Paid Offer Refinement Checks

- [ ] `docs/business/PAID_OFFER.md` exists.
- [ ] `docs/business/PRICING_LADDER.md` exists.
- [ ] `docs/business/SERVICE_PACKAGES.md` exists.
- [ ] `docs/business/CLIENT_INTAKE.md` exists.
- [ ] `docs/business/SAMPLE_SCOPE_OF_WORK.md` exists.
- [ ] `docs/business/SALES_FAQ.md` exists.
- [ ] `docs/business/PAID_WORK_BOUNDARIES.md` exists.
- [ ] `metadata/paid_offer_catalog.json` parses.
- [ ] `python3 scripts/generate_paid_offer_index.py --check` passes.
- [ ] `reports/paid_offer_index.md` exists.
- [ ] `templates/client_intake.md` exists.
- [ ] Readiness Snapshot, Pre-Audit Sprint, and Contest Readiness scope
      templates exist.
- [ ] Paid docs clearly say paid work is not a formal audit.
- [ ] Paid docs clearly say there are no security or bounty guarantees.
- [ ] README links to paid readiness support.
- [ ] Search index includes paid-offer docs and catalog.
- [ ] No customer, adoption, auditor-trust, platform-affiliation, or official
      certification claims added.
- [ ] No payment processing, CRM, email automation, live-chain, RPC, or
      offensive behavior added.
- [ ] Docs link check passes.
- [ ] Version consistency check passes.
- [ ] Safety wording check passes in strict mode.
- [ ] Unit tests pass.

## v1.3.0 Ecosystem Pack Checks

- [ ] `docs/ecosystem/ECOSYSTEM_PACK.md` exists.
- [ ] `docs/ecosystem/MULTI_REPO_READINESS_WORKFLOW.md` exists.
- [ ] `docs/ecosystem/ANONYMIZED_REPORTING.md` exists.
- [ ] `docs/ecosystem/ECOSYSTEM_READINESS_PILOT.md` exists.
- [ ] `metadata/ecosystem_pack_schema.json` parses.
- [ ] `metadata/ecosystem_pilot_example.json` parses and is clearly synthetic.
- [ ] `templates/ecosystem_intake.md` exists.
- [ ] `templates/ecosystem_readiness_pilot_scope.md` exists.
- [ ] `templates/ecosystem_manifest.example.json` exists.
- [ ] `python3 scripts/generate_ecosystem_report.py --check` passes.
- [ ] `reports/ecosystem_readiness_summary.md` exists.
- [ ] `reports/ecosystem_common_gaps.md` exists.
- [ ] Paid offer docs mention Ecosystem Readiness Pilot.
- [ ] README links ecosystem readiness workflow.
- [ ] Search index includes ecosystem readiness docs and reports.
- [ ] No remote cloning, external APIs, unauthorized repo workflow, live-chain,
      RPC, or offensive behavior added.
- [ ] No customer, adoption, partnership, endorsement, or certification claims
      added.
- [ ] Docs link check passes.
- [ ] Version consistency check passes.
- [ ] Safety wording check passes in strict mode.
- [ ] Unit tests pass.

## Safety Scan

- [ ] No live-target workflow added.
- [ ] No RPC requirement added to scanner or action.
- [ ] No transaction submission, key handling, or deployed-contract testing.
- [ ] No private keys, mnemonics, RPC credentials, or secrets in the diff.
- [ ] No banned/suspicious marketing phrases from the CI safety list.

## GitHub Surface

- [ ] Issue templates render correctly.
- [ ] GitHub Action path is correct.
- [ ] CI workflow runs scanner tests and fixture scans.
- [ ] Recommended topics reviewed in README/search guide.
- [ ] Discussions/categories updated manually if part of release.

## Release Steps

- [ ] Commit changes.
- [ ] Open release PR.
- [ ] Wait for CI green.
- [ ] Merge to `main`.
- [ ] Tag from `main` only after approval.
- [ ] Publish GitHub release from `CHANGELOG.md`.
- [ ] Announce only with honest, bounded language.

Releases are checkpoints, not finish lines.

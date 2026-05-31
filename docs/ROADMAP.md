# Roadmap

Honest. Subject to change. No commitment dates. No milestone is claimed until
committed artifacts support it.

## Product Roadmap

Arkheionx is now oriented around a local-first DeFi value-flow workbench:
map how value moves, find missing tests, and support builders and researchers
with evidence-backed local/static review artifacts.

Existing audit-prep, SARIF, CI, issue-plan, report, search, and test-plan
outputs remain supported as advanced workflows. Future work prioritizes
value-flow mapping, missing tests, developer workflow, and researcher review
maps.

Current milestone: v2.10.0.
Latest stable: v2.9.0 — Multi-Fixture Demo Expansion & Public Workflow Hardening.
Foundation shipped: v2.9.0 — Multi-Fixture Demo Expansion & Public Workflow Hardening; v2.8.0 — Package Data & Distribution Hardening; v2.7.0 — Guided Demo Fixtures & First Real Workflow; v2.6.0 — arkup & Version-Manager MVP; v2.5.0 — Installer & Onboarding; v2.4.0 — Evidence Workflow Hardening; v2.3.0 — Evidence & Report Package; v2.2.0 — Execution Proof & Trace Workbench; v2.1.0 — Value Flow Map MVP.
v3.0.0 target: DeFi Value Flow Workbench.

- [x] **v0.1.0: Scanner MVP shipped.** Local scanner, GitHub Action, Markdown report,
      JSON report, mini-vault fixture, safe invariant skeleton generator.
- [x] **v0.2.0: Vault rule pack shipped.** ERC4626 and vault-accounting
      signals, vault-specific scoring, Vault Rule Pack reports, vault-risk
      fixture, scanner tests, and vault service path.
- [x] **v0.3.0: GitHub Action UX shipped.** GitHub Step Summary output,
      optional PR comment mode, generated issue checklist, stable finding IDs,
      local config suppression, and external repo onboarding docs.
- [x] **v0.4.0: SARIF output and report diff mode released.** SARIF output
      marked as readiness notes/warnings, baseline JSON, diff-aware summaries,
      stable fingerprints, and optional readiness gates.
- [x] **v0.4.1: Public polish and release consistency shipped.**
      README onboarding, stable action examples, docs consistency checks, and
      public first-impression cleanup.
- [x] **v0.5.0: Generated GitHub issue workflow and rule-pack expansion shipped.**
      Structured issue plans, dry-run/create/update issue workflow, oracle,
      access/upgradeability, reentrancy/value-flow, and reward accounting rule
      packs.
- [x] **v0.6.0: Semantic-lite Solidity extraction and false-positive reduction shipped.**
      Evidence-based findings, optional local Slither integration, source
      structure extraction, smarter affected-function mapping, SARIF location
      improvements, and rule calibration.
- [x] **v0.7.0: Launch Report OS and Contest Readiness Mode shipped.**
      Client-facing Launch Reports, Pre-Audit Sprint plans, Contest Readiness
      reports, executive summaries, remediation roadmaps, and paid-service
      delivery workflow artifacts.
- [x] **v0.8.0: External validation, public demos, and rule calibration shipped.**
      Public demo workflow, case-study style sample reports, external feedback
      templates, false-positive calibration workflow, and honest outreach
      material.
- [x] **v0.9.0: Security Memory Graph and search upgrade released.**
      Finding knowledge map, local security memory graph, rule calibration
      matrix, search helper CLI, and Related Knowledge report integration.
- [x] **v0.9.1: Negative evidence detection and score calibration released.**
      Missing-test comments no longer inflate coverage evidence or readiness
      scores.
- [x] **v0.9.2: Generated artifact ignore and self-ingestion guard released.**
      Previous Arkheionx outputs are ignored as source evidence by default.
- [x] **v1.0.0: Stable public release, schema freeze, and production-ready documentation released.**
      Stable CLI/action interface, schema freeze, docs freeze, calibrated rule
      packs, release artifacts, and contribution workflow.
- [x] **v1.0.1: Docs link validation hotfix released.**
      Documentation link validation and release consistency checks.
- [x] **v1.1.0: Feedback Loop and External Calibration released.**
      Public feedback triage, false-positive and false-negative workflows,
      feedback dashboard, validation levels, and rule calibration backlog
      without unsupported adoption claims.
- [x] **v1.1.1: Public Surface Polish released.**
      README front-page clarity, repository About guidance, topic
      recommendations, and onboarding path cleanup before the next major
      service-packaging milestone.
- [x] **v1.2.0: Paid Offer Refinement released.**
      Clearer Launch Report, Pre-Audit Sprint, and Contest Readiness service
      packaging tied to generated artifacts, client intake, pricing guidance,
      and paid-work boundaries.
- [x] **v1.3.0: Ecosystem Pack released.**
      Multi-repository readiness workflows and standardized Markdown reporting
      for authorized ecosystem support.
- [x] **v1.4.0: AMM + Lending Protocol Packs released.**
      Defensive readiness rule packs, fixtures, reports, and knowledge mappings
      for AMM and lending protocol shapes.
- [x] **v1.5.0: Invariant/Test Plan Generator Upgrade released.**
      Finding-to-test-plan mapping, defensive test-plan generator, and safe
      Foundry starter skeletons for readiness findings.
- [x] **v1.6.0: Internal Engine Split released.**
      Internal package scaffold, shared helper modules, rule registry metadata,
      generator extraction, and preview CLI health commands without changing
      the stable script surface.
- [x] **v1.7.0: Config + Rule Pack Stabilization released.**
      Stable config schema, safe validator, suppression references, config
      examples, and rule-pack registry helpers.
- [x] **v1.8.0: Report UX + Noise Reduction released.**
      Improve report clarity, Fix First prioritization, output profiles,
      suppression visibility, and developer-facing summaries after config
      behavior is stable.
- [x] **v1.9.0: Pre-v2 CLI Candidate released.**
      Prepare the installable CLI surface while preserving stable scripts,
      schemas, GitHub Action usage, and local/static safety boundaries.
- [x] **v2.0.0: Installable Arkheionx CLI / Package released.**
      Local editable installation, `arkheionx` console entrypoint, module CLI,
      old script compatibility, and packaging hygiene.
- [x] **v2.0.1: Packaging + Product Repositioning Hotfix shipped.**
      Reframed Arkheionx as a local-first DeFi value-flow workbench while
      preserving existing CLI, report, SARIF, issue-plan, test-plan, and CI
      workflows.
- [x] **v2.1.0: Value Flow Map MVP shipped (Foundry-style workbench CLI).**
      Local/static protocol map, money-flow graph, hunter ranking, source-kind
      filtering, fully-qualified targets, and proof scaffolding.
- [x] **v2.2.0: Execution Proof & Trace Workbench shipped.**
      Targeted Foundry execution proof, structured proof artifacts, trace
      summaries, and honest evidence levels.
- [x] **v2.3.0: Evidence & Report Package shipped.**
      Package proof/trace into a structured evidence package and a responsible
      local report draft (no auto-submit, no final severity).
- [x] **v2.4.0: Evidence Workflow Hardening shipped.**
      evidence-status, validate-artifacts, artifact index, report readiness,
      and a stronger next-command chain.
- [x] **v2.5.0: Installer & Onboarding shipped.**
      Safe local `install.sh`/`uninstall.sh`, `doctor --install` health view,
      and first-run onboarding docs (no PyPI, no sudo, no profile edits).
- [x] **v2.6.0: arkup & Version-Manager MVP shipped.**
      `arkup` lifecycle helper, local install receipt, stable/main/ref/local
      source model, and explicit update flow (no PyPI, no Homebrew, no binaries).
- [x] **v2.7.0: Guided Demo Fixtures & First Real Workflow shipped.**
      `arkheionx demo` (list/show/commands/copy), a demo fixture registry, and a
      safe local first-run workflow (no RPC, no secrets, no mainnet).
- [x] **v2.8.0: Package Data & Distribution Hardening shipped.**
      Demo fixtures bundled as package data, resolved via importlib.resources so
      `arkheionx demo --copy` works from an installed package (no PyPI claim).
- [x] **v2.9.0: Multi-Fixture Demo Expansion & Public Workflow Hardening shipped.**
      Adds amm-swap and lending-vault bundled demos, demo registry category/risk
      metadata, and broader first-use workflow coverage (local-only toy demos).
- [ ] **v2.3.0: Evidence & Report Package next milestone.**
      Package execution-confirmed evidence into reviewer-ready report drafts.
- [ ] **v2.4.0: Flow-Based Foundry Test Templates.**
      Generate safe local starter templates from mapped flows.
- [ ] **v2.5.0: Researcher Review Map.**
      Prioritize high-signal review areas for security researchers and junior
      reviewers.
- [ ] **v2.6.0: Flow Verify / Before-After.**
      Compare whether local changes address mapped flow assumptions and test
      gaps.
- [ ] **v2.7.0: Flow Baseline + Diff.**
      Track mapped value-flow changes over time.
- [ ] **v2.8.0: AI-Agent Fix Specs from Value Flows.**
      Produce bounded, defensive implementation specs for authorized local
      AI-agent work.
- [ ] **v2.9.0: Pre-v3 Hardening.**
      Stabilize docs, tests, CLI UX, and safety language before v3.
- [ ] **v3.0.0: DeFi Value Flow Workbench target.**
      Value-flow maps, missing tests, explain mode, Foundry templates,
      researcher review maps, verify/before-after, and diff workflows.

## Archive Roadmap

- [ ] Continue improving weak assertion PoCs to medium or strong.
- [ ] Produce L4 archival-confirmed reports only when archival run evidence is
      committed.
- [ ] Publish L5 case studies only after the underlying entry reaches L4.
- [ ] Keep EVM/Foundry active and honest.
- [ ] Graduate SVM/Anchor and MoveVM/Aptos from scaffold only when real
      entries exist.

## Market Roadmap

- [x] GitHub-native service surface in `SERVICES.md`.
- [x] Sponsor and monetization docs.
- [x] Issue forms for readiness requests, Launch Reports, Pre-Audit Sprints,
      false positives, and rule requests.
- [ ] GitHub Discussions categories for support, rule requests, release notes,
      and sponsor updates.
- [ ] First public Launch Report sample beyond the toy fixture.
- [ ] First ecosystem-ready portfolio dashboard template.

## Explicitly Not On The Roadmap

- Live-target workflows.
- Deployed-contract attack automation.
- Private key, mnemonic, or secret handling.
- A separate SaaS dashboard.
- A separate website.
- Inflated verification claims.
- Claims that scanner output proves protocol safety.
- Sponsor influence over taxonomy, severity, inclusion, or verification status.

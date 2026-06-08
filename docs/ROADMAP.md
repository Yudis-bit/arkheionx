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

Current milestone: v5.0.0.
Next milestone: v5.1.0.
Latest stable: v5.0.0 — Blind Spot Intelligence.

## v5.0 — Blind Spot Intelligence (finalized locally)

v5.0 is the first **major** step beyond mapping. v4 maps the protocol; **v5 maps
where research attention is weakest relative to how much could go wrong.** It adds
a Blind Spot Intelligence layer on top of the stable review-map and v4.1
research-memory workflow:

- `arkheionx blind-spots` — rank likely blind-spot candidates (high-impact
  surfaces with weak review evidence) with a transparent additive score.
- `arkheionx criticality-map` — map criticality potential (heuristic blast
  radius, not severity) across every surface.
- `arkheionx counterfactuals` — negate guarding assumptions into testable
  research prompts ("what if this assumption is false?").
- `arkheionx research-pack` — bundle the above with an agent brief, hypotheses,
  an evidence log, and a do-not-claim file into one local, vendor-agnostic pack.

It adds no RPC, no live-chain action, no exploit automation, and no severity or
vulnerability claims. Blind spot candidates are review prompts; criticality
potential is not severity; human review is required. The package version is now
`5.0.0`; the `v5.0.0` tag, GitHub Release, and site deploy are founder actions
(the last published tag remains `v4.0.0`, the installer-pinned stable remains
`v3.1.0`). See [`BLIND_SPOT_INTELLIGENCE.md`](BLIND_SPOT_INTELLIGENCE.md) and
[`V5_WORKFLOW.md`](V5_WORKFLOW.md).

## v5.1 — Blind spot precision (planned)

v5.1 is planned direction: tighten the blind-spot scoring with real-protocol
calibration, deepen authorization and periphery/behavior-mismatch detection, and
reduce false-priority surfaces. No dates; no commitment until committed artifacts
support it.

## v4.1 — Research memory (finalized locally)

v4.1 extends the stable v4.0 review-map workflow into an AI-assisted **research
memory** layer, built on real bug bounty / competition workflow feedback. The
lesson: ArkheionX is most useful as a workflow layer, not a bug finder —
ArkheionX gives the map, an agent grinds the tests, the research memory keeps the
evidence, and the human makes the final call.

Finalized v4.1 branch work (local/static, additive). The package version is now
`4.1.0`; the `v4.1.0` tag, GitHub Release, and site deploy are founder actions
(the last published tag remains `v4.0.0`, the installer-pinned stable remains
`v3.1.0`):

- `arkheionx agent-brief` — an AI-agent-ready review brief.
- `arkheionx hypothesis-log` — a structured hypothesis log and rejected-finding
  memory (rejected hypotheses are useful evidence).
- `arkheionx case-study` — a sanitized research-session report.
- A research surface engine: coverage weakness ranking, authorization-surface
  detection (signature / Merkle / role / gate / domain / nonce / deadline),
  periphery-to-core flow mapping, and behavior-mismatch heuristics.

It adds no RPC, no live-chain action, no exploit automation, and no severity or
vulnerability claims. Hypotheses are review prompts; human review is required.
See [`V4_1_RESEARCH_WORKFLOW.md`](V4_1_RESEARCH_WORKFLOW.md) and
[`RESEARCH_MEMORY_MODEL.md`](RESEARCH_MEMORY_MODEL.md).

Foundation shipped: v3.1.0 — Protocol Review Map; v3.0.0 — Public Stable Launch; v2.10.0 — Pre-v3 Public Readiness & Stability Hardening; v2.9.0 — Multi-Fixture Demo Expansion & Public Workflow Hardening; v2.8.0 — Package Data & Distribution Hardening; v2.7.0 — Guided Demo Fixtures & First Real Workflow; v2.6.0 — arkup & Version-Manager MVP; v2.5.0 — Installer & Onboarding; v2.4.0 — Evidence Workflow Hardening; v2.3.0 — Evidence & Report Package; v2.2.0 — Execution Proof & Trace Workbench; v2.1.0 — Value Flow Map MVP.
v3.0.0 target: DeFi Value Flow Workbench. v3.0.0 shipped as the public stable
launch and v3.1.0 — Protocol Review Map shipped as the v3 stable review surface
(a structured, developer-native review surface built on the workbench). The
latest stable release is now v5.0.0 — Blind Spot Intelligence.
v3.2.0 is finalized locally as the Developer-Native Review Map and Local Artifact
Foundation. v3.3.0 is finalized locally as Focused Review Commands:
`test-gap-map`, `value-paths`, `assumptions`, `proof-plan`, and
`evidence-links`. v3.4.0 is finalized locally as deeper proof and evidence
workflow; it has not been pushed, published, or post-release cleaned up.
v3.5.0 — Protocol Intelligence Model is finalized locally: an internal, additive
Protocol Intelligence Model (stable IDs and dataclasses built from existing
`analyze()` / `review-map` output) is complete on the v3.5 branch with a local
`v3.5.0` tag. It has not been pushed, published, or post-release cleaned up, and
it adds no new public command or schema.
v3.6.0 — Review Package Workspace (`arkheionx review-package`) is finalized
locally: a local, reviewer-ready package with a checksummed manifest, strict
validation, a deterministic local export, and a protocol-model sidecar with
exact-match cross-reference checks. It has a local `v3.6.0` tag and has not been
pushed, published, or post-release cleaned up; see
[`REVIEW_PACKAGE.md`](REVIEW_PACKAGE.md). v3.7.0 — Foundry / Local Validation
Integration is finalized locally: saved Foundry-output ingestion via
`arkheionx local-validate`, review-package inclusion of local-validation
artifacts, and evidence/report supporting context. It reads saved output only and
does not run `forge`, has a local `v3.7.0` tag, and has not been pushed,
published, or post-release cleaned up. The next milestone is v3.8.0; the broader
Foundry-coverage lane and the Rule Packs lane are resequenced to later
milestones. See [`LOCAL_VALIDATION.md`](LOCAL_VALIDATION.md).

On the active v3.8.0 branch — **Protocol Intelligence Core Machine Leverage** —
the internal `arkheionx/intelligence/` engines (function roles, value paths,
assumptions, test gaps, a protocol graph builder, and local-validation coverage
correlation) are connected into one deterministic review surface, with optional
protocol-graph context in evidence/report drafts and optional protocol-graph
artifact inclusion in the review package. This milestone prioritizes core review
depth over new UI or command surface: it adds no new public command, no new CLI
flags, and no metadata change beyond the milestone bump, and keeps exact-only
linking with deterministic IDs. It does not confirm vulnerabilities, assign a
final severity, claim an audit passed, or establish bounty-eligibility. v3.8.0 is
finalized locally with a local annotated `v3.8.0` tag and a verified local backup
bundle — not pushed, not published, with no GitHub Release and no post-release
cleanup; the latest stable release remains `v3.1.0` (unchanged) and v3.9.0
followed as the next milestone. See
[`PROTOCOL_INTELLIGENCE_CORE.md`](PROTOCOL_INTELLIGENCE_CORE.md),
[`PROTOCOL_GRAPH_WORKFLOW.md`](PROTOCOL_GRAPH_WORKFLOW.md), and
[`REVIEW_PACKAGE.md`](REVIEW_PACKAGE.md).

v3.9.0 — **Core Machine Hardening** is finalized locally: an internal, additive
fixture benchmark harness (`arkheionx/fixture_harness/`) with a deterministic
benchmark runner, committed benchmark snapshot baselines, three local/static
illustrative fixture sets (nine fixtures), a combined all-fixtures benchmark
suite, standalone benchmark crossrefs, and a fixture-harness QA gate. It is a
deterministic regression and review surface only: it adds no new public command,
no new CLI flag, and no public schema, keeps exact-only linking with deterministic
IDs, and does not confirm vulnerabilities, assign a final severity, claim an audit
passed, or establish bounty-eligibility. v3.9.0 is finalized locally with a local
annotated `v3.9.0` tag and a verified local backup bundle — not pushed, not
published, with no GitHub Release and no post-release cleanup; the latest stable
release remains `v3.1.0` (unchanged) and the next milestone is v4.0.0. See
[`FIXTURE_HARNESS.md`](FIXTURE_HARNESS.md),
[`FIXTURE_BENCHMARKS.md`](FIXTURE_BENCHMARKS.md), and
[`FIXTURE_SNAPSHOT_WORKFLOW.md`](FIXTURE_SNAPSHOT_WORKFLOW.md).

Pre-v3 readiness is tracked in [`V3_READINESS.md`](V3_READINESS.md); the public
command contract is in [`PUBLIC_SURFACE.md`](PUBLIC_SURFACE.md) and
[`STABILITY_CONTRACT.md`](STABILITY_CONTRACT.md).

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
- [x] **v3.0.0: Public Stable Launch shipped.**
      Coherent local workflow, stable command surface, honest evidence levels,
      and a safe install/update lifecycle.
- [x] **v3.1.0: Protocol Review Map shipped.**
      `arkheionx review-map`: contracts, value paths, assumptions, test gaps,
      proof suggestions, and evidence links, written as JSON/Markdown artifacts.
      Local/static and heuristic by default; review guidance, not findings.
- [x] **v3.2.0: Developer-Native Review Map and Local Artifact Foundation shipped.**
      TerminalUI-backed `open` / `review-map` output, Test Gap Map artifacts,
      public docs clarification, preserved JSON/no-write compatibility, and
      deferred governance for schema dialects, evidence aliases, artifact
      validation exit codes, and committed workspace policy.
- [x] **v3.3.0: Focused Review Commands.**
      Promote key review-map artifacts into first-class focused commands:
      `test-gap-map`, `value-paths`, `assumptions`, `proof-plan`, and
      `evidence-links`. This builds on the v3.2.0 local artifact foundation
      without treating v4 workspace/control-plane features as shipped.
- [x] **v3.4.0: Proof and Evidence Workflow.**
      Deepen `prove` / `trace` / `evidence` / `report` with trace-bounded
      evidence readiness, evidence package manifests, report receipt linkage,
      and enriched read-only evidence-link backfill. Release prep and QA have
      passed; final local release metadata and local tag are complete.
- [x] **v3.5.0: Protocol Intelligence Model.**
      Introduce shared internal model and stable IDs so command outputs can
      derive from one model without changing the local/static safety boundary.
      Implemented additively and internal-only (no new public command, no public
      schema break); QA gate passed and the release is finalized locally with a
      local `v3.5.0` tag, not pushed or published.
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

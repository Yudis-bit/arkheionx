# Arkheionx Paid Offer Index

Generated from `metadata/paid_offer_catalog.json`.

Paid Arkheionx work is a readiness engagement, not a formal audit.
It helps teams prepare authorized repositories for audits, contests,
and bug bounty launches by turning readiness gaps into reports, issue
plans, and remediation workflows.

No paid offer includes live-chain scanning, transaction execution,
private key handling, exploit automation, security guarantees, bounty
guarantees, or formal audit sign-off.

## Offer Summary

| Offer | Starting price | Typical range | Duration |
|---|---:|---|---|
| Arkheionx Readiness Snapshot | USD 500 | Pilot: $500-$1,000; standard: $1,000-$2,500 | 1-2 business days after intake and repository access are ready. |
| Arkheionx Pre-Audit Sprint | USD 2,500 | Pilot: $2,500-$5,000; standard: $5,000-$12,000 | 3-5 business days, with optional follow-up calibration when scoped. |
| Contest Readiness Pack | USD 1,500 | $1,500-$6,000 | 2-4 business days depending on repository and documentation size. |
| GitHub Action Setup | USD 500 | $500-$2,500 | 1-2 business days after repository workflow access is ready. |
| Ecosystem Readiness Pilot | USD 5,000 | Pilot: $5,000-$15,000; expanded: $15,000-$40,000+ | Scoped pilot across 3-5 repositories; expanded engagement across 5-10 authorized repositories. |

## Arkheionx Readiness Snapshot

- Offer ID: `readiness-snapshot`
- Audience: DeFi founders and small teams that need a quick pre-audit readiness picture.
- Starting price: USD 500
- Typical range: Pilot: $500-$1,000; standard: $1,000-$2,500
- Duration: 1-2 business days after intake and repository access are ready.

Small, fast readiness engagement that runs Arkheionx on an authorized repository and turns obvious blockers into a short report and issue plan.

### Deliverables

- Pre-Audit Readiness Report
- Executive Summary
- GitHub-native Issue Plan
- Top 5-10 readiness gaps
- 30-minute walkthrough

### Required Inputs

- Authorized repository URL or archive
- Protocol type and primary concerns
- Audit, contest, or launch timeline
- Existing test and documentation commands

### Not Included

- Formal audit
- Exploit PoC development
- Live-chain testing
- Unlimited remediation support

### Safety Boundaries

- Local/static repository review only
- No private keys, mnemonics, RPC secrets, or API tokens
- No public disclosure of unpatched vulnerability details
- Findings are readiness signals and review recommendations

### Recommended For

- First-pass audit preparation
- Small teams that need a concise blocker list
- Repositories that already build and test locally

### Not Recommended For

- Emergency incident response
- Formal audit sign-off
- Teams seeking exploit development or live-target testing

## Arkheionx Pre-Audit Sprint

- Offer ID: `pre-audit-sprint`
- Audience: Teams preparing for a formal audit, contest, or bug bounty launch.
- Starting price: USD 2,500
- Typical range: Pilot: $2,500-$5,000; standard: $5,000-$12,000
- Duration: 3-5 business days, with optional follow-up calibration when scoped.

Three-to-five day guided readiness workflow that turns scanner output into prioritized remediation, invariant/test planning, and audit handoff artifacts.

### Deliverables

- Pre-Audit Report
- SARIF output
- GitHub Issue Plan
- Remediation Roadmap
- Contest Readiness Report
- Suggested invariant/test plan
- 60-90 minute walkthrough
- Optional follow-up calibration pass

### Required Inputs

- Authorized repository access
- Build and test instructions
- Protocol architecture notes
- Known limitations and open security questions
- Audit/contest/bounty timeline

### Not Included

- Formal audit sign-off
- Security guarantee
- Exploit development
- Emergency incident response

### Safety Boundaries

- Authorized repository evaluation only
- Local/static analysis and human-guided readiness review
- No deployed-contract scanning
- No exploit payload generation

### Recommended For

- Teams within 1-4 weeks of audit intake
- Protocols with missing invariants or documentation gaps
- Teams that want GitHub-native remediation tasks

### Not Recommended For

- Protocols requiring full audit coverage
- Live incident handling
- Unauthorized third-party repositories

## Contest Readiness Pack

- Offer ID: `contest-readiness-pack`
- Audience: Teams preparing for an authorized audit contest, bug bounty launch, or public security review.
- Starting price: USD 1,500
- Typical range: $1,500-$6,000
- Duration: 2-4 business days depending on repository and documentation size.

Repository and documentation readiness package focused on scope clarity, researcher onboarding, and obvious audit blockers before external review.

### Deliverables

- Contest Readiness Report
- Scope clarity review
- Documentation gap review
- Issue Plan
- Researcher onboarding notes
- Common audit-blocker list

### Required Inputs

- Authorized repository
- Candidate in-scope and out-of-scope contract list
- Build/test instructions
- Known issues and limitations safe to document
- Planned review timeline

### Not Included

- Contest strategy for exploiting systems
- Bounty outcome promises
- Platform endorsement
- Formal audit

### Safety Boundaries

- No endorsement or affiliation with named contest platforms
- No live-target testing
- No exploit steps for active systems
- Respect platform and responsible disclosure rules

### Recommended For

- Teams opening an authorized external review
- Maintainers that want cleaner scope docs
- Protocols with incomplete researcher onboarding

### Not Recommended For

- Bounty farming
- Bypassing contest rules
- Unpatched vulnerability disclosure in public channels

## GitHub Action Setup

- Offer ID: `github-action-setup`
- Audience: Teams that want Arkheionx readiness checks in CI.
- Starting price: USD 500
- Typical range: $500-$2,500
- Duration: 1-2 business days after repository workflow access is ready.

Implementation support for adding the Arkheionx GitHub Action, artifacts, SARIF, config, and safe threshold guidance to an authorized repository.

### Deliverables

- GitHub Action integration
- SARIF output setup
- Report artifact setup
- Config/suppression setup
- Recommended readiness thresholds
- Short handoff guide

### Required Inputs

- Authorized GitHub repository
- Current CI workflow constraints
- Preferred artifact paths
- Desired readiness gates

### Not Included

- GitHub organization administration
- Secret management
- Custom CI platform migration
- Remote issue creation unless explicitly scoped

### Safety Boundaries

- No GitHub token collection by Arkheionx docs or scripts
- No external API integration beyond user-controlled GitHub workflows
- Issue creation remains opt-in and token-scoped
- No network dependency for default scan

### Recommended For

- Teams already using GitHub Actions
- Repositories that want SARIF and report artifacts
- Builders who want baseline/diff tracking

### Not Recommended For

- Teams requiring non-GitHub CI automation
- Repositories without authorization to install workflows

## Ecosystem Readiness Pilot

- Offer ID: `ecosystem-readiness-pilot`
- Audience: Chain ecosystems, grant programs, accelerators, venture studios, and audit-prep cohorts supporting multiple authorized DeFi builders.
- Starting price: USD 5,000
- Typical range: Pilot: $5,000-$15,000; expanded: $15,000-$40,000+
- Duration: Scoped pilot across 3-5 repositories; expanded engagement across 5-10 authorized repositories.

Multi-repository readiness pilot that uses local Arkheionx reports to produce repo-by-repo summaries, anonymized common gaps, rule-family heatmaps, and ecosystem-level remediation themes.

### Deliverables

- Ecosystem Readiness Summary
- Repo-by-Repo Readiness Table
- Common Gap Report
- Rule-Family Heatmap
- Anonymized Recommendations
- GitHub Action Setup Recommendations
- Feedback and Calibration Notes
- 60-90 minute ecosystem walkthrough

### Required Inputs

- Written authorization for every repository
- Scope list and repository contacts
- Preferred anonymity and reporting rules
- Program timeline
- Local Arkheionx JSON reports or repository access method agreed privately

### Not Included

- Formal audit
- Vulnerability certification
- Exploit development
- Live-chain testing
- Emergency incident response
- Public claims without permission
- Reviewing unauthorized repositories

### Safety Boundaries

- Authorized repositories only
- No public naming without explicit permission
- No private code or vulnerability disclosure in public artifacts
- Anonymized summaries must not reveal sensitive project details
- No live-chain behavior

### Recommended For

- Ecosystems exploring standardized readiness support
- Grant programs that want repeatable Markdown artifacts
- Accelerators with several authorized DeFi repos
- Audit-prep cohorts that need shared readiness themes

### Not Recommended For

- Programs needing formal certification
- Large portfolios without scoped authorization
- Public marketing claims without consent
- Remote scanning of repositories without authorization

## Inquiry Path

Start with `templates/client_intake.md` and the relevant scope
template under `templates/`. Share only repositories you own or are
authorized to evaluate. Do not paste secrets, private keys, mnemonics,
RPC credentials, API tokens, or unpatched vulnerability details into
public channels.

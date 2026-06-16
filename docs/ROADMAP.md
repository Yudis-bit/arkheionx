# Roadmap

ArkheionX is local-first review infrastructure for smart contract security.

This roadmap is about credibility, not hype. No date is guaranteed. No milestone is claimed until the repository proves it.

Current milestone: v10.1.0-dev.
Next milestone: v10.1.0.
Latest stable: v8.0.1.

## Direction

The next stage is not random feature expansion.

The next stage is:

- real usage on established DeFi protocols;
- external reviewer feedback;
- protocol-team feedback;
- clear case studies;
- lower-noise outputs;
- better installation and docs;
- honest versioning and repository identity cleanup.

## Near term

1. Keep the public docs navigable.
2. Reframe the repository identity around ArkheionX.
3. Collect feedback from auditors and protocol teams.
4. Add case studies only when the workflow evidence is real.
5. Reduce noisy or vague output language.
6. Keep CLI behavior stable.
7. Preserve local-first and human-review-required boundaries.

## Validation roadmap

| stage | goal | evidence needed |
|---|---|---|
| Internal fixtures | Keep deterministic regression confidence. | Tests, fixtures, generated example artifacts. |
| Public demo review | Let external reviewers inspect output safely. | Demo output feedback. |
| Public repo trial | Run on authorized public protocol code. | Commands, outputs, reviewer notes. |
| Private authorized trial | Get protocol-team or auditor feedback. | Anonymized or permissioned notes. |
| Case study | Show how ArkheionX helped a real review workflow. | Target, context, evidence, human validation, limitations. |
| Independent evaluations | Let external reviewers reproduce value. | Multiple public evaluations or permissioned summaries. |

## Non-goals

ArkheionX should not claim:

- automatic vulnerability discovery;
- auditor replacement;
- final severity automation;
- bounty outcome guarantees;
- Ethereum Foundation endorsement;
- enterprise readiness without proof;
- live-chain exploit automation;
- safety certification.

## Current blocker

The public repository has been renamed to `Yudis-bit/arkheionx`. The old `DeFi-Exploit-PoCs` slug may remain only in historical documents, archived material, generated artifacts, or compatibility notes.

See [`REPO_IDENTITY_MIGRATION.md`](REPO_IDENTITY_MIGRATION.md).

## Current credibility gaps

- More real-protocol usage is needed.
- External reviewer feedback is needed.
- Protocol-team feedback is needed.
- Case studies need reproducible evidence.
- Documentation still contains historical version material.
- Some tests and scripts still assert older public-surface assumptions.

## Historical milestone index

This compact history is preserved for release and version checks.

- v0.1.0: Scanner MVP shipped.
- v0.2.0: Vault rule pack shipped.
- v0.3.0: GitHub Action UX shipped.
- v0.4.0: SARIF output and report diff mode released.
- v0.4.1: Public polish and release consistency shipped.
- v0.5.0: Generated GitHub issue workflow and rule-pack expansion shipped.
- v0.6.0: Semantic-lite Solidity extraction and false-positive reduction shipped.
- v0.7.0: Launch Report OS and Contest Readiness Mode shipped.
- v0.8.0: Public demo workflow shipped.
- v1.0.0: Stable public release.
- v1.2.0: Paid Offer Refinement released.
- v1.3.0: Ecosystem Pack released.
- v1.4.0: AMM + Lending Protocol Packs released.
- v1.5.0: Invariant/Test Plan Generator Upgrade released.
- v1.6.0: Internal Engine Split released.
- v1.7.0: Config + Rule Pack Stabilization released.
- v1.8.0: Report UX + Noise Reduction released.
- v1.9.0: Pre-v2 CLI Candidate released.
- v2.0.0: Installable Arkheionx CLI / Package released.
- v2.1.0 — Value Flow Map MVP.
- v2.2.0: Execution Proof & Trace Workbench shipped.
- v2.3.0: Evidence & Report Package shipped.
- v2.4.0: Evidence Workflow Hardening shipped.
- v2.5.0: Installer & Onboarding shipped.
- v2.6.0 — arkup & Version-Manager MVP.
- v2.7.0 — Guided Demo Fixtures & First Real Workflow.
- v2.8.0 — Package Data & Distribution Hardening.
- v2.9.0 — Multi-Fixture Demo Expansion & Public Workflow Hardening.
- v2.10.0 — Pre-v3 Public Readiness & Stability Hardening.
- v3.0.0 DeFi Value Flow Workbench target.
- v3.0.0 — Public Stable Launch.
- v3.1.0 — Protocol Review Map.
- v4.0.0 — Stable local review-map workflow.
- v4.1.0 — Research memory.
- v5.0.0 — Blind Spot Intelligence.
- v6.0.0 — Evidence Graph and Interaction Matrix.
- v7.0.0 — Scope-Aware Orchestration.
- v7.5.0 — Protocol Lens Packs.
- v8.0.0 — One-command review pack.
- v8.0.1 — Clean Product Surface.
- v10.1.0-dev — current development milestone in this checkout.

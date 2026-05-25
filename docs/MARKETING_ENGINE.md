# Marketing Engine

Arkheionx can grow without a website. GitHub is the landing page, product,
support channel, sales surface, distribution system, and public proof.

## Market Thesis

Indie DeFi builders need security preparation before they can afford or
schedule formal audits.

They do not need fear-based marketing. They need a practical way to find
missing invariants, unclear assumptions, weak tests, and audit blockers while
their protocol is still cheap to change.

## Positioning

Arkheionx is not a substitute for a formal audit.

Arkheionx is a pre-audit readiness layer:

> Historical DeFi failures turned into practical GitHub-native readiness
> checks for the next generation of indie protocols.

## Core Message

> Before you spend thousands on a formal audit, check if your protocol is
> audit-ready.

Short version:

> Not an audit. A way to prepare for one.

## Audience Segments

- Solo DeFi founder.
- Hackathon winner.
- Grant-funded builder.
- Small DAO.
- Vault builder.
- L2 ecosystem.
- Accelerator.
- Junior security researcher.

## GitHub-Only Funnel

Discovery:

- GitHub search;
- GitHub topics;
- X posts;
- LinkedIn posts;
- Discord and Telegram builder communities;
- hackathons;
- L2 grant communities;
- audit-preparation conversations.

Activation:

- user copies GitHub Action;
- user runs local CLI;
- user opens the mini-vault sample report.

Value:

- user receives a Markdown report;
- user sees top readiness gaps;
- user gets suggested invariant skeletons;
- user has a checklist for formal audit prep.

Conversion:

- user opens a GitHub issue for Launch Report or Pre-Audit Sprint;
- sponsor clicks GitHub Sponsors;
- ecosystem asks about a readiness pack.

Retention:

- Sponsors receive updates;
- Discussions collect Q&A;
- rule requests improve the scanner;
- examples and reports compound.

Expansion:

- Ecosystem Pack for L2s, accelerators, hackathons, and grant programs.

## Content Engine

Weekly:

- one historical exploit lesson;
- one readiness checklist;
- one invariant testing tip;
- one founder-focused security post.

Monthly:

- research dashboard update;
- sponsor update;
- new rule pack;
- sample report;
- roadmap note.

## v0.2.0 Vault Launch Message

Primary v0.2.0 message:

> Arkheionx v0.2.0 focuses on indie vault builders: ERC4626-like readiness
> checks, share/accounting gaps, missing invariants, withdrawal lifecycle
> risks, and oracle-dependent vault review prompts.

Short version:

> Building a vault? Arkheionx v0.2.0 helps you find missing share-accounting,
> strategy, withdrawal, fee, and oracle readiness gaps before formal audit.

CTA:

> Run the GitHub Action with `protocol-type: vault` and read the generated
> Markdown report.

## v0.3.0 GitHub Action UX Message

Primary v0.3.0 message:

> Arkheionx v0.3.0 makes pre-audit readiness visible where indie builders
> already work: GitHub Actions summaries, optional PR comments, generated issue
> checklists, stable finding IDs, and local config suppressions.

Short version:

> Run Arkheionx in a pull request and get a readiness score, top gaps, and a
> remediation checklist without leaving GitHub.

CTA:

> Add the GitHub Action, keep PR comment mode off by default, then enable it
> when your team wants readiness feedback directly in code review.

## v0.4.0 SARIF And Baseline Diff Message

Primary v0.4.0 message:

> Arkheionx v0.4.0 brings pre-audit readiness into GitHub security workflows:
> SARIF output, baseline snapshots, diff reports, stable finding fingerprints,
> and explicit CI gates that stay disabled by default.

Short version:

> Track new, resolved, and unchanged readiness gaps across pull requests. Still
> not an audit. A GitHub-native way to prepare for one.

CTA:

> Generate SARIF for Code Scanning, save a baseline, and use diff mode to show
> readiness progress before formal audit intake.

## v0.5.0 Issue Workflow And Rule Pack Message

Primary v0.5.0 message:

> Arkheionx v0.5.0 turns readiness gaps into GitHub-native remediation plans:
> generated issue-plan JSON, dry-run issue creation, duplicate-safe markers,
> and expanded oracle, access control, reentrancy, and reward accounting rule
> packs.

Short version:

> Scan, review the issue plan, dry-run it, then choose whether to create
> owner-ready GitHub tasks. Still not an audit. A way to prepare for one.

CTA:

> Generate an Arkheionx issue plan and use it as the starting point for a
> Launch Report or Pre-Audit Sprint remediation plan.

## Example X Posts

0. Arkheionx v0.2.0 is vault-focused: ERC4626-like checks, share/accounting
   readiness gaps, missing invariants, withdrawal lifecycle prompts, strategy
   accounting checks, and oracle-dependent vault review guidance. Not an audit.
   A way to prepare for one.

1. Most indie DeFi builders cannot afford a formal audit on day one. Arkheionx
   helps them get audit-ready first: missing invariants, exploit-pattern risks,
   and launch blockers, all inside GitHub. Not an audit. A way to prepare for
   one.

2. A vault without roundtrip tests is not ready for audit pressure. Add
   deposit -> withdraw checks, totalAssets consistency, donation edges, and
   fee conservation before paying reviewers to find the basics.

3. Historical DeFi failures are not just stories. They are test prompts.
   Arkheionx turns root causes into GitHub-native readiness checks for indie
   builders.

4. If your protocol uses an oracle, your audit prep should explain freshness,
   decimals, bounds, fallback behavior, and who can update the source.
   Arkheionx flags that as a readiness gap.

5. The first Arkheionx scanner is deliberately boring: local files only, no
   RPC, no live targets, no secrets, Markdown output. Boring is good when the
   goal is defensive preparation.

6. A pre-audit report should not say "you are safe." It should say: here are
   the assumptions, here are the missing invariants, here are the blockers to
   fix before formal review.

7. The best security tool for small teams is often a checklist that actually
   gets used. Arkheionx makes the checklist executable inside GitHub.

8. Indie DeFi teams need a path between "we wrote contracts" and "we can afford
   a formal audit." Arkheionx is building that path as an open GitHub repo.

9. Every readiness gap is cheaper to fix before audit intake. Tests, invariants,
   role docs, oracle assumptions, and launch scope should not be discovered on
   the final week.

10. Arkheionx is becoming a security memory layer: historical exploit research
    plus pre-audit readiness tooling for the next wave of DeFi builders.

11. Arkheionx v0.3.0 adds the GitHub-native product loop: Action summary,
    optional PR comment, stable finding IDs, generated issue checklist, and
    local config suppression. Not an audit. A way to prepare for one.

12. Arkheionx v0.4.0 adds SARIF output and baseline diff mode: new, resolved,
    unchanged, and suppressed readiness gaps in GitHub-native artifacts. The
    output is readiness guidance, not vulnerability confirmation.

## LinkedIn-Style Technical Posts

1. **Why pre-audit readiness matters**

   Most early DeFi teams approach audits with preventable gaps: missing
   invariant tests, unclear role docs, oracle assumptions that live only in a
   founder's head, and no clean scope. Arkheionx gives those teams a GitHub
   Action that produces a Markdown readiness report before formal review.

2. **Historical incidents as product input**

   Arkheionx started as an assertion-driven DeFi exploit PoC archive. The next
   layer is practical: map historical failure classes to defensive checks that
   builders can run against their own repositories.

3. **The right language for automated security tooling**

   A static readiness scanner should not claim proof from heuristics. It should
   say "risk signal," "readiness gap," "review recommended," and "missing
   invariant." That language protects users and keeps the output useful.

4. **What a good launch report should contain**

   A useful Launch Report should include protocol shape, score breakdown, top
   gaps, historical pattern similarity, suggested tests, role assumptions, and
   formal audit recommendation. It should not pretend to be certification.

5. **Why GitHub-native matters**

   Indie builders already live in GitHub. A readiness product that outputs
   Markdown, JSON, issue checklists, and action logs can fit their workflow
   without asking them to adopt another dashboard.

## GitHub Discussion Announcement Templates

1. **New scanner rule pack**

   Arkheionx has added a new defensive readiness rule pack for `<protocol
   type>`. It maps `<risk class>` signals to suggested checks and invariant
   themes. Try it with the GitHub Action and open a Rule Request if the signal
   needs better calibration.

2. **Monthly readiness update**

   This month Arkheionx improved `<rule/docs/example>`, regenerated the sample
   report, and updated the roadmap. Current archive truth remains unchanged
   unless the maturity index says otherwise.

3. **False positive review thread**

   If the scanner produced a noisy readiness signal for your authorized repo,
   share the report section and code context here or open the False Positive
   Report form. The goal is useful signal, not alarm.

4. **Indie builder office hours**

   Drop questions about pre-audit readiness, invariant planning, report
   interpretation, or audit-scope prep. Do not post secrets, private keys,
   undisclosed exploit details, or confidential production material.

5. **Sponsor update**

   Sponsor funding this cycle supported `<artifact>`. The next useful target is
   `<specific milestone>`. As always, sponsor support does not influence
   severity, taxonomy, or verification claims.

## Founder DM Templates

Use these only in opted-in, public, or clearly relevant builder contexts.
Personalize them. Do not mass-send.

1. Saw your `<protocol>` repo is moving toward `<testnet/grant/audit>`. I am
   building Arkheionx, a GitHub-native pre-audit readiness scanner for indie
   DeFi teams. It outputs a Markdown report with missing invariants and audit
   blockers. Happy to share the free action if useful.

2. Your vault work caught my eye because Arkheionx currently has a vault
   readiness path: totalAssets consistency, roundtrip tests, share accounting,
   and role docs. Not an audit, just prep before formal review. Want the link?

3. I noticed your team is applying for ecosystem support. One gap I see often
   in grant-stage DeFi repos is no clear pre-audit report. Arkheionx generates
   a GitHub-native readiness report you can use internally or for audit prep.

4. I am looking for a few indie DeFi builders to pressure-test Arkheionx's
   scanner output. It is local-only, no RPC, no secrets, Markdown report. If
   your repo is public and authorized, I can take feedback on false positives.

5. If your team is not ready for a formal audit yet, Arkheionx may still help:
   it identifies missing invariants, historical pattern similarity, and launch
   blockers from your GitHub repo. No claims of safety, just readiness prep.

## Anti-Hype Rules

- No fake metrics.
- No fake partnerships.
- No guarantee claims.
- No fearmongering.
- No exploit-bait wording.
- No claim that the archive has more verification evidence than the committed
  reports support.
- No claim that scanner output confirms exploitability.
- No claim that Arkheionx replaces professional review.

## Stop Rules

Stop or decline when:

- authorization is unclear;
- the request involves active target testing without permission;
- the buyer wants value extraction, evasion, or stealth;
- private keys, mnemonics, or secrets are requested or shared;
- the buyer wants a safety guarantee;
- the requested deliverable would weaken Arkheionx's defensive boundary.

## Related Pages

- [`INDIE_BUILDER_OFFER.md`](INDIE_BUILDER_OFFER.md)
- [`MONETIZATION.md`](MONETIZATION.md)
- [`SPONSORSHIP.md`](SPONSORSHIP.md)
- [`../SERVICES.md`](../SERVICES.md)

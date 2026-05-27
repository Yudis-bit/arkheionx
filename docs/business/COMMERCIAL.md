# Commercial Work

Arkheionx commercial work is human-guided pre-audit readiness support around
the open-source scanner, reports, issue plans, Security Memory Graph, and
delivery artifacts.

Paid Arkheionx work is a readiness engagement, not a formal audit.

The historical Arkheionx Vault archive remains part of the public security
memory layer, but the primary paid surface is now repository readiness before
formal audits, contests, or bug bounty launches.

This page is intentionally specific. It describes work that can be delivered
from the repository's existing strengths without claiming verified outcomes,
customers, adoption, or security guarantees.

## Available Work

| Offer | Best for | Deliverable | Starting range |
|---|---|---|---|
| Readiness Snapshot | Teams that need a fast blocker scan before audit intake | Pre-Audit Report, Executive Summary, Issue Plan, top 5-10 gaps, 30-minute walkthrough | USD 500-2,500 |
| Pre-Audit Sprint | Teams preparing for audit, contest, or bounty launch | Report bundle, SARIF, Issue Plan, Remediation Roadmap, test plan, walkthrough | USD 2,500-12,000 |
| Contest Readiness Pack | Teams preparing authorized external review | Scope checklist, researcher onboarding notes, documentation gap review | USD 1,500-6,000 |
| GitHub Action Setup | Teams that want Arkheionx in CI | Action integration, SARIF/report artifacts, config, threshold guidance | USD 500-2,500 |
| Ecosystem Readiness Pilot | Ecosystems, grant programs, accelerators, or audit-prep cohorts with multiple authorized repos | Repo-by-repo readiness table, anonymized common gaps, rule-family heatmap, calibration notes | Pilot USD 5,000-15,000; expanded USD 15,000-40,000+ |
| PoC assertion hardening sprint | A team with an existing exploit replay that ends in logs or weak checks | Foundry assertion patch, invariant map, metadata notes, reviewer summary | USD 750-2,500 per PoC |
| Historical reproduction report | Protocols, researchers, or education teams studying a resolved incident | Fork reproduction review, root-cause narrative, assertion checklist, verification plan | USD 2,500-7,500 per incident |
| Auditor training workshop | Teams learning exploit anatomy and invariant-driven review | Live workshop, slides, selected PoC walkthroughs, exercises | USD 1,000-3,000 per session |
| Research review retainer | Teams that want recurring review of incident notes or internal PoC quality | Monthly review window, written feedback, prioritized hardening queue | USD 2,000-5,000 per month |
| Corpus sponsorship | Individuals or organizations that want to fund the public archive | Sponsor acknowledgement, funded roadmap notes, public progress updates | USD 250-2,000 per month |

Ranges are anchors, not quotes. Final scope depends on incident complexity,
chain, availability of public sources, archival RPC needs, and whether the work
requires a fresh reproduction or only review of an existing PoC.

## What This Work Includes

- Historical, patched, or otherwise resolved incidents.
- Authorized repository readiness review.
- Generated report, issue-plan, and delivery artifact review.
- Remediation roadmap and test/invariant planning.
- GitHub Action setup support.
- Ecosystem-level anonymized common-gap summaries for authorized repositories.
- Fork-based reproduction planning.
- Assertion-family mapping against `docs/ASSERTION_STANDARD.md`.
- Root-cause and invariant writeups.
- Metadata review against `metadata/schema.json`.
- Verification-report preparation for archival runs.
- Training material based on public incidents already in the archive.

## What This Work Does Not Include

- Live-target exploitation.
- Scanner, drain, or target-enumeration tooling.
- Private-key, RPC-key, or credential handling.
- Emergency incident response for an active exploit.
- Full smart-contract audit signoff.
- Security guarantees, bounty guarantees, or contest placement promises.
- Public ecosystem claims without permission.
- Legal, compliance, or security certification.

If the work involves an unpatched live target, use coordinated disclosure with
the protocol's security team. Do not send exploit details through a public
issue.

## Scoping Checklist

Before asking for commercial work, prepare:

- Incident name, chain, and date.
- Public post-mortem or authoritative writeup.
- Attack transaction hash if public.
- Current PoC path or repository link, if one exists.
- Desired output: assertion patch, report, workshop, or sponsorship.
- Deadline and preferred communication channel.
- Confirmation that the target is historical, patched, or authorized.
- For ecosystem pilots, repository aliases, authorization confirmation for each
  repository, and anonymization preferences.

## Inquiry Template

```text
Subject: Arkheionx readiness inquiry - <offer>

Name / organization:
Preferred contact:
Offer requested:
Incident or topic:
Chain / VM:
Public references:
Current PoC or code link:
Desired deliverable:
Deadline:
Budget range:
Authorization / patch status:
Notes:
```

Do not include private keys, RPC URLs, undisclosed exploit details, customer
data, or confidential protocol material in a first message.

## Positioning

The commercial surface should be described as:

> GitHub-native pre-audit readiness support that turns authorized repository
> signals into reports, issue plans, and remediation workflows.

It should not be described as:

> A formal audit provider, live-target toolkit, bounty guarantee, or verified
> exploit database.

The public archive stays honest: verification counts, maturity levels, and
assertion quality continue to come from `metadata/registry.json` and generated
reports.

## Related Pages

- [`../SERVICES.md`](../SERVICES.md) — public one-page service menu.
- [`SPONSORSHIP.md`](SPONSORSHIP.md) — sponsor tiers and boundaries.
- [`SPONSOR_PROSPECTUS.md`](SPONSOR_PROSPECTUS.md) — sponsor package details.
- [`PAID_OFFER.md`](PAID_OFFER.md) — current paid readiness offer overview.
- [`PRICING_LADDER.md`](PRICING_LADDER.md) — pricing guidance and pilot rules.
- [`SERVICE_PACKAGES.md`](SERVICE_PACKAGES.md) — package-by-package deliverables.
- [`PAID_WORK_BOUNDARIES.md`](PAID_WORK_BOUNDARIES.md) — commercial safety boundaries.
- [`TRAINING.md`](TRAINING.md) — workshop modules and pricing.
- [`PROPOSAL_TEMPLATE.md`](../business/PROPOSAL_TEMPLATE.md) — paid engagement template.
- [`CASE_STUDY_SAMPLE.md`](CASE_STUDY_SAMPLE.md) — sample premium output.

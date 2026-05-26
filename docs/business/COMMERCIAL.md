# Commercial Work

Arkheionx Vault is an archive first. Commercial work is available only where it
supports defensive research, reproducibility, auditor education, or historical
incident analysis.

This page is intentionally specific. It describes work that can be delivered
from the repository's existing strengths without claiming verified outcomes the
archive has not earned yet.

## Available Work

| Offer | Best for | Deliverable | Starting range |
|---|---|---|---|
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
- Assured bounty outcomes or contest placement.

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

## Inquiry Template

```text
Subject: Arkheionx Vault commercial inquiry - <offer>

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

> Defensive exploit-reproduction research, assertion hardening, and auditor
> training built from historical DeFi incidents.

It should not be described as:

> An offensive live-target toolkit, an audit firm, a bounty guarantee, or a verified
> exploit database.

The public archive stays honest: verification counts, maturity levels, and
assertion quality continue to come from `metadata/registry.json` and generated
reports.

## Related Pages

- [`../SERVICES.md`](../SERVICES.md) — public one-page service menu.
- [`SPONSORSHIP.md`](SPONSORSHIP.md) — sponsor tiers and boundaries.
- [`SPONSOR_PROSPECTUS.md`](SPONSOR_PROSPECTUS.md) — sponsor package details.
- [`TRAINING.md`](TRAINING.md) — workshop modules and pricing.
- [`PROPOSAL_TEMPLATE.md`](../business/PROPOSAL_TEMPLATE.md) — paid engagement template.
- [`CASE_STUDY_SAMPLE.md`](CASE_STUDY_SAMPLE.md) — sample premium output.

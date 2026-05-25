# Outreach Kit

This kit turns the archive into qualified conversations without overstating
what it is. Use it for direct messages, emails, community posts, and workshop
outreach.

## Ideal Customers

Best early targets:

- small audit teams that train junior researchers,
- Web3 security bootcamps,
- protocol security teams with internal education budgets,
- bug bounty researchers who maintain private PoC collections,
- security communities that discuss DeFi post-mortems.

Avoid early:

- protocols in the middle of an active incident,
- teams asking for urgent unauthorized live-target help,
- buyers who only want a bounty outcome,
- projects with no public source material.

## Positioning Sentence

Short:

> I help teams turn historical DeFi exploit replays into assertion-driven
> learning artifacts.

Long:

> Arkheionx Vault is a public archive of historical DeFi exploit PoCs. I offer
> scoped defensive work around the archive: assertion hardening, root-cause
> reports, verification planning, and auditor workshops based on public
> incidents.

## Direct Message

```text
Hi <name>, I maintain Arkheionx Vault, a defensive archive of historical DeFi
exploit PoCs focused on assertions, root cause, and reproducibility.

I noticed your team publishes security education / audit notes. I am opening a
few scoped sessions around exploit anatomy and assertion-driven PoCs:

- 90-minute workshop for auditors
- PoC assertion hardening sprint
- historical exploit report for a resolved incident

The work is limited to patched or authorized targets. Would this be useful for
your team this month?
```

## Email

```text
Subject: Assertion-driven DeFi exploit training

Hi <name>,

I maintain Arkheionx Vault, a public defensive archive of historical DeFi
exploit PoCs. The archive focuses on pinned forks, hard assertions, broken
invariants, and root-cause notes rather than raw exploit collection.

I am offering a small number of scoped engagements:

1. Assertion hardening for existing Foundry PoCs
2. Historical exploit reproduction reports
3. Auditor workshops based on public DeFi incidents

This is not live-target work and not a bounty guarantee. It is for teams that
want better internal learning material or stronger PoC review discipline.

A good first session is a 90-minute workshop on turning console-log exploit
replays into assertion-hardened tests.

Would it make sense to send a one-page outline?

Best,
Yudistira Putra / arkheionx
```

## Follow-Up

```text
Quick follow-up. The most practical starter format is:

Assertion Hardening Sprint
- review one existing PoC
- map the broken invariant
- add category-appropriate assertions
- write a short reviewer memo

Typical range: USD 750-2,500 depending on complexity.

Useful if your team keeps internal exploit replays but wants them to fail
loudly when the proof is weak.
```

## Community Post

```text
I am opening a few paid slots around Arkheionx Vault.

The work is defensive and historical:
- assertion hardening for Foundry exploit PoCs
- root-cause and invariant writeups
- auditor workshops using public DeFi incidents

No live-target tooling, no scanner work, no bounty guarantees.

If your PoC ends with logs but no hard post-state checks, that is the exact
thing I can help improve.
```

## Discovery Questions

Ask these before quoting:

- Is the target historical, patched, or explicitly authorized?
- Is there a public post-mortem or authoritative writeup?
- Does a PoC already exist?
- Does it compile?
- Does it currently run on a pinned fork?
- What does it assert today?
- What output do you need: code, report, workshop, or all three?
- Is archival RPC available?
- What is the deadline?

## Qualification Rules

Proceed when:

- scope is historical, patched, or authorized,
- buyer wants defensive learning or proof quality,
- references are public or shareable,
- deliverable can be described in one page.

Decline when:

- target appears live and unpatched,
- request includes private exploit adaptation,
- buyer asks for detection evasion,
- buyer wants payout guarantees,
- buyer will not confirm authorization or patch status.

## Simple Proposal Structure

Use [`docs/PROPOSAL_TEMPLATE.md`](PROPOSAL_TEMPLATE.md) for paid work.

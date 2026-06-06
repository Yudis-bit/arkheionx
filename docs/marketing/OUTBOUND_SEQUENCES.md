# Outbound Sequences

Use these sequences for qualified, personalized outreach. Keep the messages
short and specific. Do not send exploit details in first contact.

## Rules

- Send only to accounts with a clear security education or research fit.
- Personalize the first line.
- Make one offer per message.
- Stop after two follow-ups unless the person engages.
- Keep all scope historical, patched, or authorized.
- Never imply audit signoff, bounty outcomes, or live-target capability.

## DM: Audit Team

```text
Hi <name>, I saw <specific post/project> from <team>.

I maintain Arkheionx Vault, a defensive archive of historical DeFi exploit PoCs
focused on hard assertions, root cause, and reproducibility.

Quick question: do you train junior reviewers with exploit replays?

I am offering a 90-minute workshop on turning log-based PoCs into
assertion-driven review exercises. Historical public incidents only.
```

Follow-up:

```text
Small follow-up. The workshop output is practical:

- read one historical exploit PoC
- identify the broken invariant
- map assertion families
- rewrite weak proof into reviewer-readable checks

Useful if your team wants a repeatable internal training format.
Want a one-page outline?
```

Close loop:

```text
Closing the loop here. I will keep publishing the public archive work either
way. If PoC assertion training becomes useful later, the service menu is here:
<link>
```

## Email: Protocol Security Team

```text
Subject: Historical DeFi exploit training for <team>

Hi <name>,

I saw <specific reference> and thought this may be relevant to your security
training or incident education work.

I maintain Arkheionx Vault, a public defensive archive of historical DeFi
exploit PoCs. The archive focuses on pinned forks, hard assertions, broken
invariants, and honest verification status.

I am opening a few scoped engagements:

1. Assertion hardening for existing Foundry PoCs
2. Historical exploit reports for resolved incidents
3. Auditor workshops based on public DeFi incidents

This is not live-target work and not a bounty guarantee.

Would a one-page outline be useful?

Best,
Yudistira
```

Follow-up:

```text
Subject: Re: Historical DeFi exploit training for <team>

Quick follow-up.

The narrow starter offer is an Assertion Hardening Sprint:

- review one existing PoC
- map the broken invariant
- add hard post-state assertions
- write a short reviewer memo

Typical range: USD 750-2,500 depending on complexity.

Useful when a PoC currently proves mostly through logs.
```

## Community Organizer

```text
Hi <name>,

I maintain Arkheionx Vault, a public archive for historical DeFi exploit PoCs.

Would <community> be interested in a practical guest session on
assertion-driven exploit analysis?

The session uses public historical incidents only:

- separating setup from exploit body
- identifying broken invariants
- turning logs into assertions
- avoiding inflated verification claims

No live-target tooling or exploit adaptation.
```

## Sponsor Ask

```text
Hi <name>, I am looking for a few early sponsors for Arkheionx Vault.

The archive is a public defensive research project around historical DeFi
exploit PoCs. Sponsorship funds slow work that is hard to do casually:

- assertion hardening
- archival verification attempts
- root-cause writeups
- training material

Sponsors do not influence severity, category, or verification status.

Would this be relevant to your public-goods or security education budget?
```

## Warm Intro Ask

```text
Hi <name>, quick ask.

I am opening paid slots around Arkheionx Vault:
historical DeFi exploit PoC hardening, root-cause reports, and auditor
workshops.

Do you know one audit lead, protocol security lead, or Web3 security community
organizer who would care about assertion-driven exploit training?

Happy to send a concise blurb you can forward.
```

Forwardable blurb:

```text
Yudistira maintains Arkheionx Vault, a defensive archive of historical DeFi
exploit PoCs focused on assertions, root cause, and reproducibility.

He is opening scoped paid work around assertion hardening, historical exploit
reports, and auditor workshops. Historical, patched, or authorized targets
only.

Service menu: <link>
```

## Reply Handling

If they ask "how much?":

```text
The smallest starter package is usually USD 750-2,500 for one Assertion
Hardening Sprint, depending on whether the PoC already runs and how much
root-cause/report work is needed.

Workshops usually start around USD 1,000-3,000 per session.
```

If they ask for exploit help:

```text
I cannot help adapt exploit logic for a live or unpatched target.

If the target is historical, patched, or explicitly authorized, I can help with
defensive reproduction quality: assertions, invariant notes, verification
planning, or training material.
```

If they are interested:

```text
Great. The next step is a 20-minute fit call.

Before the call, I only need:
- incident/topic
- historical, patched, or authorization status
- current PoC link if available
- desired output: code, report, workshop, or sponsorship
```

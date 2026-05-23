---
name: Unsafe content report
about: Flag content here that may aid attack against an unpatched live system, or otherwise crosses the defensive-only line.
title: "[unsafe-content] "
labels: ["unsafe-content", "priority"]
---

> **Read this first.** If you believe a PoC published here could
> meaningfully help attack a system that is **not yet patched**, please
> redact specific exploitation detail from this issue and contact the
> maintainer privately via the GitHub profile in
> [`docs/SECURITY.md`](../../docs/SECURITY.md). A short notice in this
> issue is fine; full detail belongs in the private channel.

## Unsafe content location

<!-- Path(s) in this repository that the report concerns. File paths,
     line ranges, or registry ids are all fine. Do not paste full
     exploitation transcripts here. -->

## Why this may be unsafe

<!-- Pick one or more, or describe in your own words. -->

- [ ] PoC reproduces against a target that is still in production with
      the same vulnerability.
- [ ] Content includes operational detail not present in the cited
      public post-mortem.
- [ ] Content reads as live-target framing (drain helper, scanner,
      attacker automation).
- [ ] Content includes private keys, RPC URLs, API keys, or other
      secrets.
- [ ] Content lacks attribution in a way that could enable
      uncoordinated re-disclosure.
- [ ] Other:

## Suggested remediation

- [ ] Take down (delete file or revert PoC).
- [ ] Redact specific operational detail.
- [ ] Add safety framing or post-mortem reference.
- [ ] Move to internal / embargoed channel.
- [ ] Other:

## Urgency

- [ ] Critical — live target still exploitable, public availability
      adds material risk.
- [ ] High — public availability does not help an attacker materially
      more than already-public sources, but content should be revised.
- [ ] Medium — defensive scope concern, no immediate live risk.
- [ ] Low — process / framing concern.

## Reporter context (optional)

- Affiliation (researcher, protocol team, third party):
- How you can be contacted privately for follow-up:

## Acknowledgement

- [ ] I have read [`docs/ETHICS.md`](../../docs/ETHICS.md) and
      [`docs/SECURITY.md`](../../docs/SECURITY.md).
- [ ] I am not posting attacker tooling or exploitation detail in this
      public issue.

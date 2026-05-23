---
name: Unsafe content report
about: Report content here that could meaningfully aid an attack against an unpatched live system.
title: "[unsafe-content] "
labels: ["unsafe-content", "needs-triage"]
---

> **Read this first.** If the content you're reporting could meaningfully
> help attack a live, unpatched system, do not paste exploitation detail
> here. File a short stub of this issue and contact the maintainer
> privately via the GitHub profile in [docs/SECURITY.md](../../docs/SECURITY.md).

## Where

<!-- File path or URL inside this repository. -->

## What

<!-- One paragraph: what the content is, and why it crosses the
     defensive-research line. Avoid pasting the unsafe content itself. -->

## Why this is unsafe

- [ ] Targets a live, unpatched protocol.
- [ ] Hardcodes attacker-favorable on-chain artifacts (private keys,
      bot infra, drain helpers).
- [ ] Provides target-discovery / scanning automation.
- [ ] Provides detection-evasion tooling.
- [ ] Other (describe):

## Suggested fix

<!-- Redact / remove / move to embargoed pipeline / replace with
     defensive-only writeup. -->

## Disclosure

- [ ] I am open to being contacted privately via the maintainer's
      GitHub profile to coordinate disclosure.

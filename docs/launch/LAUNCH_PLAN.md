# Launch Plan

This document is the public-facing companion to
[`RELEASE_PROCESS.md`](RELEASE_PROCESS.md). It describes how a release
of Arkheionx Vault is announced when the maintainer chooses to
announce it. Most releases will not need a public post; technical
checkpoints can land silently.

The plan exists so that, when a release is announced, the messaging
matches the artifacts. No release post should claim something the
registry, the dashboard, or the verification reports do not already
support.

## When to announce

Default: stay quiet.

Announce when at least one of the following is true:

- A milestone in [`EXPANSION_PLAN.md`](EXPANSION_PLAN.md) has been
  reached honestly (not approximated).
- A meaningful batch of PoCs has been promoted to L4 (archival
  verified).
- A long-form research artifact (case study, methodology note,
  taxonomy expansion) has landed.

Do **not** announce because the calendar moved. Do not announce a
release that exists only to publish.

## What never goes in announcement copy

- Any of the banned framings in
  [`metadata/backlog/rejection-criteria.md`](../metadata/backlog/rejection-criteria.md).
- "Largest", "biggest", "best", "world-class", "industry-leading",
  "production-grade", "trusted by", "verified" (without artifact
  backing).
- Affiliation with audit firms, contest platforms, or bounty programs
  the maintainer is not in fact part of.
- Bounty win counts.
- Comparisons to specific named firms, programs, or other archives by
  way of claiming superiority.
- "Thrilled to announce", "honoured to share", and similar tone-deaf
  filler.
- Catastrophist or hype phrasing about DeFi security generally.

If the post needs any of the above to feel impressive, the post is
not ready.

## Channels

### GitHub Release

Primary channel. The release notes draft template is at
[`launch/GITHUB_RELEASE_NOTES.md`](launch/GITHUB_RELEASE_NOTES.md).

Every release:

- has a release title under 70 characters,
- references the tag,
- summarises the corpus delta in numbers,
- lists the new artifacts (reports, dashboards, docs),
- links to the dashboard at the tag,
- credits the maintainer.

### LinkedIn

Optional. Used when a milestone has long-form research value worth
surfacing to a wider security audience.

The draft is at
[`launch/LINKEDIN_LAUNCH_POST.md`](launch/LINKEDIN_LAUNCH_POST.md).

LinkedIn-specific guidance:

- Lead with the artifact, not the brand.
- One paragraph, not five. Link to the GitHub release for detail.
- No emoji-driven framing. No bullet-point manifestos.
- The angle is *not to make it bigger, to make it harder to lie*.

### X / Twitter

Optional. Most releases will not need a thread; a single link to the
GitHub release is usually enough.

When a thread is appropriate, the draft is at
[`launch/X_THREAD.md`](launch/X_THREAD.md). Cap at six tweets. Each
tweet must stand alone if read out of order.

### Other channels

If a release has a research deliverable (case study, methodology
note, taxonomy expansion), it may be cross-posted to the relevant
research forum. Always link back to the GitHub release. Never
cross-post hype copy that did not pass the GitHub release bar.

## Follow-up cadence

After a major release, queue at most five follow-up posts over the
following weeks:

1. **Methodology note** — how a specific PoC was hardened, with code
   citations.
2. **Verification note** — what archival verification of a single
   incident looked like end-to-end.
3. **Taxonomy note** — why a category exists, what it includes, what
   it excludes.
4. **Auditor checklist excerpt** — applying one checklist section to
   one PoC.
5. **Maintenance note** — what is in the working set, what is open,
   what the next milestone needs.

Each follow-up is its own small post. None of them are "look at the
archive again" reposts of the release.

## Quality gates

Every announcement must pass:

- **Honesty check.** Every numeric in the post matches the registry
  and dashboard at the release tag.
- **Banned-phrase check.** Run a grep against the banned list above
  before publishing.
- **Maintainer voice.** Voice is sober, technical, first-person where
  appropriate, never overproduced. No hype copy, no fake humility.
- **Defensive framing.** No content reads as live-target, attacker
  tooling, or detection-evasion.
- **Acknowledgement.** External writeups, post-mortems, and prior
  research that the release builds on are credited.

## Recovery

If a post needs to be corrected after publication:

- Edit in place if the platform supports it. Note the correction.
- If a numeric was wrong, link to the corrected dashboard at the tag.
- If a framing was wrong, retract the framing in a follow-up post.
  Do not silently delete.

## Author identity

All public-facing posts are by Yudistira Putra (arkheionx). No ghost
accounts, no sock puppets, no impersonation of other researchers.
Co-authorship is acknowledged where applicable.

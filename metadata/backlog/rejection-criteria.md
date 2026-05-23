# Backlog Rejection Criteria

A candidate in `metadata/backlog/candidates/` may be rejected at any
stage. This document records the rejection rubric so the process is
public and reviewable.

A rejection does not mean the incident is unimportant. It means it does
not fit the archive's defensive-research scope, the public-evidence
bar, or the quality bar.

When a candidate is rejected, the rejection reason is recorded in the
candidate file under `status: "rejected"` and `notes`. The file is not
deleted; the rejection is part of the public record.

## Hard rejections

A candidate is rejected outright if any of the following apply:

### 1. Live-target framing

The proposal reads as live attacker tooling: drain helpers, target
scanners, attacker automation against production systems, detection
evasion. Arkheionx Vault is defensive-only.

### 2. Unpatched live target

The protocol is still vulnerable in production with the same primitive
the candidate would reproduce. Such cases must go through the embargo
path, not the public backlog. Contact the maintainer privately first.

### 3. No public sources

There is no post-mortem, no advisory, no audit finding, and no
authoritative third-party write-up. A bare tweet, a Discord screenshot,
or a Telegram rumour does not meet the source bar. We document what is
already public; we do not break embargoes.

### 4. Inadequate attribution

A PoC that would be ported from another repository without preserving
the original author and upstream commit SHA is rejected. Honest
attribution is non-negotiable.

### 5. Secrets or PII required

The reproduction would require committing real RPC URLs, real API keys,
real private keys, or other sensitive material. The repository never
takes secrets.

### 6. Cannot be reproduced defensively

The exploit primitive cannot be demonstrated without targeting a
production system as part of the test. Foundry forks against pinned
historical state are the correct method; anything that requires live
network interaction with a deployed protocol is out of scope.

## Soft rejections

A candidate is held or returned for revision if any of the following
apply.

### 7. Insufficient root-cause clarity

The proposed `root_cause`, `invariant_broken`, or
`protocol_assumption_failure` is generic ("smart contract vulnerability",
"reentrancy bug", "logic error") and the cited references do not
support a more precise statement.

### 8. Duplicate

The incident is already represented in the registry, or another
candidate covers the same primitive with similar quality. Duplicates
are rejected unless the new candidate provides materially better
sources, code, or root-cause analysis.

### 9. No clean taxonomy fit and no proposal

The candidate does not fit any
[`docs/EXPLOIT_TAXONOMY.md`](../../docs/EXPLOIT_TAXONOMY.md) category
and does not propose a new category. Held under
`blocked_on: taxonomy-review`.

### 10. Out-of-scope chain

A chain we cannot reproduce on (no archival RPC available, no Foundry
support, opaque execution environment). Held under
`blocked_on: rpc` or `blocked_on: vm-support`.

### 11. Saturated lane

The primary lane is already saturated for the current milestone and a
better-fit candidate exists. Held until lane balance allows it. See
[`priority-lanes.md`](priority-lanes.md).

### 12. Insufficient defensive lesson

The reproduction would not teach a reader something useful about
designing or auditing similar protocols. "Big number was lost" alone is
not a research lesson.

## Banned framings

Independent of the candidate itself, certain framings are not accepted
in any candidate file:

- "Largest exploit archive" claims.
- Comparisons to specific named audit firms or contest platforms.
- Bounty marketing ("this would have won X").
- Affiliations the maintainer does not actually have.
- Catastrophist or hype language.

## Appeal

A rejected candidate may be reopened if the rejection reason is
materially addressed:

- New public source published.
- Patch landed (moves an unpatched-target rejection to acceptable).
- Better post-mortem available.
- Researcher provides revised root-cause notes meeting the bar.

The candidate file is updated; the rejection record is preserved with
the appeal outcome.

## Why this exists

A backlog without a rejection rubric drifts toward "everything looks
interesting". The point of the rubric is that triage decisions are
defensible: any researcher reading the candidate file can see why a
slot was given or refused, and reviewers can challenge the call against
the same rubric.

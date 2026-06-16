---
name: Research candidate
about: Propose a new historical incident as a candidate validation fixture.
title: "[candidate] <YYYY-MM-protocol>"
labels: ["candidate", "intake"]
---

<!-- Read docs/INCIDENT_INTAKE.md and metadata/backlog/priority-lanes.md
     before opening. Candidates with insufficient public sources, embargoed
     status, or live-target framing will be closed. -->

## Incident

- **Protocol**:
- **Date** (`YYYY-MM`):
- **Chain**:
- **Suggested registry id** (`YYYY-MM-protocol-slug`):

## Public sources

- Post-mortem URL:
- Authoritative writeup URL (if different):
- Other references (advisory, contest report, audit finding):

<!-- At least one source must be a post-mortem from the protocol team
     or a respected third party. Twitter / X threads alone are not
     enough. -->

## Suspected root cause

<!-- One paragraph. What invariant broke? Which protocol assumption
     turned out to be false? -->

## Attack details (if known)

- Attack tx hash:
- Approximate fork block:
- Attacker address (optional):
- Approximate loss (USD):

## Candidate category

<!-- Match against docs/EXPLOIT_TAXONOMY.md. If no category fits, mark
     "needs-taxonomy-review" and explain. -->

- Category:
- Priority lane (see metadata/backlog/priority-lanes.md):

## Reproduction notes

- Required RPC type (public / archival):
- Expected difficulty (trivial / easy / moderate / hard / very-hard):
- Known reproduction risks (state pruning, dead contracts, missing
  source, etc.):

## Safety

- [ ] Protocol is patched OR the incident is otherwise no longer
      exploitable on the live system at the declared block.
- [ ] No private exploitation detail is being published here that is
      not already in the cited sources.
- [ ] No live-target framing.

## Notes

<!-- Anything else worth knowing during triage. -->

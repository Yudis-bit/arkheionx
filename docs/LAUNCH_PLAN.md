# Launch Plan

How Arkheionx Vault is presented to the world. This is a one-page,
honest plan. It is intentionally not a marketing campaign.

## Goal

Make the repository visible to the people who would benefit from it —
DeFi auditors, smart-contract security researchers, learners,
contest participants — without overstating what it currently is.

The bar for every public post is the same as the bar for the README:
honest counts, no fake affiliations, no claims the registry does not
back. The principle is on the LinkedIn launch copy:

> Not to make it bigger. To make it harder to lie.

## What we are launching

The repository as of the release commit. Specifically:

- 18 historical DeFi exploit PoCs.
- An assertion-quality model with strong / medium / weak counts that
  match the registry.
- A six-level maturity ladder (`docs/POC_MATURITY_MODEL.md`) with
  honest current distribution.
- A research dashboard (`reports/research_dashboard.md`).
- A standards layer covering taxonomy, reproducibility, root-cause
  playbook, and verification reporting.
- A contributor system (issue templates, PR template, backlog).
- A release process (`docs/RELEASE_PROCESS.md`).

We are **not** launching:

- "The largest" or "best" archive.
- Verified counts the registry does not back.
- Audit-firm affiliation, bounty wins, or contest credentials.
- Live exploitation tooling.

## Channels and timing

| Channel | Asset | Notes |
|---|---|---|
| GitHub repo | README + dashboards | Source of truth for every other channel. |
| GitHub Release | `docs/launch/GITHUB_RELEASE_NOTES.md` | Cut after merge to `main`. |
| LinkedIn | `docs/launch/LINKEDIN_LAUNCH_POST.md` | Posted same day as GitHub release. |
| X (Twitter) | `docs/launch/X_THREAD.md` | Posted within 24h of LinkedIn. |
| Personal blog (optional) | Long-form deep dive | Future, when an L4/L5 entry exists. |

The order is: GitHub → LinkedIn → X. Every public number traces back
to the README.

## Tone

- Sober. No "thrilled to announce."
- Technical. Lead with the thesis, not the personal arc.
- Concrete. Cite specific incidents and assertion families.
- Confident, not defensive. Honest L2-heavy distribution is the right
  position; it does not need apology.

## Follow-up posts

After launch, planned posts:

1. A walk-through of one entry's assertion patch, showing weak → strong
   on a specific category.
2. A note on archival RPC: what changes when the L3 → L4 boundary is
   crossed.
3. The first L4 entry, with verification report linked.
4. A "what we won't add" post — the anti-goals from the expansion
   plan, defended.

These post when there is something concrete to point at, not on a
schedule.

## What not to claim

This list applies to every channel:

- No "verified" without a runtime report.
- No comparison to specific named firms.
- No "we" phrasing that implies a team larger than the maintainer.
- No "production-grade exploit lab."
- No invented counts (stars, forks, downloads, deployments).
- No retroactive bounty / audit credit.

## Manual launch steps

These cannot be done from inside the repository:

1. Push the release branch to GitHub.
2. Merge the PR to `main` (or push the branch to `main` if that is the
   intended workflow).
3. Run `bash scripts/github_surface_setup.sh --apply` after `gh auth`.
4. Convert `.github/assets/social-preview.svg` to PNG and upload via
   GitHub Settings → Social preview.
5. Update the GitHub profile (name, bio, avatar) per
   `docs/internal/GITHUB_PROFILE_POLISH_CHECKLIST.md`.
6. Pin the repository on the GitHub profile.
7. Open the repo in incognito and verify the About panel + README +
   social preview.
8. Cut a GitHub release using `docs/launch/GITHUB_RELEASE_NOTES.md`.
9. Post the LinkedIn copy from `docs/launch/LINKEDIN_LAUNCH_POST.md`.
10. Post the X thread from `docs/launch/X_THREAD.md`.

Step 1 and step 2 are gated on the release checklist passing.

# Arkheionx V4 information architecture

Internal product-planning note. It defines the public information architecture so
the README, docs, website, CLI, demo, and release notes tell **one** coherent
story. It is descriptive, not a guarantee.

## Canonical anchors

Every surface must reuse these three anchors verbatim:

- **Canonical sentence:** Arkheionx is a local review map for DeFi smart-contract repos.
- **Canonical command:** `arkheionx review-map .`
- **Canonical demo:** `arkheionx review-map examples/vault-strategy-oracle-fixture`

Core message: Foundry tells you whether the tests you wrote pass. Arkheionx
helps show the value paths you may have forgotten to test.

Core workflow (the spine of every page):

> repo → review-map → value paths → assumptions → test gaps → proof direction → human review

## Audience

- **DeFi builders / protocol engineers** — prepare a repo before an audit.
- **Security researchers** — keep a repeatable review surface.
- **Bug bounty hunters** — triage where to look first; generate hypotheses.
- **Auditors / reviewers** — standardize review context across revisions.
- **Open-source maintainers** — give contributors a shared map.

## Main user journey

1. Land on the homepage or GitHub README.
2. Understand the one-liner in under 60 seconds.
3. See the canonical command.
4. Try the bundled demo.
5. Read what the output means.
6. Run `review-map` on their own repo.
7. Understand the limitations and safety boundary.
8. Report feedback or noisy output.

## Website pages

| Page | Path | Purpose |
|---|---|---|
| Home | `/` | Explain Arkheionx in 60 seconds; demo + workflow + safety + CTAs |
| Quickstart | `/docs/quickstart` | Run the demo in five minutes |
| How it works | `/docs/how-it-works` | The review-map pipeline, input → output → limits |
| Examples / demo | `/examples` | The V4 vault/strategy/oracle fixture with real output |
| Bug bounty | `/docs/bug-bounty` | Safe triage and hypothesis workflow |
| Pre-audit | `/docs/pre-audit` | Builder/reviewer preparation workflow |
| Safety / limitations | `/docs/safety-model` | Boundaries impossible to miss |
| V4 release | `/docs/v4` | What V4 stabilizes; stable vs experimental |
| Install | `/install` | Source install and verification |
| Roadmap | `/roadmap` | Honest next steps |
| Docs index | `/docs` | Navigation hub |

## Root README sections (in order)

1. Hero — name + canonical sentence + core message.
2. Why Arkheionx exists.
3. What it does.
4. What it does not do.
5. Quick start (version → doctor → review-map).
6. Try the V4 demo.
7. Example output (real excerpt with `Source:` evidence).
8. Core workflow.
9. V4 stable scope (stable vs experimental commands).
10. Bug bounty and pre-audit usage.
11. Install.
12. Documentation.
13. Contributing and feedback.
14. License.
15. Version / release status (kept low, not the lead).

## docs/ structure

- **Start here:** `TRY_IN_5_MINUTES.md`, `INTERPRET_RESULTS.md`, `WHAT_ARKHEIONX_IS_NOT.md`.
- **Workflows:** `BUG_BOUNTY_WORKFLOW.md`, `PRE_AUDIT_WORKFLOW.md`, `REAL_PROTOCOL_PROOF_PLAN.md`.
- **Release:** `V4_STABLE_SCOPE.md`, `releases/V4_RELEASE_NOTES.md`, `releases/V4_RELEASE_CHECKLIST.md`, `PACKAGING.md`.
- **Reference:** `CLI_REFERENCE.md`, `REVIEW_MAP.md`, `REPO_IDENTITY_MIGRATION.md`, and the existing long-tail docs.

The curated entry map lives in [`README.md`](README.md) (the docs index).

## Content principles

- Explain before showing commands.
- Show actual commands and real output excerpts; never invent output.
- Never overclaim; mark limitations and roadmap clearly.
- Every page answers "what do I do next?".
- No page is vague marketing.
- Keep capitalization consistent: review-map, value paths, assumptions, test gaps, proof direction.

## Out of scope for V4

No RPC, no live-chain, no exploit automation, no severity assignment, no
vulnerability confirmation, no audit replacement, no SaaS/dashboard/telemetry.
Repo identity is an accepted risk for this sprint (see
[`REPO_IDENTITY_MIGRATION.md`](REPO_IDENTITY_MIGRATION.md)).

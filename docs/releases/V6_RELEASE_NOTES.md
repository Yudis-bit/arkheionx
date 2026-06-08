# Arkheionx v6.0.0 — Evidence Graph and Interaction Matrix

> Local/static and heuristic. An evidence state is not a vulnerability claim.
> Confirmed-candidate is not a confirmed vulnerability. Interaction priority is
> not severity. Unresolved does not mean vulnerable. Human review is required.

V6 adds evidence graphing and interaction matrix analysis so high-impact DeFi
review surfaces can be classified as tested, rejected with evidence, unresolved,
insufficient evidence, or needs human review. It builds on the stable v4.0.0
`review-map` workflow and the v5 Blind Spot Intelligence layer without removing or
changing them.

> V5 shows where to look. V6 shows what is proven, what is unresolved, and which
> interactions still lack evidence.

## Highlights

- **Evidence Graph** (`arkheionx evidence-graph`) — classify every important
  review surface into one of eight evidence states with an evidence strength.
- **Interaction Matrix** (`arkheionx interaction-matrix`) — detect dangerous
  combinations of surfaces, scored by a transparent interaction priority.
- **Unresolved Map** (`arkheionx unresolved-map`) — everything important that
  local evidence does not yet close.
- **Complete Review** (`arkheionx complete-review`, headline) — the full local,
  vendor-agnostic V6 review package with a model-agnostic agent input and a human
  review checklist.

## Boundaries

Local/static only. No RPC, no live-chain calls, no private keys, no exploit
automation, no auto-submit, no severity, no vulnerability claims, no audit
replacement, and no guaranteed bug discovery. Evidence quality still depends on
the tests that exist and on human review.

## Release status

The package version is `6.0.0`; the latest stable release is `v6.0.0`. The
release metadata is finalized locally and pending the founder push, tag, GitHub
release, and site deploy. Full notes: [`../../release-notes/v6.0.0.md`](../../release-notes/v6.0.0.md).

## Founder release commands

```bash
git push origin main
git tag -a v6.0.0 -m "Arkheionx v6.0.0 — Evidence Graph and Interaction Matrix"
git push origin v6.0.0
gh release create v6.0.0 \
  --title "Arkheionx v6.0.0 — Evidence Graph and Interaction Matrix" \
  --notes-file docs/releases/V6_RELEASE_NOTES.md \
  dist/arkheionx-6.0.0-py3-none-any.whl \
  dist/arkheionx-6.0.0.tar.gz
```

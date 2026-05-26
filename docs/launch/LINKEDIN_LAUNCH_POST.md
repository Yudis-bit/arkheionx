# LinkedIn Launch Post — Draft

This file is a working draft for the LinkedIn announcement of an
Arkheionx Vault release. Use it only when a release has long-form
research value worth surfacing to a wider security audience. Most
releases should not be announced.

The angle is **not to make the archive bigger — to make it harder to
lie**.

---

## Constraints

Before writing the post, re-read
[`docs/launch/LAUNCH_PLAN.md`](LAUNCH_PLAN.md) and
[`metadata/backlog/rejection-criteria.md`](../../metadata/backlog/rejection-criteria.md).

The post must not contain:

- "Thrilled to announce", "honoured to share", "excited to launch".
- "Largest", "best", "world-class", "industry-leading", "trusted by".
- Affiliations the maintainer does not actually have.
- Bounty wins or contest results unless they really happened.
- Comparisons to specific named firms or other archives.
- Hype framing of DeFi security generally.
- Numbers that are not in the registry or the dashboard at the
  release tag.

The post must contain:

- The artifact link.
- A concrete claim about what the release contains.
- Maintainer attribution.

---

## Draft (paste into LinkedIn, edit before publishing)

---

Released `<vMAJOR.MINOR.PATCH>` of **Arkheionx Vault** — a defensive
research archive for historical DeFi exploit PoCs.

What I am trying to do with this archive is narrow. Most exploit
collections optimise for size. I am optimising for one axis: a PoC
should prove the failure mode it claims, not just compile.

This release contains:

- `<N>` PoCs total.
- `<N>` assertion-hardened (medium / strong).
- `<N>` archival-verified (L4+).
- `<N>` distinct exploit categories represented.

What is intentionally **not** in this release:

- Any "verified" claim that is not backed by an archival fork run and a
  committed verification report. The current archival-verified count
  is `<N>`, and that number stays low until archival RPC is configured
  and the run transcripts are committed.
- Any framing that compares this archive to specific named firms or
  to other archives.

Why assertions matter: a PoC that ends in `console.log(balance)` does
not prove a compromise. The exploit could have reverted silently, the
balance could have been pre-seeded, the attacker pool could have
already held the funds. Without hard assertions, a green test says
nothing.

Why archival RPC matters: most historical DeFi exploits were exploited
against state that public RPCs no longer retain. A test that passes on
a non-archival endpoint at a recent block did not actually fork the
incident.

What is becoming Arkheionx Vault, in plain language: a small,
sober, evidence-driven corpus that auditors can read, fork, learn
from, and challenge.

Repository: <github.com/Yudis-bit/DeFi-Exploit-PoCs>
Maturity model: <link to docs/POC_MATURITY_MODEL.md at tag>
Dashboard: <link to reports/research_dashboard.md at tag>

— Yudistira Putra (`arkheionx`)

---

## Self-review checklist before posting

- [ ] Numeric values match the dashboard at the tag.
- [ ] No banned phrases (run grep against the LAUNCH_PLAN list).
- [ ] No affiliations claimed that the maintainer does not have.
- [ ] Tone is technical and sober. No filler. No emoji-driven framing.
- [ ] Defensive-only framing throughout.
- [ ] Maintainer named.
- [ ] Link to repo, model, and dashboard included.

If a checkbox cannot be honestly ticked, do not publish.

# X / Twitter Thread — Draft

This file is a working draft for the X thread version of an Arkheionx
Vault release announcement. Use it only when a release deserves a
thread; most releases do not. A single link to the GitHub release is
usually enough.

Cap the thread at six tweets. Each tweet must stand alone if read out
of order — assume reposts strip context.

---

## Constraints

Read [`docs/launch/LAUNCH_PLAN.md`](LAUNCH_PLAN.md) before writing the
thread. Do not include:

- Banned phrases ("largest", "world-class", "industry-leading",
  "trusted by", "AI-powered" outside of intended use, "verified"
  without artifact backing).
- Comparisons to specific named firms or other archives.
- Numbers that do not match the dashboard at the release tag.
- Affiliations the maintainer does not have.

---

## Draft (paste into X, edit before publishing)

---

**1/**

Released `<vMAJOR.MINOR.PATCH>` of Arkheionx Vault — a defensive
research archive for historical DeFi exploit PoCs.

The goal is not size. The goal is: every PoC should prove what it
claims.

`<github link>`

---

**2/**

What is in this release:

— `<N>` PoCs total
— `<N>` assertion-hardened
— `<N>` archival-verified

What is not in this release: any "verified" claim without a real run
transcript and a committed verification report.

---

**3/**

Why hard assertions:

A PoC that ends in `console.log(balance)` proves nothing. The exploit
could have reverted silently. The pool could have already held the
funds. Without `assertEq` / `assertGt` against pinned pre-state, a
green test is just a compiled file.

---

**4/**

Why archival RPC:

Most historical DeFi exploits ran against state that public RPCs no
longer retain. A test that passes on a recent block did not fork the
incident. The maturity model treats these as separate levels —
public-RPC smoke vs archival verification.

---

**5/**

Maturity model: L0 raw replay → L1 structured metadata → L2
assertion-hardened → L3 public-RPC smoke → L4 archival verified → L5
research-grade case study. Every PoC sits at exactly one level. The
gates are public.

`<link to docs/POC_MATURITY_MODEL.md at tag>`

---

**6/**

Maintainer: Yudistira Putra (`arkheionx`).

This is a solo defensive-research project. No affiliations claimed.
No bounty wins claimed. The dashboard at the tag is the source of
truth.

`<link to reports/research_dashboard.md at tag>`

---

## Self-review checklist before posting

- [ ] Six tweets or fewer.
- [ ] Each tweet stands alone.
- [ ] Numerics match the dashboard at the tag.
- [ ] No banned phrases.
- [ ] No claimed affiliations.
- [ ] Defensive-only framing throughout.
- [ ] Maintainer named.
- [ ] At least one link to the repo, the maturity model, and the
      dashboard.
- [ ] Tone is technical and sober.

If any of the above is not honestly tickable, do not publish.

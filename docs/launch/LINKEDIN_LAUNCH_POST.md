# LinkedIn Launch Post

Draft for the public launch of Arkheionx Vault. Numbers must match the
README and `reports/research_dashboard.md` at the moment of posting.

---

I have been working on something quietly for a while.

**Arkheionx Vault** — an independent archive of historical DeFi exploit
proofs-of-concept, focused on assertions, root-cause analysis, and
fork-verification readiness.

A PoC that compiles is not verified.
A PoC that logs balances is not enough.
A serious exploit PoC should prove the failure mode, not just rerun
its shape.

So I built the archive around that.

---

What is in it today (honest snapshot):

- 18 historical DeFi exploit PoCs, Foundry-based, pinned to fork blocks.
- A six-level maturity ladder: from raw replay (L0) to research-grade
  case study (L5).
- An assertion-quality model with strong / medium / weak counts that
  match the registry — no inflation.
- A taxonomy, an auditor checklist per category, and a root-cause
  playbook.
- Generated reports: quality matrix, maturity index, research dashboard.
- A contributor system: issue templates, PR template, release process.

What it is not:

- Not a live-target attack toolkit.
- Not a scanner or drain framework.
- Not affiliated with any audit firm, contest platform, or bounty
  program.
- Not "verified" yet — most entries sit at L2 and need archival RPC to
  cross into L3 / L4. That is recorded honestly per entry.

---

The point is not to make this the largest archive of exploit code.
There are larger collections.

The point is to make it harder to lie. Each entry asks the same
questions. What was the primitive? What invariant broke? What
assumption failed? What does the post-state look like, and does the
test prove it?

That is the bar. The corpus grows when entries clear it.

---

If you build, audit, or learn smart-contract security, take a look:
github.com/Yudis-bit/DeFi-Exploit-PoCs

Issues and PRs welcome — there are templates for new research
candidates and assertion-hardening proposals.

— Yudistira Putra (`arkheionx`)

---

## Notes for the poster

- Replace "18" with the live count from `metadata/registry.json` if
  the corpus has changed.
- Do not add hashtag spam.
- Do not add "thrilled" / "excited" / fire emojis.
- Do not name specific audit firms in the post.
- The line "Not to make it bigger. To make it harder to lie." can be
  used verbatim in the body or as the lead, depending on layout.

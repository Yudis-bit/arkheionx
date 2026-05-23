# X (Twitter) Thread

Draft for the launch thread. Numbers must match the README and
`reports/research_dashboard.md` at the moment of posting.

---

**Tweet 1**

I built a thing.

Arkheionx Vault — an independent archive of historical DeFi exploit
PoCs, focused on assertions, root-cause analysis, and fork
verification.

A PoC that compiles isn't verified.
A PoC that logs balances isn't enough.

github.com/Yudis-bit/DeFi-Exploit-PoCs

---

**Tweet 2**

What's in it:

- 18 historical exploit PoCs (Foundry, EVM, pinned to fork blocks)
- Assertion-quality model (strong / medium / weak, no inflation)
- Six-level maturity ladder L0 → L5
- Generated quality matrix, maturity index, dashboard
- Per-category auditor checklist + root-cause playbook

---

**Tweet 3**

Honest current state:

- 0 entries promoted to deterministic-confirmed.
- Most entries sit at L2 (assertion-hardened) blocked on archival RPC.
- That's recorded per entry. Public-RPC limitations are RPC limitations,
  not PoC defects.

The point isn't to be the largest archive. It's to be harder to lie.

---

**Tweet 4**

Each entry answers the same questions:

- What was the exploit primitive?
- What invariant broke?
- What protocol assumption failed?
- What does the post-state look like?
- Does the test prove it, or just rerun the shape?

That's the bar. Corpus grows when entries clear it.

---

**Tweet 5**

What it is NOT:

- Not a live-target attack toolkit
- Not a scanner / drain framework
- Not affiliated with any audit firm or bounty platform
- Not "verified" until a real fork run is recorded

Defensive research only. See docs/ETHICS.md.

---

**Tweet 6**

If you build, audit, or learn smart-contract security, take a look.

Issue templates for new research candidates and assertion-hardening
proposals.

PR template enforces one-PoC-per-patch and a safety checklist.

— Yudistira Putra (`arkheionx`)

---

## Notes for the poster

- Replace the count "18" with the live registry count if it changed.
- Each tweet is independent; reorder if the lead doesn't carry the
  thread.
- Do not add hype emojis or "🧵" ladder spam.
- Do not name specific firms or contests.
- The "harder to lie" phrasing is the load-bearing line; keep it.

# GitHub Profile / Repository Polish Checklist

Manual GitHub-side polish steps that cannot be applied from this
repository alone. The repository contents (README, descriptions, social
preview, topics) are addressed under
[`PHASE_9_GITHUB_SURFACE_POLISH.md`](PHASE_9_GITHUB_SURFACE_POLISH.md).
This document covers the **GitHub account surface** that lives outside
the repo: profile name, avatar, bio, pinned repos.

---

## Scope

This is a checklist, not an automated script.

GitHub does not let a repository edit its owner's profile name, avatar,
bio, or pinned repositories. Those settings live on the user account
and must be changed by **Yudistira Putra** while signed in to
[github.com/Yudis-bit](https://github.com/Yudis-bit) under
**Settings → Public profile**.

---

## Profile name

The display name shown on the profile page (separate from the `@handle`).

**Suggested:** `Yudistira Putra`

This is the real name of the maintainer and is already used as the
"Maintained by" line in `README.md` and as the `maintainer` field in
`metadata/registry.json`. Keep them consistent.

The handle (`Yudis-bit`) and the brand identity (`arkheionx`) are
separate from the display name. Both should remain visible:

- handle: `@Yudis-bit` (account URL, not changing)
- brand:  `arkheionx` (referenced in README, bio, and registry)

---

## Bio

GitHub bios are limited to 160 characters.

Pick one. Do not stack adjectives, do not use marketing language, do
not claim affiliations.

**Option A — research framing**

> DeFi security researcher focused on exploit PoCs, root-cause analysis,
> and fork-based reproducibility.

(112 chars)

**Option B — project framing**

> Independent Web3 security researcher. Building Arkheionx Vault: DeFi
> exploit PoCs, assertions, and incident analysis.

(126 chars)

**Option C — neutral / portfolio framing**

> Smart contract security researcher focused on DeFi exploit
> reproduction and assertion-driven PoCs.

(98 chars)

Recommended: **Option B**. It names the project, the role, and the
output without overclaiming.

---

## Location, pronouns, social links

- **Location:** optional. If included, use a real city or "Remote".
  Avoid timezone-only entries.
- **Pronouns:** maintainer's choice; not load-bearing.
- **Social links:** add only links that are real and maintained. Empty
  or 404 links read worse than no link.

Reasonable links to add when they exist:

- The repository: `https://github.com/Yudis-bit/DeFi-Exploit-PoCs`
- A personal site, only if it is real and reflects the brand.
- A research-focused Twitter/X or Mastodon handle, only if posts are
  on-topic.

Do not link to:

- Personal social accounts unrelated to security research.
- Sites under construction.
- Anything implying affiliation with audit firms, contest platforms, or
  bounty programs.

---

## Avatar guidance

The current avatar belongs to GitHub user `Yudis-bit`. It can only be
changed from
**Settings → Public profile → Profile picture**.

Design direction for a professional avatar:

- **Clean headshot** — simple background, neutral framing. Reads as a
  real person.
- **Minimalist arkheionx monogram** — letter-mark on a dark background.
  Reads as a researcher operating under a personal brand.
- **Abstract security/archive mark** — a single technical motif (vault,
  cipher, glyph). Avoid generic shield/lock clipart.

Avoid:

- Anime / cartoon stock avatars.
- Crypto / NFT-style profile pictures.
- Logos that imitate any audit firm, contest platform, or bounty
  program.
- Default GitHub identicons.

The avatar appears next to every PR comment, issue, and commit. Treat
it as part of the research surface.

---

## Pinned repositories

GitHub allows up to **6 pinned repositories** on a profile. They are
the first thing visitors see after the bio.

Recommended pinning strategy:

1. **`Yudis-bit/DeFi-Exploit-PoCs`** — pin first.
2. Pin only repositories that are public, finished or in active
   research, and that you would defend in an interview.
3. Do not pin tutorial follow-alongs, course projects, or experiments
   that have been abandoned.
4. If only one repository qualifies, pin only one. Six pinned slots is
   a maximum, not a target.

Re-evaluate the pinned set whenever a new substantial repository ships.

---

## Repository "About" panel (separate from profile)

Once `scripts/github_surface_setup.sh --apply` runs, verify the
repository **About** panel on
`https://github.com/Yudis-bit/DeFi-Exploit-PoCs`:

- [ ] Description matches the one set by the script.
- [ ] All recommended topics are present.
- [ ] No off-brand or misleading topics remain.
- [ ] **Releases**, **Packages**, **Used by**, and **Deployments**
      sections are either populated or hidden via the gear icon next to
      "About".
- [ ] **Website** field is blank unless a real site exists.
- [ ] Social preview image is uploaded
      (Settings → Social preview).
      See [`/.github/assets/README.md`](../../.github/assets/README.md).

---

## Do-not-overclaim rules

These apply equally to the profile bio, repository description, README,
social preview, and any pinned repos:

- **Do not** imply affiliation with Spearbit, OpenZeppelin, Trail of
  Bits, Cantina, Code4rena, Immunefi, HackenProof, or any audit firm,
  contest platform, or bounty program unless there is a documented
  engagement.
- **Do not** claim "verified" PoCs without an archival fork
  verification report under `reports/verification/`.
- **Do not** claim "the largest archive". There are larger collections.
- **Do not** add fake bounty wins, audit rankings, contest placements,
  or client lists.
- **Do not** describe the project as a product or platform. It is a
  research archive.

When in doubt, prefer the smaller, accurate framing.

---

## Verification after changes

After updating any profile or repo surface:

1. Open `https://github.com/Yudis-bit` in a logged-out browser tab to
   see the public view.
2. Open `https://github.com/Yudis-bit/DeFi-Exploit-PoCs` similarly.
3. Share the repo URL into a link-preview surface (Slack, Twitter/X,
   Mastodon) and confirm the social preview renders correctly.
4. Skim the bio and About text once more — easy to miss typos in the
   character-counter pressure.

---

## Out of scope for this checklist

- Repository code, tests, metadata, or workflows. Those are owned by
  the rest of the repository.
- GitHub organization-level settings. The repository is owned by a
  user account, not an organization.
- External branding (Twitter/X, Mastodon, personal site). Optional and
  not part of the GitHub surface itself.

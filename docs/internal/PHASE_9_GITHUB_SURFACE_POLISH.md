# Phase 9 GitHub Surface Polish Report

## Summary

Phase 9 polishes the GitHub-facing surface of the Arkheionx Vault
repository so a first-time visitor immediately understands what this
repo is (an independent DeFi exploit PoC research archive) and what it
is not (an offensive live-target toolkit, an audit firm product, a generic
web3 hype project).

Concretely, this phase:

- Removed the unfinished `web/` Next.js application from the repo
  root. The web app was off-brand (`<h1>Yudis-bit</h1>`, hard-coded
  severity by id) and not part of the current product surface.
- Updated `scripts/generate_registry.py`, the `metadata` workflow,
  the PR template, `metadata/README.md`, `scripts/README.md`, and the
  root README's repository-layout block to drop dangling web
  references.
- Added a clean technical social-preview SVG under
  `.github/assets/social-preview.svg`, with conversion / upload
  instructions in `.github/assets/README.md`.
- Added a safe-by-default `scripts/github_surface_setup.sh` that uses
  `gh` to set the repository description and topics in dry-run mode
  by default.
- Added `docs/internal/GITHUB_PROFILE_POLISH_CHECKLIST.md` covering
  the GitHub-account-side polish (profile name, bio, avatar, pinned
  repos) that cannot be applied from the repo itself.
- Added `.reference_data/` to `.gitignore` so reference clones used
  by `poc_factory.py` cannot be accidentally committed.

No PoC source, test, metadata entry, or verification report was
modified. No verification claim was upgraded. No platform affiliation
was added.

## GitHub Surface Audit

### What looked professional already

- `README.md` (sober tone, named maintainer, defensive-use framing,
  honest status table after Phase 8).
- `.github/ISSUE_TEMPLATE/` with bug, documentation, and PoC
  verification templates.
- `.github/pull_request_template.md` with safety checklist.
- Workflows scoped per surface (`docs.yml`, `evm.yml`,
  `metadata.yml`).
- `EVM/README.md`, `metadata/README.md`, `scripts/README.md`,
  `SVM/README.md`, `MoveVM/README.md` — each truthful about scope
  and template-only state where applicable.
- `.gitignore`, `.env.example`, `.gitmodules` clean.

### What still looked unfinished or off-brand

- `web/` Next.js app titled `"Yudis-bit | The DeFi Security Vault"`,
  hero `<h1>Yudis-bit</h1>`, hard-coded `severity = 'critical' if id <= 3`
  logic that diverges from the registry. Reads as a half-finished
  product page; conflicts with the research-archive framing.
- `web/public/metadata.json` only existed to feed the web app; nothing
  else consumed it.
- The README "Repository layout" block listed `web/` as
  `Next.js archive interface`, which overstated scope.
- The PR template carried a `Web app change` row that would have
  become a dangling option after web removal.
- No social preview asset.
- `.reference_data/` was an empty tracked directory; `poc_factory.py`
  documents cloning DeFiHackLabs into it.

### What looked AI-generated

- Minor: the web app's marketing-style copy ("Uncovering vulnerabilities
  to build a more resilient Web3"). Removed by deleting `web/`.

### What looked misleading

- The registry table's "Status" column header (`historical` /
  `needs-verification`) is fine, but the README registry paragraph
  previously said the registry drove "the web archive under `web/`".
  Phase 9 dropped that line.

### Visual clutter on root listing

Before:
```
.github  .reference_data  EVM  MoveVM  SVM  docs  metadata
reports  scripts  web  .env.example  .gitignore  .gitmodules  README.md
```

After:
```
.github  EVM  MoveVM  SVM  docs  metadata  reports  scripts
.env.example  .gitignore  .gitmodules  README.md
```

Tighter, on-message. `web/` and the empty tracked `.reference_data/`
are gone.

### `web/` decision: remove

Audit of references showed the web app was:

- Stylistically inconsistent with the rest of the repo (motion-heavy
  Next.js page with framer-motion vs sober Foundry/Python research
  surface).
- Logically inconsistent with the registry (its severity heuristic
  conflicted with `metadata/registry.json`).
- Not depended on by anything except its own generator
  (`render_web_metadata` in `scripts/generate_registry.py`).
- Off-brand in title and copy (`Yudis-bit | The DeFi Security Vault`,
  not `Arkheionx Vault`).

Options considered:

| Option | Verdict |
|---|---|
| A. Remove entirely | **Chosen.** Cleanest. Future UI can be built fresh. |
| B. Keep, mark archived | Rejected. Leaves stale Next.js code visible. |
| C. Move to `archive/web/` | Rejected. Replaces visible clutter with hidden clutter. |
| D. Leave untouched | Rejected. Conflicts with research framing. |

## Web Folder Decision

Removed `git rm -r web/`. Side effects handled in the same phase:

- `scripts/generate_registry.py` — dropped `WEB_METADATA` constant,
  the `render_web_metadata` helper, and the second `write_file` call.
  The script now generates only the README registry section.
- `.github/workflows/metadata.yml` — removed `web/public/metadata.json`
  from both `push` and `pull_request` `paths` triggers.
- `.github/pull_request_template.md` — removed the `Web app change`
  type checkbox and the "stale README registry / web metadata"
  parenthetical (now reads "stale README registry").
- `metadata/README.md` — text now references the README registry
  table only, not "the web app metadata".
- `scripts/README.md` — removed the bullet pointing to
  `web/public/metadata.json`.
- `README.md` — repository layout block no longer lists `web/`; the
  "What this repository is" bullet no longer mentions the web archive.

No workflow ran the web app, no script other than the generator
referenced it, and the generated metadata file was its only
dependency. Removal is clean.

## Root Visual Clutter Decision

| Item | Decision | Reason |
|---|---|---|
| `web/` | Removed | Off-brand, divergent from registry, no consumers. |
| `.reference_data/` | gitignored, untracked | Empty placeholder; user-clones into it locally. |
| `MoveVM/` | Kept | README clearly marks it template-only. |
| `SVM/` | Kept | README clearly marks it template-only. |
| `docs/internal/` | Kept | Engineering log. Visible but useful. |
| `archive/` | Not created | Nothing earned a place there yet. |

## README Changes

Surgical edits only. Phase 8 already produced a strong README; the
changes here only delete dangling web references:

- "A canonical metadata file (`metadata/registry.json`) that drives the
  registry table below and the web archive under `web/`." → drop
  `and the web archive under web/`.
- Repository layout block: drop `├── web/        Next.js archive interface`
  line. `└── README.md` becomes the closing line under `docs/`.

No headline, no status table, no severity table, no roadmap, no
verification model section was touched. Front-page tone is unchanged.

## Repository Description Recommendation

Selected (used by `scripts/github_surface_setup.sh`):

> Arkheionx Vault: independent DeFi exploit PoC archive focused on
> reproducibility, assertion quality, and root-cause analysis.

Rationale: names the project, names the focus, names what is *not*
claimed (no platform, no firm, no "verified" framing).

Considered alternatives:

- "Independent DeFi exploit PoC archive focused on reproducibility,
  assertion quality, and root-cause analysis." — accurate but does
  not mention the project name.
- "Historical DeFi exploit PoCs with assertion-driven analysis,
  metadata discipline, and fork verification readiness." — accurate
  but reads as a feature list.

Homepage: leave **blank**. No website is intended at this time.
Setting a homepage that 404s or points to a placeholder hurts more
than it helps.

## Topics Recommendation

Recommended set (12 topics, applied by the setup script):

```
web3-security
defi-security
smart-contract-security
smart-contract-auditing
solidity
foundry
exploit-poc
incident-analysis
security-research
reproducible-research
root-cause-analysis
arkheionx
```

Excluded by policy (would imply false affiliation):

```
spearbit  openzeppelin  trail-of-bits  immunefi
cantina   code4rena     hackenproof
```

The script does not auto-remove topics; if any of the above are
present from earlier phases, remove them by hand:

```sh
gh repo edit Yudis-bit/DeFi-Exploit-PoCs --remove-topic <name>
```

## Social Preview Asset

- Source: `.github/assets/social-preview.svg`
- Documentation: `.github/assets/README.md`

Design: dark background, subtle grid, single technical motif, brand
mark "Arkheionx Vault", subtitle "DeFi Exploit PoC Research Archive",
maintainer line "Yudistira Putra / arkheionx", repo URL footer. No
firm logos, no platform badges, no fake metrics, no "verified" or
"largest" claims.

Conversion (any one):

```sh
rsvg-convert -w 1280 -h 640 \
  .github/assets/social-preview.svg \
  -o .github/assets/social-preview.png

# or
convert -density 192 -resize 1280x640 \
  .github/assets/social-preview.svg \
  .github/assets/social-preview.png
```

Neither tool is currently installed on the development machine. The
SVG is the authoritative source under version control; PNG conversion
is left for the manual upload step.

Upload manually: **Settings → Social preview → Upload an image**.

## Profile / Avatar Guidance

See `docs/internal/GITHUB_PROFILE_POLISH_CHECKLIST.md`. Highlights:

- Profile name: `Yudistira Putra` (matches README and registry).
- Bio: prefer Option B,
  > Independent Web3 security researcher. Building Arkheionx Vault: DeFi
  > exploit PoCs, assertions, and incident analysis.
- Avatar: clean headshot, minimalist arkheionx monogram, or simple
  technical mark. No anime, no NFT-style, no firm-logo lookalikes.
- Pinned repos: pin `Yudis-bit/DeFi-Exploit-PoCs` first; pin nothing
  else unless it is finished and on-brand.

These steps cannot be applied from this repository; they live on the
GitHub user account and must be set manually.

## Commands Prepared

Repository description and topics are applied by:

```sh
# default: dry-run
./scripts/github_surface_setup.sh

# explicit dry-run
./scripts/github_surface_setup.sh --dry-run

# actually apply (NOT executed by this phase)
./scripts/github_surface_setup.sh --apply
```

The script:

- Checks `gh` is installed and authenticated; exits non-zero with a
  clear message otherwise.
- Prints the description and topic list before doing anything.
- In dry-run mode, prints the exact `gh repo edit` commands that would
  run.
- In apply mode, calls `gh repo edit Yudis-bit/DeFi-Exploit-PoCs`
  with `--description` and one `--add-topic` per topic.
- Never changes visibility, never deletes anything, never pushes,
  never modifies code, never uploads secrets.

## Files Changed

Modified:

- `.github/pull_request_template.md` (removed "Web app change", tweaked checklist phrasing)
- `.github/workflows/metadata.yml` (removed web/public/metadata.json from triggers)
- `.gitignore` (added `.reference_data/`)
- `README.md` (dropped two web references)
- `metadata/README.md` (dropped web mentions)
- `scripts/README.md` (dropped web/public/metadata.json bullet)
- `scripts/generate_registry.py` (dropped web metadata generation)

Added:

- `.github/assets/README.md`
- `.github/assets/social-preview.svg`
- `docs/internal/GITHUB_PROFILE_POLISH_CHECKLIST.md`
- `docs/internal/PHASE_9_GITHUB_SURFACE_POLISH.md`
- `scripts/github_surface_setup.sh`

Removed (under `git rm`):

- `web/.eslintrc.json`
- `web/next-env.d.ts`
- `web/next.config.js`
- `web/package.json`
- `web/public/metadata.json`
- `web/src/app/globals.css`
- `web/src/app/layout.tsx`
- `web/src/app/metadata.json`
- `web/src/app/page.tsx`
- `web/tsconfig.json`

Untouched (per phase scope):

- `EVM/src/**`
- `EVM/test/**/*.t.sol`
- `metadata/registry.json`
- `reports/verification/*.md`
- `SVM/**`, `MoveVM/**` (only README/de-scope notes were allowed; not
  needed since their READMEs already declare template-only state)

## Validation Results

```
$ git status --short
 M .github/pull_request_template.md
 M .github/workflows/metadata.yml
 M .gitignore
 M README.md
 M metadata/README.md
 M scripts/README.md
 M scripts/generate_registry.py
D  web/.eslintrc.json
D  web/next-env.d.ts
D  web/next.config.js
D  web/package.json
D  web/public/metadata.json
D  web/src/app/globals.css
D  web/src/app/layout.tsx
D  web/src/app/metadata.json
D  web/src/app/page.tsx
D  web/tsconfig.json
?? .github/assets/
?? docs/internal/GITHUB_PROFILE_POLISH_CHECKLIST.md
?? docs/internal/PHASE_9_GITHUB_SURFACE_POLISH.md
?? scripts/github_surface_setup.sh
```

```
$ python3 scripts/validate_metadata.py
ok: 18 entries valid

$ python3 scripts/generate_registry.py --check
ok: 18 entries

$ python3 scripts/score_pocs.py --check
ok: matrix unchanged (18 entries)

$ python3 scripts/generate_verification_report.py --check
ok: 18 entries processed, 0 changed

$ (cd EVM && forge build) ; echo $?
0

$ (cd EVM && forge fmt --check) ; echo $?
0
```

All Phase 9 changes are reflected in working-tree status; all
validators pass; build and format are clean.

## Manual GitHub Steps Remaining

These cannot be applied from this repository:

1. **Apply repository description and topics**

   ```sh
   ./scripts/github_surface_setup.sh --apply
   ```

   Defaults to dry-run. Requires `gh auth status` to be green.

2. **Upload social preview image**

   - Convert `.github/assets/social-preview.svg` to PNG (see
     `.github/assets/README.md` for both `rsvg-convert` and
     `ImageMagick` recipes).
   - Repository → Settings → Social preview → Upload an image.
   - Verify by sharing the repo URL into a link-preview surface
     (Slack, Twitter/X, Mastodon).

3. **Polish the GitHub account profile**

   See `docs/internal/GITHUB_PROFILE_POLISH_CHECKLIST.md`. Profile
   name, bio, avatar, social links, and pinned repositories.

4. **Pin the repository on the profile**

   `Yudis-bit/DeFi-Exploit-PoCs` should be the first pinned
   repository.

5. **Verify the About panel**

   After step 1, open
   `https://github.com/Yudis-bit/DeFi-Exploit-PoCs` in a logged-out
   browser tab and confirm:

   - Description matches the one set by the script.
   - All recommended topics are present.
   - No platform-affiliation topics are present.
   - Website field is blank.
   - Releases / Packages / Used by / Deployments sections are either
     populated or hidden via the gear icon next to "About".

## Risks

- **Stale internal references.** Internal phase reports under
  `docs/internal/` (Phase 4A, 5, 6A–6G, 7, 7B–7D) still mention
  `web/` as part of out-of-scope assertions ("did not modify `web/`").
  These are historical engineering logs, not user-facing
  documentation, and rewriting them would be revisionist. Left
  untouched.
- **Future regeneration.** If `scripts/generate_registry.py` is ever
  regrown to write a non-web artifact, the phrasing in
  `metadata/README.md` and `scripts/README.md` may need to be
  updated again. Current state matches reality.
- **Topic visibility.** GitHub limits a repo to 20 topics. The
  proposed list is 12, leaving room. Topics are not order-stable on
  the GitHub side; do not rely on display order.
- **Social preview.** Conversion tooling (`rsvg-convert`,
  `convert`/`magick`, `inkscape`) is not present on the development
  machine. The PNG must be produced on a machine that has one of
  those tools, or via an online SVG-to-PNG converter, before upload.

## Recommended Commit Message

```
chore(repo): polish GitHub repository surface

- remove unfinished web/ Next.js app and all dangling references
- drop web metadata generation from scripts/generate_registry.py
- update metadata workflow paths and PR template
- add .github/assets/social-preview.svg + asset README
- add scripts/github_surface_setup.sh for description and topics
- add docs/internal/GITHUB_PROFILE_POLISH_CHECKLIST.md
- gitignore .reference_data/ used by poc_factory.py
```

No PoC source, test, metadata entry, or verification report changed.

## Recommended Push / PR Steps

Working branch: `arkheionx/research-grade-rebuild`. Do not commit or
push without operator review.

```sh
# 1. Review changes.
git status --short
git diff --stat

# 2. Stage only the files this phase touched.
git add \
  .github/assets/README.md \
  .github/assets/social-preview.svg \
  .github/pull_request_template.md \
  .github/workflows/metadata.yml \
  .gitignore \
  README.md \
  docs/internal/GITHUB_PROFILE_POLISH_CHECKLIST.md \
  docs/internal/PHASE_9_GITHUB_SURFACE_POLISH.md \
  metadata/README.md \
  scripts/README.md \
  scripts/generate_registry.py \
  scripts/github_surface_setup.sh
git add -u web/   # stage the web/ deletions

# 3. Commit with the recommended message.
git commit

# 4. Push.
git push -u origin arkheionx/research-grade-rebuild

# 5. Open the PR (operator step; do not run here).
gh pr create \
  --base main \
  --head arkheionx/research-grade-rebuild \
  --title "chore(repo): polish GitHub repository surface" \
  --body  "See docs/internal/PHASE_9_GITHUB_SURFACE_POLISH.md"

# 6. After merge, apply repo description and topics.
./scripts/github_surface_setup.sh --apply

# 7. Manually upload the social preview PNG and update the profile per
#    docs/internal/GITHUB_PROFILE_POLISH_CHECKLIST.md.
```



### `.reference_data/` decision

Empty tracked directory used by `scripts/poc_factory.py` as the clone
target for SunWeb3Sec/DeFiHackLabs. Should never be committed. Added
to `.gitignore` and removed from tracking.

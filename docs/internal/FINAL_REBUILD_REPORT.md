# Final Rebuild Report

Branch: `arkheionx/research-grade-rebuild`
Date: 2026-05-21
Maintainer: Yudistira Putra (`arkheionx` / `Yudis-bit`)

---

## 1. Summary

The repository has been rebuilt from a mixed-tone marketing site with a 2-row
README registry into a research-grade archive whose public surfaces are
generated from a single canonical metadata source.

The biggest wins:

- README and web app no longer make claims the repository can't substantiate.
- 18 EVM PoCs are catalogued with structured metadata; the README registry is
  generated, not hand-edited.
- CI works against the actual `EVM/` working directory and clearly distinguishes
  build-only jobs from RPC-gated fork tests.
- `poc_factory.py` is dry-run by default, never auto-commits, never auto-pushes.
- SVM and MoveVM are documented honestly as templates rather than advertised
  as supported.

## 2. Files added

### Documentation (`docs/`)

- `BRAND.md` — name, tone, words to avoid.
- `RESEARCH_STANDARD.md` — what qualifies as a PoC.
- `ETHICS.md` — defensive-only scope, disclosure handling.
- `REPRODUCIBILITY.md` — RPC requirements, common failure modes.
- `CONTRIBUTING.md` — submission flow + PR checklist.
- `SECURITY.md` — reporting unsafe content here, secrets policy.
- `STYLEGUIDE.md` — naming, prose, code style.
- `VM_SUPPORT.md` — honest current status per VM family.
- `METADATA_SCHEMA.md` — full field-by-field spec.
- `ROADMAP.md` — short / mid / long term, plus what is explicitly *not*
  on the roadmap.
- `internal/REBUILD_LOG.md` — phase-by-phase working log.

### Metadata (`metadata/`)

- `schema.json` — JSON Schema for one registry entry.
- `registry.json` — 18 entries, all currently merged EVM PoCs.
- `README.md` — how to edit and regenerate.

### Scripts (`scripts/`)

- `validate_metadata.py` — pure-stdlib validator (schema + repo rules).
- `generate_registry.py` — generates README registry section + web metadata.
  `--check` mode for CI.
- `poc_factory.py` — safe-by-default port helper. `--report`, `--dry-run`,
  `--apply`. No git operations.
- `README.md` — script index and workflow.

### CI (`.github/workflows/`)

- `evm.yml` — `forge fmt --check` + `forge build` (no RPC), then RPC-gated
  fork test job that explicitly notes when it skipped.
- `metadata.yml` — runs validator and `generate_registry.py --check`.
- `web.yml` — `npm ci` (or `install`), `lint --if-present`, `build`.
- `docs.yml` — verifies all required docs exist and are non-empty.

### GitHub templates (`.github/`)

- `ISSUE_TEMPLATE/bug_report.md` — broken PoC.
- `ISSUE_TEMPLATE/poc_verification_issue.md` — reproducibility regression.
- `ISSUE_TEMPLATE/documentation_issue.md` — docs / unsafe content.
- `ISSUE_TEMPLATE/config.yml` — disables blank issues, links ETHICS.md.
- `pull_request_template.md` — checklist + test evidence section.

### Other

- `.env.example` — RPC env var template.
- `EVM/README.md`, `SVM/README.md`, `MoveVM/README.md`.

## 3. Files removed

- `README.md`'s old hand-written HTML registry (replaced by generated section).
- `.github/workflows/foundry.yml` — replaced by `evm.yml` with correct
  `working-directory: EVM`.
- `EVM/.github/` — stray duplicate workflow tree.
- `build` — empty zero-byte file at repo root.
- `poc_factory.py` (root) — moved to `scripts/poc_factory.py`, fully rewritten.
- `generate_web_metadata.py` (root) — replaced by `scripts/generate_registry.py`.
  The legacy "rotating educational insights" filler is gone; web metadata
  is now sourced from real fields (`summary`, `root_cause`, `impact`,
  `references`).

## 4. Architecture changes

- Single source of truth: `metadata/registry.json`.
- Generator: `scripts/generate_registry.py` writes README registry section
  (between markers) and `web/public/metadata.json`.
- Validator: `scripts/validate_metadata.py` enforces schema + repo invariants.
- CI gates: every PR touching `metadata/` or generated outputs is checked.
- VM directory ownership: each VM (`EVM/`, `SVM/`, `MoveVM/`) has its own
  README setting honest expectations.

## 5. Documentation changes

The README has been rewritten end-to-end. Removed: fake CI badges,
"Embargoed Research" placeholder table, "Soroban / cryptography (TBD)"
fabrications, hand-edited 2-row registry, marketing tone.

Added: honest VM status table, repo layout, run commands, link to research
standard / ethics / reproducibility, single-source-of-truth note for the
registry table.

## 6. Metadata changes

- 18 entries written (every existing `EVM/test/<YYYY-MM>/` folder has one).
- All entries currently mark `reproducibility: unverified` because the
  maintainer has not re-run them since porting. Promoting a single entry to
  `deterministic` requires running its `forge test` against an archival
  RPC and confirming the assertions hold.
- Entries cite public post-mortems where the original PoC headers carried
  them; entries with no clear post-mortem in the file (Saddle 2021-01,
  Cheese Bank 2020-11) cite the protocol's own announcement and are
  flagged for verification.

## 7. CI changes

- `evm.yml` builds + checks formatting on every PR. Fork tests run only
  when `ETH_RPC_URL` is configured; absence is logged, not silently
  treated as success.
- `metadata.yml` makes drift between `registry.json` and generated outputs
  fail PRs.
- `web.yml` exercises the Next.js build.
- `docs.yml` makes a missing docs file fail PRs.

## 8. Web changes

- Brand: "Yudis-bit | The DeFi Security Vault" → "Arkheionx Vault".
- Removed "Active Research: 4" / "Chain Support: 12" hardcoded stats
  (unsubstantiated).
- Removed "Hire Yudis-bit" / "Audit Request" CTAs (no audit history
  documented in the repo to back the offer).
- Removed `framer-motion` heavy animation surface; the layout is now
  static cards with filters.
- Severity is now a real field on each entry, not derived from `id <= 3`.
- Filters: VM, severity, chain, category, status, plus full-text search.
- Each card shows summary, root cause, impact, block number, references,
  and a deep-link to the PoC file on GitHub.

## 9. Commands run

```sh
python3 scripts/validate_metadata.py     # ok: 18 entries valid
python3 scripts/generate_registry.py --check   # ok
python3 scripts/poc_factory.py --report  # ok (no .reference_data git checkout)

cd EVM
forge fmt                                # formatted upstream-imported PoCs
forge fmt --check                        # clean
forge build                              # exit 0
forge test --no-match-test testExploit   # 7 fork tests fail without RPC
                                         # (expected — no archival RPC configured)
```

## 10. Passing checks

- Metadata validation: 18 entries valid.
- Generator drift check: clean.
- Formatter check: clean (after one `forge fmt` pass).
- EVM build: clean. (Lint warnings about unchecked ERC20 `transfer` returns
  exist on imported PoCs; they are upstream artifacts, not introduced by
  this rebuild, and are not blocking.)

## 11. Failing / skipped checks

- `forge test` against fork URLs: skipped. No `ETH_RPC_URL` /
  `BASE_RPC_URL` configured in this environment. Documented in
  `docs/REPRODUCIBILITY.md`. CI's `evm.yml` has the same gating.
- `npm install` + `npm run build` for the web app: not run locally
  (no `node_modules`, no network policy attempted). The rewrite uses only
  React + Next 14 + standard CSS — no new dependencies — but the build
  has not been physically exercised on this branch.
- Each PoC's reproducibility status is `unverified`. Promoting requires
  per-PoC fork runs.

## 12. Remaining risks

- The 18 metadata entries were authored from the file headers and public
  post-mortems. A handful (Cheese Bank `block_number`, Spank `block_number`,
  Indexed Finance `block_number`) were inferred from incident dates rather
  than read out of upstream PoCs that didn't pin a block. These should
  be cross-checked against the upstream sources before publishing an
  authoritative table.
- `metadata/registry.json` `loss_usd` numbers are rounded approximations
  from public post-mortems. They are not evidence; treat them as labels.
- Web app build is unverified locally. CI will exercise it on first push.
- Foundry lint warnings on imported PoCs (unchecked `transfer`) remain.
  They reflect upstream code; tightening them would touch many files
  and would deviate from "imported as-is for historical record."

## 13. Suggested next commits

The work splits cleanly into reviewable commits:

1. `chore: add research archive documentation skeleton`
   — `docs/*`, `docs/internal/REBUILD_LOG.md`, `.env.example`.
2. `feat(metadata): add canonical PoC registry schema and 18 entries`
   — `metadata/*`, `scripts/validate_metadata.py`,
   `scripts/generate_registry.py`, `scripts/README.md`.
3. `fix(ci): replace foundry.yml with EVM/web/metadata/docs workflows`
   — `.github/workflows/*`, remove old `foundry.yml` + `EVM/.github/`.
4. `refactor(scripts): make poc_factory safe and reviewable`
   — `scripts/poc_factory.py`, remove root `poc_factory.py`,
   remove root `generate_web_metadata.py`.
5. `feat(EVM): document EVM project; add chain RPC aliases`
   — `EVM/README.md`, `EVM/foundry.toml`, formatter pass.
6. `feat(SVM,MoveVM): add honest template READMEs`
   — `SVM/README.md`, `MoveVM/README.md`.
7. `docs(README): rebuild README around generated registry`
   — `README.md`.
8. `feat(web): consume canonical registry; drop unverified claims`
   — `web/src/app/{layout.tsx,page.tsx,globals.css}`,
   `web/public/metadata.json` (regenerated).
9. `chore: add issue and PR templates`
   — `.github/ISSUE_TEMPLATE/*`, `.github/pull_request_template.md`.

## 14. Suggested GitHub repository settings

- **About description**: "Deterministic Web3 exploit PoCs and security
  research archive. Maintained by arkheionx."
- **Topics**: `web3-security`, `defi-security`, `exploit-poc`,
  `solidity-security`, `foundry`, `smart-contract-auditing`,
  `incident-analysis`, `reproducible-research`, `arkheionx`.
- **Default branch**: `main`.
- **Branch protection on `main`**: require `evm / fmt-build`,
  `metadata / validate`, `docs / required-docs` to pass; require PR
  review; disallow force-push.
- **Discussions**: enable for "ideas" and "research notes" only;
  disable Q&A bug-report category (use issue templates instead).
- **Releases**: not necessary until volume justifies tagged research drops.

## 15. Suggested pinned items

- A pinned README issue: "How to add a PoC" linking
  `docs/CONTRIBUTING.md` and `docs/RESEARCH_STANDARD.md`.
- A pinned issue: "Reproducibility verification queue" listing the 18
  entries and tracking which have been re-run on an archival RPC.
- A project board with three columns: `unverified`, `running locally`,
  `reproduced`. One card per PoC.

---

End of report.

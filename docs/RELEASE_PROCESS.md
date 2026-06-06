# Release Process

Arkheionx Vault publishes research milestones as releases. A release is
a tagged checkpoint that says: at this commit, the corpus had this
shape, this many entries were at each maturity level, and these
artifacts were produced.

The process is intentionally low-ceremony. It exists so the archive's
public history is reviewable, not so milestones become marketing
events.

---

## Release types

| Type | What it marks | Required artifact |
|---|---|---|
| Corpus milestone | Net-new PoCs added since the last release | Updated registry, regenerated quality matrix and maturity index |
| Assertion-hardening milestone | A batch of existing PoCs upgraded from `weak` / `none` to `medium` / `strong` | Per-PoC assertion-patch report under `docs/internal/` |
| Verification milestone | A batch of PoCs promoted to L4 (archival verified) | Verification reports with run transcripts, commit SHAs, verifier handles |
| Case-study milestone | A new L5 case study published | Long-form write-up + auditor checklist walkthrough |
| Taxonomy milestone | A new exploit category added or an existing category restructured | Updated `docs/EXPLOIT_TAXONOMY.md`; mapping notes for any re-classified entries |

A single release may combine types. Combining is allowed; conflating is
not — each artifact must be traceable.

---

## Release checklist

Run before tagging:

```sh
python3 scripts/validate_metadata.py
python3 scripts/generate_registry.py --check
python3 scripts/score_pocs.py --check
python3 scripts/generate_verification_report.py --check
python3 scripts/poc_maturity_index.py --check

cd EVM && forge fmt --check && forge build && cd -
```

Required:

- All commands above exit `0`.
- Registry table in README is in sync with `metadata/registry.json`.
- Maturity index counts match what the release notes claim.
- No PoC has been promoted to L4 or L5 without the corresponding
  artifact (see [`docs/POC_MATURITY_MODEL.md`](POC_MATURITY_MODEL.md)).
- No platform / firm affiliation has been added to the README.

---

## Release notes

A release tag MUST be accompanied by release notes covering:

1. **What changed** — net new PoCs, hardening, verifications,
   case studies, taxonomy edits.
2. **Maturity index delta** — counts at each level before / after.
3. **Honest gaps** — what was attempted and did not land (e.g.
   archival RPC unavailable, public-RPC smoke failed, source quality
   blocked an intake).
4. **Next milestone target** — one sentence; not a timeline.

Release notes do not claim:

- "Largest" or "most comprehensive" archive.
- Affiliation with audit firms, contest platforms, bounty programs.
- Verified status that the maturity index does not back.

---

## Tagging

```sh
git tag -a v0.M-N -m "M0.N — <short title>"
git push origin v0.M-N
```

Tag scheme: `v0.<milestone>.<patch>` while the corpus is below 100
verified PoCs. The `0.` prefix reflects that the archive's public
methodology is still maturing. After M3 (100 verified PoCs), drop the
`0.` prefix and switch to a normal `vMAJOR.MINOR.PATCH` scheme.

A release without a corresponding maturity-index regeneration is
treated as a documentation-only release and tagged accordingly:

```sh
git tag -a docs-YYYY-MM-DD -m "docs: <topic>"
```

---

## Where releases live

- Source of truth: git tag on `main`.
- GitHub Releases page: optional, used for narrative summary.
- Public registry: `metadata/registry.json` at the tagged commit.
- Public maturity index: `reports/poc_maturity_index.md` at the tagged
  commit.

The README never claims a release that does not exist as a tag.

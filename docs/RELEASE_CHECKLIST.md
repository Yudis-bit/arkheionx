# Release Checklist

A printable, item-by-item gate for cutting a release of Arkheionx Vault.
The full process is documented in
[`RELEASE_PROCESS.md`](RELEASE_PROCESS.md). This file is the literal
checklist — copy it into the release PR description and tick the boxes
honestly.

A release is not cut until every applicable box is checked or marked
N/A with a written reason in the PR.

---

## 1. Trigger

- [ ] Release type identified (corpus / assertion / verification /
      maturity / case study / taxonomy).
- [ ] Milestone or trigger documented in the PR description.
- [ ] Release manager named (Yudistira Putra / arkheionx by default).

## 2. Tree state

- [ ] Working on `main` (or a release branch about to merge to `main`).
- [ ] `git status --short` is empty.
- [ ] No tracked secrets, no `.env`, no real RPC URLs in the diff.
- [ ] `.reference_data/` is not tracked.

## 3. Metadata and registry

- [ ] `python3 scripts/validate_metadata.py` passes.
- [ ] `python3 scripts/generate_registry.py --check` passes.
- [ ] `python3 scripts/score_pocs.py --check` passes.
- [ ] `python3 scripts/generate_verification_report.py --check` passes.
- [ ] `python3 scripts/poc_maturity_index.py --check` passes.
- [ ] `python3 scripts/research_dashboard.py --check` passes.

## 4. EVM build

- [ ] `cd EVM && forge fmt --check` passes.
- [ ] `cd EVM && forge build` passes.
- [ ] Fork tests are skipped or green per release type:
  - corpus / assertion / maturity / taxonomy: not required.
  - verification milestone: required, with the run transcript stored
    under the PoC's verification report.

## 5. Reports

- [ ] `reports/poc_quality_matrix.md` regenerated.
- [ ] `reports/poc_maturity_index.md` regenerated.
- [ ] `reports/research_dashboard.md` regenerated.
- [ ] `reports/verification/<id>.md` updated for any PoC that flipped
      verification status in this release.

## 6. README

- [ ] Status table reflects current truth (totals, assertion mix,
      verified count, maturity distribution).
- [ ] Links work (registry, dashboard, maturity index, quality matrix,
      verification reports).
- [ ] No banned hype phrases ("largest", "world-class",
      "industry-leading", "AI-powered" outside of intended use,
      "trusted by", "verified" without basis).
- [ ] No stale `web/` references in the public surface.

## 7. Documentation

- [ ] `docs/POC_MATURITY_MODEL.md` matches the maturity index gates.
- [ ] `docs/EXPANSION_PLAN.md` reflects the milestones being claimed.
- [ ] `docs/RELEASE_PROCESS.md` matches the steps actually taken.
- [ ] No new docs introduced without a link from README or another doc.

## 8. GitHub surface

- [ ] `bash scripts/github_surface_setup.sh --dry-run` produces the
      intended description and topic list.
- [ ] Social preview asset under `.github/assets/` is current. (Manual
      upload via Repository Settings → Social preview.)
- [ ] Issue templates render correctly:
      `research_candidate.md`, `assertion_hardening.md`,
      `poc_verification_issue.md`, `documentation_issue.md`,
      `unsafe_content_report.md`, `bug_report.md`.
- [ ] PR template up to date.

## 9. Safety scan

- [ ] No live-target instructions, scanners, or attacker automation
      added.
- [ ] No new `vm.envString`, `PRIVATE_KEY`, `--broadcast`, or
      `scan.target` calls in PoC source.
- [ ] No fake claims (verified-without-report, fake affiliations,
      fake bounty wins, fake "trusted by").
- [ ] No new content that could meaningfully aid attack against an
      unpatched live system.

## 10. Release notes

- [ ] `docs/launch/GITHUB_RELEASE_NOTES.md` template instantiated for
      this tag.
- [ ] Numeric deltas honest (entries added, hardened, verified).
- [ ] Maintainer attribution present (Yudistira Putra / arkheionx).
- [ ] No claims unsupported by the registry, the dashboard, or the
      verification reports.

## 11. CI

- [ ] `metadata` workflow green.
- [ ] `evm` workflow green (fmt + build job; fork test job per release
      type).
- [ ] `docs` workflow green.

## 12. Tag and publish

- [ ] PR merged to `main`.
- [ ] Tag created from `main` (`vMAJOR.MINOR.PATCH`).
- [ ] Tag pushed: `git push origin <tag>`.
- [ ] GitHub release published from the rendered notes.
- [ ] (Optional) Repository surface refreshed:
      `bash scripts/github_surface_setup.sh --apply`.
- [ ] (Optional) Social preview re-uploaded if changed.

## 13. Announcement

- [ ] Decision recorded: announce or stay quiet.
- [ ] If announcing, the [`LAUNCH_PLAN.md`](LAUNCH_PLAN.md) outline is
      followed and the post avoids hype copy.

## 14. Post-release

- [ ] Open follow-up issues for any known gaps surfaced during this
      release (weak entries remaining, archival-RPC-blocked entries,
      taxonomy gaps).
- [ ] Update `docs/internal/` with a release log entry if the release
      is non-trivial (corpus / verification / maturity).
- [ ] Decompress. Releases are checkpoints, not finish lines.

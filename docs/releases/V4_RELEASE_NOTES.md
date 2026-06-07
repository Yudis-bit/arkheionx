# Arkheionx v4.0.0 — Stable local review-map workflow

**Status: released as v4.0.0 — tagged in git, GitHub release published, site
live.** This document describes the v4.0.0 release of the review-map workflow.
The package version is `4.0.0`; the last tagged stable release the source
installers and the GitHub Action pin to remains `v3.1.0`. Nothing here is
published to PyPI.

## 1. What V4 stabilizes

V4 makes the **local review-map workflow** the stable, supported public surface:
`review-map` and its focused views (`value-paths`, `assumptions`,
`test-gap-map`, `proof-plan`), plus `version` and `doctor`.

## 2. Why V4 exists

DeFi review is not just checking whether the tests you wrote pass. Reviewers need
to know where value enters, moves, and exits, which assumptions protect each
path, and which value paths have no tests. V4 treats that workflow as stable so
teams can rely on it.

## 3. What changed

- The review-map workflow and focused views are the canonical, documented surface.
- The Test Gap Map prints honest `Source: <file>:<line>` evidence from parsed source.
- A coherent product surface across README, docs, website, CLI, and demo.
- New workflow docs: pre-audit and bug-bounty triage.
- Restructured documentation index and website (how-it-works, bug-bounty,
  pre-audit, V4 release pages).

## 4. Stable commands

`arkheionx version`, `arkheionx doctor`, `arkheionx review-map`,
`arkheionx value-paths`, `arkheionx assumptions`, `arkheionx test-gap-map`,
`arkheionx proof-plan`. These run on any install (editable or non-editable).

## 5. Quickstart

```sh
python3 -m pip install -e .
arkheionx doctor
arkheionx review-map .
```

## 6. V4 demo

```sh
arkheionx review-map examples/vault-strategy-oracle-fixture
```

Vault / Strategy / PriceOracle / MockToken. `deposit` is tested; the value exits
and admin setters are deliberately untested, so they surface as value paths and
test gaps. Output is real engine output, locked by tests.

## 7. Bug bounty workflow

Triage and hypothesis generation only. See
[`../BUG_BOUNTY_WORKFLOW.md`](../BUG_BOUNTY_WORKFLOW.md). Do not submit ArkheionX
output as a vulnerability by itself; validate manually; authorized targets only.

## 8. Pre-audit workflow

Map value paths, close test gaps, hand a reviewer a clearer surface. See
[`../PRE_AUDIT_WORKFLOW.md`](../PRE_AUDIT_WORKFLOW.md).

## 9. Safety boundaries

Local and static only. No RPC, no live-chain calls, no exploit automation, no
private-key handling. ArkheionX does not confirm vulnerabilities, assign final
severity, prove protocol safety, or replace an audit. Human review is required.

## 10. Known limitations

- Static heuristics, not execution.
- Cross-contract value flow is surfaced as per-contract paths; end-to-end tracing
  is roadmap work.
- `evidence_links` is empty until you generate local proof/trace artifacts.
- Depth is shown on fixtures; real-protocol validation is planned
  ([`../REAL_PROTOCOL_PROOF_PLAN.md`](../REAL_PROTOCOL_PROOF_PLAN.md)).
- Repository identity is an accepted risk for this release
  ([`../REPO_IDENTITY_MIGRATION.md`](../REPO_IDENTITY_MIGRATION.md)).

## 11. Validation matrix

Docs links, safety wording, version consistency, release readiness, the full
unit-test suite, `make validate`, and the website build all pass. See
[`V4_RELEASE_CHECKLIST.md`](V4_RELEASE_CHECKLIST.md).

## 12. Package / install notes

No PyPI publication. Install from source (`pip install -e .` or `pip install .`).
The source-tree commands `scan`, `test-plan`, and `search` are not bundled in the
wheel and fail gracefully in a non-editable install. See
[`../PACKAGING.md`](../PACKAGING.md).

## 13. Upgrade notes

No breaking changes to the review-map workflow. The focused views read the same
artifacts. Existing `review-map` users need no migration.

## 14. GitHub release draft

> **Arkheionx v4.0.0 — Stable local review-map workflow.** V4 stabilizes the
> local, static review-map workflow: value paths → assumptions → test gaps →
> proof direction → human review. Local-first, no RPC, no exploit automation,
> not an audit, human review required. See the release notes and `docs/V4_STABLE_SCOPE.md`.

## 15. Founder release commands

The package version is already finalized at `4.0.0` in this tree. To release:

```sh
git status --short --branch
git log --oneline --decorate -25
make validate
git push origin main
git tag -a v4.0.0 -m "Arkheionx v4.0.0 — stable local review-map workflow"
git push origin v4.0.0
```

The package metadata is already finalized at `4.0.0`; the `v4.0.0` tag marks the
stable review-map workflow milestone, and the last tagged stable release stays
`v3.1.0` (the installer/action pin) until the tag is cut.

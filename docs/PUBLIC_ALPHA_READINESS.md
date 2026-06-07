# Public alpha readiness

**Status: `PUBLIC_ALPHA_READY_EXCEPT_REPO_IDENTITY`**

This note records exactly what is ready for a limited public alpha and what is
intentionally deferred. It is descriptive, not a guarantee.

## Ready

- **Local/static CLI** — installs and runs offline, no RPC, no live-chain calls,
  no exploit automation, no secrets.
- **Canonical path** — `arkheionx review-map .` is the single first command,
  consistent across README, CLI `--help`, `doctor`, the quickstart, and the
  website.
- **Multi-contract demo** — `examples/vault-strategy-oracle-fixture` (Vault /
  Strategy / PriceOracle / token) produces real value paths, assumptions, and
  test gaps through the actual engine, and is locked by tests.
- **License** — Apache-2.0 in [`LICENSE`](../LICENSE), enforced by the
  release-readiness gate.
- **Safety boundaries** — centralized disclaimer wording, a strict safety-wording
  gate, and a results-interpretation guide
  ([`INTERPRET_RESULTS.md`](INTERPRET_RESULTS.md),
  [`WHAT_ARKHEIONX_IS_NOT.md`](WHAT_ARKHEIONX_IS_NOT.md)).
- **Docs quickstart** — [`TRY_IN_5_MINUTES.md`](TRY_IN_5_MINUTES.md) follows the
  canonical path; the legacy scanner is demoted to an advanced section.
- **Validation gates** — `make validate`, unit tests, docs-link, version, safety,
  and release-readiness checks pass.
- **Install smoke** — a non-editable `pip install .` runs `version`, `doctor`,
  and `review-map`; source-tree-only commands fail gracefully with guidance.

## Deferred (not done; not claimed as done)

- **Repository identity** — the repo is still named `DeFi-Exploit-PoCs` and keeps
  its legacy `EVM/`, `MoveVM/`, and `SVM/` material. This is **intentionally
  deferred by founder decision** and is *not* solved here. Do not treat it as
  resolved.
- **Real-protocol case studies** — depth is demonstrated on fixtures only; there
  is no real-world protocol case study yet.
- **Deeper heuristic engine** — value-flow detection remains static and
  heuristic; cross-contract tracing is illustrative, not a proven trace.
- **Legacy scanner packaging** — the source-tree `scan`/`test-plan`/`search`
  commands are not bundled in the installed wheel (see
  [`PACKAGING.md`](PACKAGING.md)).
- **Website deployment** — the site builds locally; `arkheionx.dev` DNS
  deployment is pending and is not claimed to be live.
- **Adoption** — no users, customers, partners, or production usage are claimed.

## Checklist

- [x] `LICENSE` exists (Apache-2.0)
- [x] README first screen leads with the review-map value proposition
- [x] Canonical command aligned (`arkheionx review-map .`)
- [x] Multi-contract demo fixture exists and is tested
- [x] Docs quickstart aligned to the canonical path
- [x] Safety wording gate passes
- [x] `make validate` passes
- [x] Site build passes
- [x] Non-editable install smoke passes (`version`, `doctor`, `review-map`)
- [ ] Repository identity (deferred by founder decision)

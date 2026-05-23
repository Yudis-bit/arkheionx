# GitHub Release Notes

Draft for the first public release of Arkheionx Vault. Replace counts
with live values from `metadata/registry.json` and the generated
reports at release time.

---

# Arkheionx Vault — first public snapshot

Independent DeFi exploit PoC research archive, maintained by
Yudistira Putra (`arkheionx`).

## What this release is

The first public, productized snapshot of Arkheionx Vault. The corpus
is small by design: standards, taxonomy, assertion model, and
verification process come first; corpus growth follows.

## Snapshot

- 18 historical DeFi exploit PoCs (Foundry, EVM).
- Per-PoC metadata in `metadata/registry.json`.
- Static-readiness scoring: `reports/poc_quality_matrix.md`.
- Maturity ladder distribution: `reports/poc_maturity_index.md`.
- Aggregated dashboard: `reports/research_dashboard.md`.
- Per-PoC verification reports: `reports/verification/`.

## What this release adds vs. earlier work

- Six-level PoC maturity model (`docs/POC_MATURITY_MODEL.md`).
- Maturity index generator (`scripts/poc_maturity_index.py`).
- Research dashboard generator (`scripts/research_dashboard.py`).
- Release process and checklist (`docs/RELEASE_PROCESS.md`,
  `docs/RELEASE_CHECKLIST.md`).
- Launch kit (`docs/LAUNCH_PLAN.md`, `docs/launch/`).
- Expanded contributor system: research-candidate, assertion-hardening,
  and unsafe-content-report issue templates; tightened PR template.
- GitHub surface setup script (dry-run by default).

## Honest current state

- Deterministic-confirmed entries: 0. Public RPC cannot serve
  historical state for most entries; archival RPC is required for
  final verification. This is recorded per entry, not papered over.
- The corpus is dominated by L2 (assertion-hardened) entries blocked
  at the L3 → L4 boundary by archival RPC availability.
- This release does not promote any entry past what the registry and
  verification artifacts back.

## What is intentionally not here

- No live-target tooling, scanners, or drain helpers.
- No "verified archive" claim.
- No audit-firm affiliation, bounty wins, or contest credentials.
- No `web/` frontend — earlier versions had one; it has been removed.

## How to use

```sh
git clone https://github.com/Yudis-bit/DeFi-Exploit-PoCs.git
cd DeFi-Exploit-PoCs/EVM
forge install
export ETH_RPC_URL=https://your-archival-node-endpoint
forge test --match-path "test/2017-07/*.t.sol" -vvvv
```

Most historical PoCs require an archival RPC. See
`docs/FORK_VERIFICATION.md`.

## Contributing

Issue templates: `research_candidate`, `assertion_hardening`,
`poc_verification_issue`, `documentation_issue`,
`unsafe_content_report`. The PR template enforces a safety checklist
and one-PoC-per-patch.

## Roadmap

- Configure archival RPC; produce verification reports for entries
  that pass static review.
- Move strong-static entries to deterministic-confirmed where archival
  fork run produces real output.
- Expand to ~25 verified-ready PoCs at the existing quality bar.

Long-form roadmap: `docs/EXPANSION_PLAN.md`.

## Maintainer

Yudistira Putra — `arkheionx` / [@Yudis-bit](https://github.com/Yudis-bit).

---

## Release notes for the publisher

Before cutting this release:

- Update the snapshot numbers to live registry counts.
- Confirm `python scripts/research_dashboard.py --check` is clean.
- Confirm the README's current-status table matches.
- Do not add a "verified" count line if the registry's
  deterministic-confirmed count is zero.

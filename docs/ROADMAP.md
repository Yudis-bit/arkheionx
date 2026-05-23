# Roadmap

Honest. Subject to change. No commitment dates.

## Short-term

- [x] Fix CI working-directory so EVM workflow actually runs.
- [x] Add canonical metadata schema and registry generator.
- [x] Generate README registry from metadata, not by hand.
- [x] Remove the unfinished web frontend; repository is research-only.
- [x] Make `poc_factory.py` dry-run by default; remove auto-push.
- [x] Add PoC maturity model, maturity index, and research dashboard.
- [ ] Re-verify each merged PoC and update `reproducibility` accordingly.
- [ ] Backfill `block_number`, `severity`, `category` for every existing entry.

## Mid-term

- [ ] First real SVM PoC (replace empty `it()` stub).
- [ ] First real MoveVM PoC (replace empty entry function).
- [ ] WRITEUP.md per PoC: short root-cause analysis with trace excerpt.
- [ ] Per-PoC archival RPC documentation when the standard `mainnet` alias
      isn't sufficient.
- [ ] Optional CI fork-test runs gated by configured secrets, with skip behavior
      that doesn't pretend to pass.

## Long-term

- [ ] Cross-VM exploit taxonomy doc.
- [ ] Auditor-training modules built around selected PoCs.
- [ ] Periodic research notes (no schedule).
- [ ] If volume justifies it, a static site over the registry instead of the
      current Next.js app.

## Explicitly not on the roadmap

- Live-target tooling.
- Generic Web3 audit consultancy product.
- Affiliated branding with audit firms or contest platforms.
- Anything requiring private RPC keys, paid APIs, or non-public protocol
  material checked into the repo.

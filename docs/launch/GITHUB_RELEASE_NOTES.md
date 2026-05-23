# GitHub Release Notes — Template

This file is a template. For each tagged release, copy this template
into the GitHub release UI, instantiate it against the registry and
dashboard at the tag, and remove unused sections.

The numeric placeholders below are deliberately empty. Fill them
honestly from the artifacts at the tagged commit. Do not estimate.

---

## Title

`Arkheionx Vault <vMAJOR.MINOR.PATCH> — <release type>`

Examples:

- `Arkheionx Vault v1.0.0 — research-grade rebuild`
- `Arkheionx Vault v1.1.0 — assertion hardening milestone`
- `Arkheionx Vault v1.2.0 — first archival-verified batch`

Cap the title at 70 characters. The detail belongs in the body.

---

## Body

### Summary

One paragraph. What this release contains and why someone should care.

State only what the registry, the dashboard, and the verification
reports support. No hype copy. No "thrilled to announce".

### Corpus snapshot at this tag

Pulled from `reports/research_dashboard.md` at the tag.

| Metric | Value |
|---|---|
| Total PoCs | <N> |
| Assertion-hardened (medium / strong) | <N> |
| Archival-verified (L4+) | <N> |
| Public-RPC smoke attempted | <N> |
| Maturity distribution | L0 <N> · L1 <N> · L2 <N> · L3 <N> · L4 <N> · L5 <N> |

### What changed

Cite commits or PRs. Group by type:

- **Corpus** — entries added or removed.
- **Hardening** — entries promoted in `assertion_quality`.
- **Verification** — entries promoted to L4 with verification reports.
- **Tooling** — scripts, CI, dashboards.
- **Docs** — model, taxonomy, intake, release process.

Each line should be a verifiable claim, not a marketing line.

### New artifacts

Optional. List artifacts introduced or substantially updated in this
release. Examples:

- `reports/research_dashboard.md`
- `docs/POC_MATURITY_MODEL.md`
- `metadata/backlog/priority-lanes.md`

### Known gaps at this tag

Be explicit:

- Number of entries still at `assertion_quality: weak`.
- Number of entries still requiring archival RPC.
- Categories with no representative entry yet.
- Outstanding contributor or intake gaps.

This section is required. A release without a known-gaps section is
not a release.

### How to read this archive

```sh
git clone https://github.com/Yudis-bit/DeFi-Exploit-PoCs.git
cd DeFi-Exploit-PoCs
git checkout <vMAJOR.MINOR.PATCH>

# Static reports.
open reports/research_dashboard.md
open reports/poc_maturity_index.md
open reports/poc_quality_matrix.md

# Build the EVM project.
cd EVM
forge install
forge build

# Run a single PoC against an archival RPC, if configured.
export ETH_RPC_URL="<archival rpc>"
forge test --match-path "test/<folder>/*.t.sol" -vvv
```

### Maintainer

Yudistira Putra (`arkheionx` /
[@Yudis-bit](https://github.com/Yudis-bit)).

### Disclaimer

Defensive security research. Reproductions target historical, patched,
or otherwise resolved incidents. Nothing here is investment, legal, or
security advice. Read [`docs/ETHICS.md`](../../docs/ETHICS.md) and
[`docs/SECURITY.md`](../../docs/SECURITY.md) before redistributing or
adapting any content.

---

## What this template is not

- It is **not** a marketing post. The LinkedIn / X drafts live
  separately and are optional.
- It is **not** a place to claim verification, affiliation, or coverage
  beyond what the artifacts back.
- It is **not** a compliance document — the legal disclaimer is brief
  by design.

If a section needs to be empty for a given release, delete it. Do not
fill it with filler.

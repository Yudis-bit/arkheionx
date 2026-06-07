# Arkheionx V4 stable scope

**Arkheionx v4.0.0 stabilizes the local review-map workflow.** It does not mean
Arkheionx guarantees protocol safety, confirms vulnerabilities, or replaces an
audit. V4 is the milestone where the review-map path — and its focused views —
are treated as the stable, supported public surface.

Status: prepared locally. The package version reads `3.9.0` until a maintainer
tags `v4.0.0`; the full release package lives under `docs/releases/`
(`V4_RELEASE_NOTES.md` and `V4_RELEASE_CHECKLIST.md`).

## Stable in V4

The review-map workflow and its focused views are stable and supported:

| Command | What it does |
|---|---|
| `arkheionx version` | Print package and milestone metadata |
| `arkheionx doctor` | Check local environment and project layout |
| `arkheionx review-map .` | Build the local review map (canonical first command) |
| `arkheionx value-paths .` | Where value enters, moves, exits |
| `arkheionx assumptions .` | Trust conditions each path depends on |
| `arkheionx test-gap-map .` | Value-sensitive functions with missing tests, with `Source:` refs |
| `arkheionx proof-plan .` | Local Foundry proof-scaffold directions |

These run on any install (editable or non-editable) and operate locally and
statically.

## Experimental / advanced (source-tree only)

These remain available but are **not** the canonical first run, and are not
bundled in the installed wheel — run them from a repository checkout:

- `arkheionx scan` — legacy pre-audit readiness scanner.
- `arkheionx test-plan` — defensive test-plan generator from scanner JSON.
- `arkheionx search` — local security-memory search.

In a non-editable install they exit with a clear message pointing at
`arkheionx review-map` rather than a traceback. See [`PACKAGING.md`](PACKAGING.md).

## Known limitations (kept honest)

- Static heuristics, not execution: value paths are derived from names and
  token-transfer calls, not a proven runtime trace.
- Cross-contract value flow is surfaced as per-contract entry/exit paths;
  connecting them into a single end-to-end trace is roadmap work.
- `evidence_links` is empty until you generate local proof/trace artifacts.
- Depth is demonstrated on fixtures; real-protocol validation is planned
  (see [`REAL_PROTOCOL_PROOF_PLAN.md`](REAL_PROTOCOL_PROOF_PLAN.md)).

## What V4 does not change

No RPC, no live-chain calls, no exploit automation, no private-key handling, no
severity assignment, no vulnerability confirmation, no audit replacement. Human
review is required. See [`WHAT_ARKHEIONX_IS_NOT.md`](WHAT_ARKHEIONX_IS_NOT.md).

## Next

After V4, the focus is engine sharpness (deeper cross-contract value flow) and
real-protocol case studies. See [`ROADMAP.md`](ROADMAP.md).

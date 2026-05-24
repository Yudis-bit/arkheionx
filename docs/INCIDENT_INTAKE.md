# Incident Intake

How a new incident enters Arkheionx Vault, from "I read about this" to
a published, verified PoC entry.

This pipeline exists so the archive can grow safely. Skipping steps
produces entries that look credible but aren't.

---

## Stage 0: Source discovery

A new incident is first noted somewhere external — a post-mortem, a
contest report, a researcher's writeup, a Twitter / X thread, a block
explorer trace. Capture the raw source URL and the date you found it.

Add the candidate to `metadata/backlog/candidates/<candidate-id>.json`
in the candidate format defined in
`metadata/backlog/candidates.template.json`.

Stop here if the incident is still under coordinated disclosure or if
the protocol is unpatched. Mark `embargoed`.

## Stage 1: Reference collection

Collect at minimum:

- The protocol's own post-mortem (if any).
- The attack transaction hash on a block explorer.
- One independent analysis (security firm, researcher, contest).
- Any prior PoC repository for the same incident, with author and
  commit SHA.

If only one source exists, note that in `notes`. A single-source
incident enters the archive only as `compile-only` or marked clearly
that the analysis is single-sourced.

## Stage 2: Incident classification

Place the incident in the [taxonomy](EXPLOIT_TAXONOMY.md):

- Pick a single primary `category` (the root cause, not the means).
- Add secondary causes to `tags`.
- Set initial `severity` based on public loss figures.

If the incident does not fit any category, raise it for taxonomy
review rather than dropping it into `other`.

## Stage 3: Metadata draft

Draft a registry entry by copying `metadata/intake.template.json`. Fill
required fields:

- `id` — `<YYYY-MM>-<protocol-slug>` lowercase, kebab-case.
- `title`, `protocol`, `date`.
- `vm`, `chain`, `rpc_alias`.
- `block_number` — at or one block before the attack tx.
- `category`, `severity`, `status` (start `needs-verification`).
- `summary`, `root_cause`, references.

Mark `reproducibility: unknown` until execution status is known.

## Stage 4: Fork block identification

Confirm the fork block:

- Look up the attack transaction on a block explorer.
- Use `block - 1` for the fork unless setup requires the same block.
- Verify the chain alias resolves on the maintainer's RPC.
- Verify archival data is available at that block.

If the chain has had reorgs, hard forks, or contract redeployments
between the incident and now, capture that in `notes`.

## Stage 5: PoC creation

Copy `EVM/templates/ExploitTemplate.t.sol` to
`EVM/test/<YYYY-MM>/Exploit_<YYYY-MM>.t.sol` (or the protocol-named
pattern for newer entries). Implement:

- `setUp`: fork at `FORK_BLOCK`, fund attacker, snapshot pre-state.
- `_exploit`: the attacker's actual sequence.
- Assertions for every required family in the entry's category.

Constraints:

- No live-target instructions.
- No drain helpers.
- No private keys or RPC URLs in code.
- Setup separated from exploit.

## Stage 6: Assertion creation

Map the entry's `category` to required assertion families in
[ASSERTION_STANDARD.md](ASSERTION_STANDARD.md). Implement each. Bound
profits and losses with lower bounds, not exact values.

If a required family cannot be expressed for this incident, document
why in `notes` and accept that the entry cannot reach
`deterministic-confirmed` until the gap is closed.

## Stage 7: Verification

Run:

```sh
cd EVM
forge fmt --check
forge build
forge test --match-path "test/<YYYY-MM>/*.t.sol" -vvv
```

Generate a verification report:

```sh
python3 scripts/generate_verification_report.py --id <id>
```

Hand-fill the dynamic fields (commit SHA, RPC provider, exit status,
output of each assertion). Commit at `reports/verification/<id>.md`.

## Stage 8: Review

Open a PR using `.github/pull_request_template.md`. Reviewer checks:

- Metadata schema valid (`scripts/validate_metadata.py`).
- Generated artifacts current (`generate_registry.py --check`).
- Score is grade C or better (`score_pocs.py`).
- Verification report attached and matches the metadata fields.
- Safety checklist signed.
- No live-target / drain / scanner content.

A reviewer who is not the author of the PoC should run the test
themselves where feasible.

## Stage 9: Publication

Merge to `main`:

- Update `metadata/registry.json` with final values, including
  `reproducibility` and `verification_status`.
- Regenerate downstream artifacts (`generate_registry.py`).
- Move the candidate from
  `metadata/backlog/candidates/<id>.json` to "published".

The PR is the announcement. The README registry table is regenerated
from metadata.

---

## Backlog management

Candidates that don't reach publication are not failures — they are
the queue. A candidate may be:

- Held for embargo.
- Held for archival RPC availability.
- Held for taxonomy review.
- Closed as out-of-scope (live-target only, insufficient sources,
  duplicate of an existing entry).

Closed candidates are kept in the backlog with the close reason for
traceability.

---

## When intake is rushed

The most common failure mode of intake pipelines is skipping verification
under time pressure. The cost of an entry that says `verified` without
being verified is much higher than the cost of an entry that says
`deterministic-likely-but-unverified` honestly. When in doubt, leave
the lower status and ship the verification report later.

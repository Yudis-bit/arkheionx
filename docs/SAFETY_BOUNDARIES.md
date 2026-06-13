# Safety boundaries

Arkheionx is local-first and static-first. It produces research context, not final
security judgments. These boundaries hold across every command and artifact.

## What Arkheionx does not do

- Does not confirm vulnerabilities.
- Does not replace audits.
- Does not assign final severity.
- Does not scan live chains or require RPC.
- Does not execute exploits or generate exploit automation.
- Does not auto-submit reports or bounties.
- Does not require private keys, seed phrases, or secrets.

## Lines that always hold

- A planning artifact is not a finding.
- A review lane is not a vulnerability.
- A blind spot is not a bug.
- Evidence quality is not vulnerability validity.
- A candidate with evidence is not automatically valid.
- Human review and local proof are required.

## Private scope stays local

Private contest scope, private terms, and all generated output live under
`.arkheionx/` (including `.arkheionx/private/`, `.arkheionx/runs/`, and review
output directories). That path is gitignored and is never committed. The lens and
scope layers run a private-term leak check and warn when output is written outside
`.arkheionx/`.

## Exit codes

Arkheionx analysis commands use exit codes as review signals, not just crash codes:

- `0` — completed; no heuristic warning needs attention.
- `1` — completed, but the output is heuristic and needs human review. This is a
  **warning-style** exit code, not a runtime crash.
- `2` — usage or runtime error (for example, a repo or scope path was not found).

In CI, run analysis commands with `--json` and inspect the decision fields in the
JSON (for example, the report-filter outcomes) instead of treating every non-zero
analysis exit as fatal. The exit-code contract is also recorded in each review
pack's `manifest.json` (`exit_code_semantics`) and in
[`CLI_REFERENCE.md`](CLI_REFERENCE.md).

## Public surface stays generic

The current public surface is target-agnostic. Protocol Lens Packs model protocol
*families* (for example, the generic Fixed Credit Market family); they do not name
or target a specific deployed protocol. A guard test
(`tests/test_public_surface_is_generic.py`) keeps it that way.

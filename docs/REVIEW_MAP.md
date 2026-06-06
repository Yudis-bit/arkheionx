# Protocol Review Map

`arkheionx review-map` turns a local DeFi repository into a structured review
surface: contracts, value paths, assumptions, test gaps, proof suggestions, and
links to any evidence artifacts you have already produced.

> Review-map outputs are review guidance. They are not confirmed vulnerabilities
> unless connected to proof, trace, and human review. Most review-map signals
> start at `HEURISTIC`. Human review remains required.

In release-prep v3.5.0, review-map internals also carry additive Protocol
Intelligence Model IDs (shared `contract_id` / `function_id`) used by the
internal model. This is additive only: every existing review-map key and
artifact (`value-paths`, `assumptions`, `test-gaps`, `proof-plan`,
`evidence-links`, and `review-map --json`) is unchanged, old IDs are preserved
as aliases, and no mandatory `protocol-model.json` is written.

## What is the Protocol Review Map?

Foundry tells you which tests passed. The review map shows what the protocol
still needs to prove. It reads your Solidity (and any local Foundry tests),
classifies value-sensitive functions, traces where value enters and exits, names
the assumptions those paths rely on, points out tests that appear to be missing,
and suggests the next local proof to write.

It is local and static by default: no RPC, no private keys, no live-chain calls,
no Foundry required, and no network access.

## Why it exists

Protocol structure and value flow are usually scattered across files; review
notes and proof artifacts end up ad hoc. The review map gives that work a
single, repeatable, developer-native shape so a reviewer can decide what to look
at first instead of guessing.

## What it does

- Maps contracts and functions that matter.
- Shows where value enters, moves, and can exit (value paths).
- Names the assumptions that protect those paths.
- Surfaces test gaps for value-sensitive functions.
- Suggests local Foundry proof work for the highest-priority gaps.
- Connects existing `proof` / `trace` / `evidence` / `report` artifacts when present.
- Writes JSON and Markdown artifacts for reviewers and for diffing over time.

## What it does not do

- It does not confirm vulnerabilities or assign severity.
- It does not claim bounty eligibility or replace a manual audit.
- It does not run exploits, broadcast transactions, or call live chains.
- It does not guarantee discovery; missed paths and false-positive test gaps are
  expected from static heuristics.

## How to run it

```sh
arkheionx review-map .
arkheionx review-map . --top 5
arkheionx review-map . --target Vault.withdraw
arkheionx review-map . --json
arkheionx review-map . --no-write
arkheionx review-map . --out ./review-out
arkheionx review-map . --include-low-confidence
arkheionx test-gap-map .
arkheionx test-gap-map . --json
arkheionx test-gap-map . --no-write
arkheionx value-paths .
arkheionx value-paths . --json
arkheionx value-paths . --no-write
arkheionx assumptions .
arkheionx assumptions . --json
arkheionx assumptions . --no-write
arkheionx proof-plan .
arkheionx proof-plan . --json
arkheionx proof-plan . --no-write
arkheionx evidence-links .
arkheionx evidence-links . --json
arkheionx evidence-links . --no-write
```

| Option | Purpose |
| --- | --- |
| `--out <dir>` | Write artifacts to `<dir>` (default: `<repo>/.arkheionx/out/review-map/`). |
| `--top <n>` | Number of top review targets to show. |
| `--json` | Print machine-readable JSON to stdout only (no human text, no ANSI). |
| `--no-write` | Print the summary only; write no artifact files. |
| `--include-low-confidence` | Include low-confidence test gaps. |
| `--target <Contract.function>` | Limit the map to a single function. |

## Status and exit codes

A static run is heuristic by default, so it prints a `Status:` line in the
**Boundary** section noting the result is heuristic review guidance and **exits 1
by design** — this is expected, not a crash or an error. Exit codes follow the
workbench convention:

- `0` — ok (only when the map is compiler-confirmed).
- `1` — heuristic review guidance (the normal static case).
- `2` — usage/input error (bad path, no Solidity files, invalid `--top`,
  unknown `--target`).

## Output artifacts

By default, artifacts are written under `<repo>/.arkheionx/out/review-map/`
(gitignored, like all generated output):

| File | Contents |
| --- | --- |
| `review-map.json` | Complete structured review map. |
| `review-map.md` | Human-readable overview. |
| `value-paths.json` | Value paths only. |
| `test-gaps.json` | Test gaps only. |
| `assumptions.json` | Assumptions only. |
| `proof-plan.json` | Proof suggestions only. |
| `evidence-links.json` | Links to existing evidence artifacts. |
| `review-summary.md` | Short reviewer-facing summary. |
| `review-map.mmd` | Mermaid graph: value paths and assumptions. |
| `test-gap-map.json` | Test gaps prioritized for "what to test/prove first" (derived view). |
| `test-gap-map.md` | Concise human Test Gap Map. |

All artifacts are plain text (no ANSI), contain no secrets, no RPC URLs, and no
private keys, and use repo-relative paths where possible.

## How to read value paths

A value path describes how value can move through a contract:

- **Entry function** — where value enters (for example `deposit`, `stake`).
- **Movement** — accounting/transfer steps in between.
- **Exit function** — where value can leave (for example `withdraw`, `borrow`).
- **Conditions to verify** — guards a reviewer should confirm (entitlement
  checks, fresh-price checks, reentrancy ordering, health-factor checks).
- **Assumptions** — the properties the path relies on.
- **Test coverage hint** — `none`, `partial`, or `referenced` (a weak hint, not
  proof of coverage).

Start with the highest-priority value paths (value leaving the system).

## Focused Value Paths

`review-map` writes `value-paths.json` as the focused value-path artifact. The
v3.3.0 surface adds the matching command:

```sh
arkheionx value-paths .
arkheionx value-paths . --json
arkheionx value-paths . --target Vault.withdraw --no-write
```

The command reads an existing
`<repo>/.arkheionx/out/review-map/value-paths.json` when present. If no
artifact exists, it builds the review map locally and extracts the existing
`ReviewMap.value_paths` data. `--no-write` keeps that build in memory; `--out
<dir>` reads or writes the explicit review-map artifact directory.

JSON mode emits the same payload shape as `value-paths.json` and does not wrap
it in a new envelope. Human mode is a bounded terminal view showing totals,
priority buckets, entry/exit functions, review assumptions, and the next local
commands. Priority remains **review order, not severity**. Value paths are
review guidance, not confirmed bugs, and the focused command does not change
`review-map --json` or existing artifact filenames.

## How to read assumptions

Assumptions are protective properties a value path appears to rely on — for
example "oracle price is fresh", "tokens behave like standard ERC20", "admin role
is bounded", or "reward index is monotonic". They are review prompts: confirm
each holds, or write a test that checks it. Each assumption lists the functions
that use it and any related test gaps.

## Focused Assumptions

`review-map` writes `assumptions.json` as the focused assumption artifact. The
v3.3.0 surface adds the matching command:

```sh
arkheionx assumptions .
arkheionx assumptions . --json
arkheionx assumptions . --target Vault.withdraw --no-write
```

The command reads an existing
`<repo>/.arkheionx/out/review-map/assumptions.json` when present. If no artifact
exists, it builds the review map locally and extracts the existing
`ReviewMap.assumptions` data. `--no-write` keeps that build in memory; `--out
<dir>` reads or writes the explicit review-map artifact directory.

JSON mode emits the same payload shape as `assumptions.json` and does not wrap
it in a new envelope. Human mode is a bounded terminal view showing totals,
assumption categories, related functions, related test gaps, and the next local
commands. Priority remains **review order, not severity**. Assumptions are
review prompts, not confirmed bugs, and the focused command does not change
`review-map --json` or existing artifact filenames.

## How to read test gaps

A test gap is a suggestion to add or strengthen a local test for a
value-sensitive function. Each gap lists suggested scenarios (for example
withdrawal boundary, stale oracle, double claim, slippage bound) and a
confidence level. Low-confidence gaps are hidden by default; pass
`--include-low-confidence` to see them. A test gap is not a claim that a bug
exists.

## Test Gap Map

`review-map` writes a **Test Gap Map** (`test-gap-map.json` and
`test-gap-map.md`) to help answer one question before review or audit: _which
tests or local proofs should I write first?_ v3.2.0 emitted this as an artifact;
the v3.3.0 surface adds the focused command:

```sh
arkheionx test-gap-map .
arkheionx test-gap-map . --json
arkheionx test-gap-map . --target Vault.withdraw --no-write
```

The command reads an existing `<repo>/.arkheionx/out/review-map/test-gap-map.json`
when present. If no artifact exists, it builds the review map locally and derives
the Test Gap Map with the same builder used by `review-map`. `--no-write` keeps
that build in memory; `--out <dir>` reads or writes the explicit review-map
artifact directory.

It is a derived, developer-first view of the existing test gaps — it adds no new
analysis and reuses the same `gap-<contract>-<function>` ids. Each entry joins a
test gap to its review priority, scenario category, related value paths and
assumptions, suggested scenarios, proof suggestion, evidence status, and the
exact next command. The JSON also carries a `summary` (totals by priority,
with-proof, missing-evidence).

Priority here is **review order, not severity**, and confidence stays
conservative (HEURISTIC by default). The Test Gap Map is review guidance, not
confirmed vulnerabilities, and the focused command does not change
`review-map --json` or the existing artifact filenames.

## How to read proof suggestions

A proof suggestion is a local Foundry proof you could write next. It includes an
objective, a setup, an action, and assertions, plus a `foundry_hint` that reuses
the existing workflow:

```sh
arkheionx prove . --target Vault.withdraw --run
```

## Focused Proof Plan

`review-map` writes `proof-plan.json` as the focused proof suggestion artifact.
The v3.3.0 surface adds the matching planning command:

```sh
arkheionx proof-plan .
arkheionx proof-plan . --json
arkheionx proof-plan . --target Vault.withdraw --no-write
```

The command reads an existing
`<repo>/.arkheionx/out/review-map/proof-plan.json` when present. If no artifact
exists, it builds the review map locally and extracts the existing
`ReviewMap.proof_suggestions` data. `--no-write` keeps that build in memory;
`--out <dir>` reads or writes the explicit review-map artifact directory.

JSON mode emits the same payload shape as `proof-plan.json` and does not wrap it
in a new envelope. Human mode is a bounded terminal view showing proof targets,
objectives, setup, actions, assertions, related gaps or assumptions, and next
commands. `proof-plan` is planning only: it does not execute Foundry, does not
create proof/evidence/report artifacts, and does not replace
`arkheionx prove <repo> --target <target> --run`. Proof plans are review
guidance, not confirmed bugs or executed proofs, and the focused command does
not change `review-map --json` or existing artifact filenames.

## How to read evidence links

Evidence links are references from review-map targets to existing local
proof/trace/evidence/report artifacts under `.arkheionx/out/`. They help answer:
which review-map targets already have local evidence records to inspect? They
do not create evidence, execute proofs, promote evidence levels, or indicate
that human review has happened.

When local proof, trace, evidence package, or report draft artifacts exist,
`evidence-links.json` can include additive linkage fields such as proof receipt
IDs, trace receipt IDs, evidence package IDs, evidence readiness, and report
draft paths. IDs are copied only from existing local artifacts; Arkheionx does
not invent receipt or package IDs during evidence-link generation.

## Focused Evidence Links

`review-map` writes `evidence-links.json` as the focused evidence-link artifact.
The v3.3.0 surface adds the matching read-only command:

```sh
arkheionx evidence-links .
arkheionx evidence-links . --json
arkheionx evidence-links . --target Vault.withdraw --no-write
```

The command reads an existing
`<repo>/.arkheionx/out/review-map/evidence-links.json` when present. If no
artifact exists, it builds the review map locally and extracts the existing
`ReviewMap.evidence_links` data. `--no-write` keeps that build in memory;
`--out <dir>` reads or writes the explicit review-map artifact directory.

JSON mode emits the same payload shape as `evidence-links.json` and does not
wrap it in a new envelope. Human mode is a bounded terminal view showing total
links, evidence-level and readiness buckets, source buckets, related targets,
artifact paths, evidence package IDs, receipt IDs, and report draft links when
present. `evidence-links` is distinct from `arkheionx evidence`: it does not
package evidence, does not execute proofs, does not create report artifacts, and
does not change `review-map --json` beyond additive evidence-link contents.
Report links remain draft/manual-review only. Evidence links are review
guidance, not confirmed bugs, final severity, or proof of audit readiness.
The v3.4.0 workflow enriches these links with local proof/trace
receipt IDs, evidence package IDs, readiness, and report draft paths when those
existing artifacts contain them. The v3.4.0 finalization is local only; it does
not imply public publication.

## Evidence levels

The review map uses the same conservative ladder as the rest of Arkheionx:

- `HEURISTIC` — static analysis and pattern matching only (the default).
- `COMPILER_CONFIRMED` — the target compiles in the local project.
- `EXECUTION_CONFIRMED` — a relevant local Foundry test executed.
- `EVIDENCE_READY` — proof and trace artifacts are packaged for review.
- `HUMAN_REVIEWED` — manual reviewer attestation only; not emitted automatically.

Most review-map signals start at `HEURISTIC`. They only rise when connected to
proof/trace/evidence artifacts and, finally, human review.

## Safety boundaries

- Local/static repository analysis only.
- No RPC, no live-chain calls, no deployed-contract scanning.
- No private keys, seed phrases, or secrets.
- No exploit automation and no transaction broadcasting.
- Review guidance only — not confirmed vulnerabilities, severity, or audit.

Use only on repositories you own or are authorized to review.

## Demo examples

```sh
arkheionx demo --copy amm-swap ./arkheionx-demo
arkheionx review-map ./arkheionx-demo
arkheionx review-map ./arkheionx-demo --json
arkheionx review-map ./arkheionx-demo --no-write
```

The bundled `oracle-staking`, `amm-swap`, and `lending-vault` demos all produce a
full review map (see [`DEMO_WORKFLOW.md`](DEMO_WORKFLOW.md)).

## JSON output

```sh
arkheionx review-map . --json
```

Emits the complete review map to stdout as JSON only (no human text, never any
ANSI). It includes `schema_version` and `generated_at`. The schema is
[`../schemas/review-map.schema.json`](../schemas/review-map.schema.json).

## No-write mode

```sh
arkheionx review-map . --no-write
```

Prints the CLI summary and writes no artifact files (it does not create the
output directory). Useful in CI or for a quick look.

## How it connects to the rest of Arkheionx

The review map sits on top of the existing workbench. After mapping, raise
evidence levels with the existing commands:

```text
review-map -> proof-plan -> prove --run -> trace -> evidence -> report -> evidence-links -> human review
```

See [`CLI_REFERENCE.md`](CLI_REFERENCE.md), [`PUBLIC_SURFACE.md`](PUBLIC_SURFACE.md),
[`OUTPUT_STANDARD.md`](OUTPUT_STANDARD.md), [`EXECUTION_PROOF.md`](EXECUTION_PROOF.md),
and [`EVIDENCE_PACKAGE.md`](EVIDENCE_PACKAGE.md).

# Protocol Review Map

`arkheionx review-map` turns a local DeFi repository into a structured review
surface: contracts, value paths, assumptions, test gaps, proof suggestions, and
links to any evidence artifacts you have already produced.

> Review-map outputs are review guidance. They are not confirmed vulnerabilities
> unless connected to proof, trace, and human review. Most review-map signals
> start at `HEURISTIC`. Human review remains required.

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
```

| Option | Purpose |
| --- | --- |
| `--out <dir>` | Write artifacts to `<dir>` (default: `<repo>/.arkheionx/out/review-map/`). |
| `--top <n>` | Number of top review targets to show. |
| `--json` | Print machine-readable JSON to stdout only (no human text, no ANSI). |
| `--no-write` | Print the summary only; write no artifact files. |
| `--include-low-confidence` | Include low-confidence test gaps. |
| `--target <Contract.function>` | Limit the map to a single function. |

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

## How to read assumptions

Assumptions are protective properties a value path appears to rely on — for
example "oracle price is fresh", "tokens behave like standard ERC20", "admin role
is bounded", or "reward index is monotonic". They are review prompts: confirm
each holds, or write a test that checks it. Each assumption lists the functions
that use it and any related test gaps.

## How to read test gaps

A test gap is a suggestion to add or strengthen a local test for a
value-sensitive function. Each gap lists suggested scenarios (for example
withdrawal boundary, stale oracle, double claim, slippage bound) and a
confidence level. Low-confidence gaps are hidden by default; pass
`--include-low-confidence` to see them. A test gap is not a claim that a bug
exists.

## How to read proof suggestions

A proof suggestion is a local Foundry proof you could write next. It includes an
objective, a setup, an action, and assertions, plus a `foundry_hint` that reuses
the existing workflow:

```sh
arkheionx prove . --target Vault.withdraw --run
```

## Evidence levels

The review map uses the same conservative ladder as the rest of Arkheionx:

- `HEURISTIC` — static analysis and pattern matching only (the default).
- `COMPILER_CONFIRMED` — the target compiles in the local project.
- `EXECUTION_CONFIRMED` — a relevant local Foundry test executed.
- `EVIDENCE_READY` — proof and trace artifacts are packaged for review.
- `HUMAN_REVIEWED` — a human reviewer has confirmed the result.

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
review-map -> hunt -> prove --run -> trace -> evidence -> report -> human review
```

See [`CLI_REFERENCE.md`](CLI_REFERENCE.md), [`PUBLIC_SURFACE.md`](PUBLIC_SURFACE.md),
[`OUTPUT_STANDARD.md`](OUTPUT_STANDARD.md), [`EXECUTION_PROOF.md`](EXECUTION_PROOF.md),
and [`EVIDENCE_PACKAGE.md`](EVIDENCE_PACKAGE.md).

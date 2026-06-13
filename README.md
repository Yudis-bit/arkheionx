# Arkheionx

Local-first Ethereum security research workflow for Solidity and DeFi repositories.

Arkheionx turns scope, value flow, protocol behavior, invariants, and local evidence
into focused review lanes before report writing.

**No RPC. No live-chain scanning. No auto-submit. Human review required.**

```bash
python3 -m pip install -e .
arkheionx review . --scope-file scope.md --out .arkheionx/review
```

## What it does

Arkheionx reads a Solidity or DeFi repository and a scope note and writes a single
local review pack — Markdown for humans and JSON for tools. It maps where value
moves, the assumptions that guard each path, which paths have no tests, and a ranked
order of what a human should inspect first.

- Maps contracts, functions, value paths, assumptions, and review lanes.
- Surfaces a prioritized "inspect first" order (review order, not severity).
- Turns hypotheses into local evidence tasks, each with a kill condition.
- Grades whether local proof actually supports a candidate.
- Filters weak, out-of-scope, or under-proven candidates before report writing.
- Runs `arkheionx review-map` for a quick read of any repo or the bundled demo.

## Why it exists

Reviewing a DeFi protocol is not just checking whether your tests pass. A reviewer
needs to know where value enters, moves, and exits, which assumptions protect each
path, and which paths have no tests at all. Arkheionx makes that surface explicit and
repeatable before manual review, so review time goes where value moves.

## Quickstart

```bash
# Install from source (editable), or run the source installer:
python3 -m pip install -e .   # or: sh install.sh
arkheionx version
arkheionx doctor

# Explore the bundled demos:
arkheionx demo --list

# Build a local review pack:
arkheionx review . --scope-file scope.md --out .arkheionx/review

# Quick review map of a repo or the bundled demo:
arkheionx review-map examples/vault-strategy-oracle-fixture
```

No API key, private key, RPC URL, or token is required. See
[`docs/INSTALLER.md`](docs/INSTALLER.md) and [`docs/DEMO_WORKFLOW.md`](docs/DEMO_WORKFLOW.md).

## Core workflow

Arkheionx supports one workflow end to end:

```text
Scope → Value flow → Protocol behavior → Review lanes → Evidence tasks → Evidence judge → Report filter
```

- **Scope** — start from the actual review rules.
- **Value flow** — map where assets enter, move, and exit.
- **Protocol behavior** — capture the promises the system appears to rely on.
- **Review lanes** — prioritize where a human should inspect first.
- **Evidence tasks** — turn hypotheses into local tests with kill conditions.
- **Evidence judge** — check whether local proof actually supports the claim.
- **Report filter** — block weak, out-of-scope, or under-proven candidates.

A human always makes the security call. See
[`docs/CORE_WORKFLOW.md`](docs/CORE_WORKFLOW.md).

## Protocol Lens Packs

A protocol lens models a protocol family — value flows, behavior promises, economic
invariants, and temporal windows — so the review lanes, tasks, and evidence
requirements become protocol-aware. The engine stays generic; a lens adds context,
not target-specific knowledge.

```bash
arkheionx review . --scope-file scope.md --lens fixed-credit-market --out .arkheionx/review
```

The first lens is the generic **Fixed Credit Market** family. A lens is a planning
model, not a finding: it encodes no line numbers and no known bug, and it never runs
against a live chain. See
[`docs/PROTOCOL_LENS_PACKS.md`](docs/PROTOCOL_LENS_PACKS.md) and
[`docs/FIXED_CREDIT_MARKET_LENS.md`](docs/FIXED_CREDIT_MARKET_LENS.md).

## Outputs

The review pack is written under `.arkheionx/` — generated, local, gitignored, and
not intended to be committed as source truth:

- Scope map, value-flow map, and interaction map.
- Review lanes and evidence tasks with kill conditions.
- Protocol model, economic invariants, and an evidence rubric.
- A report filter and a model-agnostic agent input.
- Machine-readable `review.json` and `manifest.json`. See
  [`docs/SCHEMAS.md`](docs/SCHEMAS.md).

## Safety boundaries

Arkheionx provides review context, not final security judgments. Human review is
required.

Default operation is intentionally narrow:

- Local repository analysis only.
- No RPC by default.
- No live-chain mutation.
- No private keys or secrets.
- No automated exploitation.
- No auto-submit.
- No guaranteed vulnerability discovery.
- No severity guarantee.
- Not an audit, certification, or replacement for manual review.

Machine-generated context helps prioritize inspection; it does not decide impact or
severity. Even a relevant local Foundry test executed is still review context, not a
final security judgment. Run Arkheionx only on repositories you are authorized to
review. See [`docs/SAFETY_BOUNDARIES.md`](docs/SAFETY_BOUNDARIES.md).

## Documentation

Full index: [`docs/README.md`](docs/README.md).

- [`docs/CORE_WORKFLOW.md`](docs/CORE_WORKFLOW.md) — `arkheionx review` and the review pack
- [`docs/PROTOCOL_LENS_PACKS.md`](docs/PROTOCOL_LENS_PACKS.md) — protocol-aware lenses
- [`docs/FIXED_CREDIT_MARKET_LENS.md`](docs/FIXED_CREDIT_MARKET_LENS.md) — the first generic lens
- [`docs/SCHEMAS.md`](docs/SCHEMAS.md) — machine-readable artifacts
- [`docs/SAFETY_BOUNDARIES.md`](docs/SAFETY_BOUNDARIES.md) — boundaries and the exit-code contract
- [`docs/CLI_REFERENCE.md`](docs/CLI_REFERENCE.md) — every command and flag
- [`docs/PUBLIC_SURFACE.md`](docs/PUBLIC_SURFACE.md) — the stable command surface
- [`docs/ROADMAP.md`](docs/ROADMAP.md) — direction

## GitHub Action

Pinned stable action example:

```yaml
uses: Yudis-bit/DeFi-Exploit-PoCs/.github/actions/pre-audit@v8.0.1
```

See [`docs/GITHUB_ACTION_USAGE.md`](docs/GITHUB_ACTION_USAGE.md).

## Release status

Latest stable release: **v8.0.1** — Clean Product Surface. Current package version:
**8.0.1**. This is a product-surface patch on top of v8.0.0: it cleans the README and
website and changes no engine behavior, CLI command, or analysis. Release tags, the
GitHub Release, and the site deploy are cut at release time.

## License

Arkheionx is licensed under the Apache License 2.0. See [`LICENSE`](LICENSE).
Security policy: [`SECURITY.md`](SECURITY.md).

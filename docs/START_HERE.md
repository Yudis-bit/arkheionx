# Start Here

A 60-second orientation to Arkheionx. For the full command surface see
[`CLI_REFERENCE.md`](CLI_REFERENCE.md); for terminal behaviour see
[`CLI_UX.md`](CLI_UX.md).

## What Arkheionx is

A local/static pre-audit readiness CLI for DeFi repositories. It turns a
Solidity/Foundry repo into a structured review map: contracts, value paths,
assumptions, test gaps, proof suggestions, and links to existing evidence.

## 30-second mental model

Foundry runs tests and tells you pass/fail. Arkheionx maps what your protocol
still needs to prove before audit or review:

| Foundry | Arkheionx |
| --- | --- |
| Runs tests | Maps value paths |
| Reports pass/fail | Lists assumptions and test gaps |
| — | Suggests local proofs and links existing evidence |

## What it does not do

No RPC. No live-chain calls. No private keys or secrets. No transaction
broadcasting. No exploit automation. No auto-submit. It does not confirm
vulnerabilities, assign severity, or replace a formal audit.

## First run

```sh
arkheionx review-map .
```

No Solidity repo handy? Copy a bundled demo first:

```sh
arkheionx demo --copy amm-swap ./arkheionx-demo
arkheionx review-map ./arkheionx-demo
```

Focused review-map views are available on the v3.3.0 development branch:

```sh
arkheionx test-gap-map ./arkheionx-demo
arkheionx value-paths ./arkheionx-demo
arkheionx assumptions ./arkheionx-demo
arkheionx proof-plan ./arkheionx-demo
arkheionx evidence-links ./arkheionx-demo
```

They read existing `.arkheionx/out/review-map/` artifacts when present or derive
the same payloads locally when missing. Use `--json` for machine-readable output
and `--no-write` to build in memory without creating artifact directories.
`evidence-links` is read-only over existing linked local artifacts; it does not
create evidence.

## How to read the output

The terminal output is, top to bottom:

1. A banner and the mode/safety line (local/static, no RPC, no keys).
2. Honest phase lines — inspecting, mapping, writing — with real counts.
3. Review Priorities — what to look at first (review order, not findings).
4. Summary — the counts behind the map.
5. Artifacts — files written under `.arkheionx/out/review-map/`.
6. Next — the exact commands to run next.
7. Boundary — the safety reminder.

Start with Review Priorities, then open the test gaps, then the proof
suggestions.

## What artifacts mean

Artifacts are written under `.arkheionx/out/review-map/` (gitignored):
`review-map.md` and `review-map.json` (the full map), plus focused
`value-paths.json`, `assumptions.json`, `test-gaps.json`, `proof-plan.json`,
`evidence-links.json`, a `review-summary.md`, and a `review-map.mmd` diagram.
A `test-gap-map.json` / `test-gap-map.md` pair ranks which tests or local proofs
to write first (review order, not severity). All are plain text. Use `--no-write`
to skip writing and `--json` for a machine-readable map on stdout.

## After review-map

Use the proof suggestions to create or run local proofs, then raise evidence
levels with the existing workflow:

```sh
arkheionx prove . --target <Contract.function> --run
arkheionx trace . --target <Contract.function>
arkheionx evidence . --target <Contract.function>
```

See [`REVIEW_MAP.md`](REVIEW_MAP.md) for the full review-map reference.

## Safety boundaries

Arkheionx uses authorized local/static repository analysis only. Review-map
output is review guidance; most signals start at `HEURISTIC` and only rise when
connected to proof, trace, and evidence. Human review remains required. Use it
only on repositories you own or are authorized to review.

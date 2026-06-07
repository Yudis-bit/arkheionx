# Try ArkheionX in 5 minutes

This guide runs ArkheionX against a bundled **multi-contract** demo and walks the
canonical review path: map value flow, read the trust assumptions, and see which
value paths have no tests.

Everything here is local and static. It does not call RPC, inspect deployed
contracts, submit transactions, or create GitHub issues.

## 1. Install (source)

```sh
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e .
```

See [`INSTALLER.md`](INSTALLER.md) or [`INSTALLATION.md`](INSTALLATION.md) for the
helper script and other install paths. No API key, private key, RPC URL, or
GitHub token is required.

## 2. Check your environment

```sh
arkheionx doctor
```

## 3. Build the review map (the canonical command)

```sh
arkheionx review-map examples/vault-strategy-oracle-fixture
```

You will see a ranked **Inspect first** list, a summary of contracts, value
paths, assumptions, and test gaps, and the artifacts written under
`.arkheionx/out/review-map/` (gitignored). The bundled fixture is a small
Vault / Strategy / PriceOracle / token protocol whose test only covers
`deposit` — so the value exits show up as uncovered.

## 4. Read the focused views

```sh
arkheionx value-paths   examples/vault-strategy-oracle-fixture
arkheionx assumptions   examples/vault-strategy-oracle-fixture
arkheionx test-gap-map  examples/vault-strategy-oracle-fixture
arkheionx proof-plan    examples/vault-strategy-oracle-fixture
```

- **value-paths** — where value enters, moves, and exits (look for
  `coverage none`).
- **assumptions** — the trust each path depends on (oracle freshness, access
  control, accounting).
- **test-gap-map** — value-sensitive functions with missing or weak test
  references.
- **proof-plan** — local Foundry scaffolds you can fill in.

## 5. Interpret the result

Read [`INTERPRET_RESULTS.md`](INTERPRET_RESULTS.md). In short: the review map is
a prioritization aid. Value paths are static heuristics, assumptions are review
prompts, and a test gap means coverage *looks* missing — none of it confirms a
bug. A human makes the security call. See
[`WHAT_ARKHEIONX_IS_NOT.md`](WHAT_ARKHEIONX_IS_NOT.md) for the boundaries.

## 6. Next action

Point ArkheionX at a repository you own or are authorized to review:

```sh
arkheionx review-map .
```

Then optionally scaffold a local proof for a high-priority value exit (requires
Foundry, never fakes a result):

```sh
arkheionx prove . --target Vault.withdraw --run
```

For a guided first run, see [`ONBOARDING.md`](ONBOARDING.md). To install, check,
and update via the lifecycle helper, see [`ARKUP.md`](ARKUP.md). For problems,
see [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md).

---

## Advanced / legacy readiness scanner

ArkheionX also ships a deeper, legacy pre-audit readiness scanner
(`scripts/pre_audit_scan.py`, also available as `arkheionx scan`). It produces
readiness reports, SARIF, baselines, issue plans, and longer-form delivery
artifacts. It is heavier than `review-map` and is not the recommended first run,
but it remains supported for teams that want the full readiness report set.

```sh
make demo
```

That shortcut runs the scanner against `examples/oracle-staking-fixture` and
writes the `examples/reports/demo-*` artifacts (technical report, JSON, SARIF,
baseline, issue plan, launch report, sprint plan, contest-readiness, executive
summary, and remediation roadmap). The equivalent explicit invocation and an
optional dry-run GitHub issue workflow are documented in
[`PUBLIC_DEMO_WORKFLOW.md`](PUBLIC_DEMO_WORKFLOW.md).

You can also search the local security memory graph:

```sh
python3 scripts/search_knowledge.py "oracle stale price"
```

Generated artifacts are written under `.arkheionx/out/` (review-map) or
`examples/reports/` (scanner demo). A passing test does not prove the absence of
a bug; human review is required. ArkheionX output is not a formal audit and not a
security guarantee. It helps teams prepare for review.

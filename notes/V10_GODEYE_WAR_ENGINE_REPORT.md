# ARKHEIONX V10 GODEYE WAR ENGINE — REPORT (private, internal)

Status: deeper than the first slice. The vertical slice is complete, working, and
tested; the three previously-PARTIAL benchmark families now have dedicated
end-to-end fixtures (benchmark 6/9 -> 9/9), and four new analytical layers were
added (named taint detectors, state-machine contradictions, an explainable severity
score, and pre-output quality gates), plus an operational memory CLI and artifact
schema hardening.

Branch: private/v10-godeye-war-engine. Pushed: No. Tagged: No. Released: No.
Website/VPS: untouched. Global package version: unchanged (`9.1.0.dev0`; stable
remains v8.0.1). The V10 milestone `v10.0.0-dev` is surfaced only inside war-run
artifacts, not in package metadata. V9.1 stable behavior is untouched.

This is an internal technical note. No hype, no guarantees, no public claims.
Arkheionx does not find all bugs; it reconstructs the economic machine, derives
candidate invariants, ranks attack candidates, and tells the researcher which are
worth proving. A human always makes the security call.

## How to run

```bash
# War-run on an authorized local target (writes under <target>/.arkheionx/war-run/):
arkheionx war-run tests/fixtures/godeye/oracle_decimal_normalization_fixture
arkheionx war-run <repo> --scope scope.yaml --out .arkheionx/war-run --asset-decimals 6

# Operate the root-cause memory brain:
arkheionx memory add --invariant-family DEBT_REPAYMENT_RECONCILIATION \
  --entry-function LoanRouter.repay --attacker borrower --status submitted --notes "..."
arkheionx memory classify --invariant-family DEBT_REPAYMENT_RECONCILIATION \
  --entry-function OtherMarket.repay --attacker borrower   # -> SAME_ROOT_CAUSE
arkheionx memory export   # shareable fingerprint; notes redacted

# Run the benchmark fixtures / tests:
python3 -m unittest discover -s tests            # full suite
python3 -m unittest discover -s tests -p "test_v10_*.py"   # V10 only
```

## What is truly working now

1. Local source indexing (read-only, capped). 2. Fallback semantic extraction
(contracts, functions, inheritance, state vars, structs+fields, call graph,
alias-aware storage map, external-call ordering / reentrancy relevance,
calldata->value-sink data flow). 3. Named taint detectors (consent-gap, oracle,
credit-from-nominal, message-id-to-mint, status-after-call, ...). 4. DeFi entity
extraction. 5. State transitions for borrow/repay/deposit/withdraw/redeem/consume
with internal-call closure, plus shape flags that attach families by semantics, not
just by name. 6. State-machine contradiction detection. 7. Invariant generation with
suspicious-here reasons for nine families. 8. Attack-candidate construction +
ranking. 9. Economic severity gate with an explainable numeric score, typed
impact/cap/proof, and a PARK_INCOMPLETE gate. 10. Foundry PoC skeletons with honest
compile-readiness, family-specific assertions, and secret-redaction notes. 11. Fork
requirement generation with chain inference + secret redaction (no URL/keys, no
broadcast). 12. Root-cause memory file store + semantic dedup + an operational
`arkheionx memory` CLI. 13. War-run with pre-output quality gates and stamped,
schema-hardened artifacts + a console verdict. 14. ~190 V10 tests.

## What became stronger than the first V10 slice

- Benchmark 6/9 -> 9/9: adapter actual-received-vs-credited (SUBMIT_MEDIUM, local),
  oracle decimal normalization (SUBMIT_HIGH), and cross-chain supply conservation
  (SUBMIT_HIGH) now have dedicated fixtures, shape-driven detection, candidates, PoC
  skeletons, severities, and end-to-end tests.
- Severity engine: full label taxonomy, impact/cap/proof typing, an explainable
  numeric SeverityScore, and a PARK_INCOMPLETE gate.
- PoC skeletons: family-specific assertions for every benchmark family, an honest
  compile-readiness ladder, and richer headers.
- New semantic depth: named taint/dataflow detectors and state-machine
  contradictions, both wired into war-run as artifacts.
- Operational memory CLI and artifact schema hardening + quality gates.

## What is still partial / deferred

- AST mode: interface only. `ast_loader.detect_artifacts` records provenance, but
  `load_ast_map` returns None — the fallback parser is primary. Full solc/Foundry AST
  ingestion is deferred.
- Fallback parsing is regex + brace/paren matching (medium confidence): it can miss
  assembly-heavy, deeply-nested, or unusual Solidity; confidence is never "high".
- Data flow / taint is intraprocedural with a bounded internal-call closure;
  cross-contract flows are not fully tracked.
- A dedicated consent-binding package and a real-target replay/comparison mode were
  not added in this pass (the consent invariant + the `CALLDATA_NOT_IN_HASH_*` taint
  detector already cover the consent shape).

## How to interpret the severity labels

`SUBMIT_{CRITICAL,HIGH,MEDIUM}_CANDIDATE` worth proving + submitting at that level;
`SUBMIT_LOW_ONLY` / `VALID_BUT_LOW` / `VALID_BUT_LOW_LIKELIHOOD` valid but capped;
`NEEDS_{LOCAL_POC,FORK_PROOF,REAL_ASSET_PROOF,CAPTURE_PROOF}` prove the named thing
first; `PARK_{CONTEXT,THEORY,REACHABILITY,INCOMPLETE}` hold; `KILL_*`
(dust / self-grief / trusted-role / admin-only / out-of-scope / duplicate /
not-reachable / expected-design) do not pursue. A label is review guidance, never a
confirmed vulnerability and never a guaranteed payout.

## How memory works

The root-cause hash is semantic (invariant family + function role + attacker
category), so the same root cause on a different pool dedupes the same and a
genuinely different bug does not. `arkheionx memory` records and classifies prior
root causes; `export` redacts the private `notes` field.

## How fork plans work

When a candidate's real loss depends on deployed external state (AMM liquidity,
deployed feed decimals/staleness, bridge peer config), the fork lab emits a plan: the
chain (inferred from scope), the RPC env var name (never a URL), the contracts and
static calls to verify, a success/failure condition, and `do_not_broadcast`. It is a
plan only — Arkheionx does not fork, broadcast, or execute anything.

## Safety restrictions

Local/static; no RPC by default; no live-chain mutation; no broadcast; no signing
keys; no auto-submit; secrets redacted (URLs/keys/mnemonics scrubbed; env var names
only); fork is a plan only; no report is generated until an invariant is proven;
human review is always required. An artifact guard rejects overclaiming outcome
strings, and the NO_SECRET / NO_REPORT quality gates re-check before output.

## Benchmark

9/9 PASS on generic synthetic fixtures under `tests/fixtures/godeye/` (no
protocol/token names hardcoded). See [`../docs/V10_GODEYE_BENCHMARK.md`](../docs/V10_GODEYE_BENCHMARK.md).

## Risk of overclaiming

Detection is heuristic and medium-confidence; suspicious != confirmed; a severity
label is review guidance, not a payout; the oracle/cross-chain "High" labels come
from a locally-provable shape and the real magnitude still depends on the deployed
feed/token decimals and real bridged supply. Human review remains required.

# Hunter Mode — Limitations

Private, local-only. Read this before trusting any hunter output.

## What hunter mode does not do

```text
It does not automatically find vulnerabilities.
It does not confirm bugs.
It does not assign final severity.
It does not submit reports and has no auto-submit.
It does not mutate any chain and sends no transactions.
It does not sign anything and never reads private keys or seed phrases.
It does not exploit live systems.
It does not scan remote or unauthorized infrastructure.
It does not replace a human reviewer or an audit.
It does not guarantee a finding, a payout, or a severity.
```

## Heuristic boundaries

- Scope, dedup, freshness, source recovery, and deployment reality are heuristic, not
  exhaustive. A "no duplicate found" result is only as good as the corpus that was
  parsed; with DEDUP_BLIND it is unverified.
- The value-flow, state-machine, and call-graph engines use a lightweight Solidity scan
  (regex plus brace matching), not a compiler. They favor precision over recall: a real
  value path, state machine, or call edge can be missed, but a fabricated one should not
  appear. Missed surfaces are a real risk.
- Freshness can only be positive with concrete evidence. Without a baseline, a genuinely
  fresh surface will read as FRESHNESS_UNKNOWN and be parked — a deliberate
  false-negative trade to avoid false freshness boosts.
- A deployment mismatch is a priority signal, not a bug. The read-only checks cover code
  existence, EIP-1967 implementation/admin/beacon slots, a beacon implementation, and
  user-specified read-only calls; they do not enumerate full storage layouts or every
  role. The local code hash is a digest for comparison, not the on-chain keccak hash.
- Source recovery defaults to local material. Verified-source recovery is opt-in and
  goes through an injectable hook; ABI-only or missing source caps source-level leads.
- PDF known/audit material is parsed only if a lightweight library is already importable;
  otherwise it is marked UNPARSED_PDF_TEXT_EXTRACTION_UNAVAILABLE. There is no OCR.
- Lead scores are a research-priority ordering for time allocation. They are not a
  severity and not a validity claim.

## Where a human is still required

- Confirming the exact root behavior of each top lead by hand.
- Writing and running the PoC, and confirming the expected assertion passes before any
  report.
- Confirming the surface is in scope, non-duplicate, and attacker reachable.
- Deciding impact, severity, and whether to submit.

## Known failure modes

- A real bug can still be bounty-dead (out of scope, duplicate, trusted-role-only,
  public-test-covered). Hunter mode tries to surface that early, but the program's
  reviewer makes the final call.
- A scope collision (two versions, two products, a chain mismatch) parks everything on
  scope until the exact product/version/chain is confirmed.
- An unverified live deployment (addresses provided but no read-only `--rpc-url`) parks
  live-wiring-dependent leads on deployment.

# V10.1 Root Cause Fingerprints

## What Changed

V10.1 adds semantic root-cause fingerprinting for memory entries. A stored
entry now carries normalized text, canonical family, subfamily, lifecycle,
affected function, attacker capability, victim type, impact path, cap type,
proof status, program outcome, confidence, warnings, and a deterministic hash.

The hash is built from semantic fields, not raw prose. This keeps a generic
root cause stable across different local fixtures while still separating
different families and impact paths.

Legacy memory entries that only contain family, function role, and attacker
category remain usable for deduplication. They match by canonical family,
lifecycle, and attacker class.

## How To Run

```bash
arkheionx memory add \
  --target generic-rejected-rounding-benchmark \
  --program generic-policy \
  --root-cause "repayment asymmetric rounding between aggregate borrower repayment and per-tranche lender distribution" \
  --status rejected \
  --finding-id generic-duplicate \
  --severity informational \
  --do-not-resubmit
```

Expected shape:

```text
memory: added [findings] family=ROUNDING_REPAYMENT_RECONCILIATION hash=<non-empty> status=rejected do_not_resubmit=True
```

## Verdict Interpretation

- `family` is the canonical root-cause family.
- `subfamily` captures the more specific shape when the classifier has enough
  evidence.
- `fingerprint_hash` is deterministic over semantic fields.
- `UNKNOWN` is allowed, but it still receives a non-empty hash and a low
  confidence warning.

## Generic Examples

- `rejected_rounding_reconciliation_benchmark` classifies repayment rounding
  reconciliation.
- `lender_consent_route_buffer_benchmark` classifies route-buffer consent
  binding.
- `key_reuse_replay_carveout_benchmark` classifies replay that depends on key
  reuse or missing domain binding.
- `offchain_validation_carveout_benchmark` classifies validation omissions that
  belong outside on-chain exploit claims.

## Limitations

The classifier is deterministic and generic, but it is still text and pattern
based. It improves memory hygiene and deduplication; it does not prove bounty
eligibility or economic exploitability.

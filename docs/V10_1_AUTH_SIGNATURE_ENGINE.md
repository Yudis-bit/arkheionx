# V10.1 Authorization And Signature Engine

## What Changed

V10.1 adds a generic authorization analysis pass for signed operations,
threshold checks, replay domains, delegated execution, and factory
initialization. The engine activates when source contains signals such as
signer recovery, owner or threshold checks, nonce or sequence fields, execution
functions, delegated execution, factories, create2 flows, or initializer logic.

The engine emits:

- signed operation summaries
- hash binding matrices
- threshold analysis
- replay analysis
- delegated execution analysis
- factory initialization analysis
- auth-derived candidates

## How To Run

```bash
arkheionx war-run tests/fixtures/repos/generic_signature_binding_bug \
  --out artifacts/smoke-signature-binding-bug \
  --max-candidates 10 \
  --json
```

Relevant artifacts:

- `18-auth-signature-analysis.json`
- `18-auth-signature-analysis.md`
- `09-attack-graph.json`
- `17-bounty-reality.json`

## Interpretation

Hash binding fields are classified as:

- `BOUND`
- `UNBOUND_CRITICAL`
- `UNBOUND_VALUE_FIELD`
- `UNBOUND_CONTROL_FIELD`
- `UNBOUND_BUT_NON_VALUE`
- `OUT_OF_SCOPE_POLICY`
- `TRUSTED_ONLY`
- `UNKNOWN`

Replay analysis distinguishes same-domain nonce or sequence replay from
cross-domain replay that depends on reused signing authority. Threshold analysis
checks signer membership, duplicate rejection, sorted-order enforcement, zero
address handling, recovery failure handling, and malleability impact.

## Generic Fixtures

- `generic_multisig_safe`: bound operation fields and replay protection.
- `generic_multisig_missing_chainid`: replay-domain concern that depends on key
  reuse.
- `generic_multisig_missing_destination_in_hash`: value redirection candidate.
- `generic_multisig_duplicate_signer_bug`: threshold bypass candidate.
- `generic_multisig_delegatecall_unbound`: delegated execution control risk.
- `generic_factory_create2_safe`: owner and salt fields are bound.
- `generic_factory_init_takeover`: initialization takeover candidate.

## Limitations

The engine is intentionally generic and conservative. It uses source and parsed
fallback facts unless compiler artifacts are available. A promoted auth
candidate still needs local proof and bounty reality review before any
submission decision.

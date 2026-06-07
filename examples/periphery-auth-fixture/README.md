# Periphery + Authorization demo fixture

> Local/static demo only. Not production code, not a deployable recommendation,
> and not an exploit target. Review guidance only; human review required.

A small, generic protocol used to exercise the ArkheionX v4.1 research surface
engine. It is intentionally synthetic and is **not** modeled on any specific
real protocol.

## Contracts

- `OfferAuth` — an authorization surface: EIP-712 signed offers (`ecrecover`,
  `domainSeparator`, `block.chainid`, verifying contract, `nonce`, `deadline`),
  a Merkle allowlist gate (`merkleRoot`, leaf, proof, `MerkleProof.verify`), and
  an explicit `setAuthorization` / `isAuthorized` mapping behind `onlyOwner`.
- `LedgerCore` — core credit/debt accounting. Value enters via `supply()`,
  credit/debt mutate via `borrow()`/`repay()`, and value exits via `withdraw()`.
- `OfferBundler` — a periphery that loops over operations and routes them into
  `LedgerCore`. It is documented to **skip a failing item** (best effort,
  continue-on-error) using `try/catch`. A pre-call computation (`_normalize`)
  can revert before the skip handler is reached — a behavior-mismatch surface
  worth a local test.
- `MockToken` — a minimal ERC20-like token.

## What ArkheionX surfaces here

```bash
arkheionx review-map examples/periphery-auth-fixture
arkheionx agent-brief examples/periphery-auth-fixture
arkheionx hypothesis-log examples/periphery-auth-fixture
arkheionx case-study examples/periphery-auth-fixture
```

- **Authorization surfaces** — signature, domain, nonce/deadline, Merkle, and
  ownable/authorization signals on `OfferAuth`.
- **Periphery/core surfaces** — `OfferBundler.executeBundle` (loop + try/catch
  into `LedgerCore`) and `runOne` (direct-call equivalent).
- **Behavior-mismatch surfaces** — the documented skip-on-revert behavior vs the
  earlier `_normalize` revert.
- **Coverage weakness ranking** — `supply` is tested; `borrow`, `repay`,
  `withdraw`, the bundler, and the authorization paths are not.

Everything ArkheionX reports here is review guidance, not a confirmed finding.
Hypotheses are review prompts to validate locally; human review is required.

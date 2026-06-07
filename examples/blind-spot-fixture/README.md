# Blind Spot Intelligence demo fixture

A small, generic, multi-contract protocol used to exercise ArkheionX v5 **Blind
Spot Intelligence** end to end. It is synthetic and deliberately broad so the v5
engine has every detector category to work with in one repository.

Local/static demo only. Not production code, not a deployable recommendation,
and not an exploit target. It contains **no planted vulnerabilities** — it
exercises detection, it does not pretend to hide a real bug.

## What it contains

- `PriceOracle` — an oracle/price source with an admin setter (oracle surface).
- `CreditVault` — core share/credit/debt accounting: `deposit` (value entry),
  `withdraw` (value exit), `borrow`/`repay` (debt mutation against the oracle),
  `liquidate` (seizure boundary), and admin setters.
- `ClaimGate` — authorization surfaces: an EIP-712 signed claim with
  nonce/deadline replay protection and a Merkle allowlist gate.
- `BundleRouter` — a periphery router that loops over operations with a
  documented skip-on-revert handler and exposes a settlement callback.
- `MockToken` — a minimal ERC20-like token.

The bundled test (`test/CreditVault.t.sol`) covers **only** `deposit`. Everything
else — the value exit, the debt/oracle path, liquidation, the signature and
Merkle authorization surfaces, and the periphery batch — is intentionally left
untested so ArkheionX surfaces them as likely blind spots.

## Try it

```bash
arkheionx review-map      examples/blind-spot-fixture
arkheionx blind-spots     examples/blind-spot-fixture
arkheionx criticality-map examples/blind-spot-fixture
arkheionx counterfactuals examples/blind-spot-fixture
arkheionx research-pack   examples/blind-spot-fixture --out .arkheionx/research-pack
```

## Safety

Local/static only. No RPC, no live-chain calls, no private keys, no secrets, no
exploit automation. Blind spot candidates are not vulnerabilities and criticality
potential is not severity. Human review is required for every conclusion.

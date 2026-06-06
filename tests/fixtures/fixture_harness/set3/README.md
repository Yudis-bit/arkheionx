# Fixture Harness — Real Protocol Fixture Set 3

These are **local/static illustrative fixtures** used only to harden Arkheionx's
deterministic fixture and benchmark coverage (v3.9). They extend Sets 1 and 2 with
three additional protocol shapes that exercise the Protocol Intelligence Core
(function roles, value paths, assumptions, test gaps, graph, coverage).

Set 3 contains three tiny illustrative source files:

- `bridge_message/BridgeMessageShape.sol` — a bridge / message shape
  (send / receive / verify / processed-nonce tracking / verifier authority).
- `liquidation_engine/LiquidationEngineShape.sol` — a liquidation / borrow-repay
  shape (collateral / borrow / account liquidity / liquidatable / liquidate).
- `governance_timelock/GovernanceTimelockShape.sol` — a governance / timelock
  shape (propose / queue / execute / cancel / delay / roles).

## What these fixtures are not

- They are **not** audited contracts.
- They are **not** deployment-ready.
- They are **not** vulnerability reports and make no vulnerability claim.
- They are **not** attack proof-of-concepts and contain no attack instructions.
- They do **not** require any network, and they require no RPC, no fork URL, no
  private keys, no seed phrases, and no live chain.
- They do **not** require compilation or Foundry; they are read as static text.

## Why they exist

They exist only to give the deterministic fixture/benchmark harness realistic,
local/static structure to run over, so the core's IDs, counts, and outputs stay
stable and reviewable across releases. A fixture passing the harness never proves
the source is safe, and a fixture failing the harness never proves the source has
a vulnerability.

Manual review remains required, and `ready_for_submission` remains false for every
fixture record.

# Fixture Harness — Real Protocol Fixture Set 1

These are **local/static illustrative fixtures** used only to harden Arkheionx's
deterministic fixture and benchmark coverage (v3.9). They exercise the Protocol
Intelligence Core (function roles, value paths, assumptions, test gaps, graph,
coverage) across realistic protocol shapes.

Set 1 contains three tiny illustrative source files:

- `erc20_like/ERC20Like.sol` — a simple ERC20-like token shape.
- `lending_vault/LendingVault.sol` — a small lending vault shape.
- `staking_reward/StakingReward.sol` — a small staking / reward shape.

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

# Style Guide

Conventions for files, names, and prose.

## Repository naming

- **Brand name (public):** Arkheionx Vault.
- **Repo slug (URL):** `DeFi-Exploit-PoCs`. Kept for backwards compatibility
  with existing clones; the README and web app use the brand name.
- **Maintainer attribution:** Yudistira Putra (`arkheionx` /
  [@Yudis-bit](https://github.com/Yudis-bit)).

## Folder naming

- EVM PoCs: `EVM/test/<YYYY-MM>/` (date-only) for current entries; future
  entries should use `EVM/test/<YYYY-MM-ProtocolName>/` once renames are
  performed (see [internal/REBUILD_LOG.md](internal/REBUILD_LOG.md)).
- SVM PoCs: `SVM/tests/<YYYY-MM-ProtocolName>/`.
- MoveVM PoCs: `MoveVM/sources/<YYYY-MM-ProtocolName>/`.

## File naming

| Type | Pattern |
|---|---|
| EVM PoC | `Exploit_<YYYY-MM>.t.sol` (current) or `Exploit_<YYYY_MM>_<ProtocolPascalCase>.t.sol` (preferred for new) |
| SVM PoC test | `<protocol>.test.ts` or `<protocol>.rs` |
| MoveVM PoC | `<protocol>.move` |

## Solidity style

- License header: `// SPDX-License-Identifier: UNLICENSED` (PoCs are not
  redistributable beyond defensive use).
- Pragma: `pragma solidity >=0.8.0 <0.9.0;` for ported PoCs;
  `pragma solidity ^0.8.20;` for new files.
- Use Foundry's `Test` base directly; only inherit from `BaseTestWithBalanceLog`
  when balance logging is part of the PoC.
- Constants for attacker, victim, fork block, stolen amount.
- One PoC contract per file. One `testExploit` per contract.
- Hard assertions that prove the post-exploit state.

## Header comment

Use the structured header only when it improves clarity. Do not duplicate
metadata that already lives in `metadata/registry.json`. A short attribution
block referencing the post-mortem and the original PoC author is preferred
over a 20-line ASCII banner.

Example (preferred):

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity >=0.8.0 <0.9.0;

// Parity Multisig — initWallet hijack (2017-07).
// Post-mortem: https://www.openzeppelin.com/news/on-the-parity-wallet-multisig-hack-405a8c12e8f7
// Ported from: <upstream-url> (commit <sha>) — adapted for forge-std + pinned fork.
```

## Metadata style

- IDs are kebab-case, e.g. `2017-07-parity-multisig`.
- `summary`, `root_cause`, `impact` are one paragraph each, plain prose.
- `references` always include `title` and `url`.
- Don't pad with adjectives; state the failure mode and the consequence.

## Prose style

- Short paragraphs.
- Active voice.
- Concrete claims: "drained 153,037 ETH at block 4,043,799" beats
  "catastrophic loss of funds".
- No emoji in code, comments, README, or docs.
- No marketing words (see [BRAND.md](BRAND.md) for the avoid-list).
- Tables only when they improve clarity.
- Code blocks fenced with the correct language tag.

## Commit messages

- Conventional prefixes: `feat`, `fix`, `chore`, `docs`, `refactor`.
- Subject under 72 characters.
- Body explains *why*, not what the diff already shows.
- Reference issues by number.

## What to avoid

- Inflated headlines.
- Hardcoded "stats" the repo can't substantiate.
- "Hire me" / "audit request" CTAs without delivered audit history to back them.
- Auto-generated "educational insights" or rotating filler text.
- AI-flavored sentence structure: long opening clause, abstract noun phrase,
  no concrete claim.

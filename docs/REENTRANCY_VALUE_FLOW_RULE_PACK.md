# Reentrancy / Value Flow Rule Pack

This starter rule pack reviews local/static signs of external calls, claim
flows, withdrawals, callbacks, and value-transfer ordering assumptions.

It is defensive-only and does not generate exploit payloads.

## Signals

- `withdraw`, `redeem`, `claim`, `payout`, `refund`
- `transfer`, `transferFrom`, `safeTransfer`, `call{`, `.call(`
- `delegatecall`, callbacks, ERC721/ERC1155 receivers, ERC777 hooks
- `flashLoan`, `executeOperation`, `nonReentrant`, `ReentrancyGuard`

## Readiness Findings

- `ARK-REENT-001`: Value flow with external calls needs reentrancy review.
- `ARK-REENT-002`: Callback-capable token or receiver path detected.
- `ARK-REENT-003`: Claim/refund flow without state-transition tests.
- `ARK-REENT-004`: External call path without documented ordering assumptions.

## Suggested Defensive Tests

- local reentrant receiver mock,
- state update before external call,
- double-claim prevention,
- refund/claim mutual exclusion,
- failed external call behavior,
- callback token assumptions.

## Limitations

This rule pack does not build an exploit, execute a callback attack, or prove a
path is vulnerable. It prompts defensive review before formal audit.


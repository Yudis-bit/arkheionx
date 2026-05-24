# Case Study Sample

This is a compact example of the kind of paid case-study output Arkheionx Vault
can produce. It uses an existing public registry entry so the sample does not
claim new private research.

## BeautyChain BEC — Batch Transfer Overflow

**Incident date:** 2018-04  
**Category:** `arithmetic-precision-rounding`  
**Primary invariant:** token transfers should conserve supply.

## Vulnerable Assumption

The token assumed `count * value` would stay within the integer range used by
the contract. In pre-0.8 Solidity, arithmetic overflow could wrap silently, so
an attacker could choose values that made the total debit appear small while
crediting huge balances to receivers.

## Attacker-Controlled Variable

The attacker controlled:

- receiver count,
- transfer amount per receiver,
- the product used to compute the sender debit.

The exploit chose a transfer amount that wrapped the multiplication result.

## Broken Invariant

Should have held:

> Total credited balances cannot exceed the token's declared supply as a result
> of a transfer.

In the PoC, the assertion target is:

```solidity
assertGt(a1After + a2After, bec.totalSupply(), "supply invariant broken");
```

That assertion is useful because it fails if the overflow no longer produces
an impossible supply relationship.

## Assertion Families

Required by category:

- **F1 or F3** from `docs/ASSERTION_STANDARD.md`.

This case is best represented by F3: invariant break assertion. The PoC also
asserts exact attacker balance deltas for both receiver accounts.

## Auditor Questions

- Does the contract use Solidity before 0.8 without SafeMath?
- Are multiplication results checked before use?
- Does transfer logic conserve supply for all input sizes?
- Are batch operations tested at boundary values?
- Do tests include values near `type(uint256).max`?

## Patch Lesson

Arithmetic behavior is part of the security model. Any token accounting path
that uses attacker-chosen multiplication must either use checked arithmetic or
prove the product cannot overflow.

## Commercial Reuse

A full paid case study would add:

- transaction trace notes,
- fork verification transcript when available,
- patch diff or mitigation reference,
- a workshop exercise,
- a reviewer checklist for similar token code.

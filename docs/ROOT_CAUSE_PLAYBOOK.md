# Root Cause Playbook

How to write a credible root-cause section for a PoC entry. The goal is
that someone reading the entry six months from now can reconstruct the
failure without re-reading the post-mortem.

---

## What a root cause is, and isn't

A root cause is **the broken assumption**, not the broken line.

- "`call.value` was used instead of `transfer`" is a code-level symptom.
- "The protocol assumed callees could not modify protocol state mid-call"
  is a root cause.

If your root-cause sentence still reads as a fix instruction, keep
asking *why* until it reads as an assumption.

A root cause is **about the protocol's model**, not about the attacker.

- "The attacker took a flash loan" is a means.
- "The protocol's collateral price could be moved by any actor with
  sufficient temporary capital" is a root cause.

---

## The seven slots

For each PoC, fill these seven slots in `notes` or in the writeup:

### 1. Vulnerable assumption

The thing the protocol's code assumed about the world that turned out
to be false. Write this as a single sentence beginning with "Assumed
that...".

### 2. Violated invariant

A property the protocol *should* have maintained. Write as "Should
have held: ..." This is what your assertions test for in
[ASSERTION_STANDARD.md](ASSERTION_STANDARD.md).

### 3. Attacker-controlled variable

The specific value, parameter, balance, or order-of-operations the
attacker steered. Be concrete: "Curve 3pool spot price",
"`msg.value` reused across array iterations", "first-deposit share
count".

### 4. Missing validation

The check that, if present, would have prevented the exploit. If no
single check would suffice, say so — sometimes the design is wrong, not
the validation.

### 5. Economic dependency

What economic assumption the protocol's safety relied on. "Attacker
cannot have > $X capital", "spot price reflects fair price",
"governance token holders are long-term aligned".

### 6. Trust boundary failure

Where the protocol crossed a boundary it shouldn't have, or failed to
treat a boundary as one. "Treated user-supplied target as trusted",
"used a downstream pool's view as oracle without considering callback
context".

### 7. Patch lesson

The smallest general statement that, if applied to similar protocols,
would prevent the same incident. Not "use TWAP" — "any pricing input
that an attacker can move within the same transaction the protocol
reads it must not gate value flows".

---

## Worked example

**Incident.** Harvest Finance, October 2020 (`2020-10-harvest`).

1. **Vulnerable assumption.** Assumed that the Curve Y-pool spot
   price reflected the fair USD price of fUSDT / fUSDC at the moment
   of deposit and withdrawal.
2. **Violated invariant.** Should have held: a deposit immediately
   followed by a withdrawal returns approximately the deposited value
   (minus fees), regardless of intervening market activity.
3. **Attacker-controlled variable.** Curve Y-pool reserves at the
   moment Harvest sampled them.
4. **Missing validation.** No deviation check between the spot price
   and a manipulation-resistant reference; no minimum-output check on
   deposit / withdraw.
5. **Economic dependency.** Assumed attacker capital was bounded by
   real holdings — flash loans broke that.
6. **Trust boundary failure.** Treated the Curve pool as a trusted
   oracle while sharing it with the attacker as a trading venue.
7. **Patch lesson.** A pool that the attacker can move within the
   same transaction cannot serve as that transaction's price source.

---

## Anti-patterns

These produce root-cause sections that look fine but teach nothing:

- **The fix as the cause.** "The contract was missing a nonReentrant
  modifier" — *why* did its absence matter?
- **The bug class as the cause.** "It was a reentrancy" — what was the
  protocol's assumption that reentrancy violated?
- **The attacker's profit as the cause.** "The attacker drained 1278
  ETH" — that is impact, not cause.
- **One word.** "Oracle." Useless.
- **Restating the summary.** Root cause should add information beyond
  what `summary` already says.

---

## When you do not know

If the public record does not give enough to fill the seven slots,
say so explicitly:

```
notes: "Public post-mortem does not specify the exact ordering of state
updates. Root cause is inferred from PeckShield's transaction trace and
may need refinement once Harvest's internal report is published."
```

Honest gaps are better than confident guesses. A root cause section that
admits uncertainty is more credible than one that pretends to certainty
it doesn't have.

---

## Style

- Past tense for the incident, present tense for the lesson.
- Avoid passive voice when naming what failed: say "the contract did X",
  not "X was done".
- Name actors: protocol, attacker, victim contract, oracle source.
- Keep it under 200 words. If you can't, the root cause is more than one
  thing — split the entry or use `tags` to record the secondary cause.

# PoC Standard

This document defines what qualifies as a valid PoC inside Arkheionx Vault.
Anything that does not meet this bar should be marked `incomplete`,
`needs-verification`, or `template` rather than `historical`.

This standard exists so the archive can scale beyond a few dozen entries
without losing credibility.

---

## 1. Scope

A valid PoC is one of:

- **Historical reproduction** — a faithful local reproduction of a real,
  publicly disclosed exploit against a real protocol, against pinned chain
  state.
- **Educational template** — a clearly marked teaching artifact that
  demonstrates a class of vulnerability without targeting a real protocol.

A PoC is **not** any of:

- Live attack tooling.
- Generic scanners or exploit-discovery automation.
- Drain helpers or generalized value-extraction utilities.
- Anything aimed at production systems that are still vulnerable.

If an incident is still under embargo or affects an unpatched live system,
the entry stays in `embargoed` status with no `poc_path`.

## 2. Required components

Every PoC entry must have:

1. A pinned **fork block** at or just before the attack transaction (for
   incidents on a live chain).
2. A declared **chain alias** matching `EVM/foundry.toml`.
3. **Setup separated from exploit.** Setup builds the pre-attack state.
   The exploit body contains the actual sequence the attacker used.
4. A clear **root cause** statement describing the broken assumption.
5. A documented **attacker path** — the sequence of calls.
6. A statement of the **invariant broken**.
7. A **profit / success assertion** — what proves the attacker won.
8. A **victim loss / state-damage assertion** where applicable.
9. **References** — at least one external link (post-mortem, advisory,
   contest report, or original PoC author).
10. An honest **reproducibility status** (see
    [REPRODUCIBILITY_STANDARD.md](REPRODUCIBILITY_STANDARD.md)).

A PoC missing any of items 1–9 should not be marked `historical` /
`verified`. It belongs in `incomplete` or `needs-verification`.

## 3. Setup vs. exploit separation

The exploit logic must be readable on its own. A typical structure:

```solidity
function setUp() public {
    vm.createSelectFork("mainnet", FORK_BLOCK);
    // fund attacker, deploy helper, snapshot pre-state, etc.
}

function testExploit() public {
    uint256 before = _measureAttackerBalance();
    _exploit();
    _assertProfit(before);
    _assertVictimLoss();
    _assertInvariantBroken();
}
```

`_exploit()` should contain only what the attacker actually did. Anything
that exists purely to make the test runnable belongs in `setUp` or in
helpers, not inline.

## 4. Assertion bar

Logs alone are not proof. Each PoC must end with hard `assert*` calls.
See [ASSERTION_STANDARD.md](ASSERTION_STANDARD.md). Required assertion
families depend on the exploit category but always include at least:

- attacker profit (or successful unauthorized state transition), and
- victim loss / state damage (or invariant violation if no balance moves).

A PoC whose only proof is `console.log` is `incomplete`.

## 5. Forensic accuracy

- Block number and chain must match the on-chain incident.
- Attacker / victim addresses, where used, must match the real attack
  unless the file is clearly marked educational.
- USD loss figures must reflect the public post-mortem at the time of the
  incident. Mark estimates and rounding in `notes`.
- Patches and disclosure links must be the protocol's own communication
  where possible.

Do not invent block numbers, transaction hashes, addresses, or losses.
Mark `unknown` if a value is not known.

## 6. Safety boundary

A PoC must not:

- Hardcode RPC URLs, private keys, or any operational credential.
- Carry instructions to redeploy the exploit against a live network.
- Include scanner logic or target enumeration.
- Include "drain everything from address X" helpers.
- Include MEV or front-running tooling against live mempools.

If a contributor cannot reproduce an incident without crossing this
boundary, the incident stays in the backlog as a candidate, not as a PoC.

## 7. Status the PoC may use

See [METADATA_SCHEMA.md](METADATA_SCHEMA.md) for the canonical enum.
Practical guidance:

- `historical` — finished, references attached, assertions present, runs
  against the declared fork block (or is honestly marked
  `requires-archival-rpc`).
- `patched` — same as `historical`, but the protocol has shipped a fix
  worth linking under `patch_reference`.
- `educational` — synthetic teaching artifact; no live target.
- `template` — scaffolding only; do not include in PoC counts.
- `incomplete` — known gaps; must list them in `notes`.
- `needs-verification` — believed correct but not yet rerun against fork.
- `embargoed` — incident still under coordinated disclosure; no PoC path.

A PoC that compiles but has no meaningful assertions is `incomplete`,
not `historical`.

## 8. References

References are part of the PoC, not an afterthought. Prefer in this order:

1. The protocol's own post-mortem.
2. The original disclosing researcher's writeup.
3. A reputable security firm's analysis.
4. Block explorer links to the actual attack transaction.

Twitter / X threads are acceptable only when no longer-form writeup
exists; capture archive.org snapshots when feasible.

## 9. What promotes a PoC to `verified`

A PoC moves from `needs-verification` to `verified` only when:

- The fork test passes against the declared block.
- All required assertions pass.
- A verification report exists under `reports/verification/<id>.md`.
- The verification was performed by a maintainer or recorded contributor.

Self-reporting alone does not promote status. The artifact under
`reports/verification/` is the source of truth.

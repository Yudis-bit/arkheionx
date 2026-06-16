# Reachability Truth Engine

Arkheionx V9.1 separates Solidity visibility from attacker reachability. A function
being `public` or `external` does not prove that an unprivileged caller can execute it.

The hunter scans local Solidity with regex, balanced-brace matching, and line-preserving
comment removal. It does not use a compiler, network access, subprocesses, Slither, or
LLM calls.

## Evidence

The engine records the modifier, direct body check, helper call, AccessControl role,
allowlist, authority call, role getter, parser limitation, and initialization context
that produced each classification. Evidence and warnings are included in
`triage.json` and `06-value-flow-map.md`.

Unknown custom modifiers fail closed. If Arkheionx cannot prove that a custom modifier
is non-auth, it emits `UNKNOWN_MODIFIER_GATED_EXTERNAL`, parks the lead on
`PARK_REACHABILITY`, keeps `Submit: NO`, and does not produce a normal PoC plan.

Role-gated functions default to `KILL_TRUSTED_ROLE`. They can only become useful through
a separate attacker-reachable authorization-bypass hypothesis, such as an unguarded
initializer that assigns a role.

## Supported Gates

- Named owner, admin, oracle, operator, minter, burner, pauser, keeper, guardian,
  controller, manager, governance, authority, role, and allowlist modifiers.
- Direct `msg.sender` and `_msgSender()` comparisons.
- Auth helpers followed to a maximum depth of four, with cycle evidence.
- AccessControl `hasRole`, `_checkRole`, `onlyRole`, and nested role mappings.
- Public address role getters, including inline assembly `sload` getters.
- Initializer, reinitializer, and proxy execution context.
- Known state-only modifiers such as pause, deadline, validation, and reentrancy gates.

## Limits

The scanner is deliberately lightweight. Overloads, complex inheritance, generated
assembly, aliases, function pointers, unusual metaprogramming, and cross-file name
collisions may require manual review. Unknown evidence must remain unknown rather than
being promoted to unprivileged reachability.

# Foundry Invariant Skeletons

Arkheionx can generate local Foundry-style invariant skeletons from readiness findings.

These skeletons are starter scaffolds. They are not formal verification, not proof of safety, and not complete coverage.

## Generated Shape

Generated skeletons include:

- SPDX and Solidity pragma;
- an Arkheionx defensive notice;
- TODO placeholders for local project bindings;
- function names derived from `metadata/finding_test_plan_map.json`;
- empty assertion bodies for humans to complete.

Example function:

```solidity
function invariant_collateralDebtSolvencyHolds() public {
    // TODO: implement a defensive property for the mapped readiness finding.
}
```

## Template Categories

Reusable examples live in `templates/invariant_skeletons/`:

- `vault_invariants.sol`
- `oracle_invariants.sol`
- `access_control_invariants.sol`
- `reentrancy_value_flow_invariants.sol`
- `reward_invariants.sol`
- `amm_invariants.sol`
- `lending_invariants.sol`
- `hybrid_invariants.sol`

## Safe Usage

Use generated skeletons only with repositories you own or are authorized to test.

Do:

- bind local contracts and mocks;
- model allowed user actions;
- add project-specific assertions;
- document intentional trust assumptions;
- keep generated TODOs visible until resolved.

Do not:

- wire production endpoints;
- paste credentials;
- add deployed-system assumptions by default;
- treat generated functions as complete coverage.

## Common Follow-Up

After editing the skeleton, run the project test suite locally and re-run Arkheionx. If readiness improves, compare with the previous baseline.

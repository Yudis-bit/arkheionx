// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @notice Arkheionx defensive reward/staking invariant skeleton.
/// @dev Starter scaffold for authorized local repositories. Human review required.
contract ArkheionxRewardInvariants {
    // TODO: bind staking contract, reward token mock, and staker actors.

    function invariant_rewardConservation() public {
        // TODO: assert claimed plus remaining claimable rewards stay within funded rewards.
    }

    function invariant_rewardIndexMonotonic() public {
        // TODO: assert reward indexes move according to documented policy.
    }
}

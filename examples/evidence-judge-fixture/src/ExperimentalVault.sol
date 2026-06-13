// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {MockToken} from "./MockToken.sol";

/// @title ExperimentalVault
/// @notice A HEAD-only experiment that is NOT part of the deployed bug bounty
///         snapshot. It is marked out-of-scope in `scope.json`. The evidence
///         judge should flag any test targeting it as out-of-scope. No planted
///         vulnerability.
contract ExperimentalVault {
    MockToken public immutable asset;
    address public owner;
    uint256 public totalDeposited;

    constructor(MockToken _asset) {
        asset = _asset;
        owner = msg.sender;
    }

    /// @notice Experimental migration entry point (out-of-scope for the snapshot).
    function migrate(uint256 amount) external {
        require(asset.transferFrom(msg.sender, address(this), amount), "transfer");
        totalDeposited += amount;
    }
}

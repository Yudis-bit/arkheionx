// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title AdminConfig
/// @notice An owner-gated configuration contract used by the evidence-judge
///         fixture to exercise the authorization lane. No planted vulnerability.
contract AdminConfig {
    address public owner;
    uint256 public maxDepositCap;
    bool public paused;

    error NotOwner();

    modifier onlyOwner() {
        if (msg.sender != owner) revert NotOwner();
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    function setMaxDepositCap(uint256 newCap) external onlyOwner {
        maxDepositCap = newCap;
    }

    function setPaused(bool newPaused) external onlyOwner {
        paused = newPaused;
    }
}

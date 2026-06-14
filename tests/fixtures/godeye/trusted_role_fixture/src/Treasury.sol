// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// Generic synthetic fixture: a value-moving function gated by a trusted role.
// A candidate here must be killed (KILL_TRUSTED_ROLE), not surfaced as a bug.

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
}

contract Treasury {
    address public owner;
    IERC20 public token;

    modifier onlyOwner() {
        require(msg.sender == owner, "not owner");
        _;
    }

    constructor(address token_) {
        owner = msg.sender;
        token = IERC20(token_);
    }

    function sweep(address to, uint256 amount) external onlyOwner {
        // Moves value, but only the trusted owner can call it.
        token.transfer(to, amount);
    }
}

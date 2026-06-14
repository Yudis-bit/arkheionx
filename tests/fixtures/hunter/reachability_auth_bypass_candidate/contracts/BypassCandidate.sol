// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;


contract BypassCandidate {
    address public owner;
    uint256 public value;
    bool public initialized;

    modifier onlyOwner() {
        require(msg.sender == owner, "ONLY_OWNER");
        _;
    }

    function initialize(address newOwner) external {
        require(!initialized, "INITIALIZED");
        owner = newOwner;
        initialized = true;
    }

    function setValue(uint256 newValue) external onlyOwner {
        value = newValue;
    }
}

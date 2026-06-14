// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;


contract InitContext {
    bool public initialized;
    address public owner;

    modifier initializer() {
        require(!initialized, "INITIALIZED");
        initialized = true;
        _;
    }

    function initialize(address newOwner) external initializer {
        owner = newOwner;
    }
}

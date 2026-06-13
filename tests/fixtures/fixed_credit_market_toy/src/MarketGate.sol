// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// Synthetic access gate for Arkheionx fixture tests. Not real-protocol source. A gate
// restricts who may enter a market; it must not trap safe exits. Illustrative.

contract MarketGate {
    mapping(uint256 => mapping(address => bool)) public allowed;
    address public admin;

    constructor() {
        admin = msg.sender;
    }

    function setAllowed(uint256 market, address account, bool ok) external {
        require(msg.sender == admin, "admin");
        allowed[market][account] = ok;
    }

    function canEnter(address account, uint256 market) external view returns (bool) {
        return allowed[market][account];
    }
}

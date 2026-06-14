// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;


contract AccessControlled {
    mapping(bytes32 => mapping(address => bool)) internal roles;
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
    uint256 public minted;

    modifier onlyRole(bytes32 role) {
        require(roles[role][msg.sender], "NO_ROLE");
        _;
    }

    function mint(uint256 amount) external onlyRole(MINTER_ROLE) {
        minted += amount;
    }
}

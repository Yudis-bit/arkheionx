// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// @title ExampleComplianceList (synthetic)
/// @notice Generic blocklist / freeze registry pushed by an off-chain service.
contract ExampleComplianceList {
    address public admin;
    mapping(address => bool) public blocked;
    mapping(address => bool) public frozen;

    error NotAdmin();

    event BlockSet(address indexed who, bool value);
    event FreezeSet(address indexed who, bool value);

    modifier onlyAdmin() {
        if (msg.sender != admin) revert NotAdmin();
        _;
    }

    constructor(address admin_) {
        admin = admin_;
    }

    /// @notice Admin-gated blocklist update (trusted off-chain compliance feed).
    function setBlocked(address who, bool value) external onlyAdmin {
        blocked[who] = value;
        emit BlockSet(who, value);
    }

    function setFrozen(address who, bool value) external onlyAdmin {
        frozen[who] = value;
        emit FreezeSet(who, value);
    }

    function isBlocked(address who) external view returns (bool) {
        return blocked[who] || frozen[who];
    }
}

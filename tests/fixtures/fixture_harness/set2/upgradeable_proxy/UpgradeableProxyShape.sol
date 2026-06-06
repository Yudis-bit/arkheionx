// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// Local/static illustrative fixture for the Arkheionx fixture harness (v3.9).
// This is NOT an audited contract, NOT deployment-ready, and NOT a vulnerability
// report. It requires no network, no RPC, no fork, no private keys,
// no seed phrases, and no live chain. It exists only as static review-surface
// text for deterministic role / value-path / graph coverage. Manual review is
// required.

contract UpgradeableProxyShape {
    // Implementation and admin authority slots (plain state in this fixture; a
    // real proxy would use dedicated storage slots).
    address private _implementation;
    address private _admin;
    bool public paused;

    event Upgraded(address indexed newImplementation);
    event AdminChanged(address indexed previousAdmin, address indexed newAdmin);

    constructor(address initialImplementation) {
        _admin = msg.sender;
        _implementation = initialImplementation;
    }

    modifier onlyAdmin() {
        require(msg.sender == _admin, "not admin");
        _;
    }

    // Authority / target views (VIEW_PURE / ACCESS_CONTROL coverage).
    function implementation() external view returns (address) {
        return _implementation;
    }

    function admin() external view returns (address) {
        return _admin;
    }

    // Upgrade the implementation target (UPGRADE_AUTHORITY / ACCESS_CONTROL coverage).
    function upgradeTo(address newImplementation) external onlyAdmin {
        require(newImplementation != address(0), "zero implementation");
        _implementation = newImplementation;
        emit Upgraded(newImplementation);
    }

    // Rotate the admin authority (ADMIN_TRANSFER / ACCESS_CONTROL coverage).
    function changeAdmin(address newAdmin) external onlyAdmin {
        require(newAdmin != address(0), "zero admin");
        emit AdminChanged(_admin, newAdmin);
        _admin = newAdmin;
    }

    // Delegation placeholder (DELEGATE_PATH coverage). This local/static fixture
    // does NOT perform any low-level delegate forwarding; it only records the
    // call shape for review. A real proxy would forward execution to the current
    // implementation, which is out of scope for this illustrative fixture.
    function delegateToImplementation(bytes calldata data) external whenNotPaused returns (bool) {
        require(_implementation != address(0), "no implementation");
        // Placeholder only: no forwarding is performed in this fixture.
        data;
        return true;
    }

    // Emergency pause controls (PAUSE_EMERGENCY / EMERGENCY_PATH coverage).
    modifier whenNotPaused() {
        require(!paused, "paused");
        _;
    }

    function pause() external onlyAdmin {
        paused = true;
    }

    function unpause() external onlyAdmin {
        paused = false;
    }
}

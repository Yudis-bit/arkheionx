// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

interface IExampleExternalPool {
    function deposit(uint256 amount) external returns (uint256 received);
    function withdraw(uint256 amount) external returns (uint256 sent);
    function balanceOf(address who) external view returns (uint256);
}

/// @title ExampleAdapter (synthetic)
/// @notice Generic adapter to a trusted external lending-like pool. Demo only.
contract ExampleAdapter {
    IExampleExternalPool public pool;
    address public vault;
    uint256 public principal;

    error NotVault();
    error AmountMismatch(uint256 requested, uint256 actual);

    modifier onlyVault() {
        if (msg.sender != vault) revert NotVault();
        _;
    }

    constructor(address pool_, address vault_) {
        pool = IExampleExternalPool(pool_);
        vault = vault_;
    }

    function supply(uint256 amount) external onlyVault returns (uint256 received) {
        received = pool.deposit(amount);
        principal += received;
    }

    /// @notice Withdraw exactly `amount` from the external pool; reverts on a mismatch.
    function withdraw(uint256 amount) external onlyVault returns (uint256 sent) {
        sent = pool.withdraw(amount);
        if (sent != amount) revert AmountMismatch(amount, sent);
        principal -= sent;
    }

    function reportedBalance() external view returns (uint256) {
        return pool.balanceOf(address(this));
    }
}

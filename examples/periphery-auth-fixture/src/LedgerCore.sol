// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
}

/// @title LedgerCore
/// @notice Core credit/debt accounting for the local review-map demo fixture.
/// Value enters through supply(), credit and debt mutate through borrow()/repay(),
/// and value exits through withdraw(). Local/static demo only. Not production
/// code and not an exploit target.
contract LedgerCore {
    IERC20 public immutable asset;
    address public bundler;

    mapping(address => uint256) public credit;
    mapping(address => uint256) public debt;
    uint256 public totalCredit;

    modifier onlyBundlerOrSelf(address account) {
        require(msg.sender == account || msg.sender == bundler, "not authorized");
        _;
    }

    constructor(IERC20 asset_) {
        asset = asset_;
    }

    function setBundler(address bundler_) external {
        require(bundler == address(0), "set");
        bundler = bundler_;
    }

    /// @notice Value entry: pull asset in and credit the account.
    function supply(address account, uint256 amount) external onlyBundlerOrSelf(account) {
        require(amount > 0, "zero amount");
        credit[account] += amount;
        totalCredit += amount;
        require(asset.transferFrom(account, address(this), amount), "pull failed");
    }

    /// @notice Mutate debt up. A malformed amount above credit must be rejected.
    function borrow(address account, uint256 amount) external onlyBundlerOrSelf(account) {
        require(amount <= credit[account], "over credit");
        debt[account] += amount;
        require(asset.transfer(account, amount), "send failed");
    }

    /// @notice Mutate debt down.
    function repay(address account, uint256 amount) external onlyBundlerOrSelf(account) {
        debt[account] -= amount;
        require(asset.transferFrom(account, address(this), amount), "pull failed");
    }

    /// @notice Value exit: burn credit and push asset out.
    function withdraw(address account, uint256 amount) external onlyBundlerOrSelf(account) {
        require(debt[account] == 0, "open debt");
        credit[account] -= amount;
        totalCredit -= amount;
        require(asset.transfer(account, amount), "payout failed");
    }
}

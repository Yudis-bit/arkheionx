// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function balanceOf(address who) external view returns (uint256);
}

interface IYieldSource {
    // New external integration wired in after the last audit.
    function pull(uint256 amount) external returns (uint256);
}

/// @title FreshAdapter
/// @notice New external-integration adapter added after the latest audit.
///         Routes user value out through a freshly wired yield source. This
///         surface is intentionally not present in the prior audit baseline.
contract FreshAdapter {
    IERC20 public asset;
    IYieldSource public source;
    address public vault;

    constructor(IERC20 asset_, IYieldSource source_, address vault_) {
        asset = asset_;
        source = source_;
        vault = vault_;
    }

    /// @notice Pull from the new yield source and push value out to `to`.
    function withdrawTo(address to, uint256 amount) external returns (uint256) {
        uint256 got = source.pull(amount);
        require(asset.transfer(to, got), "transfer failed");
        return got;
    }
}

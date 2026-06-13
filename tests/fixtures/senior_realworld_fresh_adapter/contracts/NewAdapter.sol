// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
}

interface IYieldSource {
    function pull(uint256 amount) external returns (uint256);
}

/// @title NewAdapter
/// @notice New external-integration adapter wired in after the audit baseline.
///         Routes value out through a freshly added yield source.
contract NewAdapter {
    IERC20 public asset;
    IYieldSource public source;

    function withdrawTo(address to, uint256 amount) external returns (uint256 got) {
        got = source.pull(amount);
        require(asset.transfer(to, got), "transfer failed");
    }
}

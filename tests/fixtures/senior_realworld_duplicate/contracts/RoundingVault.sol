// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function balanceOf(address who) external view returns (uint256);
}

/// @title RoundingVault
/// @notice A withdraw path with a rounding behavior. A prior finding already
///         reported this exact rounding behavior on this exact function.
contract RoundingVault {
    IERC20 public asset;
    mapping(address => uint256) public shares;
    uint256 public totalShares;

    function withdraw(uint256 shareAmount) external returns (uint256 amount) {
        // Rounding in the share->asset conversion (the previously reported behavior).
        amount = (shareAmount * asset.balanceOf(address(this))) / totalShares;
        shares[msg.sender] -= shareAmount;
        totalShares -= shareAmount;
        require(asset.transfer(msg.sender, amount), "payout failed");
    }
}

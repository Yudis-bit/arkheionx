// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IERC20 {
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    function balanceOf(address who) external view returns (uint256);
}

/// @title ShareVault
/// @notice Deposit/share accounting with a first-depositor inflation edge case.
contract ShareVault {
    IERC20 public asset;
    mapping(address => uint256) public shares;
    uint256 public totalShares;

    function deposit(uint256 amount) external returns (uint256 minted) {
        require(asset.transferFrom(msg.sender, address(this), amount), "pull failed");
        uint256 supply = totalShares;
        minted = supply == 0 ? amount : (amount * supply) / asset.balanceOf(address(this));
        shares[msg.sender] += minted;
        totalShares += minted;
    }
}

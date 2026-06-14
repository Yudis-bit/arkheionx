// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// Generic synthetic fixture: ERC4626-like vault with attacker-inflatable
// totalAssets (balance-based) and no zero-share / dead-shares guard.

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    function balanceOf(address who) external view returns (uint256);
}

contract MiniVault {
    IERC20 public asset;
    uint256 public totalShares;
    mapping(address => uint256) public shares;

    function totalAssets() public view returns (uint256) {
        // Balance-based: a direct token donation inflates the share price.
        return asset.balanceOf(address(this));
    }

    function deposit(uint256 assets) external returns (uint256 mintedShares) {
        uint256 supply = totalShares;
        // No zero-share guard, no seed/dead shares, no offset.
        mintedShares = supply == 0 ? assets : (assets * supply) / totalAssets();
        asset.transferFrom(msg.sender, address(this), assets);
        totalShares += mintedShares;
        shares[msg.sender] += mintedShares;
    }

    function redeem(uint256 sharesToBurn) external returns (uint256 assetsOut) {
        assetsOut = (sharesToBurn * totalAssets()) / totalShares;
        totalShares -= sharesToBurn;
        shares[msg.sender] -= sharesToBurn;
        asset.transfer(msg.sender, assetsOut);
    }
}

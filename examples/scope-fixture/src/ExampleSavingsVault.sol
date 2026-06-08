// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {ExampleOracle} from "./ExampleOracle.sol";

interface IExampleAsset {
    function transfer(address to, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    function balanceOf(address who) external view returns (uint256);
}

/// @title ExampleSavingsVault (synthetic)
/// @notice ERC4626-style savings vault over a synthetic asset. Demo only.
contract ExampleSavingsVault {
    IExampleAsset public asset;
    ExampleOracle public oracle;

    uint256 public totalShares;
    mapping(address => uint256) public shares;

    event Deposit(address indexed caller, uint256 assets, uint256 sharesMinted);
    event Withdraw(address indexed caller, uint256 assets, uint256 sharesBurned);

    constructor(address asset_, address oracle_) {
        asset = IExampleAsset(asset_);
        oracle = ExampleOracle(oracle_);
    }

    function totalAssets() public view returns (uint256) {
        return asset.balanceOf(address(this));
    }

    /// @notice Convert assets to shares. Rounds in favor of the vault by design.
    function convertToShares(uint256 assets) public view returns (uint256) {
        uint256 supply = totalShares;
        if (supply == 0) return assets;
        return (assets * supply) / totalAssets();
    }

    function convertToAssets(uint256 shares_) public view returns (uint256) {
        uint256 supply = totalShares;
        if (supply == 0) return shares_;
        return (shares_ * totalAssets()) / supply;
    }

    function previewRedeem(uint256 shares_) external view returns (uint256) {
        return convertToAssets(shares_);
    }

    /// @notice Deposit assets, mint shares. Value entry.
    function deposit(uint256 assets) external returns (uint256 mintedShares) {
        mintedShares = convertToShares(assets);
        asset.transferFrom(msg.sender, address(this), assets);
        totalShares += mintedShares;
        shares[msg.sender] += mintedShares;
        emit Deposit(msg.sender, assets, mintedShares);
    }

    /// @notice Redeem shares for assets. Value exit; reads oracle valuation.
    function withdraw(uint256 shares_) external returns (uint256 assetsOut) {
        assetsOut = convertToAssets(shares_);
        uint256 price = oracle.price();
        require(price > 0, "stale price");
        shares[msg.sender] -= shares_;
        totalShares -= shares_;
        asset.transfer(msg.sender, assetsOut);
        emit Withdraw(msg.sender, assetsOut, shares_);
    }
}

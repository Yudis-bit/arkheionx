// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IERC20Like {
    function transfer(address to, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
}

interface IPriceSource {
    function getPrice() external view returns (uint256);
}

/// @title Strategy
/// @notice Toy yield strategy for the local review-map demo fixture. The Vault
/// routes deposited value here via invest(), and value returns to the Vault via
/// divest(). harvest() marks gains using the oracle price. Local/static demo
/// only. Not production code and not an exploit target.
contract Strategy {
    IERC20Like public immutable asset;
    IPriceSource public oracle;
    address public vault;
    uint256 public deployedAssets;
    uint256 public reportedGains;

    modifier onlyVault() {
        require(msg.sender == vault, "not vault");
        _;
    }

    constructor(IERC20Like asset_, IPriceSource oracle_, address vault_) {
        asset = asset_;
        oracle = oracle_;
        vault = vault_;
    }

    /// @notice Pull value in from the Vault to put it to work.
    function invest(uint256 amount) external onlyVault {
        deployedAssets += amount;
        require(asset.transferFrom(msg.sender, address(this), amount), "pull failed");
    }

    /// @notice Push value back out to the Vault.
    function divest(uint256 amount) external onlyVault {
        deployedAssets -= amount;
        require(asset.transfer(vault, amount), "return failed");
    }

    /// @notice Mark gains using the oracle price (accounting only).
    function harvest() external onlyVault {
        uint256 spot = oracle.getPrice();
        reportedGains = (deployedAssets * spot) / 1e18;
    }

    function reportAssets() external view returns (uint256) {
        return deployedAssets;
    }
}

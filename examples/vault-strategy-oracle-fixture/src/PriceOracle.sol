// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title PriceOracle
/// @notice Minimal admin-set price source for the local review-map demo
/// fixture. The price is a trust assumption that protects the Vault/Strategy
/// value flow: if it is stale or wrong, downstream accounting is wrong.
/// Local/static demo only. Not production code.
contract PriceOracle {
    address public owner;
    uint256 public price;
    uint256 public updatedAt;
    uint256 public maxStaleness = 1 hours;

    modifier onlyOwner() {
        require(msg.sender == owner, "not owner");
        _;
    }

    constructor(uint256 initialPrice) {
        owner = msg.sender;
        price = initialPrice;
        updatedAt = block.timestamp;
    }

    /// @notice Privileged: the owner sets the reported price.
    function setPrice(uint256 newPrice) external onlyOwner {
        require(newPrice > 0, "zero price");
        price = newPrice;
        updatedAt = block.timestamp;
    }

    /// @notice Read the current price, reverting if it is stale.
    function getPrice() external view returns (uint256) {
        require(block.timestamp - updatedAt <= maxStaleness, "stale price");
        return price;
    }
}

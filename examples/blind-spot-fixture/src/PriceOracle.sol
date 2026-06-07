// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title PriceOracle
/// @notice Generic price source for the local review-map demo fixture. Exposes a
/// price, an update timestamp, and an admin setter. A reviewer should confirm the
/// freshness assumption (that consumers reject a stale-but-positive price).
/// Local/static demo only. Not production code and not an exploit target.
contract PriceOracle {
    address public owner;
    uint256 public price;
    uint256 public updatedAt;
    uint8 public decimals = 18;

    constructor() {
        owner = msg.sender;
        price = 1e18;
        updatedAt = block.timestamp;
    }

    /// @notice Privileged: update the price. A reviewer should confirm the admin
    /// trust boundary and that consumers check freshness/scaling downstream.
    function setPrice(uint256 newPrice) external {
        require(msg.sender == owner, "not owner");
        price = newPrice;
        updatedAt = block.timestamp;
    }

    /// @notice Latest price. Consumers assume this is fresh and correctly scaled.
    function latestPrice() external view returns (uint256) {
        return price;
    }
}

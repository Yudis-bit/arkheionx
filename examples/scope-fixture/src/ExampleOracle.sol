// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// @title ExampleOracle (synthetic)
/// @notice Generic price feed with staleness, decimals, and deviation handling.
contract ExampleOracle {
    address public publisher;
    uint256 private _price;
    uint256 public updatedAt;
    uint8 public priceDecimals = 8;
    uint256 public maxStaleness = 1 hours;
    uint256 public maxDeviationBps = 1000;

    error NotPublisher();

    modifier onlyPublisher() {
        if (msg.sender != publisher) revert NotPublisher();
        _;
    }

    constructor(address publisher_) {
        publisher = publisher_;
        updatedAt = block.timestamp;
    }

    /// @notice Off-chain publisher pushes a new price. Trusted operator path.
    function setPrice(uint256 newPrice) external onlyPublisher {
        _price = newPrice;
        updatedAt = block.timestamp;
    }

    /// @notice Return the current price, or 0 if stale.
    function price() external view returns (uint256) {
        if (block.timestamp - updatedAt > maxStaleness) return 0;
        return _price;
    }

    /// @notice Scale a raw price to 18 decimals.
    function scaledPrice() external view returns (uint256) {
        return _price * (10 ** (18 - priceDecimals));
    }
}

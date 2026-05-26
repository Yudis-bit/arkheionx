// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface AggregatorV3Interface {
    function latestRoundData()
        external
        view
        returns (uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound);
}

contract RealOracleConsumer {
    AggregatorV3Interface public priceFeed;
    address public owner;

    modifier onlyOwner() {
        require(msg.sender == owner, "owner");
        _;
    }

    constructor(AggregatorV3Interface feed) {
        priceFeed = feed;
        owner = msg.sender;
    }

    function setOracle(AggregatorV3Interface newFeed) external onlyOwner {
        priceFeed = newFeed;
    }

    function readPrice() external view returns (uint256) {
        (, int256 answer,, uint256 updatedAt,) = priceFeed.latestRoundData();
        require(answer > 0, "answer");
        require(updatedAt > 0, "updatedAt");
        return uint256(answer);
    }
}


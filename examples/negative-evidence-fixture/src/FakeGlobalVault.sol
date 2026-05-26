// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface AggregatorV3Interface {
    function latestRoundData()
        external
        view
        returns (uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound);
}

contract FakeGlobalVault {
    AggregatorV3Interface public priceFeed;
    address public owner;
    mapping(address => uint256) public balanceOf;
    uint256 public totalAssets;
    uint256 public rewardPerTokenStored;
    uint256 public totalStaked;

    modifier onlyOwner() {
        require(msg.sender == owner, "not owner");
        _;
    }

    constructor(AggregatorV3Interface feed) {
        owner = msg.sender;
        priceFeed = feed;
    }

    function setOracle(AggregatorV3Interface feed) external onlyOwner {
        priceFeed = feed;
    }

    function deposit(uint256 assets) external {
        balanceOf[msg.sender] += assets;
        totalAssets += assets;
        totalStaked += assets;
    }

    function withdraw(uint256 assets) external {
        require(balanceOf[msg.sender] >= assets, "insufficient");
        balanceOf[msg.sender] -= assets;
        totalAssets -= assets;
        payable(msg.sender).call{value: 0}("");
    }

    function latestPrice() public view returns (int256) {
        (, int256 answer,,,) = priceFeed.latestRoundData();
        return answer;
    }

    function claimReward() external {
        rewardPerTokenStored += 1;
    }
}

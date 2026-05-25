// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface AggregatorV3Interface {
    function latestRoundData()
        external
        view
        returns (uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound);

    function decimals() external view returns (uint8);
}

interface IERC20Like {
    function transfer(address to, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
}

contract OracleRewardFixture {
    IERC20Like public immutable stakingToken;
    AggregatorV3Interface public priceFeed;
    address public owner;
    address public treasury;

    uint256 public totalStaked;
    uint256 public rewardPerTokenStored;
    uint256 public accumulator;
    uint256 public emissionRate;
    bool public paused;

    mapping(address => uint256) public balanceOf;
    mapping(address => uint256) public userRewardPerTokenPaid;
    mapping(address => uint256) public pendingReward;

    modifier onlyOwner() {
        require(msg.sender == owner, "owner");
        _;
    }

    constructor(IERC20Like token, AggregatorV3Interface feed) {
        stakingToken = token;
        priceFeed = feed;
        owner = msg.sender;
        treasury = msg.sender;
        emissionRate = 1e18;
    }

    function setOracle(AggregatorV3Interface newFeed) external onlyOwner {
        priceFeed = newFeed;
    }

    function setEmissionRate(uint256 newEmissionRate) external onlyOwner {
        emissionRate = newEmissionRate;
    }

    function setTreasury(address newTreasury) external onlyOwner {
        treasury = newTreasury;
    }

    function pause() external onlyOwner {
        paused = true;
    }

    function unpause() external onlyOwner {
        paused = false;
    }

    function getPrice() public view returns (uint256) {
        (, int256 answer,, uint256 updatedAt,) = priceFeed.latestRoundData();
        require(answer > 0, "price");
        require(updatedAt != 0, "updatedAt");
        return uint256(answer);
    }

    function rewardPerToken() public view returns (uint256) {
        if (totalStaked == 0) {
            return rewardPerTokenStored;
        }
        return rewardPerTokenStored + (emissionRate * getPrice()) / totalStaked;
    }

    function earned(address account) public view returns (uint256) {
        return pendingReward[account]
            + ((balanceOf[account] * (rewardPerToken() - userRewardPerTokenPaid[account])) / 1e18);
    }

    function stake(uint256 amount) external {
        require(!paused, "paused");
        _updateReward(msg.sender);
        totalStaked += amount;
        balanceOf[msg.sender] += amount;
        require(stakingToken.transferFrom(msg.sender, address(this), amount), "transferFrom");
    }

    function unstake(uint256 amount) external {
        _updateReward(msg.sender);
        balanceOf[msg.sender] -= amount;
        totalStaked -= amount;
        require(stakingToken.transfer(msg.sender, amount), "transfer");
    }

    function claimReward() external {
        _updateReward(msg.sender);
        uint256 reward = pendingReward[msg.sender];
        pendingReward[msg.sender] = 0;
        accumulator += reward;
        require(stakingToken.transfer(msg.sender, reward), "reward transfer");
    }

    function _updateReward(address account) internal {
        rewardPerTokenStored = rewardPerToken();
        pendingReward[account] = earned(account);
        userRewardPerTokenPaid[account] = rewardPerTokenStored;
    }
}


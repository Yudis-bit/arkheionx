// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

interface IExampleRewardToken {
    function transfer(address to, uint256 amount) external returns (bool);
}

/// @title ExampleRewardsDistributor (synthetic)
/// @notice Generic staking-reward distributor with linear vesting. Demo only.
contract ExampleRewardsDistributor {
    IExampleRewardToken public rewardToken;
    address public admin;

    uint256 public rewardRatePerSecond;
    uint256 public rewardPool;

    struct Stake {
        uint256 amount;
        uint256 lastClaim;
        uint256 claimed;
    }

    mapping(address => Stake) public stakes;

    event Claimed(address indexed who, uint256 amount);

    constructor(address rewardToken_, address admin_, uint256 rate_) {
        rewardToken = IExampleRewardToken(rewardToken_);
        admin = admin_;
        rewardRatePerSecond = rate_;
    }

    function fund(uint256 amount) external {
        rewardPool += amount;
    }

    function stake(uint256 amount) external {
        Stake storage s = stakes[msg.sender];
        s.amount += amount;
        if (s.lastClaim == 0) s.lastClaim = block.timestamp;
    }

    /// @notice Accrued reward since last claim, linear in time and stake.
    function accrued(address who) public view returns (uint256) {
        Stake memory s = stakes[who];
        if (s.amount == 0) return 0;
        uint256 elapsed = block.timestamp - s.lastClaim;
        return elapsed * rewardRatePerSecond * s.amount / 1e18;
    }

    /// @notice Claim accrued rewards. Value exit from the reward pool.
    function claim() external returns (uint256 amount) {
        amount = accrued(msg.sender);
        Stake storage s = stakes[msg.sender];
        s.lastClaim = block.timestamp;
        s.claimed += amount;
        rewardPool -= amount;
        rewardToken.transfer(msg.sender, amount);
        emit Claimed(msg.sender, amount);
    }
}

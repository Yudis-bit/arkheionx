// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// Local/static illustrative fixture for the Arkheionx fixture harness (v3.9).
// This is NOT an audited contract, NOT deployment-ready, and NOT a vulnerability
// report. It requires no network, no RPC, no fork, no private keys,
// no seed phrases, and no live chain. It exists only as static review-surface
// text for deterministic role / value-path / graph coverage. Manual review is
// required.

contract StakingReward {
    address public owner;
    uint256 public rewardRate;
    bool public paused;

    mapping(address => uint256) private _staked;
    mapping(address => uint256) private _rewards;

    constructor() {
        owner = msg.sender;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "not owner");
        _;
    }

    modifier whenNotPaused() {
        require(!paused, "paused");
        _;
    }

    // Value enters / leaves staking (INFLOW / OUTFLOW coverage).
    function stake(uint256 amount) external whenNotPaused {
        _staked[msg.sender] += amount;
    }

    function withdraw(uint256 amount) external {
        _staked[msg.sender] -= amount;
    }

    // Reward accounting + claim (CLAIM_REWARD / REWARD_PATH coverage).
    function claimReward() external {
        uint256 reward = _rewards[msg.sender];
        _rewards[msg.sender] = 0;
        // Reward transfer-out is represented as accounting only in this fixture.
        _staked[msg.sender] += 0;
        reward;
    }

    function earned(address account) external view returns (uint256) {
        return _rewards[account] + (_staked[account] * rewardRate) / 10000;
    }

    // Admin reward rate under access control (ADMIN_PARAM / ACCESS_CONTROL).
    function notifyRewardAmount(uint256 newRewardRate) external onlyOwner {
        rewardRate = newRewardRate;
    }

    // Emergency pause controls (PAUSE_EMERGENCY / EMERGENCY_PATH coverage).
    function pause() external onlyOwner {
        paused = true;
    }

    function unpause() external onlyOwner {
        paused = false;
    }
}

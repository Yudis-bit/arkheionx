// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    function approve(address spender, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
}

interface IStrategy {
    function invest(uint256 amount) external;
    function divest(uint256 amount) external;
    function harvest() external;
    function reportAssets() external view returns (uint256);
}

interface IOracle {
    function getPrice() external view returns (uint256);
}

/// @title Vault
/// @notice Toy share vault for the local review-map demo fixture. Value enters
/// through deposit(), is routed to a Strategy via rebalance(), and exits through
/// withdraw()/emergencyWithdraw(). The PriceOracle is the trust assumption that
/// guards accounting. Local/static demo only. Not production code, not a
/// deployable recommendation, and not an exploit target.
contract Vault {
    IERC20 public immutable asset;
    IStrategy public strategy;
    IOracle public oracle;
    address public owner;

    uint256 public totalShares;
    mapping(address => uint256) public sharesOf;

    modifier onlyOwner() {
        require(msg.sender == owner, "not owner");
        _;
    }

    constructor(IERC20 asset_, IOracle oracle_) {
        asset = asset_;
        oracle = oracle_;
        owner = msg.sender;
    }

    // --- Value entry ---

    /// @notice Pull asset value in and mint proportional shares.
    function deposit(uint256 amount) external returns (uint256 shares) {
        require(amount > 0, "zero amount");
        uint256 balance = asset.balanceOf(address(this));
        shares = totalShares == 0 || balance == 0 ? amount : (amount * totalShares) / balance;
        totalShares += shares;
        sharesOf[msg.sender] += shares;
        require(asset.transferFrom(msg.sender, address(this), amount), "pull failed");
    }

    // --- Value exit ---

    /// @notice Burn shares and push asset value out to the caller.
    function withdraw(uint256 shares) external returns (uint256 amount) {
        uint256 balance = asset.balanceOf(address(this));
        amount = (shares * balance) / totalShares;
        sharesOf[msg.sender] -= shares;
        totalShares -= shares;
        require(asset.transfer(msg.sender, amount), "payout failed");
    }

    /// @notice Privileged escape hatch that pushes all idle value to the owner.
    function emergencyWithdraw() external onlyOwner {
        uint256 balance = asset.balanceOf(address(this));
        require(asset.transfer(owner, balance), "rescue failed");
    }

    // --- Value movement ---

    /// @notice Route idle value into the strategy or pull it back.
    function rebalance(uint256 investAmount, uint256 divestAmount) external onlyOwner {
        if (divestAmount > 0) {
            strategy.divest(divestAmount);
        }
        if (investAmount > 0) {
            asset.approve(address(strategy), investAmount);
            strategy.invest(investAmount);
        }
    }

    /// @notice Ask the strategy to mark gains (oracle-dependent accounting).
    function harvest() external onlyOwner {
        strategy.harvest();
    }

    // --- Admin / trust assumptions ---

    /// @notice Privileged: repoint the strategy that holds deployed value.
    function setStrategy(IStrategy newStrategy) external onlyOwner {
        strategy = newStrategy;
    }

    /// @notice Privileged: repoint the price oracle that guards accounting.
    function setOracle(IOracle newOracle) external onlyOwner {
        oracle = newOracle;
    }

    // --- Views ---

    function totalAssets() external view returns (uint256) {
        return asset.balanceOf(address(this)) + strategy.reportAssets();
    }
}

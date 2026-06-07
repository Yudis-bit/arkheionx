// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {PriceOracle} from "./PriceOracle.sol";

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
}

/// @title CreditVault
/// @notice Core share/credit/debt accounting for the local review-map demo
/// fixture. Value enters through deposit(), shares mint proportionally, debt
/// mutates through borrow()/repay() against an oracle price, value exits through
/// withdraw(), and liquidate() seizes collateral past a health boundary.
/// Local/static demo only. Not production code and not an exploit target.
contract CreditVault {
    IERC20 public immutable asset;
    PriceOracle public oracle;
    address public owner;
    address public router;

    mapping(address => uint256) public shares;
    mapping(address => uint256) public debt;
    uint256 public totalShares;
    uint256 public totalAssets;

    modifier onlyOwner() {
        require(msg.sender == owner, "not owner");
        _;
    }

    constructor(IERC20 asset_, PriceOracle oracle_) {
        asset = asset_;
        oracle = oracle_;
        owner = msg.sender;
    }

    /// @notice Value entry: pull asset in and mint proportional shares. Shares
    /// assume proportional accounting across rounding and donation scenarios.
    function deposit(uint256 amount) external returns (uint256 minted) {
        require(amount > 0, "zero amount");
        minted = totalShares == 0 ? amount : (amount * totalShares) / totalAssets;
        shares[msg.sender] += minted;
        totalShares += minted;
        totalAssets += amount;
        require(asset.transferFrom(msg.sender, address(this), amount), "pull failed");
    }

    /// @notice Value exit: burn shares and push asset out. Reviewer should confirm
    /// share<->asset accounting holds for first, last, and dust amounts.
    function withdraw(uint256 shareAmount) external returns (uint256 amount) {
        amount = (shareAmount * totalAssets) / totalShares;
        shares[msg.sender] -= shareAmount;
        totalShares -= shareAmount;
        totalAssets -= amount;
        require(asset.transfer(msg.sender, amount), "payout failed");
    }

    /// @notice Mutate debt up against the oracle price. Borrow must stay within
    /// the collateral value implied by the (assumed fresh) oracle price.
    function borrow(address account, uint256 amount) external {
        require(msg.sender == account || msg.sender == router, "not authorized");
        uint256 price = oracle.latestPrice();
        uint256 collateralValue = (shares[account] * price) / 1e18;
        require(debt[account] + amount <= collateralValue, "over collateral");
        debt[account] += amount;
        require(asset.transfer(account, amount), "send failed");
    }

    /// @notice Mutate debt down.
    function repay(address account, uint256 amount) external {
        debt[account] -= amount;
        require(asset.transferFrom(msg.sender, address(this), amount), "pull failed");
    }

    /// @notice Liquidation/seizure: if a position is past the health boundary,
    /// seize its shares. Reviewer should confirm the boundary cannot seize a
    /// healthy position or block a needed liquidation (off-by-one / rounding).
    function liquidate(address account) external {
        uint256 price = oracle.latestPrice();
        uint256 collateralValue = (shares[account] * price) / 1e18;
        require(debt[account] > collateralValue, "healthy");
        uint256 seized = shares[account];
        shares[account] = 0;
        shares[msg.sender] += seized;
    }

    /// @notice Privileged: rotate the oracle. Admin trust boundary.
    function setOracle(PriceOracle oracle_) external onlyOwner {
        oracle = oracle_;
    }

    /// @notice Privileged: set the periphery router allowed to act on accounts.
    function setRouter(address router_) external onlyOwner {
        router = router_;
    }
}

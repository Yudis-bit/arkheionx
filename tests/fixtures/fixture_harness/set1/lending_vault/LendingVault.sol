// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// Local/static illustrative fixture for the Arkheionx fixture harness (v3.9).
// This is NOT an audited contract, NOT deployment-ready, and NOT a vulnerability
// report. It requires no network, no RPC, no fork, no private keys,
// no seed phrases, and no live chain. It exists only as static review-surface
// text for deterministic role / value-path / graph coverage. Manual review is
// required.

// Local placeholder oracle interface (no external/live source).
interface IPriceOracle {
    function getPrice(address asset) external view returns (uint256);
}

contract LendingVault {
    address public owner;
    IPriceOracle public priceOracle;
    uint256 public collateralFactorBps;

    mapping(address => uint256) private _collateral;
    mapping(address => uint256) private _debt;

    constructor(IPriceOracle oracle) {
        owner = msg.sender;
        priceOracle = oracle;
        collateralFactorBps = 7500;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "not owner");
        _;
    }

    // Value enters / leaves the vault (INFLOW / OUTFLOW coverage).
    function deposit(uint256 amount) external {
        _collateral[msg.sender] += amount;
    }

    function withdraw(uint256 amount) external {
        _collateral[msg.sender] -= amount;
    }

    // Borrow / repay (BORROW_REPAY + accounting coverage).
    function borrow(uint256 amount) external {
        _debt[msg.sender] += amount;
    }

    function repay(uint256 amount) external {
        _debt[msg.sender] -= amount;
    }

    // Liquidation path (LIQUIDATION coverage).
    function liquidate(address account, uint256 repayAmount) external {
        _debt[account] -= repayAmount;
        _collateral[account] -= repayAmount;
    }

    // Oracle-dependent view (ORACLE_CONSUMER / ORACLE_DEPENDENT_PATH coverage).
    function getAccountLiquidity(address account) external view returns (uint256) {
        uint256 price = priceOracle.getPrice(account);
        return (_collateral[account] * price * collateralFactorBps) / 10000;
    }

    // Admin parameter under access control (ADMIN_PARAM / ACCESS_CONTROL coverage).
    function setCollateralFactor(uint256 newFactorBps) external onlyOwner {
        collateralFactorBps = newFactorBps;
    }
}

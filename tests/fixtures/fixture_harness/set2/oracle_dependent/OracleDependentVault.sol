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

contract OracleDependentVault {
    address public owner;
    IPriceOracle public oracle;
    uint256 public riskParameterBps;

    mapping(address => uint256) private _collateral;
    mapping(address => uint256) private _debt;

    constructor(IPriceOracle initialOracle) {
        owner = msg.sender;
        oracle = initialOracle;
        riskParameterBps = 8000;
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

    // Oracle-dependent health view (ORACLE_CONSUMER / ORACLE_DEPENDENT_PATH coverage).
    function getHealthFactor(address account) external view returns (uint256) {
        uint256 debt = _debt[account];
        if (debt == 0) {
            return type(uint256).max;
        }
        uint256 price = oracle.getPrice(account);
        uint256 weightedCollateral = (_collateral[account] * price * riskParameterBps) / 10000;
        return weightedCollateral / debt;
    }

    // Liquidation path (LIQUIDATION coverage).
    function liquidate(address account, uint256 repayAmount) external {
        _debt[account] -= repayAmount;
        _collateral[account] -= repayAmount;
    }

    // Oracle source under access control (ORACLE_SETTER / ACCESS_CONTROL coverage).
    function updateOracle(IPriceOracle newOracle) external onlyOwner {
        oracle = newOracle;
    }

    // Risk parameter under access control (ADMIN_PARAM / ACCESS_CONTROL coverage).
    function setRiskParameter(uint256 newRiskParameterBps) external onlyOwner {
        require(newRiskParameterBps <= 10000, "risk too high");
        riskParameterBps = newRiskParameterBps;
    }
}

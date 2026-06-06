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

contract LiquidationEngineShape {
    address public owner;
    IPriceOracle public oracle;
    uint256 public liquidationBonusBps;
    uint256 public closeFactorBps;

    mapping(address => uint256) private _collateral;
    mapping(address => uint256) private _debt;

    constructor(IPriceOracle initialOracle) {
        owner = msg.sender;
        oracle = initialOracle;
        liquidationBonusBps = 500;  // 5% illustrative bonus
        closeFactorBps = 5000;      // 50% illustrative close factor
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "not owner");
        _;
    }

    // Collateral in / out (INFLOW / OUTFLOW coverage).
    function depositCollateral(uint256 amount) external {
        _collateral[msg.sender] += amount;
    }

    function withdrawCollateral(uint256 amount) external {
        _collateral[msg.sender] -= amount;
    }

    // Borrow / repay (BORROW_REPAY + accounting coverage).
    function borrow(uint256 amount) external {
        _debt[msg.sender] += amount;
    }

    function repay(uint256 amount) external {
        _debt[msg.sender] -= amount;
    }

    // Oracle-weighted account liquidity (ORACLE_CONSUMER coverage).
    function getAccountLiquidity(address account) public view returns (uint256 collateralValue, uint256 debtValue) {
        uint256 price = oracle.getPrice(account);
        collateralValue = _collateral[account] * price;
        debtValue = _debt[account] * price;
    }

    // Liquidation eligibility view (LIQUIDATION coverage).
    function isLiquidatable(address account) public view returns (bool) {
        (uint256 collateralValue, uint256 debtValue) = getAccountLiquidity(account);
        return debtValue > collateralValue;
    }

    // Liquidation path with close factor and bonus (LIQUIDATION coverage).
    function liquidate(address account, uint256 repayAmount) external {
        require(isLiquidatable(account), "not liquidatable");
        uint256 maxRepay = (_debt[account] * closeFactorBps) / 10000;
        require(repayAmount <= maxRepay, "repay exceeds close factor");
        uint256 seized = repayAmount + ((repayAmount * liquidationBonusBps) / 10000);
        _debt[account] -= repayAmount;
        _collateral[account] -= seized;
    }

    // Admin parameters under access control (ADMIN_PARAM / ACCESS_CONTROL coverage).
    function setLiquidationBonus(uint256 newBonusBps) external onlyOwner {
        require(newBonusBps <= 5000, "bonus too high");
        liquidationBonusBps = newBonusBps;
    }

    function setCloseFactor(uint256 newCloseFactorBps) external onlyOwner {
        require(newCloseFactorBps <= 10000, "close factor too high");
        closeFactorBps = newCloseFactorBps;
    }
}

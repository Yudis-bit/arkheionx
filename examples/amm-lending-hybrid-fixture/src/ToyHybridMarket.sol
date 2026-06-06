// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract ToyReserveOracle {
    uint256 public reserve0 = 1_000 ether;
    uint256 public reserve1 = 2_000 ether;
    uint256 public kLast = reserve0 * reserve1;

    function getReserves() external view returns (uint256, uint256) {
        return (reserve0, reserve1);
    }

    function quote(uint256 amountIn) external view returns (uint256) {
        return amountIn * reserve1 / reserve0;
    }

    function swap(uint256 amountIn) external returns (uint256 amountOut) {
        amountOut = amountIn * reserve1 / (reserve0 + amountIn);
        reserve0 += amountIn;
        reserve1 -= amountOut;
        kLast = reserve0 * reserve1;
    }
}

contract ToyHybridMarket {
    ToyReserveOracle public pool;
    mapping(address => uint256) public collateral;
    mapping(address => uint256) public debt;
    uint256 public totalBorrows;
    uint256 public cash = 1_000 ether;
    uint256 public liquidationThreshold = 80e16;

    constructor(ToyReserveOracle pool_) {
        pool = pool_;
    }

    function depositCollateral() external payable {
        collateral[msg.sender] += msg.value;
    }

    function collateralValue(address user) public view returns (uint256) {
        uint256 price = pool.quote(1 ether);
        return collateral[user] * price / 1e18;
    }

    function healthFactor(address user) public view returns (uint256) {
        if (debt[user] == 0) {
            return type(uint256).max;
        }
        return collateralValue(user) * liquidationThreshold / debt[user];
    }

    function borrow(uint256 amount) external {
        require(cash >= amount, "CASH");
        require(healthFactor(msg.sender) > 1e18, "HEALTH");
        debt[msg.sender] += amount;
        totalBorrows += amount;
        cash -= amount;
    }

    function repay(uint256 amount) external {
        uint256 paid = amount > debt[msg.sender] ? debt[msg.sender] : amount;
        debt[msg.sender] -= paid;
        totalBorrows -= paid;
        cash += paid;
    }

    function liquidate(address borrower, uint256 amount) external {
        require(healthFactor(borrower) < 1e18, "HEALTHY");
        uint256 paid = amount > debt[borrower] ? debt[borrower] : amount;
        debt[borrower] -= paid;
        totalBorrows -= paid;
        cash += paid;
    }
}


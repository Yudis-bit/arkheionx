// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IPriceFeed {
    function latestRoundData() external view returns (uint80, int256, uint256, uint256, uint80);
}

contract ToyLendingMarket {
    IPriceFeed public priceFeed;
    address public owner;
    address public guardian;

    mapping(address => uint256) public collateral;
    mapping(address => uint256) public debt;

    uint256 public cash;
    uint256 public totalBorrows;
    uint256 public totalReserves;
    uint256 public borrowIndex = 1e18;
    uint256 public interestIndex = 1e18;
    uint256 public liquidationThreshold = 80e16;
    uint256 public collateralFactor = 70e16;
    uint256 public closeFactor = 50e16;
    uint256 public liquidationBonus = 108e16;
    bool public paused;

    constructor(IPriceFeed feed) {
        priceFeed = feed;
        owner = msg.sender;
        guardian = msg.sender;
        cash = 1_000 ether;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "OWNER");
        _;
    }

    function setGuardian(address nextGuardian) external onlyOwner {
        guardian = nextGuardian;
    }

    function pause(bool value) external {
        require(msg.sender == guardian, "GUARDIAN");
        paused = value;
    }

    function depositCollateral() external payable {
        collateral[msg.sender] += msg.value;
    }

    function getPrice() public view returns (uint256) {
        (, int256 answer,,,) = priceFeed.latestRoundData();
        require(answer > 0, "PRICE");
        return uint256(answer);
    }

    function collateralValue(address user) public view returns (uint256) {
        return collateral[user] * getPrice() / 1e18;
    }

    function healthFactor(address user) public view returns (uint256) {
        if (debt[user] == 0) {
            return type(uint256).max;
        }
        return collateralValue(user) * liquidationThreshold / debt[user];
    }

    function borrow(uint256 amount) external {
        require(!paused, "PAUSED");
        uint256 projectedDebt = debt[msg.sender] + amount;
        require(collateralValue(msg.sender) * collateralFactor / 1e18 >= projectedDebt, "LTV");
        require(cash >= amount, "CASH");
        debt[msg.sender] = projectedDebt;
        totalBorrows += amount;
        cash -= amount;
    }

    function repay(uint256 amount) external {
        uint256 paid = amount > debt[msg.sender] ? debt[msg.sender] : amount;
        debt[msg.sender] -= paid;
        totalBorrows -= paid;
        cash += paid;
    }

    function accrueInterest(uint256 ratePerSecond, uint256 elapsed) external {
        uint256 interest = totalBorrows * ratePerSecond * elapsed / 1e18;
        totalBorrows += interest;
        totalReserves += interest / 10;
        borrowIndex += borrowIndex * ratePerSecond * elapsed / 1e18;
        interestIndex = borrowIndex;
    }

    function liquidate(address borrower, uint256 repayAmount) external {
        require(healthFactor(borrower) < 1e18, "HEALTHY");
        uint256 closeAmount = debt[borrower] * closeFactor / 1e18;
        uint256 actualRepay = repayAmount < closeAmount ? repayAmount : closeAmount;
        uint256 seized = actualRepay * liquidationBonus / getPrice();
        debt[borrower] -= actualRepay;
        totalBorrows -= actualRepay;
        collateral[borrower] -= seized;
        collateral[msg.sender] += seized;
        cash += actualRepay;
    }
}


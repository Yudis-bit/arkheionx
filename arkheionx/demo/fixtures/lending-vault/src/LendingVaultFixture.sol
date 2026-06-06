// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IERC20Like {
    function transfer(address to, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
}

/// @dev Toy lending/vault fixture for Arkheionx demos. Not a production lending
/// market, not audited, and not a real deployment. Local/static demonstration
/// only; the price is an owner-set local value, not an external oracle.
contract LendingVaultFixture {
    IERC20Like public immutable collateralToken;
    IERC20Like public immutable debtToken;
    address public owner;

    uint256 public price;
    uint256 public collateralFactorBps;

    mapping(address => uint256) public collateralOf;
    mapping(address => uint256) public debtOf;

    modifier onlyOwner() {
        require(msg.sender == owner, "owner");
        _;
    }

    constructor(IERC20Like collateral, IERC20Like debt) {
        collateralToken = collateral;
        debtToken = debt;
        owner = msg.sender;
        price = 1e18;
        collateralFactorBps = 7500;
    }

    function setPrice(uint256 newPrice) external onlyOwner {
        require(newPrice > 0, "price");
        price = newPrice;
    }

    function depositCollateral(uint256 amount) external {
        require(collateralToken.transferFrom(msg.sender, address(this), amount), "deposit");
        collateralOf[msg.sender] += amount;
    }

    function withdrawCollateral(uint256 amount) external {
        require(collateralOf[msg.sender] >= amount, "balance");
        collateralOf[msg.sender] -= amount;
        require(_isHealthy(msg.sender), "unhealthy");
        require(collateralToken.transfer(msg.sender, amount), "withdraw");
    }

    function borrow(uint256 amount) external {
        debtOf[msg.sender] += amount;
        require(_isHealthy(msg.sender), "unhealthy");
        require(debtToken.transfer(msg.sender, amount), "borrow");
    }

    function repay(uint256 amount) external {
        require(debtToken.transferFrom(msg.sender, address(this), amount), "repay");
        uint256 debt = debtOf[msg.sender];
        debtOf[msg.sender] = amount >= debt ? 0 : debt - amount;
    }

    function liquidate(address user) external {
        require(!_isHealthy(user), "healthy");
        uint256 seized = collateralOf[user];
        collateralOf[user] = 0;
        debtOf[user] = 0;
        require(collateralToken.transfer(msg.sender, seized), "seize");
    }

    function collateralValue(address user) public view returns (uint256) {
        return (collateralOf[user] * price) / 1e18;
    }

    function healthFactor(address user) public view returns (uint256) {
        uint256 debt = debtOf[user];
        if (debt == 0) {
            return type(uint256).max;
        }
        uint256 maxDebt = (collateralValue(user) * collateralFactorBps) / 10000;
        return (maxDebt * 1e18) / debt;
    }

    function _isHealthy(address user) internal view returns (bool) {
        return healthFactor(user) >= 1e18;
    }
}

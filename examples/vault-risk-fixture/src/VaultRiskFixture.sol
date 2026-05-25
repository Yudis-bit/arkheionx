// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
}

interface IStrategy {
    function estimatedTotalAssets() external view returns (uint256);
}

interface IPriceFeed {
    function latestRoundData() external view returns (
        uint80 roundId,
        int256 answer,
        uint256 startedAt,
        uint256 updatedAt,
        uint80 answeredInRound
    );
}

contract VaultRiskFixture {
    IERC20 public immutable asset;
    IStrategy public strategy;
    IPriceFeed public priceFeed;
    address public owner;
    address public treasury;
    address public feeRecipient;
    uint256 public totalSupply;
    uint256 public performanceFee;
    uint256 public managementFee;
    uint256 public withdrawalFee;
    uint256 public depositFee;
    uint256 public totalDebt;
    uint256 public liquidityBuffer;
    uint256 public withdrawalQueue;
    uint256 public cooldown;
    bool public paused;

    mapping(address => uint256) public balanceOf;
    mapping(address => uint256) public pendingWithdraw;

    modifier onlyOwner() {
        require(msg.sender == owner, "NOT_OWNER");
        _;
    }

    modifier whenNotPaused() {
        require(!paused, "PAUSED");
        _;
    }

    constructor(IERC20 asset_, address treasury_, IPriceFeed priceFeed_) {
        asset = asset_;
        owner = msg.sender;
        treasury = treasury_;
        feeRecipient = treasury_;
        priceFeed = priceFeed_;
    }

    function totalAssets() public view returns (uint256) {
        uint256 idle = asset.balanceOf(address(this));
        uint256 strategyAssets = address(strategy) == address(0) ? 0 : strategy.estimatedTotalAssets();
        return idle + strategyAssets;
    }

    function convertToShares(uint256 assets) public view returns (uint256) {
        if (totalSupply == 0 || totalAssets() == 0) {
            return assets;
        }
        return (assets * totalSupply) / totalAssets();
    }

    function convertToAssets(uint256 shares) public view returns (uint256) {
        if (totalSupply == 0) {
            return shares;
        }
        return (shares * totalAssets()) / totalSupply;
    }

    function previewDeposit(uint256 assets) external view returns (uint256) {
        return convertToShares(assets);
    }

    function previewMint(uint256 shares) external view returns (uint256) {
        return convertToAssets(shares);
    }

    function previewWithdraw(uint256 assets) external view returns (uint256) {
        return convertToShares(assets);
    }

    function previewRedeem(uint256 shares) external view returns (uint256) {
        return convertToAssets(shares);
    }

    function maxDeposit(address) external pure returns (uint256) {
        return type(uint256).max;
    }

    function maxMint(address) external pure returns (uint256) {
        return type(uint256).max;
    }

    function maxWithdraw(address owner_) external view returns (uint256) {
        return convertToAssets(balanceOf[owner_]);
    }

    function maxRedeem(address owner_) external view returns (uint256) {
        return balanceOf[owner_];
    }

    function deposit(uint256 assets, address receiver) external whenNotPaused returns (uint256 shares) {
        shares = convertToShares(assets);
        uint256 feeShares = (shares * depositFee) / 10_000;
        require(asset.transferFrom(msg.sender, address(this), assets), "TRANSFER_FROM_FAILED");
        balanceOf[receiver] += shares - feeShares;
        balanceOf[feeRecipient] += feeShares;
        totalSupply += shares;
    }

    function mint(uint256 shares, address receiver) external whenNotPaused returns (uint256 assets) {
        assets = convertToAssets(shares);
        require(asset.transferFrom(msg.sender, address(this), assets), "TRANSFER_FROM_FAILED");
        balanceOf[receiver] += shares;
        totalSupply += shares;
    }

    function withdraw(uint256 assets, address receiver, address owner_) public whenNotPaused returns (uint256 shares) {
        shares = convertToShares(assets);
        require(balanceOf[owner_] >= shares, "INSUFFICIENT_SHARES");
        balanceOf[owner_] -= shares;
        totalSupply -= shares;
        uint256 feeAssets = (assets * withdrawalFee) / 10_000;
        require(asset.transfer(receiver, assets - feeAssets), "TRANSFER_FAILED");
        if (feeAssets != 0) {
            require(asset.transfer(feeRecipient, feeAssets), "FEE_TRANSFER_FAILED");
        }
    }

    function redeem(uint256 shares, address receiver, address owner_) external whenNotPaused returns (uint256 assets) {
        assets = convertToAssets(shares);
        return withdraw(assets, receiver, owner_);
    }

    function requestWithdraw(uint256 shares) external {
        require(balanceOf[msg.sender] >= shares, "INSUFFICIENT_SHARES");
        balanceOf[msg.sender] -= shares;
        pendingWithdraw[msg.sender] += shares;
    }

    function claimWithdraw() external {
        uint256 shares = pendingWithdraw[msg.sender];
        pendingWithdraw[msg.sender] = 0;
        uint256 assets = convertToAssets(shares);
        totalSupply -= shares;
        require(asset.transfer(msg.sender, assets), "TRANSFER_FAILED");
    }

    function cancelWithdraw() external {
        uint256 shares = pendingWithdraw[msg.sender];
        pendingWithdraw[msg.sender] = 0;
        balanceOf[msg.sender] += shares;
    }

    function allocate(uint256 assets) external onlyOwner {
        totalDebt += assets;
    }

    function withdrawFromStrategy(uint256 assets) external onlyOwner {
        totalDebt -= assets;
    }

    function harvest(int256 gain, int256 loss) external onlyOwner {
        if (gain > 0) {
            totalDebt += uint256(gain);
        }
        if (loss > 0) {
            totalDebt -= uint256(loss);
        }
    }

    function rebalance() external onlyOwner {}

    function report(uint256 profit, uint256 loss) external onlyOwner {
        totalDebt = totalDebt + profit - loss;
    }

    function emergencyExit() external onlyOwner {
        paused = true;
    }

    function setStrategy(IStrategy newStrategy) external onlyOwner {
        strategy = newStrategy;
    }

    function setOracle(IPriceFeed newPriceFeed) external onlyOwner {
        priceFeed = newPriceFeed;
    }

    function setFee(uint256 newPerformanceFee, uint256 newManagementFee) external onlyOwner {
        performanceFee = newPerformanceFee;
        managementFee = newManagementFee;
    }

    function setTreasury(address newTreasury) external onlyOwner {
        treasury = newTreasury;
    }

    function setDepositLimit(uint256) external onlyOwner {}

    function setWithdrawLimit(uint256) external onlyOwner {}

    function setMaxLoss(uint256) external onlyOwner {}

    function setSlippage(uint256) external onlyOwner {}

    function pause() external onlyOwner {
        paused = true;
    }

    function unpause() external onlyOwner {
        paused = false;
    }

    function emergencyWithdraw(uint256 assets, address receiver) external onlyOwner {
        require(asset.transfer(receiver, assets), "TRANSFER_FAILED");
    }

    function sweep(address token, address receiver) external onlyOwner {
        IERC20 sweepToken = IERC20(token);
        require(sweepToken.transfer(receiver, sweepToken.balanceOf(address(this))), "SWEEP_FAILED");
    }

    function rescue(address token, address receiver) external onlyOwner {
        IERC20 rescueToken = IERC20(token);
        require(rescueToken.transfer(receiver, rescueToken.balanceOf(address(this))), "RESCUE_FAILED");
    }

    function getPrice() external view returns (int256) {
        (, int256 answer,,,) = priceFeed.latestRoundData();
        return answer;
    }
}

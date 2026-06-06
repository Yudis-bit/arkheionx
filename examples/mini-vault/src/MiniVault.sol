// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
}

contract MiniVault {
    IERC20 public immutable asset;
    address public owner;
    address public treasury;
    uint256 public feeBps;
    uint256 public totalSupply;
    bool public paused;

    mapping(address => uint256) public balanceOf;

    event Deposit(address indexed caller, address indexed owner, uint256 assets, uint256 shares);
    event Withdraw(address indexed caller, address indexed receiver, uint256 assets, uint256 shares);
    event FeeUpdated(uint256 feeBps);
    event Paused(bool paused);

    modifier onlyOwner() {
        require(msg.sender == owner, "NOT_OWNER");
        _;
    }

    modifier whenNotPaused() {
        require(!paused, "PAUSED");
        _;
    }

    constructor(IERC20 asset_, address treasury_) {
        require(address(asset_) != address(0), "ASSET_ZERO");
        require(treasury_ != address(0), "TREASURY_ZERO");
        asset = asset_;
        owner = msg.sender;
        treasury = treasury_;
    }

    function totalAssets() public view returns (uint256) {
        return asset.balanceOf(address(this));
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

    function deposit(uint256 assets, address receiver) external whenNotPaused returns (uint256 shares) {
        require(receiver != address(0), "RECEIVER_ZERO");
        require(assets > 0, "ZERO_ASSETS");

        shares = convertToShares(assets);
        uint256 fee = (shares * feeBps) / 10_000;
        uint256 userShares = shares - fee;

        require(asset.transferFrom(msg.sender, address(this), assets), "TRANSFER_FROM_FAILED");

        totalSupply += shares;
        balanceOf[receiver] += userShares;
        if (fee != 0) {
            balanceOf[treasury] += fee;
        }

        emit Deposit(msg.sender, receiver, assets, userShares);
    }

    function withdraw(uint256 assets, address receiver) external whenNotPaused returns (uint256 shares) {
        require(receiver != address(0), "RECEIVER_ZERO");
        require(assets > 0, "ZERO_ASSETS");

        shares = convertToShares(assets);
        require(balanceOf[msg.sender] >= shares, "INSUFFICIENT_SHARES");

        balanceOf[msg.sender] -= shares;
        totalSupply -= shares;

        require(asset.transfer(receiver, assets), "TRANSFER_FAILED");

        emit Withdraw(msg.sender, receiver, assets, shares);
    }

    function setFee(uint256 newFeeBps) external onlyOwner {
        require(newFeeBps <= 500, "FEE_TOO_HIGH");
        feeBps = newFeeBps;
        emit FeeUpdated(newFeeBps);
    }

    function pause() external onlyOwner {
        paused = true;
        emit Paused(true);
    }

    function unpause() external onlyOwner {
        paused = false;
        emit Paused(false);
    }
}

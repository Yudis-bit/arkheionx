// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IERC20Min {
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
}

/// @notice Generic external yield-strategy connector. The vault trusts the
/// connector to report the underlying balance and to route value out.
interface IStrategy {
    function balanceOfUnderlying() external view returns (uint256);
    function withdrawTo(address to, uint256 amount) external;
}

/// @title YieldVault
/// @notice Generic ERC4626-style share vault with a performance fee on exit, a
/// transfer blocklist, and an external yield-strategy connector. Synthetic,
/// generic patterns used to exercise ArkheionX share-math / preview, fee,
/// blocklist, and connector detection in one place. Local/static demo only. It
/// contains no planted vulnerabilities and is not an exploit target — it exists
/// to exercise detection, not to hide a real bug.
contract YieldVault {
    IERC20Min public immutable asset;
    IStrategy public strategy; // connector / adapter to an external protocol
    address public owner;
    address public feeRecipient;
    uint256 public performanceFeeBps; // fee taken on exit
    uint256 public totalShares;

    mapping(address => uint256) public shares;
    mapping(address => bool) public frozen; // blocklist / freeze list

    modifier onlyOwner() {
        require(msg.sender == owner, "not owner");
        _;
    }

    constructor(IERC20Min asset_, IStrategy strategy_) {
        asset = asset_;
        strategy = strategy_;
        owner = msg.sender;
        feeRecipient = msg.sender;
    }

    /// @notice Total assets are read from the external strategy connector.
    function totalAssets() public view returns (uint256) {
        return strategy.balanceOfUnderlying();
    }

    /// @notice ERC4626-style share math. Reviewer should confirm conversion is
    /// consistent across rounding, first-deposit, and donation scenarios.
    function convertToShares(uint256 assets) public view returns (uint256) {
        return totalShares == 0 ? assets : (assets * totalShares) / totalAssets();
    }

    function convertToAssets(uint256 shareAmount) public view returns (uint256) {
        return totalShares == 0 ? shareAmount : (shareAmount * totalAssets()) / totalShares;
    }

    /// @notice Preview the shares burned for an asset withdrawal. Reviewer should
    /// confirm preview matches the realised amount of the matching withdraw.
    function previewWithdraw(uint256 assets) public view returns (uint256) {
        return convertToShares(assets);
    }

    /// @notice Preview the assets returned for a share redemption.
    function previewRedeem(uint256 shareAmount) public view returns (uint256) {
        return convertToAssets(shareAmount);
    }

    function maxWithdraw(address account) public view returns (uint256) {
        return convertToAssets(shares[account]);
    }

    /// @notice Value entry: pull asset into the strategy and mint shares.
    function deposit(uint256 amount) external returns (uint256 minted) {
        require(!frozen[msg.sender], "frozen");
        minted = convertToShares(amount);
        shares[msg.sender] += minted;
        totalShares += minted;
        require(asset.transferFrom(msg.sender, address(strategy), amount), "pull failed");
    }

    /// @notice Value exit: burn shares, take a performance fee, and route the
    /// net amount out through the connector. Gated by the blocklist. Reviewer
    /// should confirm the fee base, the blocklist check, and that the connector
    /// payout matches the share accounting.
    function withdraw(uint256 shareAmount) external returns (uint256 amount) {
        require(!frozen[msg.sender], "frozen");
        amount = convertToAssets(shareAmount);
        shares[msg.sender] -= shareAmount;
        totalShares -= shareAmount;
        uint256 fee = (amount * performanceFeeBps) / 10000;
        strategy.withdrawTo(feeRecipient, fee);
        strategy.withdrawTo(msg.sender, amount - fee);
    }

    /// @notice Privileged: rotate the strategy connector. Admin trust boundary.
    function setStrategy(IStrategy strategy_) external onlyOwner {
        strategy = strategy_;
    }

    /// @notice Privileged: set the performance fee in basis points.
    function setPerformanceFee(uint256 bps) external onlyOwner {
        performanceFeeBps = bps;
    }

    /// @notice Privileged: freeze or unfreeze an account on the blocklist.
    function setFrozen(address account, bool isFrozen) external onlyOwner {
        frozen[account] = isFrozen;
    }
}

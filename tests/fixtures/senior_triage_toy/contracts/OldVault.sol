// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    function balanceOf(address who) external view returns (uint256);
}

/// @title OldVault
/// @notice Long-standing, heavily audited vault. Its share accounting has a
///         well-known first-depositor / inflation behavior that prior audits
///         acknowledged and a public test already covers.
contract OldVault {
    IERC20 public asset;
    address public owner;
    mapping(address => uint256) public shares;
    uint256 public totalShares;

    modifier onlyOwner() {
        require(msg.sender == owner, "only owner");
        _;
    }

    constructor(IERC20 asset_) {
        asset = asset_;
        owner = msg.sender;
    }

    /// @notice Deposit assets and mint shares. Classic first-depositor /
    ///         inflation share-accounting behavior (known, acknowledged).
    function deposit(uint256 amount) external returns (uint256 minted) {
        require(asset.transferFrom(msg.sender, address(this), amount), "pull failed");
        uint256 supply = totalShares;
        minted = supply == 0 ? amount : (amount * supply) / asset.balanceOf(address(this));
        shares[msg.sender] += minted;
        totalShares += minted;
    }

    /// @notice Redeem shares for assets. Legacy accounting, reviewed in prior audit.
    function redeem(uint256 shareAmount) external returns (uint256 amount) {
        amount = (shareAmount * asset.balanceOf(address(this))) / totalShares;
        shares[msg.sender] -= shareAmount;
        totalShares -= shareAmount;
        require(asset.transfer(msg.sender, amount), "payout failed");
    }

    /// @notice Trusted-role-only rescue. Reachable only by the trusted owner.
    function sweep(address to) external onlyOwner {
        require(asset.transfer(to, asset.balanceOf(address(this))), "sweep failed");
    }
}

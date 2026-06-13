// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {MockToken} from "./MockToken.sol";

/// @title Vault
/// @notice A minimal share vault used by the evidence-judge fixture. Value enters
///         through `deposit` and exits through `withdraw`. `setFeeRecipient` is an
///         owner-gated admin setter. This fixture has no planted vulnerability; it
///         exists to exercise the agent-task and evidence-judge workflow.
contract Vault {
    MockToken public immutable asset;
    address public owner;
    address public feeRecipient;

    uint256 public totalShares;
    mapping(address => uint256) public shares;

    error NotOwner();
    error InsufficientShares();

    modifier onlyOwner() {
        if (msg.sender != owner) revert NotOwner();
        _;
    }

    constructor(MockToken _asset) {
        asset = _asset;
        owner = msg.sender;
        feeRecipient = msg.sender;
    }

    /// @notice Value entry: pull `amount` of asset and mint proportional shares.
    function deposit(uint256 amount) external returns (uint256 minted) {
        uint256 supply = totalShares;
        uint256 bal = asset.balanceOf(address(this));
        minted = (supply == 0 || bal == 0) ? amount : (amount * supply) / bal;
        require(asset.transferFrom(msg.sender, address(this), amount), "transfer");
        shares[msg.sender] += minted;
        totalShares += minted;
    }

    /// @notice Value exit: burn `shareAmount` and return the proportional asset.
    function withdraw(uint256 shareAmount) external returns (uint256 amount) {
        if (shares[msg.sender] < shareAmount) revert InsufficientShares();
        uint256 bal = asset.balanceOf(address(this));
        amount = (shareAmount * bal) / totalShares;
        shares[msg.sender] -= shareAmount;
        totalShares -= shareAmount;
        require(asset.transfer(msg.sender, amount), "transfer");
    }

    /// @notice Owner-gated admin setter.
    function setFeeRecipient(address newRecipient) external onlyOwner {
        feeRecipient = newRecipient;
    }
}

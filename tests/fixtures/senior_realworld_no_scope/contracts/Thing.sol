// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
}

/// @title Thing
/// @notice A value-bearing contract with no scope/program context provided.
///         Triage should refuse to pursue without a scope file.
contract Thing {
    IERC20 public asset;
    mapping(address => uint256) public bal;

    function deposit(uint256 amount) external {
        require(asset.transferFrom(msg.sender, address(this), amount), "pull failed");
        bal[msg.sender] += amount;
    }

    function withdraw(uint256 amount) external {
        bal[msg.sender] -= amount;
        require(asset.transfer(msg.sender, amount), "payout failed");
    }
}

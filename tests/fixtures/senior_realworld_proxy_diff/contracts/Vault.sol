// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
}

/// @title Vault
/// @notice Value-bearing vault deployed behind an upgradeable proxy. The source
///         here is one implementation; the live proxy may point elsewhere.
contract Vault {
    IERC20 public asset;
    mapping(address => uint256) public balanceOfUser;

    function withdraw(uint256 amount) external {
        balanceOfUser[msg.sender] -= amount;
        require(asset.transfer(msg.sender, amount), "payout failed");
    }
}

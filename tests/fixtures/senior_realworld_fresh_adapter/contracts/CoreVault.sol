// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
}

/// @title CoreVault
/// @notice Long-standing core vault. Reviewed in the prior audit baseline.
contract CoreVault {
    IERC20 public asset;
    mapping(address => uint256) public balanceOfUser;

    function deposit(uint256 amount) external {
        require(asset.transferFrom(msg.sender, address(this), amount), "pull failed");
        balanceOfUser[msg.sender] += amount;
    }

    function withdraw(uint256 amount) external {
        balanceOfUser[msg.sender] -= amount;
        require(asset.transfer(msg.sender, amount), "payout failed");
    }
}

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    function balanceOf(address a) external view returns (uint256);
}

contract PoolIsolation {
    IERC20 public asset;
    mapping(uint256 => mapping(address => uint256)) public balanceOfPool;

    function deposit(uint256 poolId, uint256 amount) external {
        asset.transferFrom(msg.sender, address(this), amount);
        balanceOfPool[poolId][msg.sender] += amount;
    }

    function withdraw(uint256 poolId, uint256 amount) external {
        balanceOfPool[poolId][msg.sender] -= amount;
        asset.transfer(msg.sender, amount);
    }
}

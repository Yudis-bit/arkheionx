// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    function balanceOf(address a) external view returns (uint256);
}

contract ClaimQueue {
    IERC20 public asset;
    mapping(uint256 => uint256) public amountOf;
    mapping(uint256 => bool) public claimed;
    uint256 public queueIndex;

    function requestWithdrawal(uint256 amount) external returns (uint256 id) {
        id = queueIndex++;
        amountOf[id] = amount;
    }

    function claimWithdrawal(uint256 id) external {
        uint256 amount = amountOf[id];
        asset.transfer(msg.sender, amount);
        claimed[id] = true;
    }
}

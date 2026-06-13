// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    function balanceOf(address a) external view returns (uint256);
}

contract Pool {
    IERC20 public token;
    mapping(address => uint256) public balanceOfUser;

    function deposit(uint256 amount) external {
        token.transferFrom(msg.sender, address(this), amount);
        balanceOfUser[msg.sender] += amount;
    }

    function withdraw(uint256 amount) external {
        balanceOfUser[msg.sender] -= amount;
        token.transfer(msg.sender, amount);
    }
}

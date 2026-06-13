// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    function balanceOf(address a) external view returns (uint256);
}

contract Vault {
    IERC20 public asset;
    function withdraw(uint256 amount) external { asset.transfer(msg.sender, amount); }
}

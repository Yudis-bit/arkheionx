// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    function balanceOf(address a) external view returns (uint256);
}

contract ShareVault {
    IERC20 public asset;
    mapping(address => uint256) public shares;
    uint256 public totalShares;

    function deposit(uint256 amount) external returns (uint256 minted) {
        asset.transferFrom(msg.sender, address(this), amount);
        minted = amount;
        shares[msg.sender] += minted;
        totalShares += minted;
    }

    function withdraw(uint256 amount) external {
        shares[msg.sender] -= amount;
        totalShares -= amount;
        asset.transfer(msg.sender, amount);
    }
}

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    function balanceOf(address a) external view returns (uint256);
}

contract FeeDispatcher {
    IERC20 public asset;
    address public feeRecipient;
    uint256 public commissionBps;

    function distribute(uint256 amount) external {
        uint256 fee = amount * commissionBps / 10000;
        asset.transfer(feeRecipient, fee);
        asset.transfer(msg.sender, amount - fee);
    }
}

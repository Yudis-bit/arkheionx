// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    function balanceOf(address a) external view returns (uint256);
}

interface IYieldSource { function pull(uint256 amount) external returns (uint256); }

contract Adapter {
    IERC20 public asset;
    IYieldSource public source;

    function withdrawTo(address to, uint256 amount) external returns (uint256 got) {
        got = source.pull(amount);
        require(asset.transfer(to, got), "transfer failed");
    }
}

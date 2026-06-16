// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    function balanceOf(address a) external view returns (uint256);
}

contract Treasury {
    IERC20 public asset;
    address public owner;

    modifier onlyOwner() { require(msg.sender == owner, "not owner"); _; }

    function sweep(address to, uint256 amount) external onlyOwner {
        asset.transfer(to, amount);
    }

    function balance() external view returns (uint256) {
        return asset.balanceOf(address(this));
    }
}

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function balanceOf(address a) external view returns (uint256);
}

contract BodyAuth {
    IERC20 public asset;
    address public owner;
    uint256 public value;

    function setValue(uint256 newValue) external {
        require(msg.sender == owner, "ONLY_OWNER");
        value = newValue;
    }

    function withdraw(address to, uint256 amount) external {
        require(msg.sender == owner, "ONLY_OWNER");
        asset.transfer(to, amount);
    }
}

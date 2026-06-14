// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function balanceOf(address a) external view returns (uint256);
}

contract MixedModifiers {
    IERC20 public asset;
    address public owner;
    bool public paused;
    uint256 public value;

    modifier onlyOwner() {
        require(msg.sender == owner, "ONLY_OWNER");
        _;
    }

    modifier whenNotPaused() {
        require(!paused, "PAUSED");
        _;
    }

    function setValue(uint256 newValue) external whenNotPaused onlyOwner {
        value = newValue;
    }

    function withdraw(address to, uint256 amount) external whenNotPaused onlyOwner {
        asset.transfer(to, amount);
    }
}

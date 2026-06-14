// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function balanceOf(address a) external view returns (uint256);
}

contract NonAuthOnly {
    IERC20 public asset;
    bool public paused;
    uint256 public value;

    modifier whenNotPaused() {
        require(!paused, "PAUSED");
        _;
    }

    function setValue(uint256 newValue) external whenNotPaused {
        value = newValue;
    }

    function withdraw(address to, uint256 amount) external whenNotPaused {
        asset.transfer(to, amount);
    }
}

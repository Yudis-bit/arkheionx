// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function balanceOf(address a) external view returns (uint256);
}

contract UnknownGate {
    IERC20 public asset;
    uint256 public value;

    modifier customGate() {
        _mystery();
        _;
    }

    function _mystery() internal view {}

    function setValue(uint256 newValue) external customGate {
        value = newValue;
    }

    function withdraw(address to, uint256 amount) external customGate {
        asset.transfer(to, amount);
    }
}

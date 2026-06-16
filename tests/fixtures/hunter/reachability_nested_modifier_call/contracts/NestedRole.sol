// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function balanceOf(address a) external view returns (uint256);
}

contract NestedRole {
    IERC20 public asset;
    address public admin;
    uint256 public value;

    modifier onlyAdmin() {
        _checkAdmin();
        _;
    }

    function _checkAdmin() internal view {
        require(msg.sender == admin, "ONLY_ADMIN");
    }

    function setValue(uint256 newValue) external onlyAdmin {
        value = newValue;
    }

    function withdraw(address to, uint256 amount) external onlyAdmin {
        asset.transfer(to, amount);
    }
}

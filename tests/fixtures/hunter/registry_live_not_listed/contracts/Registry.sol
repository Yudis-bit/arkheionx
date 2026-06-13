// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract Registry {
    address[] public pools;
    function getPools() external view returns (address[] memory) { return pools; }
    function poolCount() external view returns (uint256) { return pools.length; }
}

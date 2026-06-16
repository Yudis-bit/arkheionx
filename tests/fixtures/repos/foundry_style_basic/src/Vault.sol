pragma solidity ^0.8.20;

contract Vault {
    uint256 public total;

    function deposit(uint256 amount) external {
        total += amount;
    }
}

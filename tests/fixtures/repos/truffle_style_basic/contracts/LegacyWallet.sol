pragma solidity ^0.8.20;

contract LegacyWallet {
    uint256 public sequence;

    function execute() external {
        sequence += 1;
    }
}

pragma solidity ^0.8.20;

contract Wallet {
    uint256 public nonce;

    function execute() external {
        nonce += 1;
    }
}

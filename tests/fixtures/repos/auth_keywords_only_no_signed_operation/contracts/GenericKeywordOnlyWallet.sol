pragma solidity ^0.8.20;

contract GenericKeywordOnlyWallet {
    address public owner;
    uint256 public threshold;
    uint256 public nonce;

    constructor() {
        owner = msg.sender;
        threshold = 1;
    }

    function execute(address destination, bytes calldata data) external {
        require(msg.sender == owner, "owner");
        nonce += 1;
        (bool ok,) = destination.call(data);
        require(ok, "call");
    }
}

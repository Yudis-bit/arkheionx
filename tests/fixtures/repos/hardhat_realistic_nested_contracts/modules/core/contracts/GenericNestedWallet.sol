pragma solidity ^0.8.20;

contract GenericNestedWallet {
    mapping(address => bool) public owners;
    uint256 public nonce;

    constructor() {
        owners[msg.sender] = true;
    }

    function execute(address destination, uint256 value, bytes calldata data) external {
        require(owners[msg.sender], "owner");
        nonce += 1;
        (bool ok,) = destination.call{value: value}(data);
        require(ok, "call");
    }
}

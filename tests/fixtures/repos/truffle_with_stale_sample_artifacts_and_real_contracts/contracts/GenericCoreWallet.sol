pragma solidity ^0.8.20;

contract GenericCoreWallet {
    address public owner;
    uint256 public sequence;

    constructor() {
        owner = msg.sender;
    }

    function execute(address destination, uint256 value, bytes calldata data) external {
        require(msg.sender == owner, "owner");
        sequence += 1;
        (bool ok,) = destination.call{value: value}(data);
        require(ok, "call");
    }
}

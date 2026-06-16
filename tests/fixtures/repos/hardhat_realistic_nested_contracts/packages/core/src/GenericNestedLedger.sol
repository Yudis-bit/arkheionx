pragma solidity ^0.8.20;

contract GenericNestedLedger {
    mapping(address => uint256) public credit;

    function deposit() external payable {
        credit[msg.sender] += msg.value;
    }
}

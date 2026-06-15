pragma solidity ^0.8.20;

contract GenericFactoryAccountTakeover {
    address public owner;

    function initialize(address nextOwner) external {
        owner = nextOwner;
    }
}

contract GenericFactoryInitTakeover {
    function deploy(bytes32 salt) external returns (address) {
        GenericFactoryAccountTakeover account = new GenericFactoryAccountTakeover{salt: salt}();
        return address(account);
    }
}

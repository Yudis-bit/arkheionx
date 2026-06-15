pragma solidity ^0.8.20;

contract GenericFactoryAccountSafe {
    bool private initialized;
    address public owner;

    function initialize(address nextOwner) external {
        require(!initialized);
        initialized = true;
        owner = nextOwner;
    }
}

contract GenericFactoryCreate2Safe {
    function deploy(address owner, address controller) external returns (address) {
        bytes32 salt = keccak256(abi.encode(owner, controller));
        GenericFactoryAccountSafe account = new GenericFactoryAccountSafe{salt: salt}();
        account.initialize(owner);
        return address(account);
    }
}

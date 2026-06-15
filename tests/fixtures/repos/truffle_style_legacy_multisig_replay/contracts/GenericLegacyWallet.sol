pragma solidity ^0.8.20;

contract GenericLegacyWallet {
    mapping(address => bool) public owners;
    uint256 public threshold = 2;
    uint256 public sequence;

    function execute(
        address destination,
        uint256 value,
        bytes calldata data,
        uint8[] calldata v,
        bytes32[] calldata r,
        bytes32[] calldata s
    ) external {
        bytes32 operationHash = keccak256(
            abi.encode(destination, value, keccak256(data), sequence)
        );
        address lastSigner = address(0);
        uint256 validSigners;
        for (uint256 index; index < v.length; index++) {
            address signer = ecrecover(operationHash, v[index], r[index], s[index]);
            require(signer != address(0));
            require(owners[signer]);
            require(signer > lastSigner);
            lastSigner = signer;
            validSigners += 1;
        }
        require(validSigners >= threshold);
        sequence += 1;
        (bool success,) = destination.call{value: value}(data);
        require(success);
    }
}

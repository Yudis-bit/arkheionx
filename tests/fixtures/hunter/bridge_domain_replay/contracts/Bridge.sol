// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    function balanceOf(address a) external view returns (uint256);
}

contract Bridge {
    IERC20 public asset;
    mapping(bytes32 => bool) public processed;
    uint256 public domainId;

    function relayMessage(bytes32 messageId, address to, uint256 amount) external {
        require(!processed[messageId], "replayed");
        asset.transfer(to, amount);
        processed[messageId] = true;
    }
}

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// Generic synthetic fixture: a cross-chain bridge whose destination side mints on
// an incoming message but never records or checks that the message id was already
// processed. The same message can be replayed to mint repeatedly, so destination
// minted supply exceeds source locked/burned supply. No protocol/token name is
// encoded; this is a generic cross-chain supply-conservation shape.

contract BridgedToken {
    mapping(address => uint256) public balanceOf;
    uint256 public totalSupply;

    function mint(address to, uint256 amount) external {
        balanceOf[to] += amount;
        totalSupply += amount;
    }

    function burn(address from, uint256 amount) external {
        require(balanceOf[from] >= amount, "balance");
        balanceOf[from] -= amount;
        totalSupply -= amount;
    }
}

contract SourceBridge {
    BridgedToken public token;
    mapping(bytes32 => uint256) public locked;

    function lock(bytes32 msgId, uint256 amount) external {
        token.burn(msg.sender, amount);
        locked[msgId] = amount;
    }
}

contract DestinationBridge {
    BridgedToken public token;
    mapping(bytes32 => bool) public processed;

    // BUG: receiveMessage neither checks `processed[msgId]` nor sets it, so the
    // same cross-chain message id can be replayed to mint the amount again and
    // again. Destination minted supply is not conserved against source locked.
    function receiveMessage(bytes32 msgId, address to, uint256 amount) external {
        token.mint(to, amount);
    }
}
